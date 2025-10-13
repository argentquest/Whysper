"""
MCP Request/Response History Service

This service handles logging MCP server requests and responses to files
for persistent storage and debugging purposes. Each MCP session gets
a unique GUID-based filename following the same pattern as the frontend.
"""

import os
import json
import uuid
from datetime import datetime
from typing import Dict, Any, Optional, Tuple, List
from pathlib import Path

from common.logger import get_logger

logger = get_logger(__name__)


class MCPHistoryService:
    """
    Manages MCP request/response history logging to files.
    
    Features:
    - Creates unique GUID-based filenames for each MCP session
    - Saves complete request/response structure including metadata
    - Updates files as new requests/responses are added
    - Creates history directory if it doesn't exist
    - Follows the same pattern as the frontend history service
    """
    
    def __init__(self, history_dir: str = None):
        """Initialize the MCP history service with a target directory."""
        if history_dir is None:
            # Default to history/mcp folder in project root
            project_root = Path(__file__).parent.parent.parent
            history_dir = project_root / "history" / "mcp"
        
        self.history_dir = Path(history_dir)
        self.history_dir.mkdir(parents=True, exist_ok=True)
        
        # Track session GUIDs and start timestamps
        self._session_guids: Dict[str, str] = {}
        self._session_start_times: Dict[str, str] = {}
        
        logger.info(f"MCP history service initialized with directory: {self.history_dir}")
    
    def _ensure_session_record(self, session_id: str) -> Tuple[str, str]:
        """
        Ensure we have tracking data for this MCP session.

        Returns:
            Tuple[str, str]: (guid, start_time_iso)
        """
        if session_id not in self._session_guids:
            session_guid = str(uuid.uuid4())
            start_time_iso = datetime.now().isoformat()
            self._session_guids[session_id] = session_guid
            self._session_start_times[session_id] = start_time_iso
            logger.info(f"Created new GUID {session_guid} for MCP session {session_id}")
        else:
            # Ensure start time exists even if GUID already tracked
            if session_id not in self._session_start_times:
                start_time_iso = datetime.now().isoformat()
                self._session_start_times[session_id] = start_time_iso
                logger.info(f"Reconstructed start time for MCP session {session_id}")

        return (
            self._session_guids[session_id],
            self._session_start_times[session_id],
        )

    def get_or_create_session_guid(self, session_id: str) -> str:
        """
        Get existing GUID for MCP session or create a new one.
        
        Args:
            session_id: The session ID (can be WebSocket connection ID or request ID)
            
        Returns:
            str: GUID for this session
        """
        guid, _ = self._ensure_session_record(session_id)
        return guid

    def get_session_start_time(self, session_id: str) -> str:
        """
        Retrieve the ISO timestamp for when the session started.

        Args:
            session_id: The session ID

        Returns:
            str: ISO formatted timestamp for the session start
        """
        _, start_time_iso = self._ensure_session_record(session_id)
        return start_time_iso

    def _timestamp_prefix(self, timestamp_iso: str) -> str:
        """
        Convert an ISO timestamp into a filesystem-friendly prefix.

        Args:
            timestamp_iso: ISO formatted timestamp string

        Returns:
            str: Timestamp formatted as YYYYMMDD-HHMMSS
        """
        try:
            dt = datetime.fromisoformat(timestamp_iso)
            return dt.strftime("%Y%m%d-%H%M%S")
        except Exception:
            # Fallback: strip characters that are invalid for filenames
            return (
                timestamp_iso.replace(":", "")
                .replace("-", "")
                .replace("T", "_")
                .split(".")[0]
            )
    
    def get_history_filepath(self, session_id: str) -> Path:
        """Get the file path for a session's history."""
        guid, start_time_iso = self._ensure_session_record(session_id)
        timestamp_prefix = self._timestamp_prefix(start_time_iso)
        return self.history_dir / f"{timestamp_prefix}_{guid}.json"
    
    def log_request_response(
        self, 
        session_id: str, 
        request_data: Dict[str, Any], 
        response_data: Dict[str, Any],
        tool_name: str = None,
        metadata: Dict[str, Any] = None
    ) -> bool:
        """
        Log a request/response pair to the session history file.
        
        Args:
            session_id: The session ID (WebSocket connection ID or request ID)
            request_data: The complete request data
            response_data: The complete response data
            tool_name: Optional name of the tool that was called
            metadata: Optional metadata about the request/response
            
        Returns:
            bool: True if logged successfully, False otherwise
        """
        try:
            guid = self.get_or_create_session_guid(session_id)
            start_time_iso = self.get_session_start_time(session_id)
            filepath = self.get_history_filepath(session_id)
            
            # Create request/response entry
            entry = {
                "timestamp": datetime.now().isoformat(),
                "tool_name": tool_name,
                "request": request_data,
                "response": response_data,
                "metadata": metadata or {}
            }
            
            # Load existing session data or create new
            session_data = None
            if filepath.exists():
                try:
                    with open(filepath, 'r', encoding='utf-8') as f:
                        session_data = json.load(f)
                except Exception as e:
                    logger.warning(f"Could not read existing session file {filepath}: {e}")
            
            # Initialize session data if needed
            if session_data is None:
                session_data = {
                    "session_guid": guid,
                    "session_id": session_id,
                    "created_at": start_time_iso,
                    "last_updated": datetime.now().isoformat(),
                    "request_count": 0,
                    "metadata": {},
                    "requests": []
                }
            
            # Add new entry
            session_data["requests"].append(entry)
            session_data["request_count"] = len(session_data["requests"])
            session_data["last_updated"] = datetime.now().isoformat()
            
            # Update metadata if provided
            if metadata:
                session_data["metadata"].update(metadata)
            
            # Write updated session data
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(session_data, f, indent=2, ensure_ascii=False)
            
            logger.debug(f"Logged MCP request/response: {filepath} (tool: {tool_name})")
            return True
            
        except Exception as e:
            logger.error(f"Failed to log MCP request/response for session {session_id}: {e}")
            return False
    
    def load_session_history(self, session_id: str) -> Optional[Dict[str, Any]]:
        """
        Load MCP session history from file.
        
        Args:
            session_id: The session ID
            
        Returns:
            Dict containing session history or None if not found
        """
        try:
            filepath = self.get_history_filepath(session_id)
            
            if not filepath.exists():
                logger.debug(f"No history file found for MCP session {session_id}")
                return None
            
            with open(filepath, 'r', encoding='utf-8') as f:
                session_data = json.load(f)

            # Align in-memory tracking with persisted metadata
            persisted_guid = session_data.get("session_guid")
            if persisted_guid:
                self._session_guids[session_id] = persisted_guid
            persisted_created_at = session_data.get("created_at")
            if persisted_created_at:
                self._session_start_times[session_id] = persisted_created_at
            
            logger.debug(f"Loaded MCP session history: {filepath}")
            return session_data
            
        except Exception as e:
            logger.error(f"Failed to load MCP session history for {session_id}: {e}")
            return None
    
    def list_session_histories(self) -> List[Dict[str, Any]]:
        """
        List all MCP session history files with basic info.
        
        Returns:
            List of dictionaries containing session metadata
        """
        histories = []
        
        try:
            for filepath in self.history_dir.glob("*.json"):
                try:
                    with open(filepath, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                    
                    histories.append({
                        "guid": data.get("session_guid"),
                        "session_id": data.get("session_id"),
                        "created_at": data.get("created_at"),
                        "last_updated": data.get("last_updated"),
                        "request_count": data.get("request_count", 0),
                        "filename": filepath.name
                    })
                    
                except Exception as e:
                    logger.warning(f"Could not read MCP session file {filepath}: {e}")
            
            # Sort by last_updated descending
            histories.sort(key=lambda x: x.get("last_updated", ""), reverse=True)
            
        except Exception as e:
            logger.error(f"Failed to list MCP session histories: {e}")
        
        return histories


# Global instance
mcp_history_service = MCPHistoryService()
