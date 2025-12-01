"""
Analysis node for initial request processing.

Handles the initial analysis of user requests to determine if clarification
is needed or if the system can proceed directly to diagram generation.
"""

import json
import re
from typing import Dict, Any
from ..graph_state import GraphState, SessionState
from ..prompt_loader import get_prompt
from .llm_helpers import call_llm, extract_json_from_response
from common.logging_decorator import log_method_call
from common.env_manager import env_manager
from common.logger import get_logger

logger = get_logger(__name__)


def _parse_ai_response(ai_response_str: str, session_id: str = None) -> Dict[str, Any]:
    """
    Parse AI response, attempting to clean common LLM artifacts before failing.

    Args:
        ai_response_str (str): The raw response string from the AI.
        session_id (str, optional): The session ID for logging context.

    Returns:
        Dict[str, Any]: The parsed JSON response.

    Raises:
        ValueError: If parsing fails after all attempts.
    """
    parse_errors = []

    try:
        return json.loads(ai_response_str)
    except json.JSONDecodeError as err:
        parse_errors.append(f"direct parse: {err}")

    try:
        return extract_json_from_response(ai_response_str)
    except Exception as err:  # noqa: BLE001 - wants the concrete error in logs
        parse_errors.append(f"extraction helper: {err}")

    stripped = ai_response_str.strip()
    stripped = re.sub(r"^```(?:json)?\s*", "", stripped)
    stripped = re.sub(r"```\s*$", "", stripped)
    brace_match = re.search(r"\{.*\}", stripped, re.DOTALL)
    cleaned = brace_match.group(0) if brace_match else stripped

    if cleaned != ai_response_str:
        try:
            return json.loads(cleaned)
        except json.JSONDecodeError as err:
            parse_errors.append(f"cleaned parse: {err}")

    logger.info(
        f"Failed to parse AI response after retries: {' | '.join(parse_errors)}",
        extra={'session_id': session_id} if session_id else {},
    )
    raise ValueError(f"Unable to parse AI response; attempts: {' | '.join(parse_errors)}")


@log_method_call
async def analyze_request(state: GraphState, service) -> Dict[str, Any]:
    """
    Analyzes the initial user request to decide the next step.

    Calls an LLM with a specialized prompt to determine if the request
    is clear enough to proceed with diagram generation or if clarification
    is needed.

    Args:
        state (GraphState): The current graph state.
        service: The DiagramFactoryService instance.

    Returns:
        Dict[str, Any]: Dictionary containing updates to the graph state, including:
            - next_action (str): 'clarify' or 'generate'
            - assessment_score (int): Quality score of the request
            - json_representation (dict): Preliminary architecture data
            - clarification_history (list): Updated history
            - current_state (SessionState): New state enum
    """
    session_id = state.get("_session_id")
    model_id = state.get("model_id")  # Get selected model from state

    # IMPORTANT: Skip re-analysis if we've already analyzed the request
    # This prevents infinite loops when resuming the graph after clarification
    if state.get("analysis_complete", False):
        logger.info("⏭️ Skipping re-analysis - already completed", extra={'session_id': session_id})
        return {
            "next_action": "clarify",
            "skip_analysis": True
        }

    logger.info(f"🔬 Analyzing initial user request (model: {model_id})...", extra={'session_id': session_id})

    # Get dynamic score target from environment
    score_target = env_manager.get_score_target()

    update_callback = state.get("_update_callback")
    if update_callback:
        await update_callback({
            "status": "analyzing",
            "message": "AI is analyzing your request...",
        })

    prompt_template = get_prompt("analyze_request", model_id=model_id)
    if not prompt_template:
        logger.info("analyze_request prompt not found!", extra={'session_id': session_id})
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
        logger.info(f"AI call failed in analyze_request: {error_message}", extra={'session_id': session_id})
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
        logger.debug(f"AI Response: {ai_response_str}", extra={'session_id': session_id})
        ai_response = _parse_ai_response(ai_response_str, session_id)
        analysis_summary = ai_response.get("analysis_summary") or ai_response.get("payload")
        assessment_score = ai_response.get("assessment_score", 20)
        clarity_score = ai_response.get("clarity_score", 50)
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
                logger.info(f"Failed to parse architecture_json: {json_err}", extra={'session_id': session_id})
                state["json_representation"] = {}

        # ANALYZE phase always shows results and moves to CLARIFY loop
        logger.info(f"Analysis complete: LLM score {assessment_score}/100", extra={'session_id': session_id})

        if update_callback:
            await update_callback({
                "status": "analysis_complete",
                "message": analysis_summary,
                "analysis_summary": analysis_summary,
                "assessment_score": assessment_score,
                "score": assessment_score,
                "score_target": score_target,
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
        logger.info(f"Error processing analysis response from AI: {e}", extra={'session_id': session_id})
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
