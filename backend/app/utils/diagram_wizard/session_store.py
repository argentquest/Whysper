import asyncio
import time
from datetime import datetime, timedelta
from typing import Dict, Any, Optional, List

class DiagramSessionStore:
    """
    Thread-safe in-memory session store with configurable time-to-live.

    Manages diagram generation sessions, including creation, retrieval,
    updates, deletion, and expiration cleanup.
    """

    def __init__(self, ttl_seconds: int = 3600):
        """
        Initialize the session store.

        Args:
            ttl_seconds (int): Session expiration time in seconds. Defaults to 3600.
        """
        self._sessions: Dict[str, Dict[str, Any]] = {}  # Dictionary to store sessions
        self._ttl = ttl_seconds  # Session expiration time in seconds
        self._lock = asyncio.Lock()  # Async lock for thread-safe operations

    async def create_session(
        self,
        user_id: str,
        conversation_id: str,
        initial_prompt: str,
        diagram_type: str,
    ) -> str:
        """
        Create a new session.

        Args:
            user_id (str): The user ID.
            conversation_id (str): The conversation ID.
            initial_prompt (str): The initial prompt from the user.
            diagram_type (str): The requested diagram type.

        Returns:
            str: The unique session ID.
        """
        # Create a unique session ID using user ID and current timestamp
        async with self._lock:
            session_id = f"diagram_{user_id}_{int(time.time())}"

            # Populate session with comprehensive metadata and initial state
            self._sessions[session_id] = {
                "user_id": user_id,
                "conversation_id": conversation_id,
                "created_at": datetime.utcnow().isoformat(),
                "expires_at": (
                    datetime.utcnow() + timedelta(seconds=self._ttl)
                ).isoformat(),
                "initial_prompt": initial_prompt,
                "diagram_type": diagram_type,
                "state": {},  # Placeholder for dynamic graph state
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
        Retrieve a session by ID.

        Args:
            session_id (str): The session ID.

        Returns:
            Dict[str, Any]: The session data.

        Raises:
            ValueError: If the session is not found or has expired.
        """
        # Retrieve a session, ensuring it's valid and not expired
        async with self._lock:
            session = self._sessions.get(session_id)

            # Raise error if session doesn't exist
            if not session:
                raise ValueError(f"Session not found: {session_id}")

            # Check and remove expired sessions
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
            session_id (str): The session ID.
            updates (Dict[str, Any]): The updates to apply.

        Raises:
            ValueError: If the session is not found or has expired.
        """
        # Update session state with thread-safe checks
        async with self._lock:
            session = self._sessions.get(session_id)

            # Validate session existence
            if not session:
                raise ValueError(f"Session not found: {session_id}")

            # Prevent updates to expired sessions
            expires_at = datetime.fromisoformat(session["expires_at"])
            if datetime.utcnow() > expires_at:
                del self._sessions[session_id]
                raise ValueError(f"Session expired: {session_id}")

            # Safely update session fields
            session.update(updates)

    async def delete_session(self, session_id: str) -> None:
        """
        Delete a session.

        Args:
            session_id (str): The session ID to delete.
        """
        # Remove a session from the store safely
        async with self._lock:
            self._sessions.pop(session_id, None)

    async def cleanup_expired(self) -> int:
        """
        Cleanup expired sessions.

        Returns:
            int: The number of expired sessions removed.
        """
        # Automatically remove all expired sessions
        async with self._lock:
            now = datetime.utcnow()
            expired = []

            # Find sessions past their expiration time
            for sid, sess in self._sessions.items():
                expires_at = datetime.fromisoformat(sess["expires_at"])
                if now > expires_at:
                    expired.append(sid)

            # Remove expired sessions
            for sid in expired:
                del self._sessions[sid]

            return len(expired)

    async def list_active_sessions(self, user_id: str) -> List[str]:
        """
        List active sessions for a user.

        Args:
            user_id (str): The user ID.

        Returns:
            List[str]: A list of active session IDs.
        """
        # List all non-expired sessions for a specific user
        async with self._lock:
            now = datetime.utcnow()
            active = []

            # Iterate through sessions, checking for user and expiration
            for sid, sess in self._sessions.items():
                if sess["user_id"] == user_id:
                    expires_at = datetime.fromisoformat(sess["expires_at"])
                    if now <= expires_at:
                        active.append(sid)

            return active
