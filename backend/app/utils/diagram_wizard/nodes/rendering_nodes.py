"""
Rendering node for diagram visualization.

Handles the final step of converting valid diagram code
to SVG format for display.
"""

from typing import Dict, Any
from ..graph_state import GraphState, DiagramType, SessionState
from common.logging_decorator import log_method_call
from common.logger import get_logger
from .llm_helpers import _get_model_for_id

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

    The actual AI model used for LLM correction comes from settings.default_model
    (.env DEFAULT_MODEL). The session's model_id is only used for prompt style
    selection and is not passed to the provider.

    Args:
        state (GraphState): The current graph state.

    Returns:
        Dict[str, Any]: Updates to the graph state including the generated SVG output.

    Raises:
        ValueError: If no provider is available for the diagram type.
    """
    diagram_code = state.get("diagram_code", "")
    diagram_type = state.get("diagram_type", DiagramType.MERMAID)
    session_id = state.get("_session_id")
    model_id = state.get("model_id")  # Prompt style identifier (claude, gpt5, etc.)

    # Get actual model from settings (e.g., "anthropic/claude-3.5-sonnet")
    # model_id is just for prompt selection, actual model comes from .env
    actual_model = _get_model_for_id(model_id)

    logger.info(
        f"🎨 Rendering {diagram_type} diagram to SVG using provider system "
        f"(prompt style: {model_id}, actual model: {actual_model})",
        extra={"session_id": session_id} if session_id else {},
    )

    if not diagram_code.strip():
        return {"svg_output": "", "error_message": "No diagram code to render", "current_state": SessionState.ERROR}

    # Check if provider system is available
    if not PROVIDER_AVAILABLE:
        error_msg = "Provider registry not available for rendering"
        logger.info(error_msg, extra={"session_id": session_id} if session_id else {})
        return {"svg_output": "", "error_message": error_msg, "current_state": SessionState.ERROR}

    # Direct provider system call - no fallback
    provider_registry = get_registry()
    provider = provider_registry.get_default_provider(diagram_type.value)

    if not provider:
        raise ValueError(f"No provider available for {diagram_type.value}")

    # Send rendering status update to frontend
    update_callback = state.get("_update_callback")
    if update_callback:
        await update_callback(
            {
                "status": "rendering",
                "message": f"Rendering {diagram_type.value} diagram to SVG...",
            }
        )

    try:
        # Provider's render_with_validation handles the complete pipeline:
        # 1. Validation
        # 2. Pattern-based auto-fix (fast, deterministic)
        # 3. LLM correction with retries (intelligent, adaptive)
        # 4. Rendering
        # This delegates all correction logic to the provider.

        result = await provider.render_with_validation(
            code=diagram_code,
            output_format="svg",
            auto_fix=True,  # Enable pattern-based fixes
            llm_correction=True,  # Enable LLM correction
            model=actual_model,  # Use actual model from .env (e.g., "anthropic/claude-3.5-sonnet")
            progress_callback=update_callback,  # Pass for detailed progress
        )

        if result.success:
            # Prepare the corrected code if provider fixed it
            corrected_code = getattr(result.validation, "fixed_code", None)
            final_diagram_code = corrected_code if (corrected_code and corrected_code != diagram_code) else diagram_code

            # Send rendered status update to frontend with SVG output
            # Include svgOutput here to avoid timing issues with REST API polling
            if update_callback:
                await update_callback(
                    {
                        "status": "rendered",
                        "message": "✅ Diagram rendered successfully",
                        "svgOutput": result.content,  # Include SVG for immediate display
                        "diagramCode": final_diagram_code,  # Include corrected code
                    }
                )

            # Update diagram_code if provider corrected it
            return_value = {"svg_output": result.content, "current_state": SessionState.READY}
            if corrected_code and corrected_code != diagram_code:
                return_value["diagram_code"] = corrected_code  # Update state with corrected code
            return return_value
        else:
            # Send error status update
            if update_callback:
                await update_callback(
                    {
                        "status": "error",
                        "message": f"Rendering failed: {result.error}",
                        "error": result.error,
                    }
                )

            return {
                "svg_output": "",
                "error_message": f"Rendering failed: {result.error}",
                "current_state": SessionState.ERROR,
            }
    except Exception as e:
        error_msg = f"Critical provider error during rendering: {str(e)}"
        logger.info(error_msg, exc_info=True, extra={"session_id": session_id} if session_id else {})
        return {"svg_output": "", "error_message": error_msg, "current_state": SessionState.ERROR}
