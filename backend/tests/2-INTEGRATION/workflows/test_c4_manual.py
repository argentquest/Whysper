"""Test script for C4 Manual Workflow."""
import pytest
import asyncio
from unittest.mock import MagicMock, AsyncMock
from app.services.diagram_factory_service import DiagramFactoryService

@pytest.mark.asyncio
async def test_c4_manual_workflow():
    """Test the complete workflow step by step."""

    # Mock the session
    mock_session = MagicMock()
    mock_session.session_id = "test-session"
    mock_session.history = []
    mock_session.clarifications = []
    mock_session.errors = []

    mock_queue = MagicMock()
    mock_queue.put = AsyncMock()
    mock_session.update_queue = mock_queue

    service = DiagramFactoryService(session=mock_session)
    service.graph = MagicMock()
    service.graph.ainvoke = AsyncMock()

    # Simulate step 1
    service.graph.ainvoke.return_value = {
        "messages": [],
        "current_state": "clarify_prompt",
        "next_step": "clarify_prompt",
        "clarification_question": "What kind of diagram?",
        "session_id": "test-session"
    }

    await service.start_generation("Create a diagram", diagram_type="auto")

    # Wait for the background task to complete since start_generation uses asyncio.create_task
    if service.session.graph_task:
        await service.session.graph_task

    assert service.graph.ainvoke.called

    # Simulate step 2
    service.graph.ainvoke.return_value = {
        "messages": [],
        "current_state": "clarify_prompt",
        "next_step": "clarify_prompt",
        "clarification_question": "More details?",
        "session_id": "test-session"
    }
    await service.handle_clarification("Details")

    # handle_clarification also uses create_task, wait for it
    if service.session.graph_task:
        await service.session.graph_task

    # Verify method call
    assert service.graph.ainvoke.call_count >= 2
