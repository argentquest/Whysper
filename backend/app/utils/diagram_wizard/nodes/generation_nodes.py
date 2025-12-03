"""
Generation nodes for JSON representation and diagram code creation.

Handles JSON/Structurizr generation, diagram type determination,
and diagram code generation.
"""

import json
from typing import Dict, Any
from ..graph_state import GraphState, DiagramType, SessionState
from ..prompt_loader import get_prompt
from ..keyword_scorer import determine_diagram_type
from ...architecture_schema import ArchitectureSchema
from .llm_helpers import call_llm, get_diagram_type_str, extract_json_from_response
from common.logging_decorator import log_method_call
from common.logger import get_logger

logger = get_logger(__name__)


@log_method_call
async def generate_json_representation(state: GraphState) -> Dict[str, Any]:
    """
    Generates comprehensive architecture representations (Structurizr DSL + Legacy JSON).

    Calls an LLM with a specialized prompt to convert the conversation history into:
    1. A Structurizr workspace (full with views)
    2. A clean Structurizr representation (normalized, model only)
    3. A legacy JSON object (backward compatibility)

    All three representations must be synchronized and valid.

    Args:
        state (GraphState): The current graph state.

    Returns:
        Dict[str, Any]: Dictionary containing 'structurizr_workspace', 'clean_structurizr',
                        and 'json_representation', or error information.
    """
    session_id = state.get("_session_id")
    model_id = state.get("model_id", "claude")  # Get selected model
    logger.info(f"Generating JSON representation (model: {model_id})...", extra={"session_id": session_id})

    update_callback = state.get("_update_callback")
    if update_callback:
        await update_callback(
            {
                "status": "generating_json",
                "message": "AI is validating and finalizing architecture representation...",
            }
        )

    # Load model-specific JSON_GENERATION prompt
    prompt_template = get_prompt("json_generation", model_id=model_id)
    if not prompt_template:
        logger.info(f"json_generation prompt not found for model: {model_id}", extra={"session_id": session_id})
        # Fallback: use existing representations from clarify_prompt
        return {
            "structurizr_workspace": state.get("structurizr_workspace", ""),
            "clean_structurizr": state.get("clean_structurizr", ""),
            "json_representation": state.get("json_representation", {}),
        }

    # Build prompt content from conversation history
    clarification_history = state.get("clarification_history", [])
    user_content = "\n".join([msg.get("content", "") for msg in clarification_history if msg.get("role") == "user"])

    logger.debug(f"Preparing LLM (model: {model_id})...", extra={"session_id": session_id})

    # Call LLM with model-specific prompt
    try:
        ai_response_str = await call_llm(prompt_template, user_content, session_id, model_id=model_id)
    except Exception as e:
        error_message = str(e)
        logger.info(
            f"AI call failed in generate_json_representation: {error_message}", extra={"session_id": session_id}
        )
        if update_callback:
            await update_callback(
                {
                    "status": "failed",
                    "message": f"Failed to generate JSON representation: {error_message}",
                    "error": error_message,
                }
            )
        # Return existing state representations as fallback
        return {
            "structurizr_workspace": state.get("structurizr_workspace", ""),
            "clean_structurizr": state.get("clean_structurizr", ""),
            "json_representation": state.get("json_representation", {}),
            "error_message": error_message,
        }

    logger.debug(f"AI Response {ai_response_str}", extra={"session_id": session_id})

    try:
        # Parse AI response as JSON (handles markdown code fences)
        response = extract_json_from_response(ai_response_str)

        # Extract three representations
        structurizr_workspace = response.get("structurizr_workspace", "")
        clean_structurizr = response.get("clean_structurizr", "")
        json_representation = response.get("json_representation", {})

        # Validate Structurizr syntax (basic check)
        if not structurizr_workspace or not structurizr_workspace.startswith("workspace"):
            logger.info("Structurizr workspace missing or invalid format", extra={"session_id": session_id})

        if not clean_structurizr or not clean_structurizr.startswith("model"):
            logger.info("clean_structurizr missing or invalid format", extra={"session_id": session_id})

        # Validate legacy JSON schema
        if json_representation:
            is_valid, errors = ArchitectureSchema.validate(json_representation)
            if not is_valid:
                logger.info(f"Legacy JSON schema validation issues: {errors}", extra={"session_id": session_id})
                # Don't fail - JSON node is validation, not blocking

        logger.info(
            "Successfully generated JSON representation with Structurizr and legacy schema.",
            extra={"session_id": session_id},
        )
        if update_callback:
            await update_callback(
                {
                    "status": "json_generated",
                    "message": "Successfully validated and finalized architecture representation.",
                    # Note: structurizr_workspace, clean_structurizr, json_generation_output
                    # are in LangGraph state and included via get_status() in _push_update
                }
            )

        return {
            "structurizr_workspace": structurizr_workspace,
            "clean_structurizr": clean_structurizr,
            "json_representation": json_representation,
            "json_generation_output": ai_response_str,
        }

    except json.JSONDecodeError as e:
        logger.info(f"AI response not valid JSON: {e}", extra={"session_id": session_id})
        if update_callback:
            await update_callback(
                {
                    "status": "error",
                    "message": "AI response was not valid JSON format.",
                }
            )
        # Return existing state representations as fallback
        return {
            "structurizr_workspace": state.get("structurizr_workspace", ""),
            "clean_structurizr": state.get("clean_structurizr", ""),
            "json_representation": state.get("json_representation", {}),
            "json_generation_output": ai_response_str,
        }

    except Exception as e:
        logger.info(f"Unexpected error during JSON generation: {e}", extra={"session_id": session_id})
        if update_callback:
            await update_callback(
                {
                    "status": "error",
                    "message": "Unexpected error during JSON generation.",
                }
            )
        # Return existing state representations as fallback
        return {
            "structurizr_workspace": state.get("structurizr_workspace", ""),
            "clean_structurizr": state.get("clean_structurizr", ""),
            "json_representation": state.get("json_representation", {}),
        }


