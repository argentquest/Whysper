"""
Diagram API Router for Whysper Web2 Backend

This module provides direct FastAPI endpoints for diagram generation and rendering.
No longer uses FastMCP - all functionality is directly integrated into FastAPI.
"""

from security_utils import SecurityUtils
from common.logger import get_logger
from mvp_diagram_generator.renderer_v2 import render_diagram as renderer_v2_render
import json
import sys
import os
from typing import Any, Dict, List

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

# Add parent directory to path for imports
sys.path.insert(0, "..")


logger = get_logger(__name__)


class ToolRequest(BaseModel):
    name: str
    arguments: Dict[str, Any]


class ToolResponse(BaseModel):
    content: List[Dict[str, Any]]
    isError: bool = False


class GenerateDiagramRequest(BaseModel):
    prompt: str
    diagram_type: str


class RenderDiagramRequest(BaseModel):
    code: str
    diagram_type: str
    output_format: str = "svg"


class GenerateAndRenderRequest(BaseModel):
    prompt: str
    diagram_type: str
    output_format: str = "svg"


# FastAPI router for diagram endpoints
diagram_router = APIRouter(prefix="/api/v1/diagrams", tags=["Diagrams"])


# FIXED: Implementation function with actual AI integration
async def generate_diagram_impl(prompt: str, diagram_type: str) -> str:
    """Implementation function for generate_diagram with AI integration."""
    try:
        logger.info(f"Generating {diagram_type} diagram from prompt")

        # Use secure debug logging for sensitive information
        debug_info = {"diagram_type": diagram_type, "prompt_length": len(prompt), "using_ai": True}
        logger.debug(f"Diagram generation request: {SecurityUtils.safe_debug_info(debug_info)}")

        # ACTUAL AI INTEGRATION
        try:
            # DEBUG: Log import attempts
            logger.info("DEBUG: Attempting to import app.core.config")
            from app.core.config import get_settings

            logger.info("DEBUG: Attempting to import common.ai")
            from common.ai import create_ai_processor

            logger.info("DEBUG: Attempting to import app.utils.code_extraction")
            from app.utils.code_extraction import extract_code_blocks_from_content

            logger.info("DEBUG: All imports successful, getting settings")
            settings = get_settings()

            # DEBUG: Log configuration details with masked sensitive data
            config_debug = SecurityUtils.safe_debug_info(
                {
                    "api_key_present": bool(settings.api_key),
                    "api_key_length": len(settings.api_key) if settings.api_key else 0,
                    "provider": "openrouter",
                    "model": settings.default_model,
                    "api_url": getattr(settings, "openrouter_api_url", "not_set"),
                }
            )
            logger.info(f"DEBUG: Configuration loaded: {config_debug}")

            # Get prompts directory from environment
            from common.env_manager import env_manager

            env_vars = env_manager.load_env_file()
            prompts_dir = env_vars.get("PROMPTS_DIR", "").strip()
            if not prompts_dir:
                # Default: prompts directory relative to project root
                script_dir = os.path.dirname(os.path.abspath(__file__))
                prompts_dir = os.path.join(script_dir, "..", "..", "prompts")
            else:
                # Use configured path (can be absolute or relative)
                if not os.path.isabs(prompts_dir):
                    prompts_dir = os.path.abspath(prompts_dir)
                # Append prompts if not already in path
                if not prompts_dir.endswith("prompts"):
                    prompts_dir = os.path.join(prompts_dir, "prompts")

            prompt_file_path = os.path.join(prompts_dir, "coding", "agent", f"{diagram_type}-architecture.md")
            prompt_file_exists = os.path.exists(prompt_file_path)
            logger.info(f"DEBUG: Prompt file check - exists: {prompt_file_exists}, path: {prompt_file_path}")

            if not prompt_file_exists:
                logger.info(f"DEBUG: Prompt file not found at: {prompt_file_path}")
                raise FileNotFoundError(f"Prompt file not found: {prompt_file_path}")

            # Load the appropriate agent prompt
            logger.info(f"DEBUG: Loading prompt file: {prompt_file_path}")
            with open(prompt_file_path, "r") as f:
                agent_prompt = f.read()
            logger.info(f"DEBUG: Prompt loaded, length: {len(agent_prompt)}")

            # Construct the conversation
            conversation_history = [
                {"role": "system", "content": agent_prompt},
                {"role": "user", "content": prompt},
            ]
            logger.info(f"DEBUG: Conversation history constructed with {len(conversation_history)} messages")

            # Get AI response
            logger.info("DEBUG: Creating AI processor...")
            ai_processor = create_ai_processor(settings.api_key, "openrouter")
            logger.info("DEBUG: AI processor created successfully")

            # DEBUG: Log AI processor details
            processor_debug = SecurityUtils.safe_debug_info(
                {
                    "processor_type": type(ai_processor).__name__,
                    "provider": ai_processor.provider,
                    "api_key_set": ai_processor.validate_api_key(),
                    "available_providers": ai_processor.get_available_providers(),
                }
            )
            logger.info(f"DEBUG: AI processor details: {processor_debug}")

            logger.info(f"DEBUG: Making AI call with model: {settings.default_model}")
            full_response = ai_processor.process_question(
                question=prompt,
                conversation_history=conversation_history,
                codebase_content="",
                model=settings.default_model,
                max_tokens=settings.max_tokens,
                temperature=settings.temperature,
            )

            logger.info(f"DEBUG: AI response received, length: {len(full_response)}")
            logger.info(f"DEBUG: AI response preview: {full_response[:200]}...")

            # Extract and validate the diagram
            code_blocks = extract_code_blocks_from_content(full_response, "diagram_generation")

            if not code_blocks:
                logger.info("No code blocks found in AI response")
                raise ValueError("No code blocks found in the AI response")

            diagram_code = code_blocks[0]["code"]
            logger.info(f"Diagram code extracted, length: {len(diagram_code)}")

            result = {
                "diagram_code": diagram_code,
                "diagram_type": diagram_type,
                "prompt": prompt,
                "ai_generated": True,
                "full_response": full_response,
            }

            logger.info(f"Successfully generated {diagram_type} diagram using AI")
            return json.dumps(result, indent=2)

        except Exception as ai_error:
            logger.info(f"AI generation failed, falling back to placeholder: {str(ai_error)}")
            logger.debug(
                f"AI error details: {
                    SecurityUtils.safe_debug_info(
                        {
                            'error': str(ai_error),
                            'type': type(ai_error).__name__})}"
            )

            # Fallback to placeholder implementation
            if diagram_type == "mermaid":
                diagram_code = """flowchart TD
    A[Start] --> B[{prompt}]
    B --> C[End]"""
            elif diagram_type == "d2":
                diagram_code = """# {prompt}
A -> B -> C"""
            elif diagram_type == "c4":
                diagram_code = """# {prompt}
System_1 -> System_2"""
            else:
                raise ValueError(f"Unsupported diagram type: {diagram_type}")

            result = {
                "diagram_code": diagram_code,
                "diagram_type": diagram_type,
                "prompt": prompt,
                "ai_generated": False,
                "fallback_reason": str(ai_error),
            }

            logger.info(f"Used fallback placeholder for {diagram_type} diagram")
            return json.dumps(result, indent=2)

    except Exception as e:
        logger.info(f"Error generating diagram: {str(e)}")
        error_result = {"error": str(e), "diagram_type": diagram_type, "prompt": prompt, "ai_generated": False}
        return json.dumps(error_result, indent=2)


