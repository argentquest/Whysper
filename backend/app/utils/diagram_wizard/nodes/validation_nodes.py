"""
Validation and refinement nodes for diagram code.

Handles diagram code validation and iterative refinement
to fix syntax errors and ensure valid output.
"""

from typing import Dict, Any
from ..graph_state import GraphState, DiagramType, SessionState
from ..prompt_loader import get_prompt
from .llm_helpers import call_llm, get_diagram_type_str
from common.logging_decorator import log_method_call
from common.logger import get_logger

# Import provider registry for validation
try:
    from diagrams.provider_registry import get_registry

    PROVIDER_AVAILABLE = True
except ImportError:
    PROVIDER_AVAILABLE = False

logger = get_logger(__name__)


@log_method_call
async def validate_code(state: GraphState) -> Dict[str, Any]:
    """
    Validation node.

    Validates diagram code using the provider system directly.
    No fallback logic - simplified approach requires provider system.

    Args:
        state (GraphState): The current graph state.

    Returns:
        Dict[str, Any]: Updates to the graph state including validation
                        results. Contains 'is_valid', 'validation_error',
                        'validation_details', and 'current_state'.

    Raises:
        ValueError: If no provider is available for the diagram type.
    """
    diagram_code = state.get("diagram_code", "")
    diagram_type = state.get("diagram_type", DiagramType.MERMAID)
    session_id = state.get("_session_id")

    logger.info(
        f"🔍 Validating {diagram_type} diagram code using provider system",
        extra={"session_id": session_id} if session_id else {},
    )
    logger.info(f"📝 Diagram code to validate:\n{diagram_code}", extra={"session_id": session_id} if session_id else {})

    if not diagram_code.strip():
        return {
            "is_valid": False,
            "validation_error": "No diagram code provided",
            "validation_details": None,
            "current_state": SessionState.VALIDATION_ERROR,
        }

    # Check if provider system is available
    if not PROVIDER_AVAILABLE:
        error_msg = "Provider registry not available for validation"
        logger.info(error_msg, extra={"session_id": session_id} if session_id else {})
        return {
            "is_valid": False,
            "validation_error": error_msg,
            "validation_details": None,
            "current_state": SessionState.ERROR,
        }

    # Direct provider system call - no fallback
    provider_registry = get_registry()
    provider = provider_registry.get_default_provider(diagram_type.value)

    if not provider:
        raise ValueError(f"No provider available for {diagram_type.value}")

    # Provider methods are synchronous, do not await
    result = provider.validate_code(diagram_code)

    # Note: result is a ValidationResult object which has 'error'
    # attribute (str), not 'errors' list.
    return {
        "is_valid": result.is_valid,
        "validation_error": (result.error if not result.is_valid else None),
        "validation_details": result,
        "current_state": (SessionState.RENDERING if result.is_valid else SessionState.VALIDATION_ERROR),
    }


@log_method_call
async def refine_code(state: GraphState) -> Dict[str, Any]:
    """
    Refinement node.

    Fixes invalid diagram code based on validation error.
    Uses error-specific refinement prompts.

    Args:
        state (GraphState): The current graph state.

    Returns:
        Dict[str, Any]: Updates to the graph state including refined
                        'diagram_code'.
    """
    diagram_code = state.get("diagram_code", "")
    validation_error = state.get("validation_error", "")
    diagram_type = state.get("diagram_type", DiagramType.MERMAID)
    diagram_type_str = get_diagram_type_str(diagram_type)
    refinement_attempt = state.get("refinement_attempt", 0) + 1
    final_design_summary = state.get("final_design_summary", "")

    if refinement_attempt >= 3:
        logger.info(
            "Max refinement attempts reached. Unable to fix code.", extra={"session_id": state.get("_session_id")}
        )
        return {
            "is_valid": False,
            "error_message": ("Max refinement attempts reached. Unable to fix code."),
            "current_state": SessionState.ERROR,
        }

    # Get refinement prompt template
    prompt_key = f"refine_{diagram_type_str.lower()}"
    prompt_template = get_prompt(prompt_key)

    if not prompt_template:
        # Fallback prompt if specific prompt not found
        prompt_template = (
            f"""You are a {diagram_type_str} diagram code expert. """
            f"""Fix the syntax error in this diagram code.

Original Design Summary: {final_design_summary}

Current Code (with error):
{diagram_code}

Validation Error: {validation_error}

Fix ONLY the syntax error while preserving the diagram's meaning. """
            f"""Return only the corrected code without explanations."""
        )

    # Prepare context for AI
    error_context = f"""Code: {diagram_code}
Error: {validation_error}
Attempt: {refinement_attempt}"""

    # Send progress update to frontend
    update_callback = state.get("_update_callback")
    if update_callback and callable(update_callback):
        await update_callback(
            {
                "status": "refining",
                "message": f"Working: Fixing validation errors (attempt {refinement_attempt})...",
                "message_type": "progress",
            }
        )

    # Get session ID for SSE logging
    session_id = state.get("_session_id")

    logger.info(
        f"Refining {diagram_type_str} code using AI - attempt {refinement_attempt}",
        extra={"session_id": session_id} if session_id else {},
    )
    logger.info(
        f"📤 LLM Prompt:\n{prompt_template}\n\nContext:\n{error_context}",
        extra={"session_id": session_id} if session_id else {},
    )

    try:
        ai_response = await call_llm(prompt_template, error_context, session_id)
        logger.info(f"📥 LLM Response:\n{ai_response}", extra={"session_id": session_id} if session_id else {})
    except Exception as e:
        error_message = str(e)
        logger.info(f"AI call failed in refine_code: {error_message}", extra={"session_id": session_id})
        if update_callback:
            await update_callback(
                {
                    "status": "failed",
                    "message": f"Code refinement failed: {error_message}",
                    "error": error_message,
                }
            )
        return {
            "diagram_code": diagram_code,
            "is_valid": False,
            "error_message": error_message,
            "current_state": "failed",
            "refinement_attempt": refinement_attempt,
        }

    # Clean up AI response (remove markdown formatting)
    refined_code = ai_response.strip()
    if refined_code.startswith("```"):
        lines = refined_code.split("\n")
        if lines[0].startswith("```") and lines[-1].strip() == "```":
            refined_code = "\n".join(lines[1:-1])

    if update_callback:
        await update_callback(
            {
                "status": "code_refined",
                "message": "Working Done",
                "message_type": "success",
            }
        )

    logger.info(
        f"🔧 Refined {diagram_type_str} code - " f"attempt {refinement_attempt} complete",
        extra={"session_id": session_id} if session_id else {},
    )

    return {
        "diagram_code": refined_code,
        "validation_error": "",  # Clear error after refinement
        "refinement_attempt": refinement_attempt,
        "current_state": SessionState.VALIDATING,
    }
