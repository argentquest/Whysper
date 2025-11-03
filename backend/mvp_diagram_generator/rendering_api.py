
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

import os
import re
from typing import Optional
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

# Import provider system for C4 rendering
from diagrams.provider_registry import get_registry

# Import utility functions for AI integration
from app.utils.code_extraction import extract_code_blocks_from_content
from common.ai import create_ai_processor

# Initialize module logger
logger = get_logger(__name__)

# Create FastAPI router for diagram endpoints
router = APIRouter()

# Helper function to detect C4 level from prompt
def detect_c4_level(prompt: str) -> Optional[str]:
    """
    Detect C4 level (C1, C2, C3, C4) from user prompt.

    Returns:
        str: "C1", "C2", "C3", "C4", or None if not detected
    """
    # Normalize prompt to uppercase for matching
    prompt_upper = prompt.upper()

    # Look for explicit C4 level indicators
    patterns = [
        (r'\bC1\b|SYSTEM\s+CONTEXT', 'C1'),
        (r'\bC2\b|CONTAINER(?:\s+DIAGRAM)?', 'C2'),
        (r'\bC3\b|COMPONENT(?:\s+DIAGRAM)?', 'C3'),
        (r'\bC4\b|CODE\s+LEVEL', 'C4'),
    ]

    for pattern, level in patterns:
        if re.search(pattern, prompt_upper):
            logger.debug(f"Detected C4 level '{level}' from prompt")
            return level

    return None


# Pydantic models for request/response validation
class DiagramRequest(BaseModel):
    """Request model for diagram generation."""
    prompt: str                           # Natural language description of diagram
    diagram_type: str = "d2"              # Type of diagram to generate
    c4_level: Optional[str] = None        # C4 level: "C1", "C2", "C3", "C4" (auto-detected if not provided)
    output_format: str = "svg"            # Output format (svg, png)


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

            # Determine which prompt file to load
            diagram_type_for_prompt = request.diagram_type

            # For C4 diagrams, check if user specified or we can detect a C4 level
            if request.diagram_type == "c4":
                # Use explicitly provided c4_level if available, otherwise detect from prompt
                c4_level = request.c4_level or detect_c4_level(request.prompt)

                if c4_level:
                    # Use level-specific prompt (c1-architecture.md, c2-architecture.md, etc.)
                    diagram_type_for_prompt = c4_level.lower()
                    logger.info(f"Using C4 level-specific prompt: {diagram_type_for_prompt}-architecture.md")
                else:
                    # Fallback to generic c4-architecture.md if no level detected
                    logger.info("No C4 level detected; using generic c4-architecture.md")

            prompt_file_path = os.path.join(prompts_dir, "coding", "agent", f"{diagram_type_for_prompt}-architecture.md")

            with open(prompt_file_path, "r") as f:
                agent_prompt = f.read()
        except FileNotFoundError:
            raise HTTPException(status_code=400, detail="Invalid diagram type or C4 level")

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
            max_tokens=16000,
            temperature=0.1,
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
            # For C4 diagrams, validate the PlantUML/C4 syntax
            # and render it directly through Kroki C4 provider (not converted to D2)
            is_valid = is_valid_c4_diagram(diagram_code)
            if is_valid:
                # Keep request.diagram_type as "c4" to use Kroki C4 provider directly
                # Skip the C4->D2 conversion - it was causing validation failures
                logger.info("C4 diagram validated; will render via Kroki C4 provider")

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
        # For C4 diagrams, use the provider system (Kroki C4) instead of MVP renderer
        if request.diagram_type == "c4":
            try:
                registry = get_registry()
                provider = registry.get_default_provider("c4")
                if provider and provider.is_available():
                    logger.info(
                        f"Using provider '{provider.provider_id}' for C4 rendering"
                    )
                    render_result = provider.render(
                        diagram_code, request.output_format
                    )
                    if render_result.success and render_result.content:
                        image_data = render_result.content
                    else:
                        error_msg = render_result.error or "Unknown error"
                        logger.warning(
                            f"Provider rendering failed: {error_msg}, "
                            "falling back to MVP renderer"
                        )
                        image_data = await render_diagram(
                            diagram_code, request.diagram_type, request.output_format
                        )
                else:
                    logger.warning(
                        "C4 provider not available, falling back to MVP renderer"
                    )
                    image_data = await render_diagram(
                        diagram_code, request.diagram_type, request.output_format
                    )
            except Exception as e:
                logger.warning(
                    f"Provider rendering failed: {e}, "
                    "falling back to MVP renderer"
                )
                image_data = await render_diagram(
                    diagram_code, request.diagram_type, request.output_format
                )
        else:
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
