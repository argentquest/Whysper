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
    logger.info("🔬 Analyzing initial user request...", extra={'session_id': session_id})

    update_callback = state.get("_update_callback")
    if update_callback:
        await update_callback({
            "status": "analyzing",
            "message": "AI is analyzing your request...",
        })

    prompt_template = get_prompt("analyze_request")
    if not prompt_template:
        logger.error("analyze_request prompt not found!", extra={'session_id': session_id})
        return {
            "next_action": "clarify",
            "clarification_question": "I'm having trouble understanding your request. Could you please describe the diagram you want to create in more detail?",
            "error_message": "Internal error: analysis prompt not found."
        }

    clarification_history = state.get("clarification_history", [])
    user_content = "\n".join([msg.get('content', '') for msg in clarification_history if msg.get('role') == 'user'])

    ai_response_str = await _call_llm(prompt_template, user_content, session_id)

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

        return {
            "next_action": "clarify",
            "assessment_score": assessment_score,
            "json_representation": state.get("json_representation", {}),
            "clarification_history": clarification_history + [{"role": "assistant", "content": analysis_summary or ""}],
            "current_state": SessionState.CLARIFYING,
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


@log_method_call
async def _call_llm(prompt: str, user_content: str, session_id: str = None) -> str:
    """Helper function to call AI/LLM with proper error handling and SSE logging.
    
    Args:
        prompt: System prompt template
        user_content: User message content
        session_id: Session ID for SSE filtering (optional)
        
    Returns:
        AI response string
    """
    try:
        # Load environment configuration
        env_vars = env_manager.load_env_file()
        api_key = env_vars.get("API_KEY", "")
        provider = env_vars.get("PROVIDER", "openrouter")
        model = env_vars.get("DEFAULT_MODEL", "google/gemini-2.5-flash-preview-09-2025")
        
        if not api_key:
            logger.error("No API key configured for diagram wizard AI calls", 
                        extra={'session_id': session_id} if session_id else {})
            return "ERROR: No API key configured"
        
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
        logger.error(f"❌ AI call failed due to a network error: {e}", 
                    extra={'session_id': session_id} if session_id else {})
        return f"ERROR: AI call failed due to a network error - {str(e)}"
    except json.JSONDecodeError as e:
        logger.error(f"❌ Failed to parse AI response as JSON: {e}", 
                    extra={'session_id': session_id} if session_id else {})
        return f"ERROR: Failed to parse AI response as JSON - {str(e)}"
    except Exception as e:
        logger.error(f"❌ An unexpected error occurred during the AI call: {e}", 
                    extra={'session_id': session_id} if session_id else {})
        return f"ERROR: An unexpected error occurred during the AI call - {str(e)}"


@log_method_call
async def generate_json_representation(state: GraphState) -> Dict[str, Any]:
    """
    Generates a structured JSON representation of the diagram.

    Calls an LLM with a specialized prompt to convert the conversation
    history into a JSON object that conforms to the architecture schema.

    Returns:
        - A dictionary with 'json_representation' containing the generated JSON.
    """
    session_id = state.get("_session_id")
    logger.info("Generating JSON representation...", extra={'session_id': session_id})

    update_callback = state.get("_update_callback")
    if update_callback:
        await update_callback({
            "status": "generating_json",
            "message": "AI is creating a structured representation of your diagram...",
        })

    prompt_template = get_prompt("json_generation")
    if not prompt_template:
        logger.error("json_generation prompt not found!", extra={'session_id': session_id})
        return {
            "error_message": "Internal error: JSON generation prompt not found."
        }

    clarification_history = state.get("clarification_history", [])
    user_content = "\n".join([msg.get('content', '') for msg in clarification_history if msg.get('role') == 'user'])

    ai_response_str = await _call_llm(prompt_template, user_content, session_id)

    try:
        json_representation = json.loads(ai_response_str)
        
        # Validate the JSON against the schema
        is_valid, errors = ArchitectureSchema.validate(json_representation)
        if not is_valid:
            raise ValueError(f"Generated JSON is invalid: {errors}")

        logger.info("Successfully generated and validated JSON representation.", extra={'session_id': session_id})
        if update_callback:
            await update_callback({
                "status": "json_generated",
                "message": "Successfully created structured representation.",
            })

        return {
            "json_representation": json_representation,
        }

    except (json.JSONDecodeError, ValueError) as e:
        logger.error(f"Error processing JSON response from AI: {e}", extra={'session_id': session_id})
        if update_callback:
            await update_callback({
                "status": "error",
                "message": "Failed to create a structured representation of your diagram.",
            })
        return {
            "error_message": str(e),
        }


@log_method_call
async def clarify_prompt(state: GraphState) -> Dict[str, Any]:
    """
    Clarification loop node.

    Interviews user to build a final design summary.
    Calls LLM with clarification prompts specific to diagram type.

    Returns:
        - If llm_ready: True, returns final_design_summary
        - If llm_ready: False, returns next question via SSE
    """
    # Check if we're already ready to proceed (skip clarification)
    # BUT only if user explicitly confirmed readiness, not AI-determined
    if (state.get("llm_ready", False) and
        state.get("final_design_summary") and
        state.get("user_confirmed_ready", False)):
        session_id = state.get("_session_id")
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
        logger.warning(f"Clarification timeout reached: {question_count} questions, {current_time - start_time:.1f}s elapsed",
                      extra={'session_id': state.get("_session_id")})
        return {
            "llm_ready": True,
            "final_design_summary": "TIMEOUT: Maximum clarification attempts reached. Proceeding with available information.",
            "clarification_timeout": True,
            "current_state": SessionState.GENERATING
        }

    # Get both ANALYZE and CLARIFY prompts for persistent schema context
    analyze_prompt = get_prompt("analyze_request")
    clarify_prompt_template = get_prompt("clarify_universal")

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
    logger.info(f"🤖 Making LLM call for clarification - attempt {question_count + 1}",
               extra={'session_id': session_id} if session_id else {})
    logger.info(f"📝 User context being sent to LLM: {user_content[:200]}{'...' if len(user_content) > 200 else ''}",
               extra={'session_id': session_id} if session_id else {})
    ai_response_str = await _call_llm(prompt_template, user_content, session_id)

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
        logger.error(f"❌ Failed to parse clarification response as JSON: {e}",
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
    
    # Get code generation prompt template
    prompt_key = f"generate_{diagram_type_str.lower()}"
    prompt_template = get_prompt(prompt_key)
    
    if not prompt_template:
        # Fallback prompt if specific prompt not found
        prompt_template = f"""You are a {diagram_type_str} diagram code generator.

Create ONLY the diagram code based on the following JSON representation. Do not include explanations or markdown formatting.

JSON Representation:
{json.dumps(json_representation, indent=2)}

Generate clean, syntactically correct {diagram_type_str} code:"""

    # Get session ID for SSE logging
    session_id = state.get("_session_id")
    
    logger.info(f"Generating {diagram_type_str} code using AI", 
               extra={'session_id': session_id} if session_id else {})
    
    # Send progress update to frontend
    update_callback = state.get("_update_callback")
    if update_callback and callable(update_callback):
        await update_callback({
            "status": "generating", 
            "message": f"AI is generating {diagram_type_str} diagram code...",
            "message_type": "progress"
        })
    
    ai_response = await _call_llm(prompt_template, json.dumps(json_representation, indent=2), session_id)
    
    if ai_response.startswith("ERROR:"):
        logger.error(f"AI code generation failed: {ai_response}")
        if update_callback:
            await update_callback({
                "status": "error", 
                "message": f"Code generation failed: {ai_response}",
                "message_type": "error"
            })
        return {
            "diagram_code": "",
            "current_state": SessionState.ERROR,
            "error_message": ai_response
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

    Validates diagram code using the provider registry.
    Supports D2, Mermaid (mmdc), and PlantUML via registered providers.

    Returns:
        - is_valid: True if code is valid
        - validation_error: Error message if invalid
        - validation_error_type: Classification of error
        - recovery_suggestions: List of suggestions to fix
    """
    diagram_code = state.get("diagram_code", "")
    diagram_type = state.get("diagram_type", DiagramType.MERMAID)
    provider_id = state.get("provider_id")
    session_id = state.get("_session_id")
    
    logger.info(f"🔍 Validating {diagram_type} diagram code ({len(diagram_code)} chars)", 
               extra={'session_id': session_id} if session_id else {})

    if not diagram_code.strip():
        return {
            "is_valid": False,
            "validation_error": "No diagram code provided",
            "validation_error_type": "missing_code",
            "recovery_suggestions": ["Generate diagram code first"],
            "current_state": SessionState.VALIDATION_ERROR
        }

    # Try to use provider registry for validation
    if PROVIDER_AVAILABLE:
        try:
            registry = get_registry()

            # Map diagram type to provider
            if provider_id is None:
                diagram_type_str = get_diagram_type_str(diagram_type)
                provider_id = PROVIDER_MAP.get(diagram_type_str, "mermaidv1")

            provider = registry.get(provider_id)
            if provider:
                validation_result = provider.validate_code(diagram_code)

                if validation_result.is_valid:
                    logger.info(f"✅ Code validation successful using provider {provider_id}", 
                               extra={'session_id': session_id} if session_id else {})
                    return {
                        "is_valid": True,
                        "validation_error": "",
                        "validation_error_type": "",
                        "recovery_suggestions": [],
                        "provider_id": provider_id,
                        "current_state": SessionState.RENDERING
                    }
                else:
                    logger.info(f"❌ Code validation failed: {validation_result.error}", 
                               extra={'session_id': session_id} if session_id else {})
                    return {
                        "is_valid": False,
                        "validation_error": validation_result.error or "Code validation failed",
                        "validation_error_type": "syntax_error",
                        "recovery_suggestions": ["Review the error message and fix the syntax"],
                        "provider_id": provider_id,
                        "current_state": SessionState.VALIDATION_ERROR
                    }
        except Exception as e:
            logger.warning(f"Provider validation failed: {e}, falling back to basic validation")

    # Fallback: basic validation check
    if diagram_type == DiagramType.MERMAID:
        # More specific checks for different Mermaid diagram types
        mermaid_keywords = ["flowchart", "sequenceDiagram", "gantt", "classDiagram", "stateDiagram", "pie", "erDiagram", "journey"]
        if not any(keyword in diagram_code for keyword in mermaid_keywords) and "graph" not in diagram_code:
            return {
                "is_valid": False,
                "validation_error": "Missing or invalid Mermaid diagram type declaration",
                "validation_error_type": "syntax_error",
                "recovery_suggestions": ["Start with a valid Mermaid diagram type (e.g., 'flowchart TD', 'sequenceDiagram')."],
                "provider_id": None,
                "current_state": SessionState.VALIDATION_ERROR
            }
    elif diagram_type == DiagramType.D2:
        # Check for connections or shapes
        if "->" not in diagram_code and "<->" not in diagram_code and "shape:" not in diagram_code:
            return {
                "is_valid": False,
                "validation_error": "Invalid D2 diagram: No connections or shapes found",
                "validation_error_type": "syntax_error",
                "recovery_suggestions": ["Add connections (e.g., 'a -> b') or define shapes (e.g., 'db: {shape: sql_database}')."],
                "provider_id": None,
                "current_state": SessionState.VALIDATION_ERROR
            }
    elif diagram_type == DiagramType.PLANTUML:
        plantuml_keywords = ["actor", "participant", "class", "interface", "usecase", "component"]
        if "@startuml" not in diagram_code or "@enduml" not in diagram_code or not any(keyword in diagram_code for keyword in plantuml_keywords):
            return {
                "is_valid": False,
                "validation_error": "Invalid PlantUML diagram: Missing markers or core keywords",
                "validation_error_type": "syntax_error",
                "recovery_suggestions": ["Ensure the diagram is wrapped in '@startuml' and '@enduml' and contains valid keywords (e.g., 'actor', 'class')."],
                "provider_id": None,
                "current_state": SessionState.VALIDATION_ERROR
            }

    # If we get here, assume valid (fallback validation)
    return {
        "is_valid": True,
        "validation_error": "",
        "validation_error_type": "",
        "recovery_suggestions": [],
        "provider_id": None,  # No specific provider used in fallback
        "current_state": SessionState.RENDERING
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

    if refinement_attempt >= 3:
        logger.error("Max refinement attempts reached. Unable to fix code.", extra={'session_id': state.get("_session_id")})
        return {
            "is_valid": False,
            "error_message": "Max refinement attempts reached. Unable to fix code.",
            "current_state": SessionState.ERROR,
        }
    
    # Get refinement prompt template
    prompt_key = f"refine_{diagram_type_str.lower()}"
    prompt_template = get_prompt(prompt_key)
    
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
    
    logger.info(f"Refining {diagram_type_str} code using AI - attempt {refinement_attempt}", 
               extra={'session_id': session_id} if session_id else {})
    ai_response = await _call_llm(prompt_template, error_context, session_id)
    
    if ai_response.startswith("ERROR:"):
        logger.error(f"AI code refinement failed: {ai_response}")
        # Fallback to simple rule-based fixes
        refined_code = diagram_code
        error_type = state.get("validation_error_type", "unknown")
        
        if error_type == "syntax_error":
            if diagram_type_str == "Mermaid" and "graph" not in refined_code:
                refined_code = "graph TD\n" + refined_code
            elif diagram_type_str == "D2" and "->" not in refined_code:
                refined_code = refined_code.replace("-", "->")
            elif diagram_type_str == "PlantUML" and "@startuml" not in refined_code:
                refined_code = "@startuml\n" + refined_code + "\n@enduml"
        
        if update_callback:
            await update_callback({
                "status": "fallback_fix", 
                "message": f"⚠️ AI refinement failed, applied basic syntax fixes",
                "message_type": "warning"
            })
    else:
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

    Renders valid diagram code to SVG format using provider registry.
    Uses appropriate provider based on diagram type.

    Returns:
        svg_output: SVG representation of diagram
    """
    diagram_code = state.get("diagram_code", "")
    diagram_type = state.get("diagram_type", DiagramType.MERMAID)
    provider_id = state.get("provider_id")
    session_id = state.get("_session_id")
    
    logger.info(f"🎨 Rendering {diagram_type} diagram to SVG using provider {provider_id or 'fallback'}", 
               extra={'session_id': session_id} if session_id else {})

    if not diagram_code.strip():
        return {
            "svg_output": "",
            "error_message": "No diagram code to render",
            "current_state": SessionState.ERROR
        }

    # Try to use provider registry for rendering
    if PROVIDER_AVAILABLE:
        try:
            registry = get_registry()

            # Map diagram type to provider if not set
            if provider_id is None:
                diagram_type_str = get_diagram_type_str(diagram_type)
                provider_id = PROVIDER_MAP.get(diagram_type_str, "mermaidv1")

            provider = registry.get(provider_id)
            if provider:
                # Use render_with_validation to leverage the provider's error correction
                render_result = provider.render_with_validation(
                    code=diagram_code,
                    output_format="svg",
                    auto_fix=True,
                    llm_correction=False  # Already done by wizard
                )

                if render_result.success:
                    logger.info(f"✅ SVG rendering successful ({len(render_result.content)} chars)", 
                               extra={'session_id': session_id} if session_id else {})
                    return {
                        "svg_output": render_result.content,
                        "provider_id": provider_id,
                        "current_state": SessionState.READY
                    }
                else:
                    logger.error(f"❌ SVG rendering failed: {render_result.error}", 
                                extra={'session_id': session_id} if session_id else {})
                    return {
                        "svg_output": "",
                        "error_message": f"Rendering failed: {render_result.error}",
                        "provider_id": provider_id,
                        "current_state": SessionState.ERROR
                    }
        except Exception as e:
            logger.warning(f"Provider rendering failed: {e}, falling back to placeholder")

    # Fallback: create a simple SVG placeholder with code
    diagram_type_str = diagram_type.value if hasattr(diagram_type, 'value') else str(diagram_type)
    svg_placeholder = f"""<svg width="500" height="400" xmlns="http://www.w3.org/2000/svg">
    <rect width="100%" height="100%" fill="#f9f9f9" stroke="#ddd" stroke-width="1"/>
    <rect x="20" y="20" width="460" height="80" fill="#e8f4f8" stroke="#0288d1" stroke-width="2" rx="4"/>
    <text x="50%" y="45" text-anchor="middle" dominant-baseline="middle" font-family="Arial" font-size="18" font-weight="bold" fill="#0288d1">
        {diagram_type_str} Diagram
    </text>
    <text x="50%" y="75" text-anchor="middle" dominant-baseline="middle" font-family="Arial" font-size="12" fill="#666">
        Provider rendering unavailable - code preview below
    </text>
    <rect x="20" y="120" width="460" height="260" fill="#fff" stroke="#ccc" stroke-width="1" rx="2"/>
    <text x="30" y="140" font-family="monospace" font-size="11" fill="#333">Code:</text>
    <text x="30" y="165" font-family="monospace" font-size="10" fill="#666">
        {diagram_code[:60]}...
    </text>
</svg>"""

    logger.info(f"📋 Using fallback SVG placeholder for {diagram_type_str} diagram", 
               extra={'session_id': session_id} if session_id else {})
    
    return {
        "svg_output": svg_placeholder,
        "current_state": SessionState.READY
    }
