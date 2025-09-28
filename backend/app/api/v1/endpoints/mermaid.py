"""
Mermaid diagram rendering endpoints.

This module handles Mermaid diagram rendering with multiple fallback methods:
1. mermaid-cli (if installed)
2. Puppeteer with Node.js
3. Python-based SVG generation for simple diagrams
4. Client-side fallback
"""
from typing import Optional
from fastapi import APIRouter, HTTPException
from app.utils.mermaid_helpers import (
    validate_mermaid_code,
    render_mermaid_diagram,
)
from common.logger import get_logger

logger = get_logger(__name__)
router = APIRouter()


@router.post("/render")
def render_mermaid(request: dict):
    logger.debug("render_mermaid endpoint started")
    """
    Render a Mermaid diagram using multiple fallback methods.
    
    This endpoint attempts to render Mermaid diagrams using several methods:
    1. mermaid-cli (most reliable, requires installation)
    2. Puppeteer with Node.js (good compatibility)
    3. Python-based SVG generation (limited support)
    4. Client-side fallback (returns raw code for frontend rendering)
    
    Request format:
    {
        "code": "graph TD\nA --> B",
        "format": "png" | "svg",  // optional, defaults to "png"
        "title": "My Diagram"      // optional
    }
    
    Response format:
    {
        "success": true,
        "data": "data:image/png;base64,..." | "data:text/plain;base64,...",
        "format": "png" | "svg" | "fallback",
        "fallback": false | true,
        "clientRender": false | true,
        "message": "Status message"
    }
    """
    mermaid_code = request.get("code", "").strip()
    output_format = request.get("format", "png").lower()
    title = request.get("title")
    
    # Validate input
    if not mermaid_code:
        raise HTTPException(status_code=400, detail="mermaid code is required")
    
    if output_format not in ["png", "svg"]:
        raise HTTPException(status_code=400, detail="Format must be 'png' or 'svg'")
    
    # Validate Mermaid code
    is_valid, error_message = validate_mermaid_code(mermaid_code)
    if not is_valid:
        raise HTTPException(status_code=400, detail=f"Invalid Mermaid code: {error_message}")
    
    try:
        logger.info(f"Rendering Mermaid diagram (format: {output_format})")
        success, result, is_fallback = render_mermaid_diagram(
            mermaid_code, 
            output_format, 
            title
        )
        
        if success:
            response = {
                "success": True,
                "data": result,
                "format": "fallback" if is_fallback else output_format,
                "fallback": is_fallback,
                "clientRender": is_fallback,
                "message": "Mermaid diagram rendered successfully"
            }
            
            if is_fallback:
                response["message"] = "Server-side rendering failed, using client-side fallback"
                logger.info("Using client-side fallback for Mermaid rendering")
            else:
                logger.info(f"Successfully rendered Mermaid diagram as {output_format}")
            
            return response
        else:
            raise HTTPException(
                status_code=500,
                detail="Failed to render Mermaid diagram with all available methods"
            )
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error rendering Mermaid diagram: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to render mermaid diagram: {str(e)}"
        )
