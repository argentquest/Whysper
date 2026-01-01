"""Diagram factory session primitives."""

import asyncio
import logging
import time
import uuid
from typing import Dict, Any, List, Tuple, Optional

from app.utils.diagram_wizard.graph_state import GraphState
from common.logging_decorator import log_method_call

logger = logging.getLogger(__name__)


class ToastToSSEHandler(logging.Handler):
    """Logging handler that forwards TOAST* messages to the session SSE queue."""

    def __init__(self, session: "DiagramSession"):
        super().__init__(level=logging.INFO)
        self.session = session

    def emit(self, record: logging.LogRecord):
        try:
            message = self.format(record)
            if "TOAST" not in message:
                return

            try:
                loop = asyncio.get_event_loop()
            except RuntimeError:
                return

            async def push_to_queue():
                await self.session.update_queue.put(
                    {
                        "status": record.levelname.lower(),
                        "message": message,
                        "session_id": self.session.session_id,
                    }
                )

            loop.create_task(push_to_queue())
        except Exception:
            # Avoid breaking logging pipeline on handler errors
            pass


class DiagramSession:
    """Represents a single diagram generation session.

    This class encapsulates all state information for a user's diagram
    generation session, including conversation history, current progress,
    generated code, and real-time update queues for SSE communication.

    Attributes:
        session_id: Unique identifier for the session
        history: List of conversation messages (role, content tuples)
        current_state: Current session state information
        clarifications: List of clarification questions asked by AI
        diagram_code: Generated diagram source code
        svg_output: Rendered SVG output
        errors: List of any errors encountered
        update_queue: Async queue for real-time status updates
        diagram_type: Selected diagram type (Mermaid, D2, PlantUML)
        graph_state: Current LangGraph state
        graph_task: Async task running the diagram generation
        is_running: Whether the session is currently processing
    """

    def __init__(self, session_id: str):
        self.session_id = session_id
        self.history: List[Tuple[str, str]] = []  # [(role, message), ...]
        self.current_state: Dict[str, Any] = {}  # Current session state
        self.clarifications: List[str] = []  # AI clarification questions
        self.diagram_code: str = ""  # Generated diagram code
        self.svg_output: str = ""  # Rendered SVG output
        self.errors: List[str] = []  # Error messages
        self.update_queue: asyncio.Queue = asyncio.Queue()  # Real-time updates
        self.diagram_type: str = "Mermaid"  # Selected diagram type
        self.graph_state: Optional[GraphState] = None  # LangGraph state
        self.graph_task: Optional[asyncio.Task] = None  # Generation task
        self.is_running: bool = False  # Processing status
        self.toast_handler: Optional[logging.Handler] = None
        self.pending_resume_reason: Optional[str] = None


class DiagramSessionStore:
    """Thread-safe session management for multiple concurrent diagram sessions.

    This class provides a simple in-memory store for managing multiple
    diagram generation sessions. In production, this would typically
    be replaced with a persistent database or Redis store.

    Note: This is a simple implementation using a class variable.
    For production use, consider using a proper session store with
    expiration, persistence, and better concurrency handling.
    """

    _sessions: Dict[str, DiagramSession] = {}

    @classmethod
    @log_method_call
    def create_session(cls, session_id: str = None) -> DiagramSession:
        """Create a new diagram generation session.

        If session_id is provided (from frontend tab), uses that ID;
        otherwise generates a unique UUID-based session ID.
        Creates a new DiagramSession instance and stores it in the
        session registry.

        Also performs cleanup of old sessions (simple TTL implementation)
        to prevent memory leaks.

        Args:
            session_id: Optional pre-assigned session ID from frontend tab.
                       If not provided, a UUID will be generated.

        Returns:
            DiagramSession: The newly created session instance
        """
        # Periodic cleanup: Check on every session creation for simplicity
        # In high-load production, this should be a background task
        cls._cleanup_stale_sessions()

        # Use provided session_id or generate a new UUID
        if not session_id:
            session_id = str(uuid.uuid4())

        session = DiagramSession(session_id)
        # Store creation time for TTL using standard time.time() for consistency
        session.created_at = time.time()

        cls._sessions[session_id] = session
        logger.debug(f"? Created session {session_id}")
        logger.debug(f"?? Total sessions in store: {len(cls._sessions)}")
        return session

    @classmethod
    def _cleanup_stale_sessions(cls, ttl_seconds: int = 3600):
        """
        Remove sessions older than ttl_seconds.
        Default TTL is 1 hour (3600 seconds).
        """
        try:
            current_time = time.time()
            keys_to_delete = []

            for sid, session in cls._sessions.items():
                # Check created_at if it exists (for backward compatibility)
                created_at = getattr(session, "created_at", 0)
                # Ensure we don't compare monotonic time with epoch time
                # If created_at seems too small (monotonic), ignore it or treat as very old
                # But since we standardized on time.time(), this should be consistent now.
                if created_at > 0 and (current_time - created_at > ttl_seconds):
                    keys_to_delete.append(sid)

            if keys_to_delete:
                logger.info(f"?? Cleaning up {len(keys_to_delete)} stale sessions")
                for sid in keys_to_delete:
                    del cls._sessions[sid]

        except Exception as e:
            # Don't let cleanup crash the request
            logger.info(f"Error during session cleanup: {e}")

    @classmethod
    @log_method_call
    def get_session(cls, session_id: str) -> Optional[DiagramSession]:
        """Retrieve an existing session by ID.

        Args:
            session_id: The unique identifier

        Returns:
            DiagramSession or None: The session if found, None otherwise
        """
        logger.debug(f"?? get_session called for: {session_id}")
        logger.debug(f"?? Available sessions: {list(cls._sessions.keys())}")
        session = cls._sessions.get(session_id)
        logger.debug(f"?? Found session: {session is not None}")
        return session

    @classmethod
    @log_method_call
    def delete_session(cls, session_id: str):
        """Remove a session from the store.

        Args:
            session_id: The session ID to remove
        """
        if session_id in cls._sessions:
            del cls._sessions[session_id]
