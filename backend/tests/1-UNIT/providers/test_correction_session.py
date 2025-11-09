"""
Integration tests for Correction Session Management
"""

import sys
from pathlib import Path
from datetime import datetime, timedelta

# Add backend to path
backend_dir = Path(__file__).parent.parent.parent
sys.path.insert(0, str(backend_dir))

from diagrams.correction_session import (
    CorrectionSession,
    CorrectionSessionManager,
    get_session_manager,
    set_session_manager
)
from diagrams.models import CorrectionAttemptType


def test_session_creation():
    """Test creating a correction session"""
    session = CorrectionSession(
        provider_id="mermaidv1",
        diagram_type="mermaid",
        original_code="graph TD\n  A -> B",
        original_error="Invalid syntax",
        current_code="graph TD\n  A -> B",
        current_error="Invalid syntax",
        max_llm_retries=5,
        expires_at=datetime.now() + timedelta(seconds=300)
    )

    assert session.session_id is not None, "Session should have ID"
    assert session.provider_id == "mermaidv1"
    assert session.diagram_type == "mermaid"
    assert session.llm_retries_used == 0
    assert not session.is_valid
    assert not session.is_expired

    print("[OK] Session creation test passed")


def test_session_add_attempt():
    """Test adding correction attempts to session"""
    session = CorrectionSession(
        provider_id="mermaidv1",
        diagram_type="mermaid",
        original_code="invalid",
        current_code="invalid",
        max_llm_retries=3,
        expires_at=datetime.now() + timedelta(seconds=300)
    )

    # Add ORIGINAL attempt
    attempt1 = session.add_attempt(
        attempt_type=CorrectionAttemptType.ORIGINAL,
        code="invalid",
        is_valid=False,
        error="Syntax error"
    )

    assert len(session.attempts) == 1
    assert attempt1.attempt_number == 1
    assert attempt1.attempt_type == CorrectionAttemptType.ORIGINAL

    # Add PATTERN attempt
    attempt2 = session.add_attempt(
        attempt_type=CorrectionAttemptType.PATTERN,
        code="fixed by pattern",
        is_valid=False,
        error="Still has error"
    )

    assert len(session.attempts) == 2
    assert session.pattern_attempts == 1
    assert session.current_code == "fixed by pattern"

    # Add LLM attempt
    attempt3 = session.add_attempt(
        attempt_type=CorrectionAttemptType.LLM,
        code="fixed by llm",
        is_valid=True
    )

    assert len(session.attempts) == 3
    assert session.llm_retries_used == 1
    assert session.is_valid
    assert session.current_code == "fixed by llm"

    print("[OK] Session add attempt test passed")


def test_session_llm_retry_limit():
    """Test LLM retry limit enforcement"""
    session = CorrectionSession(
        provider_id="test",
        diagram_type="mermaid",
        original_code="test",
        current_code="test",
        max_llm_retries=2,
        expires_at=datetime.now() + timedelta(seconds=300)
    )

    assert session.can_use_llm(), "Should allow LLM when under limit"

    # Use first retry
    session.add_attempt(
        attempt_type=CorrectionAttemptType.LLM,
        code="attempt1",
        is_valid=False
    )
    assert session.can_use_llm(), "Should still allow LLM"

    # Use second retry
    session.add_attempt(
        attempt_type=CorrectionAttemptType.LLM,
        code="attempt2",
        is_valid=False
    )
    assert not session.can_use_llm(), "Should not allow more LLM retries"
    assert session.llm_retries_used == 2

    print("[OK] Session LLM retry limit test passed")


def test_session_expiration():
    """Test session expiration"""
    # Create session that expires in 1 second
    session = CorrectionSession(
        provider_id="test",
        diagram_type="test",
        original_code="test",
        current_code="test",
        max_llm_retries=3,
        expires_at=datetime.now() - timedelta(seconds=1)  # Already expired
    )

    assert not session.is_expired, "Should not be marked expired initially"

    expired = session.check_expired()
    assert expired, "Should detect expiration"
    assert session.is_expired, "Should be marked as expired"

    print("[OK] Session expiration test passed")


def test_session_summary():
    """Test session summary generation"""
    session = CorrectionSession(
        provider_id="mermaidv1",
        diagram_type="mermaid",
        original_code="test",
        current_code="test",
        max_llm_retries=5,
        expires_at=datetime.now() + timedelta(seconds=300)
    )

    session.add_attempt(CorrectionAttemptType.ORIGINAL, "code1", False, "error1")
    session.add_attempt(CorrectionAttemptType.PATTERN, "code2", False, "error2")
    session.add_attempt(CorrectionAttemptType.LLM, "code3", True)

    summary = session.get_summary()

    assert summary["session_id"] == session.session_id
    assert summary["provider_id"] == "mermaidv1"
    assert summary["total_attempts"] == 3
    assert summary["llm_retries_used"] == 1
    assert summary["llm_retries_remaining"] == 4
    assert summary["pattern_attempts"] == 1
    assert summary["is_valid"] == True

    print("[OK] Session summary test passed")


