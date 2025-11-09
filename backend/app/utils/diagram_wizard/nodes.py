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

# Import provider registry for validation and rendering
try:
    from diagrams.provider_registry import get_registry
    PROVIDER_AVAILABLE = True
except ImportError:
    PROVIDER_AVAILABLE = False

logger = logging.getLogger(__name__)


async def clarify_prompt(state: GraphState) -> Dict[str, Any]:
    """
    Clarification loop node.

    Interviews user to build a final design summary.
    Calls LLM with clarification prompts specific to diagram type.

    Returns:
        - If llm_ready: True, returns final_design_summary
        - If llm_ready: False, returns next question via SSE
    """
    # TODO: Implement clarification loop
    # 1. Get clarification history from state
    # 2. Get appropriate prompts based on diagram_type
    # 3. Call LLM with CLARIFY_PROMPT
    # 4. Check if response starts with "READY:"
    # 5. If READY, extract summary and set llm_ready=True
    # 6. If not READY, add question to history and set llm_ready=False
    # 7. Return updated state
    
    # For now, return placeholder implementation
    diagram_type = state.get("diagram_type", "Mermaid")
    prompt_key = f"clarify_{diagram_type.lower()}"
    prompt = get_prompt(prompt_key)
    
    if prompt:
        # Placeholder: simulate LLM response
        llm_response = f"READY: Sample design for {diagram_type} diagram"
        if llm_response.startswith("READY:"):
            summary = llm_response.replace("READY:", "").strip()
            return {
                "llm_ready": True,
                "final_design_summary": summary,
                "current_state": "generating"
            }
    
    # Default: ask a question
    question = f"What specific details would you like in your {diagram_type} diagram?"
    history = state.get("clarification_history", [])
    history.append({"role": "ai", "content": question})
    
    return {
        "llm_ready": False,
        "clarification_history": history,
        "question_count": state.get("question_count", 0) + 1,
        "current_state": "clarifying"
    }


async def generate_code(state: GraphState) -> Dict[str, Any]:
    """
    Code generation node.

    Generates diagram code from final design summary.
    Uses diagram-type-specific generation prompt.

    Returns:
        diagram_code: The generated diagram code
    """
    # TODO: Implement code generation
    # 1. Get final_design_summary from state
    # 2. Get diagram_type from state
    # 3. Load appropriate GENERATE_PROMPT for diagram type
    # 4. Call LLM with template
    # 5. Extract and return diagram code
    
    # For now, return placeholder implementation
    diagram_type = state.get("diagram_type", "Mermaid")
    design_summary = state.get("final_design_summary", "Sample diagram")
    prompt_key = f"generate_{diagram_type.lower()}"
    prompt = get_prompt(prompt_key)
    
    if prompt:
        # Placeholder: simulate LLM response
        if diagram_type == "Mermaid":
            code = """graph TD
    A[Start] --> B{Decision}
    B -->|Yes| C[Process A]
    B -->|No| D[Process B]
    C --> E[End]
    D --> E"""
        elif diagram_type == "D2":
            code = """A: Client
B: Server
C: Database

A -> B: Request
B -> C: Query
C -> B: Response
B -> A: Result"""
        else:  # PlantUML
            code = """@startuml
actor User
participant Server
database Database

User -> Server: Request
Server -> Database: Query
Database --> Server: Data
Server --> User: Response
@enduml"""
        
        return {
            "diagram_code": code,
            "current_state": "validating"
        }
    
    return {
        "diagram_code": f"# {diagram_type} code placeholder",
        "current_state": "error"
    }


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
                    return {
                        "is_valid": True,
                        "validation_error": "",
                        "validation_error_type": "",
                        "recovery_suggestions": [],
                        "provider_id": provider_id,
                        "current_state": "rendering"
                    }
                else:
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


async def refine_code(state: GraphState) -> Dict[str, Any]:
    """
    Refinement node.

    Fixes invalid diagram code based on validation error.
    Uses error-specific refinement prompts.

    Returns:
        diagram_code: Refined and corrected code
    """
    # TODO: Implement code refinement
    # 1. Get validation_error and diagram_code
    # 2. Get final_design_summary and diagram_type
    # 3. Classify error type
    # 4. Load appropriate REFINE_PROMPT
    # 5. Call LLM with error context
    # 6. Extract and return refined code
    # 7. Increment refinement_attempt counter
    
    # For now, return placeholder implementation
    diagram_code = state.get("diagram_code", "")
    validation_error = state.get("validation_error", "")
    diagram_type = state.get("diagram_type", "Mermaid")
    refinement_attempt = state.get("refinement_attempt", 0) + 1
    
    # Simple refinement: try to fix common issues
    refined_code = diagram_code
    error_type = state.get("validation_error_type", "unknown")
    
    if error_type == "syntax_error":
        if diagram_type == "Mermaid" and "graph" not in refined_code:
            refined_code = "graph TD\n" + refined_code
        elif diagram_type == "D2" and "->" not in refined_code:
            refined_code = refined_code.replace("-", "->")
        elif diagram_type == "PlantUML" and "@startuml" not in refined_code:
            refined_code = "@startuml\n" + refined_code + "\n@enduml"
    
    return {
        "diagram_code": refined_code,
        "validation_error": "",  # Clear error after refinement
        "refinement_attempt": refinement_attempt,
        "current_state": "validating"
    }


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
                    return {
                        "svg_output": render_result.content,
                        "provider_id": provider_id,
                        "current_state": "ready"
                    }
                else:
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

    return {
        "svg_output": svg_placeholder,
        "current_state": "ready"
    }