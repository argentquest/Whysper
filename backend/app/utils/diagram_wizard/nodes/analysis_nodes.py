"""
Analysis node for initial request processing.

Handles the initial analysis of user requests to determine if clarification
is needed or if the system can proceed directly to diagram generation.
"""

import logging
import json
from typing import Dict, Any
from ..graph_state import GraphState, SessionState
from ..prompt_loader import get_prompt
from .llm_helpers import call_llm
from common.logging_decorator import log_method_call

logger = logging.getLogger(__name__)


@log_method_call
async def analyze_request(state: GraphState, service) -> Dict[str, Any]:
    """
    Analyzes the initial user request to decide the next step.

    Calls an LLM with a specialized prompt to determine if the request
    is clear enough to proceed with diagram generation or if clarification

    is needed.

    Returns:
        - A dictionary with 'next_action' set to either 'clarify' or 'generate'.
        - If 'clarify', a 'clarification_question' is also returned.
        - If 'generate', a 'suggested_diagram_type' and 'reason' are returned.
    """
    session_id = state.get("_session_id")
    model_id = state.get("model_id")  # Get selected model from state

    # IMPORTANT: Skip re-analysis if we've already analyzed the request
    # This prevents infinite loops when resuming the graph after clarification
    if state.get("analysis_complete", False):
        logger.info(f"⏭️ Skipping re-analysis - already completed", extra={'session_id': session_id})
        return {
            "next_action": "clarify",
            "skip_analysis": True
        }

    logger.info(f"🔬 Analyzing initial user request (model: {model_id})...", extra={'session_id': session_id})

    update_callback = state.get("_update_callback")
    if update_callback:
        await update_callback({
            "status": "analyzing",
            "message": "AI is analyzing your request...",
        })

    prompt_template = get_prompt("analyze_request", model_id=model_id)
    if not prompt_template:
        logger.error("analyze_request prompt not found!", extra={'session_id': session_id})
        return {
            "next_action": "clarify",
            "clarification_question": "I'm having trouble understanding your request. Could you please describe the diagram you want to create in more detail?",
            "error_message": "Internal error: analysis prompt not found."
        }

    clarification_history = state.get("clarification_history", [])
    user_content = "\n".join([msg.get('content', '') for msg in clarification_history if msg.get('role') == 'user'])

    try:
        ai_response_str = await call_llm(prompt_template, user_content, session_id, model_id=model_id)
    except Exception as e:
        error_message = str(e)
        logger.error(f"AI call failed in analyze_request: {error_message}", extra={'session_id': session_id})
        if update_callback:
            await update_callback({
                "status": "failed",
                "message": f"AI analysis failed: {error_message}",
                "error": error_message,
            })
        return {
            "next_action": "error",
            "error_message": error_message,
            "current_state": "failed",
        }

    try:
        ai_response = json.loads(ai_response_str)
        analysis_summary = ai_response.get("analysis_summary") or ai_response.get("payload")
        assessment_score = ai_response.get("assessment_score")
        clarity_score = ai_response.get("clarity_score")
        architecture_json = (
            ai_response.get("json_representation")
            or ai_response.get("architecture_json")
        )
        follow_up_question = ai_response.get("question")

        # Store the architecture_json in the state, even if incomplete
        if architecture_json:
            try:
                if isinstance(architecture_json, str):
                    state["json_representation"] = json.loads(architecture_json)
                else:
                    state["json_representation"] = architecture_json
            except json.JSONDecodeError as json_err:
                logger.warning(f"Failed to parse architecture_json: {json_err}", extra={'session_id': session_id})
                state["json_representation"] = {}

        # ANALYZE phase always shows results and moves to CLARIFY loop
        logger.info(f"Analysis complete: LLM score {assessment_score}/100", extra={'session_id': session_id})

        if update_callback:
            await update_callback({
                "status": "analysis_complete",
                "message": analysis_summary,
                "assessment_score": assessment_score,
                "score": assessment_score,
                "clarity_score": clarity_score,
                "json_representation": state.get("json_representation", {}),
                "question": follow_up_question,
                "full_ai_response": ai_response_str  # Include full raw response for "Show More"
            })

        # Mark analysis as complete to prevent re-analysis
        return {
            "next_action": "clarify",
            "assessment_score": assessment_score,
            "json_representation": state.get("json_representation", {}),
            "clarification_history": clarification_history + [
                {"role": "assistant", "content": analysis_summary or ""},
                {"role": "assistant", "content": f"QUESTION: {follow_up_question}"}
            ],
            "current_state": SessionState.CLARIFYING,
            "analysis_complete": True,  # Flag to prevent re-analysis
            "first_question_asked": True,  # Flag to skip clarify_prompt on first run
        }

    except (json.JSONDecodeError, ValueError) as e:
        logger.error(f"Error processing analysis response from AI: {e}", extra={'session_id': session_id})
        # Fallback to clarification
        fallback_question = "I'm not sure I understand. Could you please provide more details about the components and how they interact?"
        if update_callback:
            await update_callback({
                "status": "clarifying",
                "message": fallback_question,
            })
        return {
            "next_action": "clarify",
            "clarification_question": fallback_question,
            "error_message": str(e),
        }
