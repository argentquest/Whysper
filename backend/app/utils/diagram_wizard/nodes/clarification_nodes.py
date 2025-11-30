"""
Clarification node for iterative requirement refinement.

Implements the interactive clarification phase where the AI asks
targeted questions to gather missing architectural details.
"""

import json
import time
from typing import Dict, Any
from ..graph_state import GraphState, SessionState
from ..prompt_loader import get_prompt
from .llm_helpers import call_llm, extract_json_from_response
from common.logging_decorator import log_method_call
from common.env_manager import env_manager
from common.logger import get_logger

logger = get_logger(__name__)


@log_method_call
async def clarify_prompt(state: GraphState) -> Dict[str, Any]:
    """
    Iterative clarification loop node for refining system understanding.

    This node implements the interactive clarification phase where the AI asks
    targeted questions about the system architecture to gather missing details.
    It uses a conversational approach with scoring to track progress.

    ## Workflow
    1. Check if clarification is needed (clarity_score < SCORE_TARGET from .env)
    2. Call LLM with combined ANALYZE + CLARIFY prompts for full context
    3. Extract clarity_score and next question from LLM response
    4. If clarity_score >= SCORE_TARGET, mark ready and return design summary
    5. If clarity_score < SCORE_TARGET, add question to history and ask user
    6. Track all scores and questions for audit trail

    ## Features
    - **Smart Skipping**: Skips first execution to avoid duplicate questions
    - **Timeout Protection**: Max 10 questions or 5 minutes per session
    - **Scoring**: Tracks clarity_score (1-100) for each turn
    - **Persistent Context**: Combines analyze + clarify prompts for continuity
    - **JSON Building**: Progressively builds json_representation with each response
    - **User Confirmation**: Waits for explicit user confirmation before proceeding

    ## Parameters
    state (GraphState): Current workflow state containing:
        - clarification_history: List of all conversation turns
        - clarity_scores: List of scores from each LLM evaluation
        - question_count: Number of questions asked so far
        - llm_ready: Boolean indicating if AI has enough info
        - user_confirmed_ready: Whether user explicitly confirmed readiness

    ## Returns
    Dict[str, Any]: Updated state with:
        - llm_ready: True if proceeding to generation, False if more questions
        - clarity_scores: Updated list of scores
        - clarification_history: Updated conversation history
        - json_representation: Progressively refined system architecture JSON
        - final_design_summary: Design summary when ready
        - question_count: Incremented question counter

    ## Example Flow
    1. User: "A web application with API backend"
    2. AI clarification_score: 30/100 → "What database technologies?"
    3. User: "PostgreSQL and Redis"
    4. AI clarity_score: 60/100 → "Any external services?"
    5. User: "AWS S3 for file storage"
    6. AI clarity_score: SCORE_TARGET/100 → "Ready!" → Proceed to generation

    ## Timeout Behavior
    If max questions (10) or max time (5 minutes) reached, proceeds with
    available information rather than indefinitely clarifying.
    """
    session_id = state.get("_session_id")

    # Get dynamic score target from environment
    score_target = env_manager.get_score_target()

    # IMPORTANT: Skip clarify_prompt on first run (analyze_request already asked a question)
    # This prevents asking TWO questions immediately after analysis
    if state.get("first_question_asked", False) and state.get("question_count", 0) == 0:
        logger.info("⏭️ Skipping clarify_prompt - analyze_request already asked first question, waiting for user response",
                   extra={'session_id': session_id} if session_id else {})
        return {
            "llm_ready": False,
            "first_question_asked": False,  # Reset flag for next time
            "question_count": 1,  # Mark that first question has been asked
        }

    # Check if we're already ready to proceed (skip clarification)
    # BUT only if user explicitly confirmed readiness, not AI-determined
    if (state.get("llm_ready", False) and
        state.get("final_design_summary") and
        state.get("user_confirmed_ready", False)):
        logger.info("🎯 Skipping clarification - user confirmed ready with complete design summary",
                   extra={'session_id': session_id} if session_id else {})
        return {
            "llm_ready": True,
            "final_design_summary": state.get("final_design_summary"),
            "current_state": "generating"
        }

    clarification_history = state.get("clarification_history", [])
    clarity_scores = state.get("clarity_scores", [])
    question_count = state.get("question_count", 0)

    # Check for clarification timeout (max 20 questions or 30 minutes)
    current_time = time.time()
    start_time = state.get("clarification_start_time", current_time)
    if question_count >= 20 or (current_time - start_time) > 1800:  # 30 minutes
        logger.warning(f"Clarification timeout reached: {question_count} questions, {current_time - start_time:.1f}s elapsed",
                      extra={'session_id': state.get("_session_id")})
        # Send update to frontend asking for user confirmation even though timeout reached
        update_callback = state.get("_update_callback")
        if update_callback:
            await update_callback({
                "status": "clarification_ready",
                "message": "Maximum clarification attempts reached. Please confirm to proceed with diagram generation.",
                "clarity_score": state.get("clarity_score", 50),
                "awaiting_user_confirmation": True,
                "clarification_timeout": True,
                "message_type": "clarification_summary",
            })
        # Wait for user confirmation instead of auto-proceeding
        return {
            "llm_ready": False,
            "final_design_summary": "TIMEOUT: Maximum clarification attempts reached. Awaiting user confirmation to proceed.",
            "awaiting_user_confirmation": True,
            "clarification_timeout": True,
            "current_state": SessionState.CLARIFYING
        }

    # Get both ANALYZE and CLARIFY prompts for persistent schema context
    model_id = state.get("model_id")  # Get selected model from state
    analyze_prompt = get_prompt("analyze_request", model_id=model_id)
    clarify_prompt_template = get_prompt("clarify_universal", model_id=model_id)

    # Combine prompts: ANALYZE provides schema context, CLARIFY guides the clarification loop
    # This ensures the LLM has full schema reference throughout all turns
    if analyze_prompt and clarify_prompt_template:
        prompt_template = f"""{analyze_prompt}

---

## Clarification Loop Phase

{clarify_prompt_template}

### Current Clarification Turn
Continue refining the JSON representation based on the user's responses."""
    elif clarify_prompt_template:
        prompt_template = clarify_prompt_template
    else:
        # Fallback prompt if specific prompt not found
        prompt_template = f"""You are an expert system architect. Your role is to interview the user about their system architecture and iteratively refine the JSON representation of components and connections.

INSTRUCTIONS:
1. Ask ONE clarifying question per turn to understand system components and connections
2. After each user response, provide a clarity_score (1-100)
3. Update the json_representation with new information
4. Respond ONLY in JSON format with: question, clarity_score, ready, json_representation
5. Mark ready=true when clarity_score >= {score_target} and you have sufficient detail
6. When ready, include design_summary with "READY:" prefix

Determine if you have enough information or need to ask more questions."""

    # Prepare user content from conversation history - ONLY include user messages
    # Filter out AI responses to prevent feedback loops
    user_messages = [
        msg for msg in clarification_history[-10:]  # Look at more messages but filter
        if msg.get('role') == 'user'  # Only include actual user input
    ]
    user_content = "\n".join([
        f"User: {msg['content']}"
        for msg in user_messages[-5:]  # Last 5 USER messages for context
    ])

    if not user_content:
        user_content = "User wants to create a diagram. Please start the clarification process."

    # Call AI for clarification decision
    logger.info(f"🤖 Making LLM call for clarification - attempt {question_count + 1} (model: {model_id})",
               extra={'session_id': session_id} if session_id else {})
    logger.debug(f"📝 User context being sent to LLM: {user_content[:200]}{'...' if len(user_content) > 200 else ''}",
               extra={'session_id': session_id} if session_id else {})

    try:
        ai_response_str = await call_llm(prompt_template, user_content, session_id, model_id=model_id)
    except Exception as e:
        error_message = str(e)
        logger.error(f"AI call failed in clarify_prompt: {error_message}", extra={'session_id': session_id})
        update_callback = state.get("_update_callback")
        if update_callback:
            await update_callback({
                "status": "failed",
                "message": f"Clarification failed: {error_message}",
                "error": error_message,
            })
        return {
            "llm_ready": False,
            "error_message": error_message,
            "current_state": "failed",
        }

    try:
        # Parse JSON response from LLM (handles markdown-wrapped JSON)
        ai_response = extract_json_from_response(ai_response_str)

        # Log the parsed JSON structure for debugging
        logger.debug(f"📊 PARSED AI RESPONSE JSON:\n{json.dumps(ai_response, indent=2)}",
                   extra={'session_id': session_id} if session_id else {})

        question = ai_response.get("question")
        analysis_summary = ai_response.get("analysis_summary", "")
        clarity_score = ai_response.get("clarity_score", 50)
        ready = ai_response.get("ready", False)
        json_representation = ai_response.get("json_representation", {})
        if isinstance(json_representation, str):
            try:
                json_representation = json.loads(json_representation)
            except json.JSONDecodeError:
                json_representation = {}
        design_summary = ai_response.get("design_summary", "")

        # Enforce score target: If score meets or exceeds target, mark as ready regardless of AI's decision
        if clarity_score >= score_target and not ready:
            logger.info(
                f"✅ Score {clarity_score} meets target {score_target}, overriding AI ready flag",
                extra={'session_id': session_id} if session_id else {}
            )
            ready = True
            if not design_summary:
                design_summary = f"READY: System architecture understood with clarity score of {clarity_score}/{score_target}."

        # Send AI response to frontend with score and JSON
        update_callback = state.get("_update_callback")
        if update_callback and callable(update_callback):
            await update_callback({
                "status": "clarifying",
                "question": question,
                "analysis_summary": analysis_summary,
                "clarity_score": clarity_score,
                "score_target": score_target,
                "json_representation": json_representation,
                "message_type": "clarification",
                "full_ai_response": ai_response_str  # Include full raw response for "Show More"
            })

        # Check if AI thinks we're ready
        if ready or (design_summary and design_summary.startswith("READY:")):
            summary = design_summary.replace("READY:", "").strip() if design_summary else user_content
            updated_clarity_scores = clarity_scores + [clarity_score]
            # Default to requiring an explicit user confirmation before moving on
            auto_proceed_on_ready = state.get("auto_proceed_on_ready", False)
            await_user_confirmation = not auto_proceed_on_ready

            logger.info(
                f"?? AI gathered enough information (score: {clarity_score}) - "
                f"{'auto-proceeding' if auto_proceed_on_ready else 'waiting for user confirmation'}",
                extra={'session_id': session_id} if session_id else {}
            )
            state["json_representation"] = json_representation
            if update_callback:
                await update_callback({
                    "status": "clarification_ready",
                    "message": summary,
                    "analysis_summary": analysis_summary,
                    "clarity_score": clarity_score,
                    "score_target": score_target,
                    "clarity_scores": updated_clarity_scores,
                    "json_representation": json_representation,
                    "awaiting_user_confirmation": await_user_confirmation,
                    "message_type": "clarification_summary",
                    "full_ai_response": ai_response_str  # Include full raw response for "Show More"
                })

            if auto_proceed_on_ready:
                return {
                    "llm_ready": True,
                    "final_design_summary": summary,
                    "json_representation": json_representation,
                    "clarity_scores": updated_clarity_scores,
                    "clarity_score": clarity_score,
                    "awaiting_user_confirmation": False,
                    "user_confirmed_ready": True,
                    "current_state": SessionState.GENERATING
                }

            return {
                "llm_ready": False,
                "final_design_summary": summary,
                "json_representation": json_representation,
                "clarity_scores": updated_clarity_scores,
                "clarity_score": clarity_score,
                "awaiting_user_confirmation": True,
                "user_confirmed_ready": False,
                "current_state": SessionState.CLARIFYING
            }

        # AI wants more clarification - add question to conversation history
        logger.info(f"❓ AI requesting additional clarification (score: {clarity_score}/100)",
                   extra={'session_id': session_id} if session_id else {})
        updated_history = clarification_history.copy()
        updated_history.append({"role": "assistant", "content": question or "Please provide more details"})

        # Store this turn's clarity score
        updated_clarity_scores = clarity_scores + [clarity_score]

        # Update JSON representation in state
        state["json_representation"] = json_representation

        return {
            "llm_ready": False,
            "clarification_history": updated_history,
            "json_representation": json_representation,
            "clarity_scores": updated_clarity_scores,
            "clarity_score": clarity_score,
            "question_count": question_count + 1,
            "clarification_start_time": start_time,  # Track start time for timeout
            "awaiting_user_confirmation": False,
            "current_state": SessionState.CLARIFYING
        }

    except json.JSONDecodeError as e:
        logger.error(f"❌ Failed to parse clarification response as JSON: {e}",
                    extra={'session_id': session_id} if session_id else {})
        # Fallback to simple string parsing
        if ai_response_str and ai_response_str.startswith("READY:"):
            summary = ai_response_str.replace("READY:", "").strip()
            return {
                "llm_ready": False,
                "final_design_summary": summary,
                "clarity_scores": clarity_scores,
                "awaiting_user_confirmation": True,
                "current_state": SessionState.CLARIFYING
            }
        else:
            # Treat as a question
            updated_history = clarification_history.copy()
            updated_history.append({"role": "assistant", "content": ai_response_str})
            return {
                "llm_ready": False,
                "clarification_history": updated_history,
                "clarity_scores": clarity_scores,
                "question_count": question_count + 1,
                "current_state": "clarifying",
                "error_message": f"Clarification response not in expected JSON format: {str(e)}"
            }