@log_method_call
async def determine_diagram_type_node(state: GraphState) -> Dict[str, Any]:
    """
    Determines the appropriate diagram type options based on keyword analysis.

    Runs after the clarification loop completes, analyzing the final
    design summary and JSON representation to score all diagram types
    (Mermaid, D2, PlantUML, Structurizr) and present them to the user for selection.

    Args:
        state (GraphState): The current graph state.

    Returns:
        Dict[str, Any]: Updates to the graph state including keyword scores and awaiting selection flag.
    """
    session_id = state.get("_session_id")

    # Check if user has already selected a diagram type (resuming after selection)
    if state.get("user_selected_diagram_type", False):
        logger.info(
            "✅ User has already selected diagram type, proceeding to code generation...",
            extra={"session_id": session_id} if session_id else {},
        )
        # Return existing state values without changing anything
        return {
            "keyword_scores": state.get("keyword_scores", {}),
            "user_selected_diagram_type": True,  # Keep the selection flag
            "analysis_text": state.get("analysis_text", ""),
            "json_generation_output": state.get("json_generation_output", ""),
            "current_state": SessionState.GENERATING,
        }

    final_design_summary = state.get("final_design_summary", "")
    json_representation = state.get("json_representation", {})
    json_generation_output = state.get("json_generation_output", "")
    clarification_history = state.get("clarification_history", [])
    json_generation_output = state.get("json_generation_output", "")

    logger.info(
        "🎯 Analyzing diagram type options based on clarification results...",
        extra={"session_id": session_id} if session_id else {},
    )

    # Combine design summary and JSON metadata for better keyword analysis
    analysis_parts = []
    if final_design_summary:
        analysis_parts.append(final_design_summary)

    if json_representation and isinstance(json_representation, dict):
        metadata = json_representation.get("metadata", {})
        if metadata:
            description = metadata.get("description", "")
            if description:
                analysis_parts.append(description)
        # As a fallback, include the JSON structure for keyword matching
        try:
            analysis_parts.append(json.dumps(json_representation))
        except Exception:
            pass

    # Include clarification history text as additional context
    if clarification_history and isinstance(clarification_history, list):
        history_text = "\n".join(msg.get("content", "") for msg in clarification_history if isinstance(msg, dict))
        if history_text:
            analysis_parts.append(history_text)

    # Include raw JSON generation output for richer keyword context
    if json_generation_output:
        analysis_parts.append(json_generation_output)

    analysis_text = "\n".join(part for part in analysis_parts if part).strip()

    # Determine diagram type using keyword scoring (get recommended type and all scores)
    recommended_type, keyword_scores = determine_diagram_type(analysis_text)

    logger.info(
        f"📊 Diagram type scores calculated: Mermaid={
            keyword_scores.get(
                'Mermaid',
                0):.1f}%, D2={
            keyword_scores.get(
                'D2',
                0):.1f}%, PlantUML={
                    keyword_scores.get(
                        'PlantUML',
                        0):.1f}%, Structurizr={
                            keyword_scores.get(
                                'Structurizr',
                                0):.1f}% | Recommended: {
                                    recommended_type.value}",
        extra={"session_id": session_id} if session_id else {},
    )

    # Send update to frontend with all diagram type options and scores for user selection
    update_callback = state.get("_update_callback")
    if update_callback and callable(update_callback):
        await update_callback(
            {
                "status": "awaiting_diagram_type_selection",
                "message": "Please select your preferred diagram type",
                "recommended_diagram_type": recommended_type.value,
                "keyword_scores": keyword_scores,
                "analysis_text": analysis_text,
                "json_generation_output": json_generation_output,
                "awaiting_user_selection": True,
                "message_type": "diagram_type_selection",
            }
        )

    return {
        "keyword_scores": keyword_scores,
        "user_selected_diagram_type": False,  # Waiting for user selection
        "analysis_text": analysis_text,
        "json_generation_output": json_generation_output,
        "current_state": SessionState.GENERATING,
    }


