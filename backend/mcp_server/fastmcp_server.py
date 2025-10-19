"""
FastMCP Server Integration for Whysper Web2 Backend - FIXED VERSION

This module provides FastMCP integration with actual AI integration for diagram generation.
It replaces the placeholder implementation with real AI-powered diagram generation.
"""

import json
import sys
import os
from typing import Any, Dict, List
from datetime import datetime

from fastapi import APIRouter, HTTPException, WebSocket, WebSocketDisconnect
from pydantic import BaseModel

# FastMCP imports
try:
    from fastmcp import FastMCP
except ImportError:
    print("Error: FastMCP not installed. Install with: pip install fastmcp", 
          file=sys.stderr)
    sys.exit(1)

# Add parent directory to path for imports
sys.path.insert(0, "..")

from mvp_diagram_generator.renderer_v2 import render_diagram as renderer_v2_render
from common.logger import get_logger
from security_utils import SecurityUtils
from .mcp_history_service import mcp_history_service

logger = get_logger(__name__)

# Create FastMCP instance
mcp_server = FastMCP("diagram-generator")


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


# FastAPI router for MCP endpoints
mcp_router = APIRouter(prefix="/mcp", tags=["MCP"])


# FIXED: Implementation function with actual AI integration
async def generate_diagram_impl(prompt: str, diagram_type: str) -> str:
    """Implementation function for generate_diagram with AI integration."""
    try:
        logger.info(f"Generating {diagram_type} diagram from prompt")
        
        # Use secure debug logging for sensitive information
        debug_info = {
            'diagram_type': diagram_type,
            'prompt_length': len(prompt),
            'using_ai': True
        }
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
            config_debug = SecurityUtils.safe_debug_info({
                'api_key_present': bool(settings.api_key),
                'api_key_length': len(settings.api_key) if settings.api_key else 0,
                'provider': 'openrouter',
                'model': settings.default_model,
                'api_url': getattr(settings, 'openrouter_api_url', 'not_set')
            })
            logger.info(f"DEBUG: Configuration loaded: {config_debug}")
            
            # Construct path relative to this script's location
            script_dir = os.path.dirname(os.path.abspath(__file__))
            prompt_file_path = os.path.join(script_dir, f"..\prompts\coding\agent\{diagram_type}-architecture.md")
            prompt_file_exists = os.path.exists(prompt_file_path)
            logger.info(f"DEBUG: Prompt file check - exists: {prompt_file_exists}, path: {prompt_file_path}")
            
            if not prompt_file_exists:
                # DEBUG: Try alternative paths
                alt_paths = [
                    f"prompts/coding/agent/{diagram_type}-architecture.md",
                    f"../prompts/coding/agent/{diagram_type}-architecture.md",
                    f"prompts/{diagram_type}-architecture.md"
                ]
                for alt_path in alt_paths:
                    logger.info(f"DEBUG: Checking alternative path: {alt_path}")
                    if os.path.exists(alt_path):
                        prompt_file_path = alt_path
                        prompt_file_exists = True
                        logger.info(f"DEBUG: Found prompt file at alternative path: {alt_path}")
                        break
                
                if not prompt_file_exists:
                    logger.error(f"DEBUG: Prompt file not found at any path, checked: {[prompt_file_path] + alt_paths}")
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
            processor_debug = SecurityUtils.safe_debug_info({
                'processor_type': type(ai_processor).__name__,
                'provider': ai_processor.provider,
                'api_key_set': ai_processor.validate_api_key(),
                'available_providers': ai_processor.get_available_providers()
            })
            logger.info(f"DEBUG: AI processor details: {processor_debug}")
            
            logger.info(f"DEBUG: Making AI call with model: {settings.default_model}")
            full_response = ai_processor.process_question(
                question=prompt,
                conversation_history=conversation_history,
                codebase_content="",
                model=settings.default_model,
            )
            
            logger.info(f"DEBUG: AI response received, length: {len(full_response)}")
            logger.info(f"DEBUG: AI response preview: {full_response[:200]}...")
            
            # Extract and validate the diagram
            code_blocks = extract_code_blocks_from_content(
                full_response, "diagram_generation"
            )
            
            if not code_blocks:
                logger.error("No code blocks found in AI response")
                raise ValueError("No code blocks found in the AI response")
            
            diagram_code = code_blocks[0]["code"]
            logger.info(f"Diagram code extracted, length: {len(diagram_code)}")
            
            result = {
                "diagram_code": diagram_code,
                "diagram_type": diagram_type,
                "prompt": prompt,
                "ai_generated": True,
                "full_response": full_response
            }
            
            logger.info(f"Successfully generated {diagram_type} diagram using AI")
            return json.dumps(result, indent=2)
            
        except Exception as ai_error:
            logger.error(f"AI generation failed, falling back to placeholder: {str(ai_error)}")
            logger.debug(f"AI error details: {SecurityUtils.safe_debug_info({'error': str(ai_error), 'type': type(ai_error).__name__})}")
            
            # Fallback to placeholder implementation
            if diagram_type == "mermaid":
                diagram_code = f"""flowchart TD
    A[Start] --> B[{prompt}]
    B --> C[End]"""
            elif diagram_type == "d2":
                diagram_code = f"""# {prompt}
A -> B -> C"""
            elif diagram_type == "c4":
                diagram_code = f"""# {prompt}
System_1 -> System_2"""
            else:
                raise ValueError(f"Unsupported diagram type: {diagram_type}")
            
            result = {
                "diagram_code": diagram_code,
                "diagram_type": diagram_type,
                "prompt": prompt,
                "ai_generated": False,
                "fallback_reason": str(ai_error)
            }
            
            logger.warning(f"Used fallback placeholder for {diagram_type} diagram")
            return json.dumps(result, indent=2)
        
    except Exception as e:
        logger.error(f"Error generating diagram: {str(e)}")
        error_result = {
            "error": str(e),
            "diagram_type": diagram_type,
            "prompt": prompt,
            "ai_generated": False
        }
        return json.dumps(error_result, indent=2)


