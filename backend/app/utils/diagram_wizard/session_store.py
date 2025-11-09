"""
Session management for diagram factory.

Manages session state with thread-safe operations and TTL-based cleanup.
"""

import asyncio
import time
from datetime import datetime, timedelta
from typing import Dict, Any, Optional, List
from .graph_state import GraphState


class DiagramSessionStore:
    """
    Thread-safe in-memory session store for diagram factory sessions.

    Handles:
    - Session creation and retrieval
    - State updates
    - Expiration management
    - Cleanup of expired sessions
    """

    def __init__(self, ttl_seconds: int = 3600):
        """
        Initialize session store.

        Args:
            ttl_seconds: Session time-to-live in seconds (default 1 hour)
        """
        self._sessions: Dict[str, Dict[str, Any]] = {}
        self._ttl = ttl_seconds
        self._lock = asyncio.Lock()

    async def create_session(
        self,
        user_id: str,
        conversation_id: str,
        initial_prompt: str,
        diagram_type: str,
    ) -> str:
        """
        Create a new diagram session.

        Args:
            user_id: User identifier
            conversation_id: Associated conversation ID
            initial_prompt: Initial user prompt
            diagram_type: Type of diagram (Mermaid, D2, PlantUML)

        Returns:
            Session ID
        """
        async with self._lock:
            session_id = f"diagram_{user_id}_{int(time.time())}"

            self._sessions[session_id] = {
                "user_id": user_id,
                "conversation_id": conversation_id,
                "created_at": datetime.utcnow().isoformat(),
                "expires_at": (
                    datetime.utcnow() + timedelta(seconds=self._ttl)
                ).isoformat(),
                "initial_prompt": initial_prompt,
                "diagram_type": diagram_type,
                "state": {},  # Will be populated as graph progresses
                "clarification_history": [
                    {"role": "user", "content": initial_prompt}
                ],
                "diagram_code": "",
                "svg_output": "",
                "current_state": "initialized",
            }

            return session_id

    async def get_session(self, session_id: str) -> Dict[str, Any]:
        """
        Retrieve a session by ID, checking expiration.

        Args:
            session_id: Session identifier

        Returns:
            Session data

        Raises:
            ValueError: If session not found or expired
        """
        async with self._lock:
            session = self._sessions.get(session_id)

            if not session:
                raise ValueError(f"Session not found: {session_id}")

            # Check expiration
            expires_at = datetime.fromisoformat(session["expires_at"])
            if datetime.utcnow() > expires_at:
                del self._sessions[session_id]
                raise ValueError(f"Session expired: {session_id}")

            return session

    async def update_session(
        self,
        session_id: str,
        updates: Dict[str, Any],
    ) -> None:
        """
        Update session state.

        Args:
            session_id: Session identifier
            updates: Dictionary of fields to update

        Raises:
            ValueError: If session not found
        """
        async with self._lock:
            session = self._sessions.get(session_id)

            if not session:
                raise ValueError(f"Session not found: {session_id}")

            # Check expiration
            expires_at = datetime.fromisoformat(session["expires_at"])
            if datetime.utcnow() > expires_at:
                del self._sessions[session_id]
                raise ValueError(f"Session expired: {session_id}")

            # Update fields
            session.update(updates)

    async def delete_session(self, session_id: str) -> None:
        """
        Delete a session.

        Args:
            session_id: Session identifier
        """
        async with self._lock:
            self._sessions.pop(session_id, None)

    async def cleanup_expired(self) -> int:
        """
        Remove all expired sessions.

        Returns:
            Number of sessions cleaned up
        """
        async with self._lock:
            now = datetime.utcnow()
            expired = []

            for sid, sess in self._sessions.items():
                expires_at = datetime.fromisoformat(sess["expires_at"])
                if now > expires_at:
                    expired.append(sid)

            for sid in expired:
                del self._sessions[sid]

            return len(expired)

    async def list_active_sessions(self, user_id: str) -> List[str]:
        """
        List all active sessions for a user.

        Args:
            user_id: User identifier

        Returns:
            List of active session IDs
        """
        async with self._lock:
            now = datetime.utcnow()
            active = []

            for sid, sess in self._sessions.items():
                if sess["user_id"] == user_id:
                    expires_at = datetime.fromisoformat(sess["expires_at"])
                    if now <= expires_at:
                        active.append(sid)

            return active