@log_method_call
async def generate_code(state: GraphState) -> Dict[str, Any]:
    """
    Code generation node.

    Generates diagram code from the structured JSON representation.
    Uses diagram-type-specific generation prompt.

    Args:
        state (GraphState): The current graph state.

    Returns:
        Dict[str, Any]: Updates to the graph state including the generated diagram code.
    """

    diagram_type = state.get("diagram_type", DiagramType.MERMAID)
    diagram_type_str = get_diagram_type_str(diagram_type)
    json_representation = state.get("json_representation", {})
    json_generation_output = state.get("json_generation_output", "")
    model_id = state.get("model_id")  # Get selected model from state
    session_id = state.get("_session_id")

    # Try specialized first-pass system prompt per diagram type
    firstpass_key = f"firstpass_{diagram_type_str.lower()}"
    prompt_template = get_prompt(firstpass_key, model_id=model_id)
    prompt_source = firstpass_key

    # Fallback to standard generation prompt template
    if not prompt_template:
        prompt_key = f"generate_{diagram_type_str.lower()}"
        prompt_template = get_prompt(prompt_key, model_id=model_id)
        prompt_source = prompt_key

    if not prompt_template:
        # Fallback prompt if specific prompt not found
        prompt_template = f"""You are a {diagram_type_str} diagram code generator.

Create ONLY the diagram code based on the following JSON representation. Do not include explanations or markdown formatting.

JSON Representation:
{json.dumps(json_representation, indent=2)}

Generate clean, syntactically correct {diagram_type_str} code:"""
        prompt_source = "inline_fallback"

    logger.info(
        f"Generating {diagram_type_str} code using AI (model: {model_id})",
        extra={"session_id": session_id} if session_id else {},
    )

    # Prefer the raw JSON generation output if available; otherwise use structured JSON
    llm_input_payload = json_generation_output if json_generation_output else json.dumps(json_representation, indent=2)

    # Send progress update to frontend
    update_callback = state.get("_update_callback")
    if update_callback and callable(update_callback):
        await update_callback(
            {
                "status": "generating",
                "message": f"AI is generating {diagram_type_str} diagram code...",
                "message_type": "progress",
                "diagram_type": diagram_type_str,
                "generation_payload_preview": llm_input_payload[:1000],  # truncate for safety
            }
        )

    logger.info(
        f"Starting first-pass code generation for {diagram_type_str} using prompt '{prompt_source}'. Payload length={
            len(llm_input_payload)}",
        extra={"session_id": session_id} if session_id else {},
    )
    logger.debug(
        f"Payload preview (first 800 chars): {llm_input_payload[:800]}",
        extra={"session_id": session_id} if session_id else {},
    )

    try:
        ai_response = await call_llm(prompt_template, llm_input_payload, session_id, model_id=model_id)
    except Exception as e:
        error_message = str(e)
        logger.info(f"AI call failed in generate_code: {error_message}", extra={"session_id": session_id})
        if update_callback:
            await update_callback(
                {
                    "status": "failed",
                    "message": f"Code generation failed: {error_message}",
                    "error": error_message,
                }
            )
        return {
            "diagram_code": "",
            "error_message": error_message,
            "current_state": "failed",
        }

    # Clean up the response (remove any markdown formatting)
    diagram_code = ai_response.strip()
    if diagram_code.startswith("```"):
        lines = diagram_code.split("\n")
        # Remove first and last lines if they're markdown code blocks
        if lines[0].startswith("```") and lines[-1].strip() == "```":
            diagram_code = "\n".join(lines[1:-1])

    logger.info(
        f"📄 Generated {diagram_type_str} code - length: {len(diagram_code)} chars",
        extra={"session_id": session_id} if session_id else {},
    )

    # Send success update to frontend with diagram code
    # Include diagramCode here to avoid timing issues with REST API polling
    if update_callback:
        await update_callback(
            {
                "status": "code_generated",
                "message": f"✅ Generated {diagram_type_str} diagram code ({len(diagram_code)} chars)",
                "message_type": "success",
                "diagramCode": diagram_code,  # Include code for immediate display
            }
        )

    return {"diagram_code": diagram_code, "current_state": SessionState.VALIDATING}