async def render_diagram_impl(code: str, diagram_type: str, output_format: str = "svg") -> str:
    """Implementation function for render_diagram."""
    try:
        logger.info(f"Rendering {diagram_type} diagram to {output_format}")
        
        # Use secure debug logging
        debug_info = {
            'diagram_type': diagram_type,
            'output_format': output_format,
            'code_length': len(code)
        }
        logger.debug(f"Diagram render request: {SecurityUtils.safe_debug_info(debug_info)}")
        
        # Render the diagram using the existing renderer
        image_data = await renderer_v2_render(
            diagram_code=code,
            diagram_type=diagram_type,
            output_format=output_format
        )
        
        result = {
            "image_data": image_data,
            "output_format": output_format,
            "diagram_type": diagram_type
        }
        
        logger.info(f"Successfully rendered {diagram_type} diagram to {output_format}")
        return json.dumps(result, indent=2)
        
    except Exception as e:
        logger.error(f"Error rendering diagram: {str(e)}")
        error_result = {
            "error": str(e),
            "diagram_type": diagram_type,
            "output_format": output_format
        }
        return json.dumps(error_result, indent=2)


async def generate_and_render_impl(prompt: str, diagram_type: str,
                                 output_format: str = "svg") -> str:
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
        render_result = await render_diagram_impl(
            diagram_code, diagram_type, output_format
        )
        render_data = json.loads(render_result)
        
        if "error" in render_data:
            raise Exception(f"Diagram rendering failed: {render_data['error']}")
        
        result = {
            "diagram_code": diagram_code,
            "image_data": render_data["image_data"],
            "output_format": output_format,
            "diagram_type": diagram_type,
            "prompt": prompt,
            "ai_generated": gen_data.get("ai_generated", False)
        }
        
        logger.info(f"Successfully generated and rendered {diagram_type} diagram")
        return json.dumps(result, indent=2)
        
    except Exception as e:
        logger.error(f"Error in generate_and_render: {str(e)}")
        error_result = {
            "error": str(e),
            "diagram_type": diagram_type,
            "output_format": output_format,
            "prompt": prompt
        }
        return json.dumps(error_result, indent=2)


