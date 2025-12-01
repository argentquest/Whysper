"""Test script for Simple Workflow."""

import pytest
from unittest.mock import MagicMock, AsyncMock
from app.services.diagram_factory_service import DiagramFactoryService


@pytest.mark.asyncio
async def test_simple_workflow():
    """Test the complete simple workflow."""

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

    # Simulate success path
    service.graph.ainvoke.return_value = {
        "messages": [],
        "current_state": "completed",
        "diagram_code": "graph TD; A-->B;",
        "svg_output": "<svg>...</svg>",
        "session_id": "test-session",
        "message": "__end__",
    }

    await service.start_generation("Create a simple diagram", diagram_type="Mermaid")

    # Wait for task
    if service.session.graph_task:
        await service.session.graph_task

    assert service.graph.ainvoke.called
