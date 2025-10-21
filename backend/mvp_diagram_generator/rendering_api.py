
"""
Diagram Rendering API

This module provides FastAPI endpoints for generating diagrams from
natural language prompts using AI. It integrates with various diagram
types (Mermaid, D2, C4) and provides both SVG and PNG output formats.

Key Features:
- AI-powered diagram generation from text prompts
- Support for multiple diagram types (Mermaid, D2, C4)
- Diagram validation and error handling
- Multiple output formats (SVG, PNG)
- Integration with frontend rendering infrastructure

Architecture:
1. Receives natural language prompt
2. Loads appropriate agent prompt based on diagram type
3. Calls AI service to generate diagram code
4. Validates generated diagram syntax
5. Renders diagram to image format
6. Returns structured response with metadata
"""

from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel

from app.core.config import Settings, get_settings
from common.logger import get_logger

# Import diagram validation functions
from .diagram_validators import (
    is_valid_d2_diagram,
    is_valid_mermaid_diagram,
    is_valid_c4_diagram,
)
from .d2_syntax_fixer import fix_d2_syntax
from .d2_cli_validator import validate_and_fix_d2_with_cli, is_d2_cli_available

# Import rendering and conversion modules
from .renderer_v2 import render_diagram  # Use new renderer with frontend HTML
from .c4_to_d2 import convert_c4_to_d2

# Import utility functions for AI integration
from app.utils.code_extraction import extract_code_blocks_from_content
from common.ai import create_ai_processor

# Initialize module logger
logger = get_logger(__name__)

# Create FastAPI router for diagram endpoints
router = APIRouter()

# Pydantic models for request/response validation
class DiagramRequest(BaseModel):
    """Request model for diagram generation."""
    prompt: str                    # Natural language description of diagram
    diagram_type: str = "d2"       # Type of diagram to generate
    output_format: str = "svg"     # Output format (svg, png)


class ErrorInfo(BaseModel):
    """Error information model for response."""
    has_error: bool                # Whether an error occurred
    error_message: str             # Error message description


class DiagramResponse(BaseModel):
    """Complete response model for diagram generation."""
    image_data: str               # Base64-encoded image data
    image_format: str             # Format of the generated image
    initial_prompt: str           # Original user prompt
    full_response: str            # Complete AI response (includes thinking)
    diagram_code: str             # Generated diagram source code
    error_info: ErrorInfo         # Error information if any


@router.post("/generate", response_model=DiagramResponse)
async def generate_diagram(
    request: DiagramRequest,
    settings: Settings = Depends(get_settings)
):
    """
    Generate a diagram from a prompt.
    """
    logger.info(f"Received diagram generation request: {request}")

    try:
        # 1. Load the appropriate agent prompt
        try:
            from common.env_manager import env_manager

            # Get prompts directory from environment
            env_vars = env_manager.load_env_file()
            prompts_dir = env_vars.get('PROMPTS_DIR', '').strip()
            if not prompts_dir:
                # Default: prompts directory relative to project root
                script_dir = os.path.dirname(os.path.abspath(__file__))
                prompts_dir = os.path.join(script_dir, "..", "..", "prompts")
            else:
                # Use configured path (can be absolute or relative)
                if not os.path.isabs(prompts_dir):
                    prompts_dir = os.path.abspath(prompts_dir)
                # Append prompts if not already in path
                if not prompts_dir.endswith('prompts'):
                    prompts_dir = os.path.join(prompts_dir, "prompts")

            prompt_file_path = os.path.join(prompts_dir, "coding", "agent", f"{request.diagram_type}-architecture.md")

            with open(prompt_file_path, "r") as f:
                agent_prompt = f.read()
        except FileNotFoundError:
            raise HTTPException(status_code=400, detail="Invalid diagram type")

        # 2. Construct the conversation
        conversation_history = [
            {"role": "system", "content": agent_prompt},
            {"role": "user", "content": request.prompt},
        ]

        # 3. Get AI response
        ai_processor = create_ai_processor(settings.api_key, "openrouter")
        full_response = ai_processor.process_question(
            question=request.prompt,
            conversation_history=conversation_history,
            codebase_content="",
            model=settings.default_model,
        )

        # 4. Extract and validate the diagram
        code_blocks = extract_code_blocks_from_content(
            full_response, "diagram_generation"
        )
        if not code_blocks:
            error_message = "No code blocks found in the AI response."
            logger.error(error_message)
            return {
                "image_data": "",
                "image_format": request.output_format,
                "initial_prompt": request.prompt,
                "full_response": full_response,
                "diagram_code": "",
                "error_info": {
                    "has_error": True,
                    "error_message": error_message,
                },
            }

        diagram_code = code_blocks[0]["code"]

        is_valid = False
        if request.diagram_type == "d2":
            # Use CLI validation if available (most reliable)
            if is_d2_cli_available():
                is_valid, corrected_code, message = validate_and_fix_d2_with_cli(
                    diagram_code, max_attempts=8
                )
                diagram_code = corrected_code
            else:
                # Fallback to pattern-based validation
                fix_result = fix_d2_syntax(diagram_code)
                is_valid = fix_result.is_valid
                diagram_code = fix_result.corrected_code
        elif request.diagram_type == "mermaid":
            is_valid = is_valid_mermaid_diagram(diagram_code)
        elif request.diagram_type == "c4":
            is_valid = is_valid_c4_diagram(diagram_code)
            if is_valid:
                diagram_code = convert_c4_to_d2(diagram_code)
                # After conversion, the diagram type is d2
                request.diagram_type = "d2"
                # Apply D2 syntax fixing to the converted code
                if is_d2_cli_available():
                    is_valid, corrected_code, message = validate_and_fix_d2_with_cli(
                        diagram_code, max_attempts=8
                    )
                    diagram_code = corrected_code
                else:
                    fix_result = fix_d2_syntax(diagram_code)
                    is_valid = fix_result.is_valid
                    diagram_code = fix_result.corrected_code

        if not is_valid:
            error_message = (
                "Could not generate a valid diagram from the AI response."
            )
            logger.error(error_message)
            return {
                "image_data": "",
                "image_format": request.output_format,
                "initial_prompt": request.prompt,
                "full_response": full_response,
                "diagram_code": diagram_code,
                "error_info": {
                    "has_error": True,
                    "error_message": error_message,
                },
            }

        # 5. Generate the diagram image
        image_data = await render_diagram(
            diagram_code, request.diagram_type, request.output_format
        )

        # 6. Return the response
        return {
            "image_data": image_data,
            "image_format": request.output_format,
            "initial_prompt": request.prompt,
            "full_response": full_response,
            "diagram_code": diagram_code,
            "error_info": {
                "has_error": False,
                "error_message": "",
            },
        }

    except Exception as e:
        logger.error(f"Error generating diagram: {e}")
        return {
            "image_data": "",
            "image_format": request.output_format,
            "initial_prompt": request.prompt,
            "full_response": "",
            "diagram_code": "",
            "error_info": {
                "has_error": True,
                "error_message": str(e),
            },
        }