# FastMCP tool definitions - FIXED with AI integration
@mcp_server.tool()
async def generate_diagram(prompt: str, diagram_type: str) -> str:
    """Generate diagram code from a natural language prompt using AI.
    
    Supports three diagram types:
    - mermaid: Flowcharts, sequence diagrams, class diagrams, etc.
    - d2: Modern diagramming language with clean syntax
    - c4: C4 architecture diagrams (Context, Container, Component)
    
    Args:
        prompt: Natural language description of the diagram to generate
        diagram_type: Type of diagram to generate (mermaid, d2, c4)
        
    Returns:
        Generated diagram code as JSON string
    """
    return await generate_diagram_impl(prompt, diagram_type)


@mcp_server.tool()
async def render_diagram(code: str, diagram_type: str, output_format: str = "svg") -> str:
    """Render diagram code to SVG or PNG format.
    
    Takes diagram code (Mermaid, D2, or C4) and renders it to an image format.
    Uses a headless browser via Playwright for accurate rendering.
    
    Args:
        code: The diagram source code to render
        diagram_type: Type of diagram (mermaid, d2, c4)
        output_format: Output format (svg, png)
        
    Returns:
        Base64-encoded image data as JSON string
    """
    return await render_diagram_impl(code, diagram_type, output_format)


@mcp_server.tool()
async def generate_and_render(prompt: str, diagram_type: str, 
                            output_format: str = "svg") -> str:
    """Generate and render a diagram in one step.
    
    Combines generate_diagram and render_diagram into a single operation.
    Takes a natural language prompt and returns a rendered diagram.
    
    Args:
        prompt: Natural language description of the diagram
        diagram_type: Type of diagram to generate (mermaid, d2, c4)
        output_format: Output format (svg, png)
        
    Returns:
        JSON string containing both diagram code and rendered image
    """
    return await generate_and_render_impl(prompt, diagram_type, output_format)


# FastAPI endpoint wrappers for MCP tools
@mcp_router.post("/tools/generate_diagram", response_model=ToolResponse)
async def api_generate_diagram(request: GenerateDiagramRequest):
    """FastAPI endpoint for generate_diagram tool."""
    try:
        result = await generate_diagram_impl(request.prompt, request.diagram_type)
        return ToolResponse(content=[{"type": "text", "text": result}])
    except Exception as e:
        logger.error(f"API error in generate_diagram: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@mcp_router.post("/tools/render_diagram", response_model=ToolResponse)
async def api_render_diagram(request: RenderDiagramRequest):
    """FastAPI endpoint for render_diagram tool."""
    try:
        result = await render_diagram_impl(
            request.code, request.diagram_type, request.output_format
        )
        return ToolResponse(content=[{"type": "text", "text": result}])
    except Exception as e:
        logger.error(f"API error in render_diagram: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@mcp_router.post("/tools/generate_and_render", response_model=ToolResponse)
async def api_generate_and_render(request: GenerateAndRenderRequest):
    """FastAPI endpoint for generate_and_render tool."""
    try:
        result = await generate_and_render_impl(
            request.prompt, request.diagram_type, request.output_format
        )
        return ToolResponse(content=[{"type": "text", "text": result}])
    except Exception as e:
        logger.error(f"API error in generate_and_render: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@mcp_router.get("/tools")
async def list_tools():
    """List available MCP tools."""
    tools = [
        {
            "name": "generate_diagram",
            "description": "Generate diagram code from a natural language prompt using AI.",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "prompt": {
                        "type": "string", 
                        "description": "Natural language description of the diagram"
                    },
                    "diagram_type": {
                        "type": "string", 
                        "enum": ["mermaid", "d2", "c4"],
                        "description": "Type of diagram to generate"
                    }
                },
                "required": ["prompt", "diagram_type"]
            }
        },
        {
            "name": "render_diagram",
            "description": "Render diagram code to SVG or PNG format.",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "code": {
                        "type": "string", 
                        "description": "The diagram source code to render"
                    },
                    "diagram_type": {
                        "type": "string", 
                        "enum": ["mermaid", "d2", "c4"],
                        "description": "Type of diagram"
                    },
                    "output_format": {
                        "type": "string", 
                        "enum": ["svg", "png"], 
                        "description": "Output format", 
                        "default": "svg"
                    }
                },
                "required": ["code", "diagram_type"]
            }
        },
        {
            "name": "generate_and_render",
            "description": "Generate and render a diagram in one step.",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "prompt": {
                        "type": "string", 
                        "description": "Natural language description of the diagram"
                    },
                    "diagram_type": {
                        "type": "string", 
                        "enum": ["mermaid", "d2", "c4"],
                        "description": "Type of diagram to generate"
                    },
                    "output_format": {
                        "type": "string", 
                        "enum": ["svg", "png"], 
                        "description": "Output format", 
                        "default": "svg"
                    }
                },
                "required": ["prompt", "diagram_type"]
            }
        }
    ]
    return {"tools": tools}