def test_session_manager_creation():
    """Test session manager can create sessions"""
    manager = CorrectionSessionManager()

    session = manager.create_session(
        provider_id="mermaidv1",
        diagram_type="mermaid",
        original_code="test code",
        original_error="test error",
        max_llm_retries=5,
        timeout_seconds=300
    )

    assert session is not None
    assert session.provider_id == "mermaidv1"
    assert len(session.attempts) == 1, "Should have ORIGINAL attempt"
    assert session.attempts[0].attempt_type == CorrectionAttemptType.ORIGINAL

    print("[OK] Session manager creation test passed")


def test_session_manager_get_session():
    """Test retrieving sessions from manager"""
    manager = CorrectionSessionManager()

    session = manager.create_session(
        provider_id="test",
        diagram_type="test",
        original_code="test",
        original_error=None,
        max_llm_retries=3
    )

    session_id = session.session_id

    # Retrieve session
    retrieved = manager.get_session(session_id)
    assert retrieved is not None
    assert retrieved.session_id == session_id

    # Try invalid ID
    invalid = manager.get_session("invalid-id")
    assert invalid is None

    print("[OK] Session manager get session test passed")


def test_session_manager_update():
    """Test updating sessions in manager"""
    manager = CorrectionSessionManager()

    session = manager.create_session(
        provider_id="test",
        diagram_type="test",
        original_code="test",
        original_error=None,
        max_llm_retries=3
    )

    # Modify session
    session.add_attempt(CorrectionAttemptType.LLM, "new code", True)

    # Update in manager
    manager.update_session(session)

    # Retrieve and verify
    retrieved = manager.get_session(session.session_id)
    assert retrieved.llm_retries_used == 1
    assert retrieved.is_valid

    print("[OK] Session manager update test passed")


def test_session_manager_delete():
    """Test deleting sessions"""
    manager = CorrectionSessionManager()

    session = manager.create_session(
        provider_id="test",
        diagram_type="test",
        original_code="test",
        original_error=None,
        max_llm_retries=3
    )

    session_id = session.session_id
    assert manager.get_session(session_id) is not None

    # Delete session
    manager.delete_session(session_id)
    assert manager.get_session(session_id) is None

    print("[OK] Session manager delete test passed")


def test_session_manager_cleanup_expired():
    """Test cleanup of expired sessions"""
    manager = CorrectionSessionManager()

    # Create expired session
    expired_session = manager.create_session(
        provider_id="test1",
        diagram_type="test",
        original_code="test",
        original_error=None,
        max_llm_retries=3,
        timeout_seconds=-1  # Expires immediately
    )

    # Create valid session
    valid_session = manager.create_session(
        provider_id="test2",
        diagram_type="test",
        original_code="test",
        original_error=None,
        max_llm_retries=3,
        timeout_seconds=300
    )

    assert manager.get_active_sessions_count() == 2

    # Cleanup expired sessions
    manager.cleanup_expired_sessions()

    # Valid session should remain
    assert manager.get_session(valid_session.session_id) is not None
    # Expired session should be removed
    assert manager.get_session(expired_session.session_id) is None

    print("[OK] Session manager cleanup test passed")


def test_session_manager_singleton():
    """Test session manager singleton"""
    manager1 = get_session_manager()
    manager2 = get_session_manager()

    assert manager1 is manager2, "Should return same instance"

    print("[OK] Session manager singleton test passed")


def test_session_manager_active_count():
    """Test active session count"""
    # Create new manager for isolated test
    manager = CorrectionSessionManager()

    assert manager.get_active_sessions_count() == 0

    session1 = manager.create_session("test1", "mermaid", "code1", None, 3)
    assert manager.get_active_sessions_count() == 1

    session2 = manager.create_session("test2", "d2", "code2", None, 3)
    assert manager.get_active_sessions_count() == 2

    manager.delete_session(session1.session_id)
    assert manager.get_active_sessions_count() == 1

    print("[OK] Session manager active count test passed")


def run_all_tests():
    """Run all correction session tests"""
    print("\n" + "="*60)
    print("Testing Correction Session Management")
    print("="*60 + "\n")

    test_session_creation()
    test_session_add_attempt()
    test_session_llm_retry_limit()
    test_session_expiration()
    test_session_summary()
    test_session_manager_creation()
    test_session_manager_get_session()
    test_session_manager_update()
    test_session_manager_delete()
    test_session_manager_cleanup_expired()
    test_session_manager_singleton()
    test_session_manager_active_count()

    print("\n" + "="*60)
    print("[OK] All correction session tests passed!")
    print("="*60 + "\n")


if __name__ == "__main__":
    run_all_tests()
