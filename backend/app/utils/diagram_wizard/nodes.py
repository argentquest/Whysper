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
from typing import Dict, Any
from .graph_state import GraphState, DiagramType
from .prompt_loader import get_prompt
from .tool_config import DiagramToolRunner, DiagramToolConfig
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
        
    except Exception as e:
        logger.error(f"❌ AI call failed in diagram wizard: {e}", 
                    extra={'session_id': session_id} if session_id else {})
        return f"ERROR: AI call failed - {str(e)}"


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
    if state.get("llm_ready", False) and state.get("final_design_summary"):
        session_id = state.get("_session_id")
        logger.info("🎯 Skipping clarification - already have complete design summary", 
                   extra={'session_id': session_id} if session_id else {})
        return {
            "llm_ready": True,
            "final_design_summary": state.get("final_design_summary"),
            "current_state": "generating"
        }
    
    diagram_type = state.get("diagram_type", DiagramType.MERMAID)
    diagram_type_str = diagram_type.value if hasattr(diagram_type, 'value') else str(diagram_type)
    clarification_history = state.get("clarification_history", [])
    question_count = state.get("question_count", 0)
    
    # Get clarification prompt template
    prompt_key = f"clarify_{diagram_type_str.lower()}"
    prompt_template = get_prompt(prompt_key)
    
    if not prompt_template:
        # Fallback prompt if specific prompt not found
        prompt_template = f"""You are a diagram design assistant for {diagram_type_str} diagrams.

Your task is to interview the user to gather enough information to create a detailed {diagram_type_str} diagram.

CRITICAL INSTRUCTIONS:
1. If you have enough detailed information to create a comprehensive diagram, respond with "READY:" followed by a detailed design summary
2. If you need more information, ask ONE specific clarifying question
3. Focus on gathering: entities/components, relationships/connections, processes/flows, and technical details

Conversation history: {clarification_history}

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
    ai_response = await _call_llm(prompt_template, user_content, session_id)
    
    # Send AI response to frontend immediately via callback if available
    update_callback = state.get("_update_callback")
    if update_callback and callable(update_callback):
        await update_callback({
            "status": "ai_thinking", 
            "message": ai_response,
            "message_type": "clarification"
        })
    
    # Check if AI thinks we're ready to generate
    if ai_response.startswith("READY:"):
        summary = ai_response.replace("READY:", "").strip()
        logger.info("🎯 AI determined enough information gathered - proceeding to diagram generation", 
                   extra={'session_id': session_id} if session_id else {})
        return {
            "llm_ready": True,
            "final_design_summary": summary,
            "current_state": "generating"
        }
    
    # AI wants more clarification - add response to conversation history for context
    logger.info("❓ AI requesting additional clarification from user", 
               extra={'session_id': session_id} if session_id else {})
    logger.info(f"💬 AI response to be stored: {ai_response[:100]}{'...' if len(ai_response) > 100 else ''}", 
               extra={'session_id': session_id} if session_id else {})
    updated_history = clarification_history.copy()
    updated_history.append({"role": "assistant", "content": ai_response})
    
    return {
        "llm_ready": False,
        "clarification_history": updated_history,
        "question_count": question_count + 1,
        "current_state": "clarifying"
    }


@log_method_call
async def generate_code(state: GraphState) -> Dict[str, Any]:
    """
    Code generation node.

    Generates diagram code from final design summary.
    Uses diagram-type-specific generation prompt.

    Returns:
        diagram_code: The generated diagram code
    """
    diagram_type = state.get("diagram_type", DiagramType.MERMAID)
    diagram_type_str = diagram_type.value if hasattr(diagram_type, 'value') else str(diagram_type)
    design_summary = state.get("final_design_summary", "")
    
    # Get code generation prompt template
    prompt_key = f"generate_{diagram_type_str.lower()}"
    prompt_template = get_prompt(prompt_key)
    
    if not prompt_template:
        # Fallback prompt if specific prompt not found
        prompt_template = f"""You are a {diagram_type_str} diagram code generator.

Create ONLY the diagram code based on the design summary. Do not include explanations or markdown formatting.

