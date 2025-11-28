"""Test script for LLM Feedback Workflow."""
import pytest
import asyncio
from unittest.mock import MagicMock, AsyncMock
from app.services.diagram_factory_service import DiagramFactoryService

@pytest.mark.asyncio
async def test_llm_feedback_workflow():
    """Test the LLM feedback workflow."""

    # Mock the session
    mock_session = MagicMock()
    mock_session.session_id = "test-session"
    mock_session.history = []
    mock_session.clarifications = []
    mock_session.errors = []

    mock_queue = MagicMock()
    mock_queue.put = AsyncMock()
    mock_session.update_queue = mock_queue

    # Mock the service dependencies
    service = DiagramFactoryService(session=mock_session)
    # We mock the graph to avoid real execution
    service.graph = MagicMock()
    service.graph.ainvoke = AsyncMock()

    # Mock a state where we have a diagram and ask for feedback
    service.graph.ainvoke.return_value = {
        "messages": [],
        "current_state": "generate_code",
        "diagram_code": "graph TD; A-->B;",
        "session_id": "test-session"
    }

    await service.start_generation("Create a diagram", diagram_type="Mermaid")

    # Wait for task
    if service.session.graph_task:
        await service.session.graph_task

    # Simulate feedback loop
    service.graph.ainvoke.return_value = {
        "messages": [],
        "current_state": "generate_code",
        "diagram_code": "graph TD; A-->B; B-->C;",
        "session_id": "test-session"
    }

    await service.handle_clarification("Add another node C")

    # Wait for task
    if service.session.graph_task:
        await service.session.graph_task

    # Simple assertion to check if we 'processed' the feedback
    assert service.graph.ainvoke.called
