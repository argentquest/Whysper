"""
Correction Session Management

Tracks correction attempts and manages user correction workflow.
Sessions store history of correction attempts (pattern, LLM, user)
and provide a mechanism for users to manually edit and resubmit code.
"""

from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime, timedelta
from enum import Enum
import uuid
import logging

from .models import CorrectionAttemptType, CorrectionAttempt
from common.logging_decorator import log_method_call

logger = logging.getLogger(__name__)


class CorrectionSession(BaseModel):
    """
    Tracks a correction session for a diagram.
    Allows users to see what was tried and submit manual corrections.
    """

    session_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    provider_id: str
    diagram_type: str

    # Original code
    original_code: str
    original_error: Optional[str] = None

    # Current state
    current_code: str
    current_error: Optional[str] = None
    is_valid: bool = False

    # Correction history
    attempts: List[CorrectionAttempt] = Field(default_factory=list)

    # Session metadata
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)
    expires_at: datetime

    # Settings applied to this session
    max_llm_retries: int
    llm_retries_used: int = 0
    pattern_attempts: int = 0
    user_attempts: int = 0

    # Status
    is_expired: bool = False
    final_result: Optional[str] = None  # "success", "user_intervention_needed", "failed"

    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }

    @log_method_call
    def add_attempt(
        self,
        attempt_type: CorrectionAttemptType,
        code: str,
        is_valid: bool,
        error: Optional[str] = None
    ) -> CorrectionAttempt:
        """Add a correction attempt to session"""
        attempt = CorrectionAttempt(
            attempt_number=len(self.attempts) + 1,
            attempt_type=attempt_type,
            code=code,
            timestamp=datetime.now(),
            is_valid=is_valid,
            error=error,
            success=is_valid
        )

        self.attempts.append(attempt)
        self.current_code = code
        self.current_error = error
        self.is_valid = is_valid
        self.updated_at = datetime.now()

        # Update counters
        if attempt_type == CorrectionAttemptType.LLM:
            self.llm_retries_used += 1
        elif attempt_type == CorrectionAttemptType.PATTERN:
            self.pattern_attempts += 1
        elif attempt_type == CorrectionAttemptType.USER:
            self.user_attempts += 1

        logger.info(
            f"[SESSION {self.session_id[:8]}] Attempt #{attempt.attempt_number} "
            f"({attempt_type}) - {'✅ Valid' if is_valid else '❌ Invalid'}"
        )

        return attempt

    @log_method_call
    def can_use_llm(self) -> bool:
        """Check if LLM correction can still be used"""
        return self.llm_retries_used < self.max_llm_retries

    @log_method_call
    def check_expired(self) -> bool:
        """Check if session has expired"""
        if datetime.now() > self.expires_at:
            self.is_expired = True
        return self.is_expired

    @log_method_call
    def get_summary(self) -> Dict[str, Any]:
        """Get summary of the correction session"""
        return {
            "session_id": self.session_id,
            "provider_id": self.provider_id,
            "diagram_type": self.diagram_type,
            "is_valid": self.is_valid,
            "total_attempts": len(self.attempts),
            "llm_retries_used": self.llm_retries_used,
            "llm_retries_remaining": self.max_llm_retries - self.llm_retries_used,
            "pattern_attempts": self.pattern_attempts,
            "user_attempts": self.user_attempts,
            "current_error": self.current_error,
            "is_expired": self.is_expired,
            "final_result": self.final_result,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
            "expires_at": self.expires_at.isoformat()
        }


class CorrectionSessionManager:
    """Manages active correction sessions"""

    @log_method_call
    def __init__(self):
        self._sessions: Dict[str, CorrectionSession] = {}
        logger.info("Correction session manager initialized")

    @log_method_call
    def create_session(
        self,
        provider_id: str,
        diagram_type: str,
        original_code: str,
        original_error: Optional[str],
        max_llm_retries: int,
        timeout_seconds: int = 300
    ) -> CorrectionSession:
        """Create a new correction session"""

        session = CorrectionSession(
            provider_id=provider_id,
            diagram_type=diagram_type,
            original_code=original_code,
            original_error=original_error,
            current_code=original_code,
            current_error=original_error,
            max_llm_retries=max_llm_retries,
            expires_at=datetime.now() + timedelta(seconds=timeout_seconds)
        )

        # Add original code as first attempt
        session.add_attempt(
            attempt_type=CorrectionAttemptType.ORIGINAL,
            code=original_code,
            is_valid=False,
            error=original_error
        )

        self._sessions[session.session_id] = session

        logger.info(
            f"[SESSION {session.session_id[:8]}] Created for {provider_id} "
            f"(expires in {timeout_seconds}s, max LLM retries: {max_llm_retries})"
        )

        return session

    @log_method_call
    def get_session(self, session_id: str) -> Optional[CorrectionSession]:
        """Get a session by ID"""
        session = self._sessions.get(session_id)

        if session and session.check_expired():
            logger.warning(f"[SESSION {session_id[:8]}] Session has expired")
            return None

        return session

    @log_method_call
    def update_session(self, session: CorrectionSession):
        """Update a session"""
        self._sessions[session.session_id] = session

    @log_method_call
    def delete_session(self, session_id: str):
        """Delete a session"""
        if session_id in self._sessions:
            del self._sessions[session_id]
            logger.info(f"[SESSION {session_id[:8]}] Deleted")

    @log_method_call
    def cleanup_expired_sessions(self):
        """Remove expired sessions"""
        expired = [
            sid for sid, session in self._sessions.items()
            if session.check_expired()
        ]

        for sid in expired:
            del self._sessions[sid]

        if expired:
            logger.info(f"Cleaned up {len(expired)} expired session(s)")

    @log_method_call
    def get_active_sessions_count(self) -> int:
        """Get count of active sessions"""
        return len(self._sessions)

    @log_method_call
    def get_all_sessions(self) -> List[CorrectionSession]:
        """Get all active sessions (for debugging)"""
        return list(self._sessions.values())


# Global singleton
_session_manager = None

@log_method_call
def get_session_manager() -> CorrectionSessionManager:
    """Get the global session manager instance"""
    global _session_manager
    if _session_manager is None:
        _session_manager = CorrectionSessionManager()
    return _session_manager


@log_method_call
def set_session_manager(manager: CorrectionSessionManager):
    """Set global session manager instance (for testing)"""
    global _session_manager
    _session_manager = manager