async def render_diagram_impl(code: str, diagram_type: str, output_format: str = "svg") -> str:
    """Implementation function for render_diagram."""
    try:
        logger.info(f"Rendering {diagram_type} diagram to {output_format}")

        # Use secure debug logging
        debug_info = {"diagram_type": diagram_type, "output_format": output_format, "code_length": len(code)}
        logger.debug(f"Diagram render request: {SecurityUtils.safe_debug_info(debug_info)}")

        # Render the diagram using the existing renderer
        image_data = await renderer_v2_render(diagram_code=code, diagram_type=diagram_type, output_format=output_format)

        result = {"image_data": image_data, "output_format": output_format, "diagram_type": diagram_type}

        logger.info(f"Successfully rendered {diagram_type} diagram to {output_format}")
        return json.dumps(result, indent=2)

    except Exception as e:
        logger.info(f"Error rendering diagram: {str(e)}")
        error_result = {"error": str(e), "diagram_type": diagram_type, "output_format": output_format}
        return json.dumps(error_result, indent=2)


async def generate_and_render_impl(prompt: str, diagram_type: str, output_format: str = "svg") -> str:
    """Implementation function for generate_and_render."""
    try:
        logger.info(f"Generating and rendering {diagram_type} diagram")

        # Step 1: Generate diagram code
        gen_result = await generate_diagram_impl(prompt, diagram_type)
        gen_data = json.loads(gen_result)

        if "error" in gen_data:
            raise Exception(f"Diagram generation failed: {gen_data['error']}")

        diagram_code = gen_data["diagram_code"]

        # Step 2: Render the diagram
        render_result = await render_diagram_impl(diagram_code, diagram_type, output_format)
        render_data = json.loads(render_result)

        if "error" in render_data:
            raise Exception(f"Diagram rendering failed: {render_data['error']}")

        result = {
            "diagram_code": diagram_code,
            "image_data": render_data["image_data"],
            "output_format": output_format,
            "diagram_type": diagram_type,
            "prompt": prompt,
            "ai_generated": gen_data.get("ai_generated", False),
        }

        logger.info(f"Successfully generated and rendered {diagram_type} diagram")
        return json.dumps(result, indent=2)

    except Exception as e:
        logger.info(f"Error in generate_and_render: {str(e)}")
        error_result = {"error": str(e), "diagram_type": diagram_type, "output_format": output_format, "prompt": prompt}
        return json.dumps(error_result, indent=2)


# FastAPI endpoints for diagram operations
@diagram_router.post("/generate", response_model=ToolResponse)
async def api_generate_diagram(request: GenerateDiagramRequest):
    """Generate diagram code from a natural language prompt using AI."""
    try:
        result = await generate_diagram_impl(request.prompt, request.diagram_type)
        return ToolResponse(content=[{"type": "text", "text": result}])
    except Exception as e:
        logger.info(f"API error in generate_diagram: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@diagram_router.post("/render", response_model=ToolResponse)
async def api_render_diagram(request: RenderDiagramRequest):
    """Render diagram code to SVG or PNG format."""
    try:
        result = await render_diagram_impl(request.code, request.diagram_type, request.output_format)
        return ToolResponse(content=[{"type": "text", "text": result}])
    except Exception as e:
        logger.info(f"API error in render_diagram: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@diagram_router.post("/generate-and-render", response_model=ToolResponse)
async def api_generate_and_render(request: GenerateAndRenderRequest):
    """Generate and render a diagram in one step."""
    try:
        result = await generate_and_render_impl(request.prompt, request.diagram_type, request.output_format)
        return ToolResponse(content=[{"type": "text", "text": result}])
    except Exception as e:
        logger.info(f"API error in generate_and_render: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


def get_diagram_router() -> APIRouter:
    """Get the diagram router for mounting in FastAPI app."""
    return diagram_router
