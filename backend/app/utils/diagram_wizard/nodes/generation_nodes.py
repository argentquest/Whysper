"""
Generation nodes for JSON representation and diagram code creation.

Handles JSON/Structurizr generation, diagram type determination,
and diagram code generation.
"""

import logging
import json
from typing import Dict, Any
from ..graph_state import GraphState, DiagramType, SessionState
from ..prompt_loader import get_prompt
from ..keyword_scorer import determine_diagram_type
from ...architecture_schema import ArchitectureSchema
from .llm_helpers import call_llm, get_diagram_type_str
from common.logging_decorator import log_method_call

logger = logging.getLogger(__name__)


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
        logger.error(
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
        ai_response_str = await call_llm(
            prompt_template,
            user_content,
            session_id,
            model_id=model_id
        )
    except Exception as e:
        error_message = str(e)
        logger.error(f"AI call failed in generate_json_representation: {error_message}", extra={'session_id': session_id})
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
            logger.warning(
                "Structurizr workspace missing or invalid format",
                extra={'session_id': session_id}
            )

        if not clean_d2 or not clean_d2.startswith("model"):
            logger.warning(
                "clean_d2 missing or invalid format",
                extra={'session_id': session_id}
            )

        # Validate legacy JSON schema
        if json_representation:
            is_valid, errors = ArchitectureSchema.validate(json_representation)
            if not is_valid:
                logger.warning(
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
        logger.error(
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
        logger.error(
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
        ai_response = await call_llm(prompt_template, json.dumps(json_representation, indent=2), session_id, model_id=model_id)
    except Exception as e:
        error_message = str(e)
        logger.error(f"AI call failed in generate_code: {error_message}", extra={'session_id': session_id})
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
