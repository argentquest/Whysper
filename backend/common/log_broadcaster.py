"""
Real-time log broadcasting via Server-Sent Events (SSE)

This module provides a logging handler that broadcasts INFO-level logs
to connected SSE clients. Frontend can display these logs in a status bar
for real-time progress feedback.

PRIVACY: Logs are filtered by session/conversation ID to ensure users only
see their own activity.
"""
import logging
import asyncio
import queue
from typing import Set, Dict, Optional
from datetime import datetime


class LogBroadcaster:
    """
    Singleton broadcaster for real-time log streaming.

    Captures INFO-level logs and broadcasts them to connected SSE clients.
    Each client is associated with a session ID and only receives logs
    for their own session.
    """

    _instance = None
    _log_queue: queue.Queue = queue.Queue(maxsize=100)
    # Map client queues to their session IDs: {queue: session_id}
    _client_sessions: Dict[asyncio.Queue, Optional[str]] = {}

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    @classmethod
    def add_client(cls, client_queue: asyncio.Queue, session_id: Optional[str] = None):
        """
        Register a new SSE client to receive log broadcasts

        Args:
            client_queue: Async queue for sending events to this client
            session_id: Session/conversation ID to filter logs for this client.
                       If None, client receives all logs (backward compatibility).
        """
        cls._client_sessions[client_queue] = session_id
        print(f"📡 [LOG BROADCASTER] Client connected (session: {session_id or 'ALL'}). Total clients: {len(cls._client_sessions)}")

    @classmethod
    def remove_client(cls, client_queue: asyncio.Queue):
        """Unregister an SSE client"""
        session_id = cls._client_sessions.get(client_queue, 'unknown')
        cls._client_sessions.pop(client_queue, None)
        print(f"📡 [LOG BROADCASTER] Client disconnected (session: {session_id}). Total clients: {len(cls._client_sessions)}")

    @classmethod
    def broadcast_log(cls, level: str, message: str, logger_name: str, session_id: Optional[str] = None):
        """
        Broadcast a log message to connected clients (filtered by session)

        Args:
            level: Log level (INFO, WARNING, ERROR, etc.)
            message: Log message (will be truncated to 100 chars)
            logger_name: Name of the logger that emitted this log
            session_id: Session/conversation ID this log belongs to.
                       Only clients with matching session_id receive this log.
                       If None, log is sent to all clients.
        """
        # Truncate message to 100 characters
        truncated_message = message[:100] if len(message) > 100 else message

        log_event = {
            'timestamp': datetime.now().isoformat(),
            'level': level,
            'message': truncated_message,
            'logger': logger_name,
            'session_id': session_id,
        }

        # Send to matching clients only
        disconnected_clients = []
        sent_count = 0

        for client_queue, client_session_id in cls._client_sessions.items():
            # Filter: only send if session matches, or if either is None (broadcast mode)
            should_send = (
                client_session_id is None or  # Client wants all logs
                session_id is None or          # Global log (no session)
                client_session_id == session_id  # Session match
            )

            if should_send:
                try:
                    # Non-blocking put - if queue is full, skip this client
                    client_queue.put_nowait(log_event)
                    sent_count += 1
                except asyncio.QueueFull:
                    # Client queue is full, they're not consuming fast enough
                    pass
                except Exception as e:
                    print(f"⚠️ [LOG BROADCASTER] Error sending to client: {e}")
                    disconnected_clients.append(client_queue)

        # Debug output for session filtering
        if session_id:
            print(f"📡 [LOG BROADCASTER] Sent log to {sent_count}/{len(cls._client_sessions)} clients (session: {session_id})")

        # Clean up disconnected clients
        for client in disconnected_clients:
            cls.remove_client(client)


class SSELoggingHandler(logging.Handler):
    """
    Custom logging handler that broadcasts INFO-level logs via SSE

    Extracts session_id from log record's 'extra' dict for filtering.
    """

    def emit(self, record: logging.LogRecord):
        """
        Called whenever a log is emitted

        Only broadcasts INFO-level logs to avoid spam.
        Extracts session_id from record.extra if available.
        """
        if record.levelno == logging.INFO:
            try:
                message = self.format(record)

                # Extract session_id from log record if available
                # Session ID can be in multiple formats:
                # - record.session_id (if passed via extra={'session_id': ...})
                # - Extracted from logger name (e.g., 'conversation.conv-123')
                session_id = getattr(record, 'session_id', None)

                # If not in record, try to extract from logger name
                if not session_id and record.name.startswith('conversation.'):
                    session_id = record.name.split('.', 1)[1]

                LogBroadcaster.broadcast_log(
                    level=record.levelname,
                    message=message,
                    logger_name=record.name,
                    session_id=session_id
                )
            except Exception:
                # Don't let logging errors break the application
                self.handleError(record)


# Global broadcaster instance
log_broadcaster = LogBroadcaster()


def setup_log_broadcasting():
    """
    Initialize log broadcasting by adding SSE handler to root logger

    Call this once during application startup.
    """
    # Get root logger
    root_logger = logging.getLogger()

    # Check if handler already exists
    for handler in root_logger.handlers:
        if isinstance(handler, SSELoggingHandler):
            print("📡 [LOG BROADCASTER] Already initialized")
            return

    # Create and add SSE handler
    sse_handler = SSELoggingHandler()
    sse_handler.setLevel(logging.INFO)

    # Simple formatter (just the message, timestamp added by broadcaster)
    formatter = logging.Formatter('%(message)s')
    sse_handler.setFormatter(formatter)

    root_logger.addHandler(sse_handler)
    print("📡 [LOG BROADCASTER] Initialized - broadcasting INFO logs to SSE clients")
