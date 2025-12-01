import os
import re
from typing import Optional
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel

from app.core.config import Settings, get_settings
from common.logger import get_logger

# Import diagram validation functions for different diagram types
from .diagram_validators import (
    is_valid_mermaid_diagram,
    is_valid_c4_diagram,
)
from .d2_syntax_fixer import fix_d2_syntax
from .d2_cli_validator import validate_and_fix_d2_with_cli, is_d2_cli_available

# Import rendering and conversion modules for diagram generation
from .renderer_v2 import render_diagram  # Use new renderer with frontend HTML

# Import provider system for C4 rendering
from diagrams.provider_registry import get_registry

# Import utility functions for AI and code extraction
from app.utils.code_extraction import extract_code_blocks_from_content
from common.ai import create_ai_processor

# Initialize module logger for tracking events and errors
logger = get_logger(__name__)

# Create FastAPI router for handling diagram-related API endpoints
router = APIRouter()

# Helper function to detect C4 diagram level based on user's prompt


def detect_c4_level(prompt: str) -> Optional[str]:
    """
    Helper function to detect C4 diagram level based on user's prompt.

    Args:
        prompt (str): The user's prompt describing the system.

    Returns:
        Optional[str]: The detected C4 level ('C1', 'C2', 'C3', 'C4') or None if not detected.
    """
    # Normalize prompt to uppercase for consistent pattern matching
    prompt_upper = prompt.upper()

    # Define patterns to match different C4 diagram levels
    patterns = [
        (r"\bC1\b|SYSTEM\s+CONTEXT", "C1"),
        (r"\bC2\b|CONTAINER(?:\s+DIAGRAM)?", "C2"),
        (r"\bC3\b|COMPONENT(?:\s+DIAGRAM)?", "C3"),
        (r"\bC4\b|CODE\s+LEVEL", "C4"),
    ]

    # Iterate through patterns to find matching C4 level
    for pattern, level in patterns:
        if re.search(pattern, prompt_upper):
            logger.debug(f"Detected C4 level '{level}' from prompt")
            return level

    return None


# Pydantic models for request and response validation


class DiagramRequest(BaseModel):
    """
    Request model for diagram generation.

    Attributes:
        prompt (str): Natural language description of diagram
        diagram_type (str): Type of diagram to generate. Defaults to "d2".
        c4_level (Optional[str]): C4 level: "C1", "C2", "C3", "C4" (auto-detected if not provided)
        output_format (str): Output format (svg, png). Defaults to "svg".
    """

    prompt: str  # Natural language description of diagram
    diagram_type: str = "d2"  # Type of diagram to generate
    c4_level: Optional[str] = None  # C4 level: "C1", "C2", "C3", "C4" (auto-detected if not provided)
    output_format: str = "svg"  # Output format (svg, png)


class ErrorInfo(BaseModel):
    """
    Error information model for response.

    Attributes:
        has_error (bool): Whether an error occurred
        error_message (str): Error message description
    """

    has_error: bool  # Whether an error occurred
    error_message: str  # Error message description


class DiagramResponse(BaseModel):
    """
    Complete response model for diagram generation.

    Attributes:
        image_data (str): Base64-encoded image data
        image_format (str): Format of the generated image
        initial_prompt (str): Original user prompt
        full_response (str): Complete AI response (includes thinking)
        diagram_code (str): Generated diagram source code
        error_info (ErrorInfo): Error information if any
    """

    image_data: str  # Base64-encoded image data
    image_format: str  # Format of the generated image
    initial_prompt: str  # Original user prompt
    full_response: str  # Complete AI response (includes thinking)
    diagram_code: str  # Generated diagram source code
    error_info: ErrorInfo  # Error information if any