@mcp_router.post("/call_tool")
async def call_tool(request: ToolRequest):
    """Generic MCP tool call endpoint."""
    try:
        if request.name == "generate_diagram":
            result = await generate_diagram_impl(
                request.arguments.get("prompt"),
                request.arguments.get("diagram_type")
            )
        elif request.name == "render_diagram":
            result = await render_diagram_impl(
                request.arguments.get("code"),
                request.arguments.get("diagram_type"),
                request.arguments.get("output_format", "svg")
            )
        elif request.name == "generate_and_render":
            result = await generate_and_render_impl(
                request.arguments.get("prompt"),
                request.arguments.get("diagram_type"),
                request.arguments.get("output_format", "svg")
            )
        else:
            raise ValueError(f"Unknown tool: {request.name}")
        
        return ToolResponse(content=[{"type": "text", "text": result}])
        
    except Exception as e:
        logger.error(f"Error calling tool {request.name}: {str(e)}")
        return ToolResponse(
            content=[{
                "type": "text", 
                "text": json.dumps({"error": str(e), "tool": request.name})
            }],
            isError=True
        )


# WebSocket endpoint for real-time MCP communication
@mcp_router.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """WebSocket endpoint for MCP protocol communication."""
    await websocket.accept()
    logger.info("MCP WebSocket connection established")
    
    try:
        while True:
            # Receive message from client
            data = await websocket.receive_text()
            message = json.loads(data)
            
            logger.debug(f"Received WebSocket message: "
                        f"{SecurityUtils.safe_debug_info(message)}")
            
            # Handle different MCP message types
            if message.get("method") == "tools/list":
                response = {
                    "jsonrpc": "2.0",
                    "id": message.get("id"),
                    "result": await list_tools()
                }
            elif message.get("method") == "tools/call":
                params = message.get("params", {})
                tool_request = ToolRequest(
                    name=params.get("name"), 
                    arguments=params.get("arguments", {})
                )
                result = await call_tool(tool_request)
                response = {
                    "jsonrpc": "2.0",
                    "id": message.get("id"),
                    "result": result.dict()
                }
            else:
                response = {
                    "jsonrpc": "2.0",
                    "id": message.get("id"),
                    "error": {"code": -32601, "message": "Method not found"}
                }
            
            await websocket.send_text(json.dumps(response))
            
    except WebSocketDisconnect:
        logger.info("MCP WebSocket connection closed")
    except Exception as e:
        logger.error(f"WebSocket error: {str(e)}")
        await websocket.close()


def get_mcp_router() -> APIRouter:
    """Get the MCP router for mounting in FastAPI app."""
    return mcp_router


def get_mcp_server() -> FastMCP:
    """Get the FastMCP server instance."""
    return mcp_server