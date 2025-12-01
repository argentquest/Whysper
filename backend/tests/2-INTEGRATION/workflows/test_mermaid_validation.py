"""Test script for Mermaid Validation Workflow."""

import pytest
from unittest.mock import MagicMock, AsyncMock
from app.services.diagram_factory_service import DiagramFactoryService


@pytest.mark.asyncio
async def test_mermaid_validation_workflow():
    """Test the Mermaid validation workflow."""

    # Mock the session
    mock_session = MagicMock()
    mock_session.session_id = "test-session"
    mock_session.history = []
    mock_session.clarifications = []
    mock_session.errors = []

    mock_queue = MagicMock()
    mock_queue.put = AsyncMock()
    mock_session.update_queue = mock_queue

    # Mock the service
    service = DiagramFactoryService(session=mock_session)
    service.graph = MagicMock()
    service.graph.ainvoke = AsyncMock()

    # Mock validation failure
    service.graph.ainvoke.return_value = {
        "messages": [],
        "current_state": "validate_code",
        "diagram_code": "graph TD; A-->B",  # Missing semicolon maybe?
        "validation_error": "Syntax error",
        "is_valid": False,
        "session_id": "test-session",
    }

    await service.start_generation("Create a diagram", diagram_type="Mermaid")

    # Wait for task
    if service.session.graph_task:
        await service.session.graph_task

    assert service.graph.ainvoke.called
