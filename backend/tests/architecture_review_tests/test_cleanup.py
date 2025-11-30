import asyncio
import pytest
import time
from app.services.diagram_factory_service import DiagramSessionStore

@pytest.mark.asyncio
async def test_session_cleanup():
    """Test that stale sessions are cleaned up."""

    # Reset store
    DiagramSessionStore._sessions = {}

    # Create a session
    s1 = DiagramSessionStore.create_session("s1")

    # Use standard time.time() as we refactored the store to use it
    current_time = time.time()

    s1.created_at = current_time - 7200  # 2 hours ago

    # Verify s1 exists
    assert DiagramSessionStore.get_session("s1") is not None

    # Create a new session, which should trigger cleanup
    # Default TTL is 3600 (1 hour)
    s2 = DiagramSessionStore.create_session("s2")

    # Verify s1 is gone
    assert DiagramSessionStore.get_session("s1") is None

    # Verify s2 exists
    assert DiagramSessionStore.get_session("s2") is not None

    print("Session cleanup verified.")

if __name__ == "__main__":
    asyncio.run(test_session_cleanup())