For {diagram_type_str} diagrams:
{"- Start with 'graph TD' or similar" if diagram_type_str == "Mermaid" else ""}
{"- Use simple syntax: A -> B for connections" if diagram_type_str == "D2" else ""}
{"- Wrap in @startuml...@enduml" if diagram_type_str == "PlantUML" else ""}

Design Summary: {design_summary}

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
    
    ai_response = await _call_llm(prompt_template, design_summary, session_id)
    
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
            "current_state": "error",
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
        "current_state": "validating"
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
            "current_state": "validation_error"
        }

    # Try to use provider registry for validation
    if PROVIDER_AVAILABLE:
        try:
            registry = get_registry()

            # Map diagram type to provider
            if provider_id is None:
                diagram_type_str = diagram_type.value if hasattr(diagram_type, 'value') else str(diagram_type)
                # Map to provider: Mermaid -> mermaidv1, D2 -> d2v1, PlantUML -> krokiplantuml
                provider_map = {
                    "Mermaid": "mermaidv1",
                    "D2": "d2v1",
                    "PlantUML": "krokiplantuml"
                }
                provider_id = provider_map.get(diagram_type_str, "mermaidv1")

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
                        "current_state": "rendering"
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
                        "current_state": "validation_error"
                    }
        except Exception as e:
            logger.warning(f"Provider validation failed: {e}, falling back to basic validation")

    # Fallback: basic validation check
    if diagram_type == DiagramType.MERMAID:
        if "graph" not in diagram_code and "sequenceDiagram" not in diagram_code and "stateDiagram" not in diagram_code:
            return {
                "is_valid": False,
                "validation_error": "Missing Mermaid diagram type declaration",
                "validation_error_type": "syntax_error",
                "recovery_suggestions": ["Add 'graph TD', 'sequenceDiagram', or 'stateDiagram' at the beginning"],
                "provider_id": None,
                "current_state": "validation_error"
            }
    elif diagram_type == DiagramType.D2:
        if "->" not in diagram_code and ("<->" not in diagram_code):
            return {
                "is_valid": False,
                "validation_error": "No connections found in D2 diagram",
                "validation_error_type": "syntax_error",
                "recovery_suggestions": ["Add connections using '->' or '<->' syntax"],
                "provider_id": None,
                "current_state": "validation_error"
            }
    elif diagram_type == DiagramType.PLANTUML:
        if "@startuml" not in diagram_code or "@enduml" not in diagram_code:
            return {
                "is_valid": False,
                "validation_error": "Missing PlantUML diagram markers",
                "validation_error_type": "syntax_error",
                "recovery_suggestions": ["Add '@startuml' at the beginning and '@enduml' at the end"],
                "provider_id": None,
                "current_state": "validation_error"
            }

    # If we get here, assume valid (fallback validation)
    return {
        "is_valid": True,
        "validation_error": "",
        "validation_error_type": "",
        "recovery_suggestions": [],
        "provider_id": None,  # No specific provider used in fallback
        "current_state": "rendering"
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
    diagram_type_str = diagram_type.value if hasattr(diagram_type, 'value') else str(diagram_type)
    refinement_attempt = state.get("refinement_attempt", 0) + 1
    final_design_summary = state.get("final_design_summary", "")
    
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
        "current_state": "validating"
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
            "current_state": "error"
        }

    # Try to use provider registry for rendering
    if PROVIDER_AVAILABLE:
        try:
            registry = get_registry()

            # Map diagram type to provider if not set
            if provider_id is None:
                diagram_type_str = diagram_type.value if hasattr(diagram_type, 'value') else str(diagram_type)
                provider_map = {
                    "Mermaid": "mermaidv1",
                    "D2": "d2v1",
                    "PlantUML": "krokiplantuml"
                }
                provider_id = provider_map.get(diagram_type_str, "mermaidv1")

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
                        "current_state": "ready"
                    }
                else:
                    logger.error(f"❌ SVG rendering failed: {render_result.error}", 
                                extra={'session_id': session_id} if session_id else {})
                    return {
                        "svg_output": "",
                        "error_message": f"Rendering failed: {render_result.error}",
                        "provider_id": provider_id,
                        "current_state": "error"
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
        "current_state": "ready"
    }