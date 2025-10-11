"""
Conversation history logging service.

This service handles saving conversation messages to files for persistent storage
and debugging purposes. Each conversation gets a unique GUID-based filename.
"""
import os
import json
import uuid
from datetime import datetime
from typing import Dict, Any, List, Optional, Tuple
from pathlib import Path

from common.logger import get_logger

logger = get_logger(__name__)


class HistoryService:
    """
    Manages conversation history logging to files.
    
    Features:
    - Creates unique GUID-based filenames for each conversation
    - Saves complete message structure including metadata
    - Updates files as new messages are added
    - Creates history directory if it doesn't exist
    """
    
    def __init__(self, history_dir: str = None):
        """Initialize the history service with a target directory."""
        if history_dir is None:
            # Default to history folder in project root
            project_root = Path(__file__).parent.parent.parent.parent
            history_dir = project_root / "history"
        
        self.history_dir = Path(history_dir)
        self.history_dir.mkdir(exist_ok=True)
        
        # Track conversation GUIDs and start timestamps
        self._conversation_guids: Dict[str, str] = {}
        self._conversation_start_times: Dict[str, str] = {}
        
        logger.info(f"History service initialized with directory: {self.history_dir}")
    
    def _ensure_conversation_record(self, conversation_id: str) -> Tuple[str, str]:
        """
        Ensure we have tracking data for this conversation.

        Returns:
            Tuple[str, str]: (guid, start_time_iso)
        """
        if conversation_id not in self._conversation_guids:
            conversation_guid = str(uuid.uuid4())
            start_time_iso = datetime.now().isoformat()
            self._conversation_guids[conversation_id] = conversation_guid
            self._conversation_start_times[conversation_id] = start_time_iso
            logger.info(f"Created new GUID {conversation_guid} for conversation {conversation_id}")
        else:
            # Ensure start time exists even if GUID already tracked
            if conversation_id not in self._conversation_start_times:
                start_time_iso = datetime.now().isoformat()
                self._conversation_start_times[conversation_id] = start_time_iso
                logger.info(f"Reconstructed start time for conversation {conversation_id}")

        return (
            self._conversation_guids[conversation_id],
            self._conversation_start_times[conversation_id],
        )

    def get_or_create_conversation_guid(self, conversation_id: str) -> str:
        """
        Get existing GUID for conversation or create a new one.
        
        Args:
            conversation_id: The conversation ID from the frontend
            
        Returns:
            str: GUID for this conversation
        """
        guid, _ = self._ensure_conversation_record(conversation_id)
        return guid

    def get_conversation_start_time(self, conversation_id: str) -> str:
        """
        Retrieve the ISO timestamp for when the conversation started.

        Args:
            conversation_id: The conversation ID from the frontend

        Returns:
            str: ISO formatted timestamp for the conversation start
        """
        _, start_time_iso = self._ensure_conversation_record(conversation_id)
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
    
    def get_history_filepath(self, conversation_id: str) -> Path:
        """Get the file path for a conversation's history."""
        guid, start_time_iso = self._ensure_conversation_record(conversation_id)
        timestamp_prefix = self._timestamp_prefix(start_time_iso)
        return self.history_dir / f"{timestamp_prefix}_{guid}.json"
    
    def save_conversation_history(
        self, 
        conversation_id: str, 
        messages: List[Dict[str, Any]], 
        metadata: Dict[str, Any] = None
    ) -> bool:
        """
        Save complete conversation history to file.
        
        Args:
            conversation_id: The conversation ID from frontend
            messages: List of message objects with full structure
            metadata: Optional metadata about the conversation
            
        Returns:
            bool: True if saved successfully, False otherwise
        """
        try:
            guid = self.get_or_create_conversation_guid(conversation_id)
            start_time_iso = self.get_conversation_start_time(conversation_id)
            filepath = self.get_history_filepath(conversation_id)
            
            # Create comprehensive history structure
            history_data = {
                "conversation_guid": guid,
                "conversation_id": conversation_id,
                "created_at": start_time_iso,
                "last_updated": datetime.now().isoformat(),
                "message_count": len(messages),
                "metadata": metadata or {},
                "messages": messages
            }
            
            # Load existing data to preserve created_at timestamp
            if filepath.exists():
                try:
                    with open(filepath, 'r', encoding='utf-8') as f:
                        existing_data = json.load(f)
                        existing_created_at = existing_data.get("created_at")
                        if existing_created_at:
                            history_data["created_at"] = existing_created_at
                            self._conversation_start_times[conversation_id] = existing_created_at
                except Exception as e:
                    logger.warning(f"Could not read existing history file {filepath}: {e}")
            
            # Write updated history
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(history_data, f, indent=2, ensure_ascii=False)
            
            logger.debug(f"Saved conversation history: {filepath} ({len(messages)} messages)")
            return True
            
        except Exception as e:
            logger.error(f"Failed to save conversation history for {conversation_id}: {e}")
            return False
    
    def load_conversation_history(self, conversation_id: str) -> Optional[Dict[str, Any]]:
        """
        Load conversation history from file.
        
        Args:
            conversation_id: The conversation ID
            
        Returns:
            Dict containing conversation history or None if not found
        """
        try:
            filepath = self.get_history_filepath(conversation_id)
            
            if not filepath.exists():
                logger.debug(f"No history file found for conversation {conversation_id}")
                return None
            
            with open(filepath, 'r', encoding='utf-8') as f:
                history_data = json.load(f)

            # Align in-memory tracking with persisted metadata
            persisted_guid = history_data.get("conversation_guid")
            if persisted_guid:
                self._conversation_guids[conversation_id] = persisted_guid
            persisted_created_at = history_data.get("created_at")
            if persisted_created_at:
                self._conversation_start_times[conversation_id] = persisted_created_at
            
            logger.debug(f"Loaded conversation history: {filepath}")
            return history_data
            
        except Exception as e:
            logger.error(f"Failed to load conversation history for {conversation_id}: {e}")
            return None
    
    def list_conversation_histories(self) -> List[Dict[str, Any]]:
        """
        List all conversation history files with basic info.
        
        Returns:
            List of dictionaries containing conversation metadata
        """
        histories = []
        
        try:
            for filepath in self.history_dir.glob("*.json"):
                try:
                    with open(filepath, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                    
                    histories.append({
                        "guid": data.get("conversation_guid"),
                        "conversation_id": data.get("conversation_id"),
                        "created_at": data.get("created_at"),
                        "last_updated": data.get("last_updated"),
                        "message_count": data.get("message_count", 0),
                        "filename": filepath.name
                    })
                    
                except Exception as e:
                    logger.warning(f"Could not read history file {filepath}: {e}")
            
            # Sort by last_updated descending
            histories.sort(key=lambda x: x.get("last_updated", ""), reverse=True)
            
        except Exception as e:
            logger.error(f"Failed to list conversation histories: {e}")
        
        return histories
    
    def delete_conversation_history(self, conversation_id: str) -> bool:
        """
        Delete conversation history file.
        
        Args:
            conversation_id: The conversation ID
            
        Returns:
            bool: True if deleted successfully, False otherwise
        """
        try:
            filepath = self.get_history_filepath(conversation_id)
            
            if filepath.exists():
                filepath.unlink()
                logger.info(f"Deleted conversation history: {filepath}")
                
                # Remove from GUID tracking
                if conversation_id in self._conversation_guids:
                    del self._conversation_guids[conversation_id]
                if conversation_id in self._conversation_start_times:
                    del self._conversation_start_times[conversation_id]
                
                return True
            else:
                logger.warning(f"History file not found for conversation {conversation_id}")
                return False
                
        except Exception as e:
            logger.error(f"Failed to delete conversation history for {conversation_id}: {e}")
            return False


# Global instance
history_service = HistoryService()
