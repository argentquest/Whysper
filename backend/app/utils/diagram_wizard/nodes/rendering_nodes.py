"""
Rendering node for diagram visualization.

Handles the final step of converting valid diagram code
to SVG format for display.
"""

from typing import Dict, Any
from ..graph_state import GraphState, DiagramType, SessionState
from common.logging_decorator import log_method_call
from common.logger import get_logger

# Import provider registry for rendering
try:
    from diagrams.provider_registry import get_registry
    PROVIDER_AVAILABLE = True
except ImportError:
    PROVIDER_AVAILABLE = False

logger = get_logger(__name__)


@log_method_call
async def render_diagram(state: GraphState) -> Dict[str, Any]:
    """
    Rendering node.

    Renders valid diagram code to SVG format using provider system directly.
    No fallback logic - simplified approach requires provider system.

    Returns:
        svg_output: SVG representation of diagram
    """
    diagram_code = state.get("diagram_code", "")
    diagram_type = state.get("diagram_type", DiagramType.MERMAID)
    session_id = state.get("_session_id")

    logger.info(f"🎨 Rendering {diagram_type} diagram to SVG using provider system",
                extra={'session_id': session_id} if session_id else {})

    if not diagram_code.strip():
        return {
            "svg_output": "",
            "error_message": "No diagram code to render",
            "current_state": SessionState.ERROR
        }

    # Check if provider system is available
    if not PROVIDER_AVAILABLE:
        error_msg = "Provider registry not available for rendering"
        logger.error(error_msg, extra={'session_id': session_id} if session_id else {})
        return {
            "svg_output": "",
            "error_message": error_msg,
            "current_state": SessionState.ERROR
        }

    # Direct provider system call - no fallback
    provider_registry = get_registry()
    provider = provider_registry.get_default_provider(diagram_type.value)

    if not provider:
        raise ValueError(f"No provider available for {diagram_type.value}")

    # Provider methods are synchronous, do not await
    result = provider.render_with_validation(
        code=diagram_code,
        output_format="svg",
        auto_fix=False,  # Validation already done
        llm_correction=False
    )

    if result.success:
        return {
            "svg_output": result.content,
            "current_state": SessionState.READY
        }
    else:
        return {
            "svg_output": "",
            "error_message": f"Rendering failed: {result.error}",
            "current_state": SessionState.ERROR
        }