@router.post("/generate", response_model=DiagramResponse)
async def generate_diagram(request: DiagramRequest, settings: Settings = Depends(get_settings)):
    """
    Generate a diagram from a prompt using AI and available renderers.

    This endpoint handles the complete workflow:
    1. Selecting the appropriate AI prompt based on diagram type.
    2. Calling the AI model to generate diagram code.
    3. Validating and fixing the generated code.
    4. Rendering the diagram to the requested format.

    Args:
        request (DiagramRequest): The diagram generation request details.
        settings (Settings): Application settings injected by dependency.

    Returns:
        DiagramResponse: The generated diagram, code, and metadata.

    Raises:
        HTTPException: If the diagram type or C4 level is invalid.
    """
    logger.info(f"Received diagram generation request: {request}")

    try:
        # 1. Dynamically load the appropriate AI agent prompt based on diagram type
        try:
            from common.env_manager import env_manager

            # Determine prompts directory, using environment settings or default path
            env_vars = env_manager.load_env_file()
            prompts_dir = env_vars.get("PROMPTS_DIR", "").strip()
            if not prompts_dir:
                # Default: use relative path if no environment setting
                script_dir = os.path.dirname(os.path.abspath(__file__))
                prompts_dir = os.path.join(script_dir, "..", "..", "prompts")
            else:
                # Use configured path, ensuring it points to prompts directory
                if not os.path.isabs(prompts_dir):
                    prompts_dir = os.path.abspath(prompts_dir)
                if not prompts_dir.endswith("prompts"):
                    prompts_dir = os.path.join(prompts_dir, "prompts")

            # Determine appropriate prompt file for diagram type
            diagram_type_for_prompt = request.diagram_type

            # Special handling for C4 diagrams to select level-specific prompt
            if request.diagram_type == "c4":
                c4_level = request.c4_level or detect_c4_level(request.prompt)

                if c4_level:
                    # Use level-specific prompt file
                    diagram_type_for_prompt = c4_level.lower()
                    logger.info(f"Using C4 level-specific prompt: {diagram_type_for_prompt}-architecture.md")
                else:
                    # Fallback to generic C4 prompt
                    logger.info("No C4 level detected; using generic c4-architecture.md")

            # Construct path to appropriate prompt file
            prompt_file_path = os.path.join(
                prompts_dir, "coding", "agent", f"{diagram_type_for_prompt}-architecture.md"
            )

            with open(prompt_file_path, "r") as f:
                agent_prompt = f.read()
        except FileNotFoundError:
            raise HTTPException(status_code=400, detail="Invalid diagram type or C4 level")

        # 2. Prepare conversation history for AI processing
        conversation_history = [
            {"role": "system", "content": agent_prompt},
            {"role": "user", "content": request.prompt},
        ]

        # 3. Use AI processor to generate diagram code from prompt
        ai_processor = create_ai_processor(settings.api_key, "openrouter")
        full_response = ai_processor.process_question(
            question=request.prompt,
            conversation_history=conversation_history,
            codebase_content="",
            model=settings.default_model,
            max_tokens=16000,
            temperature=0.1,
        )

        # 4. Extract and validate the generated diagram code
        code_blocks = extract_code_blocks_from_content(full_response, "diagram_generation")
        if not code_blocks:
            # Handle case where no code blocks are found
            error_message = "No code blocks found in the AI response."
            logger.info(error_message)
            return {
                # Return error response with detailed information
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

        # Extract first code block for diagram generation
        diagram_code = code_blocks[0]["code"]

        # 5. Validate diagram code based on diagram type
        is_valid = False
        if request.diagram_type == "d2":
            # Prefer CLI validation for D2 diagrams if available
            if is_d2_cli_available():
                is_valid, corrected_code, message = validate_and_fix_d2_with_cli(diagram_code, max_attempts=8)
                diagram_code = corrected_code
            else:
                # Fallback to pattern-based validation
                fix_result = fix_d2_syntax(diagram_code)
                is_valid = fix_result.is_valid
                diagram_code = fix_result.corrected_code
        elif request.diagram_type == "mermaid":
            is_valid = is_valid_mermaid_diagram(diagram_code)
        elif request.diagram_type == "c4":
            # Validate C4 diagram syntax for direct rendering
            is_valid = is_valid_c4_diagram(diagram_code)
            if is_valid:
                logger.info("C4 diagram validated; will render via Kroki C4 provider")

        # Handle invalid diagram code
        if not is_valid:
            error_message = "Could not generate a valid diagram from the AI response."
            logger.info(error_message)
            return {
                # Return error response with generated (but invalid) code
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

        # 6. Render the diagram using appropriate method
        if request.diagram_type == "c4":
            # Use provider system for C4 rendering with fallback
            try:
                registry = get_registry()
                provider = registry.get_default_provider("c4")
                if provider and provider.is_available():
                    logger.info(f"Using provider '{provider.provider_id}' for C4 rendering")
                    render_result = provider.render(diagram_code, request.output_format)
                    if render_result.success and render_result.content:
                        image_data = render_result.content
                    else:
                        # Fallback to MVP renderer if provider fails
                        logger.info("Provider rendering failed, falling back to MVP renderer")
                        image_data = await render_diagram(diagram_code, request.diagram_type, request.output_format)
                else:
                    # Fallback if no provider is available
                    logger.info("C4 provider not available, falling back to MVP renderer")
                    image_data = await render_diagram(diagram_code, request.diagram_type, request.output_format)
            except Exception as e:
                # Handle any rendering exceptions
                logger.info(f"Provider rendering failed: {e}, falling back to MVP renderer")
                image_data = await render_diagram(diagram_code, request.diagram_type, request.output_format)
        else:
            # Use standard renderer for non-C4 diagram types
            image_data = await render_diagram(diagram_code, request.diagram_type, request.output_format)

        # 7. Return successful diagram generation response
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
        # Handle and log any unexpected errors during diagram generation
        logger.info(f"Error generating diagram: {e}")
        return {
            # Return generic error response
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
