"""
FastMCP Server Integration for Whysper Web2 Backend

This module provides FastMCP integration that can be mounted directly into the FastAPI application.
It replaces the stdio-based MCP server with a FastAPI-compatible implementation.

Key Features:
- FastMCP integration with FastAPI
- Same diagram generation tools as the original MCP server
- HTTP/WebSocket communication instead of stdio
- Mounted as a FastAPI router in the main application
"""

import json
import sys
from typing import Any, Dict, List

from fastapi import APIRouter, HTTPException, WebSocket, WebSocketDisconnect
from pydantic import BaseModel
import mcp
from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import Tool, TextContent

# Add parent directory to path for imports
sys.path.insert(0, "../..")

from mvp_diagram_generator.renderer_v2 import render_diagram as render_diagram_impl
from common.logger import get_logger
from security_utils import SecurityUtils

logger = get_logger(__name__)

# Create MCP server instance
mcp_server = Server("diagram-generator")


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


@mcp_server.list_tools()
async def list_tools() -> List[Tool]:
    """List available MCP tools."""
    return [
        Tool(
            name="generate_diagram",
            description="Generate diagram code from a natural language prompt.",
            inputSchema={
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
        ),
        Tool(
            name="render_diagram",
            description="Render diagram code to SVG or PNG format.",
            inputSchema={
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
        ),
        Tool(
            name="generate_and_render",
            description="Generate and render a diagram in one step.",
            inputSchema={
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
        )
    ]


@mcp_server.call_tool()
async def call_tool(name: str, arguments: Any) -> List[TextContent]:
    """Handle MCP tool calls."""
    try:
        if name == "generate_diagram":
            return await handle_generate_diagram(arguments)
        elif name == "render_diagram":
            return await handle_render_diagram(arguments)
        elif name == "generate_and_render":
            return await handle_generate_and_render(arguments)
        else:
            raise ValueError(f"Unknown tool: {name}")
    except Exception as e:
        logger.error(f"Error calling tool {name}: {str(e)}")
        return [TextContent(
            type="text",
            text=json.dumps({
                "error": str(e),
                "tool": name
            })
        )]


async def handle_generate_diagram(arguments: dict) -> List[TextContent]:
    """Generate diagram code from a prompt."""
    prompt = arguments.get("prompt")
    diagram_type = arguments.get("diagram_type")

    if not prompt or not diagram_type:
        raise ValueError("Missing required arguments: prompt, diagram_type")

    logger.info(f"Generating {diagram_type} diagram from prompt")

    # Use secure debug logging for sensitive information
    debug_info = {
        'diagram_type': diagram_type,
        'prompt_length': len(prompt)
    }
    logger.debug(f"Diagram generation request: {SecurityUtils.safe_debug_info(debug_info)}")

    # For now, return a placeholder implementation
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
        "prompt": prompt
    }

    logger.info(f"Successfully generated {diagram_type} diagram")
    return [TextContent(
        type="text",
        text=json.dumps(result, indent=2)
    )]


async def handle_render_diagram(arguments: dict) -> List[TextContent]:
    """Render diagram code to an image."""
    code = arguments.get("code")
    diagram_type = arguments.get("diagram_type")
    output_format = arguments.get("output_format", "svg")

    if not code or not diagram_type:
        raise ValueError("Missing required arguments: code, diagram_type")

    logger.info(f"Rendering {diagram_type} diagram to {output_format}")

    # Use secure debug logging
    debug_info = {
        'diagram_type': diagram_type,
        'output_format': output_format,
        'code_length': len(code)
    }
    logger.debug(f"Diagram render request: {SecurityUtils.safe_debug_info(debug_info)}")

    # Render the diagram using the existing renderer
    image_data = await render_diagram_impl(
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
    return [TextContent(
        type="text",
        text=json.dumps(result, indent=2)
    )]


async def handle_generate_and_render(arguments: dict) -> List[TextContent]:
    """Generate and render a diagram in one step."""
    prompt = arguments.get("prompt")
    diagram_type = arguments.get("diagram_type")
    output_format = arguments.get("output_format", "svg")

    if not prompt or not diagram_type:
        raise ValueError("Missing required arguments: prompt, diagram_type")

    logger.info(f"Generating and rendering {diagram_type} diagram")

    # Step 1: Generate diagram code
    gen_result = await handle_generate_diagram({
        "prompt": prompt,
        "diagram_type": diagram_type
    })
    gen_data = json.loads(gen_result[0].text)
    diagram_code = gen_data["diagram_code"]

    # Step 2: Render the diagram
    render_result = await handle_render_diagram({
        "code": diagram_code,
        "diagram_type": diagram_type,
        "output_format": output_format
    })
    render_data = json.loads(render_result[0].text)

    result = {
        "diagram_code": diagram_code,
        "image_data": render_data["image_data"],
        "output_format": output_format,
        "diagram_type": diagram_type,
        "prompt": prompt
    }

    logger.info(f"Successfully generated and rendered {diagram_type} diagram")
    return [TextContent(
        type="text",
        text=json.dumps(result, indent=2)
    )]


# FastAPI endpoint wrappers for MCP tools
@mcp_router.post("/tools/generate_diagram", response_model=ToolResponse)
async def api_generate_diagram(request: GenerateDiagramRequest):
    """FastAPI endpoint for generate_diagram tool."""
    try:
        result = await handle_generate_diagram({
            "prompt": request.prompt,
            "diagram_type": request.diagram_type
        })
        return ToolResponse(content=[{"type": "text", "text": result[0].text}])
    except Exception as e:
        logger.error(f"API error in generate_diagram: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@mcp_router.post("/tools/render_diagram", response_model=ToolResponse)
async def api_render_diagram(request: RenderDiagramRequest):
    """FastAPI endpoint for render_diagram tool."""
    try:
        result = await handle_render_diagram({
            "code": request.code,
            "diagram_type": request.diagram_type,
            "output_format": request.output_format
        })
        return ToolResponse(content=[{"type": "text", "text": result[0].text}])
    except Exception as e:
        logger.error(f"API error in render_diagram: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@mcp_router.post("/tools/generate_and_render", response_model=ToolResponse)
async def api_generate_and_render(request: GenerateAndRenderRequest):
    """FastAPI endpoint for generate_and_render tool."""
    try:
        result = await handle_generate_and_render({
            "prompt": request.prompt,
            "diagram_type": request.diagram_type,
            "output_format": request.output_format
        })
        return ToolResponse(content=[{"type": "text", "text": result[0].text}])
    except Exception as e:
        logger.error(f"API error in generate_and_render: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@mcp_router.get("/tools")
async def api_list_tools():
    """List available MCP tools."""
    tools = await list_tools()
    return {"tools": [tool.dict() for tool in tools]}


@mcp_router.post("/call_tool")
async def api_call_tool(request: ToolRequest):
    """Generic MCP tool call endpoint."""
    try:
        result = await call_tool(request.name, request.arguments)
        return ToolResponse(content=[{"type": "text", "text": r.text} for r in result])
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
                tools = await list_tools()
                response = {
                    "jsonrpc": "2.0",
                    "id": message.get("id"),
                    "result": {"tools": [tool.dict() for tool in tools]}
                }
            elif message.get("method") == "tools/call":
                params = message.get("params", {})
                result = await call_tool(params.get("name"), params.get("arguments", {}))
                response = {
                    "jsonrpc": "2.0",
                    "id": message.get("id"),
                    "result": {"content": [{"type": r.type, "text": r.text} for r in result]}
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


def get_mcp_server() -> Server:
    """Get the MCP server instance."""
    return mcp_server