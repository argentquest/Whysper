import pytest
import sys
import os

# Ensure backend is in path
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from app.utils.diagram_wizard.nodes import validation_nodes, rendering_nodes
from app.utils.diagram_wizard.graph_state import SessionState, DiagramType

@pytest.mark.asyncio
async def test_validate_code_no_provider():
    # Save original
    original = validation_nodes.PROVIDER_AVAILABLE
    validation_nodes.PROVIDER_AVAILABLE = False

    try:
        state = {
            "diagram_code": "graph TD; A-->B;",
            "diagram_type": DiagramType.MERMAID,
            "_session_id": "test"
        }
        result = await validation_nodes.validate_code(state)

        assert result["is_valid"] is False
        assert result["validation_error"] == "Provider registry not available for validation"
        assert result["current_state"] == SessionState.ERROR
    finally:
        validation_nodes.PROVIDER_AVAILABLE = original

@pytest.mark.asyncio
async def test_render_diagram_no_provider():
    # Save original
    original = rendering_nodes.PROVIDER_AVAILABLE
    rendering_nodes.PROVIDER_AVAILABLE = False

    try:
        state = {
            "diagram_code": "graph TD; A-->B;",
            "diagram_type": DiagramType.MERMAID,
            "_session_id": "test"
        }
        result = await rendering_nodes.render_diagram(state)

        assert result["svg_output"] == ""
        assert result["error_message"] == "Provider registry not available for rendering"
        assert result["current_state"] == SessionState.ERROR
    finally:
        rendering_nodes.PROVIDER_AVAILABLE = original
