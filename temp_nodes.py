"""
LangGraph nodes for diagram factory state machine.

Implements five core nodes:
1. clarify_prompt - Iterative clarification of user requirements
2. generate_code - Generate diagram code from design summary
3. validate_code - Validate diagram code syntax
4. refine_code - Fix invalid diagram code
5. render_diagram - Render valid diagram to SVG
"""

import tempfile
import os
import logging
import json
from typing import Dict, Any
from .graph_state import GraphState, DiagramType, SessionState
from .prompt_loader import get_prompt
from .keyword_scorer import determine_diagram_type
from .tool_config import DiagramToolRunner, DiagramToolConfig
import httpx
from ..architecture_schema import ArchitectureSchema
from common.logging_decorator import log_method_call
from common.ai import create_ai_processor
from common.env_manager import env_manager

# Import provider registry for validation and rendering
try:
    from diagrams.provider_registry import get_registry
    PROVIDER_AVAILABLE = True
except ImportError:
    PROVIDER_AVAILABLE = False

logger = logging.getLogger(__name__)

# Provider mapping constant to avoid duplication
PROVIDER_MAP = {
    "Mermaid": "mermaidv1",
    "D2": "d2v1",
    "PlantUML": "krokiplantuml"
}


def get_diagram_type_str(diagram_type: DiagramType) -> str:
    """
    Helper function to convert DiagramType enum to string.

    Handles both enum values and string fallbacks.
    """
    return diagram_type.value if hasattr(diagram_type, 'value') else str(diagram_type)


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
        logger.info("analyze_request prompt not found!", extra={'session_id': session_id})
        return {
            "next_action": "clarify",
            "clarification_question": "I'm having trouble understanding your request. Could you please describe the diagram you want to create in more detail?",
            "error_message": "Internal error: analysis prompt not found."
        }

    clarification_history = state.get("clarification_history", [])
    user_content = "\n".join([msg.get('content', '') for msg in clarification_history if msg.get('role') == 'user'])

    try:
        ai_response_str = await _call_llm(prompt_template, user_content, session_id, model_id=model_id)
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
                logger.info(f"Failed to parse architecture_json: {json_err}", extra={'session_id': session_id})
                state["json_representation"] = {}

        # ANALYZE phase always shows results and moves to CLARIFY loop
        logger.info(f"Analysis complete: LLM score {assessment_score}/10", extra={'session_id': session_id})

        if update_callback:
            await update_callback({
                "status": "analysis_complete",
                "message": analysis_summary,
                "assessment_score": assessment_score,
                "score": assessment_score,
                "clarity_score": clarity_score,
                "json_representation": state.get("json_representation", {}),
                "question": follow_up_question,
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


@log_method_call
def _get_model_for_id(model_id: str = None) -> str:
    """Map model_id to actual model name.

    Args:
        model_id: User-selected model ID (gpt5, grok, claude, gemini)

    Returns:
        Actual model identifier for API calls
    """
    model_map = {
        "gpt5": "openai/gpt-4-turbo",  # Deep Context
        "grok": "xai/grok-2-latest",  # Fast
        "claude": "anthropic/claude-3.5-sonnet",  # Thinking
        "gemini": "google/gemini-2.5-pro",  # Efficient
    }
    # Return the mapped model or default to Gemini
    return model_map.get(model_id, "google/gemini-2.5-flash-preview-09-2025")


async def _call_llm(prompt: str, user_content: str, session_id: str = None, model_id: str = None) -> str:
    """Helper function to call AI/LLM with proper error handling and SSE logging.

    Args:
        prompt: System prompt template
        user_content: User message content
        session_id: Session ID for SSE filtering (optional)
        model_id: Selected AI model ID (gpt5, grok, claude, gemini)

    Returns:
        AI response string

    Raises:
        Exception: When AI call fails with descriptive error message
    """
    try:
        # Load environment configuration
        env_vars = env_manager.load_env_file()
        api_key = env_vars.get("API_KEY", "")
        provider = env_vars.get("PROVIDER", "openrouter")
        # Use selected model or fall back to environment/default
        model = _get_model_for_id(model_id) if model_id else env_vars.get("DEFAULT_MODEL", "google/gemini-2.5-flash-preview-09-2025")

        if not api_key:
            logger.info("No API key configured for diagram wizard AI calls",
                        extra={'session_id': session_id} if session_id else {})
            raise Exception("No API key configured. Please configure your AI provider API key in settings.")

        # Log AI call initiation (visible via SSE)
        logger.info(f"🤖 Starting AI call for diagram generation",
                   extra={'session_id': session_id} if session_id else {})
        logger.info(f"📋 Model: {model} | Provider: {provider}",
                   extra={'session_id': session_id} if session_id else {})

        # Create AI processor
        processor = create_ai_processor(api_key=api_key, provider=provider)

        # Format conversation for AI call
        conversation_history = [
            {"role": "system", "content": prompt},
            {"role": "user", "content": user_content}
        ]

        logger.info(f"🚀 ACTUAL LLM CALL - Sending request to AI (prompt: {len(prompt)} chars, content: {len(user_content)} chars)",
                   extra={'session_id': session_id} if session_id else {})

        # Make the AI call
        result = processor.process_question(
            question=user_content,
            conversation_history=conversation_history,
            model=model,
            codebase_content="",  # No codebase context needed for diagrams
            max_tokens=2000,      # Reasonable token limit for diagram generation
            temperature=0.7       # Balance creativity and consistency
        )

        # Handle both string and dict return types
        if isinstance(result, str):
            response = result
            tokens_used = 0
            processing_time = 0.0
        else:
            response = result.get("response", "")
            tokens_used = result.get("tokens_used", 0)
            processing_time = result.get("processing_time", 0.0)

        # Log successful AI response (visible via SSE)
        logger.info(f"✅ LLM RESPONSE RECEIVED: {len(response)} chars | {tokens_used} tokens | {processing_time:.1f}s",
                   extra={'session_id': session_id} if session_id else {})

        # Log a preview of the response for debugging
        preview = response[:200].replace('\n', ' ').strip()
        if len(response) > 200:
            preview += "..."
        logger.info(f"📄 LLM RESPONSE CONTENT: {preview}",
                   extra={'session_id': session_id} if session_id else {})

        return response
    except httpx.RequestError as e:
        error_msg = f"Network error during AI call: {str(e)}. Please check your internet connection and try again."
        logger.info(f"❌ AI call failed due to a network error: {e}",
                    extra={'session_id': session_id} if session_id else {})
        raise Exception(error_msg)
    except Exception as e:
        # Check if it's an API key error from the error message
        error_str = str(e).lower()
        if "api key" in error_str or "invalid" in error_str or "expired" in error_str or "unauthorized" in error_str:
            error_msg = f"API key error: {str(e)}. Please check your AI provider API key in settings."
        else:
            error_msg = f"AI call failed: {str(e)}"

        logger.info(f"❌ An error occurred during the AI call: {e}",
                    extra={'session_id': session_id} if session_id else {})
        raise Exception(error_msg)


@log_method_call
async def generate_json_representation(state: GraphState) -> Dict[str, Any]:
    """
    Generates comprehensive architecture representations (Structurizr DSL + Legacy JSON).

    Calls an LLM with a specialized prompt to convert the conversation history into:
    1. A Structurizr workspace (full with views)
    2. A clean Structurizr representation (normalized, model only)
    3. A legacy JSON object (backward compatibility)

    All three representations must be synchronized and valid.

    Returns:
        - Dictionary with 'structurizr_workspace', 'clean_d2', 'json_representation'
    """
    session_id = state.get("_session_id")
    model_id = state.get("model_id", "claude")  # Get selected model
    logger.info(
        f"Generating JSON representation (model: {model_id})...",
        extra={'session_id': session_id}
    )

    update_callback = state.get("_update_callback")
    if update_callback:
        await update_callback({
            "status": "generating_json",
            "message": "AI is validating and finalizing architecture representation...",
        })

    # Load model-specific JSON_GENERATION prompt
    prompt_template = get_prompt("json_generation", model_id=model_id)
    if not prompt_template:
        logger.info(
            f"json_generation prompt not found for model: {model_id}",
            extra={'session_id': session_id}
        )
        # Fallback: use existing representations from clarify_prompt
        return {
            "structurizr_workspace": state.get("structurizr_workspace", ""),
            "clean_d2": state.get("clean_d2", ""),
            "json_representation": state.get("json_representation", {}),
        }

    # Build prompt content from conversation history
    clarification_history = state.get("clarification_history", [])
    user_content = "\n".join([
        msg.get('content', '')
        for msg in clarification_history
        if msg.get('role') == 'user'
    ])

    # Call LLM with model-specific prompt
    try:
        ai_response_str = await _call_llm(
            prompt_template,
            user_content,
            session_id,
            model_id=model_id
        )
    except Exception as e:
        error_message = str(e)
        logger.info(f"AI call failed in generate_json_representation: {error_message}", extra={'session_id': session_id})
        if update_callback:
            await update_callback({
                "status": "failed",
                "message": f"Failed to generate JSON representation: {error_message}",
                "error": error_message,
            })
        # Return existing state representations as fallback
        return {
            "structurizr_workspace": state.get("structurizr_workspace", ""),
            "clean_d2": state.get("clean_d2", ""),
            "json_representation": state.get("json_representation", {}),
            "error_message": error_message,
        }

    try:
        # Parse AI response as JSON
        response = json.loads(ai_response_str)

        # Extract three representations
        structurizr_workspace = response.get("structurizr_workspace", "")
        clean_d2 = response.get("clean_d2", "")
        json_representation = response.get("json_representation", {})

        # Validate Structurizr syntax (basic check)
        if not structurizr_workspace or not structurizr_workspace.startswith("workspace"):
            logger.info(
                "Structurizr workspace missing or invalid format",
                extra={'session_id': session_id}
            )

        if not clean_d2 or not clean_d2.startswith("model"):
            logger.info(
                "clean_d2 missing or invalid format",
                extra={'session_id': session_id}
            )

        # Validate legacy JSON schema
        if json_representation:
            is_valid, errors = ArchitectureSchema.validate(json_representation)
            if not is_valid:
                logger.info(
                    f"Legacy JSON schema validation issues: {errors}",
                    extra={'session_id': session_id}
                )
                # Don't fail - JSON node is validation, not blocking

        logger.info(
            "Successfully generated JSON representation with Structurizr and legacy schema.",
            extra={'session_id': session_id}
        )
        if update_callback:
            await update_callback({
                "status": "json_generated",
                "message": "Successfully validated and finalized architecture representation.",
            })

        return {
            "structurizr_workspace": structurizr_workspace,
            "clean_d2": clean_d2,
            "json_representation": json_representation,
        }

    except json.JSONDecodeError as e:
        logger.info(
            f"AI response not valid JSON: {e}",
            extra={'session_id': session_id}
        )
        if update_callback:
            await update_callback({
                "status": "error",
                "message": "AI response was not valid JSON format.",
            })
        # Return existing state representations as fallback
        return {
            "structurizr_workspace": state.get("structurizr_workspace", ""),
            "clean_d2": state.get("clean_d2", ""),
            "json_representation": state.get("json_representation", {}),
        }

    except Exception as e:
        logger.info(
            f"Unexpected error during JSON generation: {e}",
            extra={'session_id': session_id}
        )
        if update_callback:
            await update_callback({
                "status": "error",
                "message": "Unexpected error during JSON generation.",
            })
        # Return existing state representations as fallback
        return {
            "structurizr_workspace": state.get("structurizr_workspace", ""),
            "clean_d2": state.get("clean_d2", ""),
            "json_representation": state.get("json_representation", {}),
        }


@log_method_call
async def clarify_prompt(state: GraphState) -> Dict[str, Any]:
    """
    Iterative clarification loop node for refining system understanding.

    This node implements the interactive clarification phase where the AI asks
    targeted questions about the system architecture to gather missing details.
    It uses a conversational approach with scoring to track progress.

    ## Workflow
    1. Check if clarification is needed (clarity_score < 8)
    2. Call LLM with combined ANALYZE + CLARIFY prompts for full context
    3. Extract clarity_score and next question from LLM response
    4. If clarity_score >= 8, mark ready and return design summary
    5. If clarity_score < 8, add question to history and ask user
    6. Track all scores and questions for audit trail

    ## Features
    - **Smart Skipping**: Skips first execution to avoid duplicate questions
    - **Timeout Protection**: Max 10 questions or 5 minutes per session
    - **Scoring**: Tracks clarity_score (1-10) for each turn
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
    2. AI clarification_score: 3/10 → "What database technologies?"
    3. User: "PostgreSQL and Redis"
    4. AI clarity_score: 6/10 → "Any external services?"
    5. User: "AWS S3 for file storage"
    6. AI clarity_score: 8/10 → "Ready!" → Proceed to generation

    ## Timeout Behavior
    If max questions (10) or max time (5 minutes) reached, proceeds with
    available information rather than indefinitely clarifying.
    """
    session_id = state.get("_session_id")

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

    # Check for clarification timeout (max 10 questions or 5 minutes)
    import time
    current_time = time.time()
    start_time = state.get("clarification_start_time", current_time)
    if question_count >= 10 or (current_time - start_time) > 300:  # 5 minutes
        logger.info(f"Clarification timeout reached: {question_count} questions, {current_time - start_time:.1f}s elapsed",
                      extra={'session_id': state.get("_session_id")})
        return {
            "llm_ready": True,
            "final_design_summary": "TIMEOUT: Maximum clarification attempts reached. Proceeding with available information.",
            "clarification_timeout": True,
            "current_state": SessionState.GENERATING
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
        prompt_template = """You are an expert system architect. Your role is to interview the user about their system architecture and iteratively refine the JSON representation of components and connections.

INSTRUCTIONS:
1. Ask ONE clarifying question per turn to understand system components and connections
2. After each user response, provide a clarity_score (1-10)
3. Update the json_representation with new information
4. Respond ONLY in JSON format with: question, clarity_score, ready, json_representation
5. Mark ready=true when clarity_score >= 8 and you have sufficient detail
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
        user_content = f"User wants to create a {diagram_type_str} diagram. Please start the clarification process."
    
    # Get session ID for SSE logging
    session_id = state.get("_session_id")
    
    # Call AI for clarification decision
    logger.info(f"🤖 Making LLM call for clarification - attempt {question_count + 1} (model: {model_id})",
               extra={'session_id': session_id} if session_id else {})
    logger.info(f"📝 User context being sent to LLM: {user_content[:200]}{'...' if len(user_content) > 200 else ''}",
               extra={'session_id': session_id} if session_id else {})

    try:
        ai_response_str = await _call_llm(prompt_template, user_content, session_id, model_id=model_id)
    except Exception as e:
        error_message = str(e)
        logger.info(f"AI call failed in clarify_prompt: {error_message}", extra={'session_id': session_id})
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
        # Parse JSON response from LLM
        ai_response = json.loads(ai_response_str)
        question = ai_response.get("question")
        clarity_score = ai_response.get("clarity_score", 5)
        ready = ai_response.get("ready", False)
        json_representation = ai_response.get("json_representation", {})
        if isinstance(json_representation, str):
            try:
                json_representation = json.loads(json_representation)
            except json.JSONDecodeError:
                json_representation = {}
        design_summary = ai_response.get("design_summary", "")

        # Send AI response to frontend with score and JSON
        update_callback = state.get("_update_callback")
        if update_callback and callable(update_callback):
            await update_callback({
                "status": "clarifying",
                "question": question,
                "clarity_score": clarity_score,
                "json_representation": json_representation,
                "message_type": "clarification"
            })

        # Check if AI thinks we're ready
        if ready or design_summary.startswith("READY:"):
            summary = design_summary.replace("READY:", "").strip() if design_summary else user_content
            updated_clarity_scores = clarity_scores + [clarity_score]
            logger.info(
                f"🎯 AI gathered enough information (score: {clarity_score}) - waiting for user confirmation",
                extra={'session_id': session_id} if session_id else {}
            )
            state["json_representation"] = json_representation
            if update_callback:
                await update_callback({
                    "status": "clarification_ready",
                    "message": summary,
                    "clarity_score": clarity_score,
                    "clarity_scores": updated_clarity_scores,
                    "json_representation": json_representation,
                    "awaiting_user_confirmation": True,
                    "message_type": "clarification_summary"
                })
            return {
                "llm_ready": False,
                "final_design_summary": summary,
                "json_representation": json_representation,
                "clarity_scores": updated_clarity_scores,
                "clarity_score": clarity_score,
                "awaiting_user_confirmation": True,
                "current_state": SessionState.CLARIFYING
            }

        # AI wants more clarification - add question to conversation history
        logger.info(f"❓ AI requesting additional clarification (score: {clarity_score}/10)",
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
        logger.info(f"❌ Failed to parse clarification response as JSON: {e}",
                    extra={'session_id': session_id} if session_id else {})
        # Fallback to simple string parsing
        if ai_response_str.startswith("READY:"):
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


@log_method_call
async def determine_diagram_type_node(state: GraphState) -> Dict[str, Any]:
    """
    Determines the appropriate diagram type based on keyword analysis.

    Runs after the clarification loop completes, analyzing the final
    design summary and JSON representation to select the best diagram type
    (Mermaid, D2, or PlantUML).

    Returns:
        - diagram_type: The determined DiagramType
        - keyword_scores: Dictionary with scoring breakdown
    """
    session_id = state.get("_session_id")
    final_design_summary = state.get("final_design_summary", "")
    json_representation = state.get("json_representation", {})

    logger.info("🎯 Determining diagram type based on clarification results...",
               extra={'session_id': session_id} if session_id else {})

    # Combine design summary and JSON metadata for better keyword analysis
    analysis_text = final_design_summary
    if json_representation and isinstance(json_representation, dict):
        metadata = json_representation.get("metadata", {})
        if metadata:
            description = metadata.get("description", "")
            if description:
                analysis_text = f"{analysis_text}\n{description}"

    # Determine diagram type using keyword scoring
    diagram_type, keyword_scores = determine_diagram_type(analysis_text)

    logger.info(
        f"📊 Diagram type determined: {diagram_type.value} | Scores: Mermaid={keyword_scores.get('Mermaid', 0):.1f}%, D2={keyword_scores.get('D2', 0):.1f}%, PlantUML={keyword_scores.get('PlantUML', 0):.1f}%",
        extra={'session_id': session_id} if session_id else {}
    )

    # Send update to frontend with diagram type and scores
    update_callback = state.get("_update_callback")
    if update_callback and callable(update_callback):
        await update_callback({
            "status": "diagram_type_determined",
            "message": f"✅ Selected {diagram_type.value} diagram based on your design.",
            "diagram_type": diagram_type.value,
            "keyword_scores": keyword_scores,
            "message_type": "info"
        })

    return {
        "diagram_type": diagram_type,
        "keyword_scores": keyword_scores,
        "current_state": SessionState.GENERATING
    }


@log_method_call
async def generate_code(state: GraphState) -> Dict[str, Any]:
    """
    Code generation node.

    Generates diagram code from the structured JSON representation.
    Uses diagram-type-specific generation prompt.

    Returns:
        diagram_code: The generated diagram code
    """
    diagram_type = state.get("diagram_type", DiagramType.MERMAID)
    diagram_type_str = get_diagram_type_str(diagram_type)
    json_representation = state.get("json_representation", {})
    model_id = state.get("model_id")  # Get selected model from state

    # Get code generation prompt template
    prompt_key = f"generate_{diagram_type_str.lower()}"
    prompt_template = get_prompt(prompt_key, model_id=model_id)
    
    if not prompt_template:
        # Fallback prompt if specific prompt not found
        prompt_template = f"""You are a {diagram_type_str} diagram code generator.

Create ONLY the diagram code based on the following JSON representation. Do not include explanations or markdown formatting.

JSON Representation:
{json.dumps(json_representation, indent=2)}

Generate clean, syntactically correct {diagram_type_str} code:"""

    # Get session ID for SSE logging
    session_id = state.get("_session_id")

    logger.info(f"Generating {diagram_type_str} code using AI (model: {model_id})",
               extra={'session_id': session_id} if session_id else {})

    # Send progress update to frontend
    update_callback = state.get("_update_callback")
    if update_callback and callable(update_callback):
        await update_callback({
            "status": "generating",
            "message": f"AI is generating {diagram_type_str} diagram code...",
            "message_type": "progress"
        })

    try:
        ai_response = await _call_llm(prompt_template, json.dumps(json_representation, indent=2), session_id, model_id=model_id)
    except Exception as e:
        error_message = str(e)
        logger.info(f"AI call failed in generate_code: {error_message}", extra={'session_id': session_id})
        if update_callback:
            await update_callback({
                "status": "failed",
                "message": f"Code generation failed: {error_message}",
                "error": error_message,
            })
        return {
            "diagram_code": "",
            "error_message": error_message,
            "current_state": "failed",
        }
    
    # Clean up the response (remove any markdown formatting)
    diagram_code = ai_response.strip()
    if diagram_code.startswith("```"):
        lines = diagram_code.split('\n')
        # Remove first and last lines if they're markdown code blocks
        if lines[0].startswith("```") and lines[-1].strip() == "```":
            diagram_code = '\n'.join(lines[1:-1])
    
    logger.info(f"📄 Generated {diagram_type_str} code - length: {len(diagram_code)} chars", 
               extra={'session_id': session_id} if session_id else {})
    
    # Send success update to frontend
    if update_callback:
        await update_callback({
            "status": "code_generated", 
            "message": f"✅ Generated {diagram_type_str} diagram code ({len(diagram_code)} chars)",
            "message_type": "success"
        })
    
    return {
        "diagram_code": diagram_code,
        "current_state": SessionState.VALIDATING
    }


@log_method_call
async def validate_code(state: GraphState) -> Dict[str, Any]:
    """
    Validation node.

    Validates diagram code using the provider system directly.
    No fallback logic - simplified approach requires provider system.

    Returns:
        - is_valid: True if code is valid
        - validation_error: Error message if invalid
        - validation_details: Full validation result from provider
    """
    diagram_code = state.get("diagram_code", "")
    diagram_type = state.get("diagram_type", DiagramType.MERMAID)
    session_id = state.get("_session_id")

    logger.info(f"🔍 Validating {diagram_type} diagram code using provider system",
                extra={'session_id': session_id} if session_id else {})

    if not diagram_code.strip():
        return {
            "is_valid": False,
            "validation_error": "No diagram code provided",
            "validation_details": None,
            "current_state": SessionState.VALIDATION_ERROR
        }

    # Direct provider system call - no fallback
    provider_registry = get_registry()
    provider = provider_registry.get_provider_for_type(diagram_type.value)

    if not provider:
        raise ValueError(f"No provider available for {diagram_type.value}")

    result = await provider.validate_code(diagram_code)

    return {
        "is_valid": result.is_valid,
        "validation_error": "; ".join([e.message for e in result.errors]) if not result.is_valid else None,
        "validation_details": result,
        "current_state": SessionState.RENDERING if result.is_valid else SessionState.VALIDATION_ERROR
    }


@log_method_call
async def refine_code(state: GraphState) -> Dict[str, Any]:
    """
    Refinement node.

    Fixes invalid diagram code based on validation error.
    Uses error-specific refinement prompts.

    Returns:
        diagram_code: Refined and corrected code
    """
    diagram_code = state.get("diagram_code", "")
    validation_error = state.get("validation_error", "")
    diagram_type = state.get("diagram_type", DiagramType.MERMAID)
    diagram_type_str = get_diagram_type_str(diagram_type)
    refinement_attempt = state.get("refinement_attempt", 0) + 1
    final_design_summary = state.get("final_design_summary", "")
    model_id = state.get("model_id")  # Get selected model from state

    if refinement_attempt >= 3:
        logger.info("Max refinement attempts reached. Unable to fix code.", extra={'session_id': state.get("_session_id")})
        return {
            "is_valid": False,
            "error_message": "Max refinement attempts reached. Unable to fix code.",
            "current_state": SessionState.ERROR,
        }

    # Get refinement prompt template
    prompt_key = f"refine_{diagram_type_str.lower()}"
    prompt_template = get_prompt(prompt_key, model_id=model_id)
    
    if not prompt_template:
        # Fallback prompt if specific prompt not found
        prompt_template = f"""You are a {diagram_type_str} diagram code expert. Fix the syntax error in this diagram code.

Original Design Summary: {final_design_summary}

Current Code (with error):
{diagram_code}

Validation Error: {validation_error}

Fix ONLY the syntax error while preserving the diagram's meaning. Return only the corrected code without explanations."""

    # Prepare context for AI
    error_context = f"""Code: {diagram_code}
Error: {validation_error}
Attempt: {refinement_attempt}"""
    
    # Send progress update to frontend
    update_callback = state.get("_update_callback")
    if update_callback and callable(update_callback):
        await update_callback({
            "status": "refining",
            "message": f"AI is fixing diagram code (attempt {refinement_attempt})...",
            "message_type": "progress"
        })

    # Get session ID for SSE logging
    session_id = state.get("_session_id")

    logger.info(f"Refining {diagram_type_str} code using AI - attempt {refinement_attempt} (model: {model_id})",
               extra={'session_id': session_id} if session_id else {})

    try:
        ai_response = await _call_llm(prompt_template, error_context, session_id, model_id=model_id)
    except Exception as e:
        error_message = str(e)
        logger.info(f"AI call failed in refine_code: {error_message}", extra={'session_id': session_id})
        if update_callback:
            await update_callback({
                "status": "failed",
                "message": f"Code refinement failed: {error_message}",
                "error": error_message,
            })
        return {
            "diagram_code": diagram_code,
            "is_valid": False,
            "error_message": error_message,
            "current_state": "failed",
            "refinement_attempt": refinement_attempt
        }

    # Clean up AI response (remove markdown formatting)
    refined_code = ai_response.strip()
    if refined_code.startswith("```"):
        lines = refined_code.split('\n')
        if lines[0].startswith("```") and lines[-1].strip() == "```":
            refined_code = '\n'.join(lines[1:-1])

    if update_callback:
        await update_callback({
            "status": "code_refined",
            "message": f"✅ AI fixed diagram code (attempt {refinement_attempt})",
            "message_type": "success"
        })
    
    logger.info(f"🔧 Refined {diagram_type_str} code - attempt {refinement_attempt} complete", 
               extra={'session_id': session_id} if session_id else {})
    
    return {
        "diagram_code": refined_code,
        "validation_error": "",  # Clear error after refinement
        "refinement_attempt": refinement_attempt,
        "current_state": SessionState.VALIDATING
    }


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

    # Direct provider system call - no fallback
    provider_registry = get_registry()
    provider = provider_registry.get_provider_for_type(diagram_type.value)

    if not provider:
        raise ValueError(f"No provider available for {diagram_type.value}")

    result = await provider.render_with_validation(
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
