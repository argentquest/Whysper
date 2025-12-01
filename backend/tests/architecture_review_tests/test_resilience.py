import asyncio
import pytest
from unittest.mock import patch, MagicMock
from app.services.diagram_factory_service import DiagramSessionStore, DiagramFactoryService
from app.utils.diagram_wizard.graph_state import DiagramType, SessionState

# Helper to mock call_llm


async def mock_call_llm(*args, **kwargs):
    prompt = args[0] if args else kwargs.get("prompt", "")
    if "Analyze" in prompt:
        return '{"analysis_summary": "Analysis complete", "assessment_score": 90, "json_representation": {}, "question": null}'
    return "{}"


# Helper to mock get_prompt


def mock_get_prompt(*args, **kwargs):
    return "Dummy Prompt"


@pytest.mark.asyncio
async def test_resilience_provider_crash():
    """Test behavior when the rendering provider crashes (raises exception)."""
    session = DiagramSessionStore.create_session()
    service = DiagramFactoryService(session)

    with patch("app.utils.diagram_wizard.nodes.analysis_nodes.call_llm", side_effect=mock_call_llm), patch(
        "app.utils.diagram_wizard.nodes.analysis_nodes.get_prompt", side_effect=mock_get_prompt
    ), patch("app.utils.diagram_wizard.nodes.rendering_nodes.get_registry") as mock_get_registry:

        # Setup provider mock to raise exception
        mock_registry = MagicMock()
        mock_provider = MagicMock()
        mock_provider.render_with_validation.side_effect = Exception("Critical Provider Crash")
        mock_registry.get_default_provider.return_value = mock_provider
        mock_get_registry.return_value = mock_registry

        # Inject state ready for rendering
        service.session.graph_state = {
            "diagram_code": "graph TD; A-->B;",
            "diagram_type": DiagramType.MERMAID,
            "is_valid": True,
            "_session_id": session.session_id,
            "_update_callback": service._push_update,
        }

        # Import the rendering node directly to test it in isolation first
        from app.utils.diagram_wizard.nodes.rendering_nodes import render_diagram

        # The node should now catch the exception and return an error state
        result = await render_diagram(service.session.graph_state)

        # Verify the node handled the error gracefully
        assert result.get("current_state") == SessionState.ERROR
        assert "Critical Provider Crash" in result.get("error_message", "")
        assert result.get("svg_output") == ""


@pytest.mark.asyncio
async def test_resilience_malformed_llm_json():
    """Test behavior when LLM returns malformed JSON."""
    session = DiagramSessionStore.create_session()
    service = DiagramFactoryService(session)

    # Mock LLM to return bad JSON
    async def bad_json_llm(*args, **kwargs):
        return "I am not returning JSON today."

    with patch("app.utils.diagram_wizard.nodes.analysis_nodes.call_llm", side_effect=bad_json_llm), patch(
        "app.utils.diagram_wizard.nodes.analysis_nodes.get_prompt", side_effect=mock_get_prompt
    ):

        await service.start_generation("test prompt", diagram_type="auto")

        # Allow time for async execution
        await asyncio.sleep(1)

        # Check updates
        updates = []
        while not session.update_queue.empty():
            updates.append(await session.update_queue.get())

        # Should have an error or clarification request
        has_error = any(u.get("status") == "error" or u.get("status") == "failed" for u in updates)
        has_clarification = any(u.get("status") == "clarifying" for u in updates)

        assert has_error or has_clarification
