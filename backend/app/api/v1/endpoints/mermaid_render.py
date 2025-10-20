"""
Mermaid Rendering API Endpoint
Handles Mermaid diagram rendering and validation requests using the CLI service
"""

from fastapi import APIRouter, HTTPException, BackgroundTasks, Depends
from fastapi.responses import Response, FileResponse
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, List
import logging
import os
from datetime import datetime
from pathlib import Path

from app.services.mermaid_render_service import get_mermaid_service, MermaidRenderService
from security_utils import SecurityUtils

logger = logging.getLogger(__name__)
router = APIRouter()


# Request/Response Models
class MermaidRenderRequest(BaseModel):
    """Request model for Mermaid rendering"""

    code: str = Field(..., description="Mermaid diagram code to render", min_length=1)
    metadata: Optional[Dict[str, Any]] = Field(
        None, description="Optional metadata to include with the render"
    )
    return_svg: bool = Field(
        True, description="Whether to return SVG content in response"
    )
    save_to_file: bool = Field(False, description="Whether to save the SVG to a file")
    output_format: str = Field("svg", description="Output format: 'svg' or 'png'")


class MermaidRenderResponse(BaseModel):
    """Response model for Mermaid rendering"""

    success: bool = Field(..., description="Whether rendering was successful")
    svg_content: Optional[str] = Field(
        None, description="SVG content if successful and return_svg=True"
    )
    png_content: Optional[str] = Field(
        None, description="Base64-encoded PNG content if format=png"
    )
    validation: Dict[str, Any] = Field(..., description="Validation results")
    metadata: Dict[str, Any] = Field(..., description="Render metadata")
    error: Optional[str] = Field(None, description="Error message if rendering failed")
    file_path: Optional[str] = Field(
        None, description="Path to saved file if save_to_file=True"
    )


class MermaidValidationRequest(BaseModel):
    """Request model for Mermaid validation only"""

    code: str = Field(..., description="Mermaid code to validate", min_length=1)
    auto_fix: bool = Field(True, description="Attempt to auto-fix syntax errors")


class MermaidValidationResponse(BaseModel):
    """Response model for Mermaid validation"""

    is_valid: bool = Field(..., description="Whether the Mermaid code is valid")
    error: Optional[str] = Field(None, description="Error message if invalid")
    code_length: int = Field(..., description="Length of the provided code")
    auto_fixed: bool = Field(False, description="Whether code was auto-fixed")
    fixed_code: Optional[str] = Field(None, description="Auto-fixed code if applicable")
    fix_message: Optional[str] = Field(None, description="Auto-fix message")


class MermaidInfoResponse(BaseModel):
    """Response model for Mermaid CLI info"""

    available: bool = Field(..., description="Whether Mermaid CLI is available")
    executable: Optional[str] = Field(None, description="Path to Mermaid executable")
    version: Optional[str] = Field(None, description="Mermaid version")
    error: Optional[str] = Field(None, description="Error message if not available")


# Helper function to safely log Mermaid code
def safe_log_mermaid_code(code: str, max_length: int = 200):
    """Safely log Mermaid code without exposing sensitive data"""
    if len(code) <= max_length:
        return SecurityUtils.safe_debug_info({"mermaid_code": code})
    else:
        truncated = code[:max_length] + "...[truncated]"
        return SecurityUtils.safe_debug_info({"mermaid_code": truncated})


@router.post("/render", response_model=MermaidRenderResponse)
async def render_mermaid(
    request: MermaidRenderRequest,
    background_tasks: BackgroundTasks,
    mermaid_service: MermaidRenderService = Depends(get_mermaid_service),
):
    """
    Render a Mermaid diagram to SVG/PNG using the CLI

    This endpoint takes Mermaid code and renders it to SVG or PNG using the Mermaid CLI (mmdc).
    It includes validation, auto-fixing, error handling, and optional file saving.
    """
    start_time = datetime.now()

    logger.info(f"[MERMAID RENDER] Received render request")
    safe_log_mermaid_code(request.code)

    try:
        # Render with metadata
        render_metadata = {
            "endpoint": "/render",
            "return_svg": request.return_svg,
            "save_to_file": request.save_to_file,
            "output_format": request.output_format,
            **(request.metadata or {}),
        }

        result = mermaid_service.render_mermaid_with_metadata(
            request.code, render_metadata, request.output_format
        )

        # Prepare response
        response_data = {
            "success": result["success"],
            "svg_content": result.get("svg_content") if request.return_svg and request.output_format == "svg" else None,
            "png_content": result.get("png_content") if request.output_format == "png" else None,
            "validation": result["validation"],
            "metadata": result["metadata"],
            "error": result["error"],
            "file_path": None,
        }

        # Save to file if requested
        if request.save_to_file and result["success"]:
            try:
                # Create output directory
                output_dir = "backend/static/mermaid_diagrams"
                os.makedirs(output_dir, exist_ok=True)

                # Generate unique filename
                timestamp = start_time.strftime("%Y%m%d_%H%M%S")
                ext = "png" if request.output_format == "png" else "svg"
                filename = f"mermaid_diagram_{timestamp}_{hash(request.code) % 10000}.{ext}"
                file_path = os.path.join(output_dir, filename)

                # Save file
                if request.output_format == "png":
                    import base64
                    with open(file_path, "wb") as f:
                        f.write(base64.b64decode(result.get("png_content", "")))
                else:
                    with open(file_path, "w", encoding="utf-8") as f:
                        f.write(result.get("svg_content", ""))

                response_data["file_path"] = file_path
                logger.info(f"[MERMAID RENDER] Saved {ext.upper()} to: {file_path}")

            except Exception as save_error:
                logger.error(f"[MERMAID RENDER] Failed to save file: {save_error}")
                # Don't fail the request, just log the error

        # Log completion
        duration = (datetime.now() - start_time).total_seconds()
        logger.info(
            f"[MERMAID RENDER] Render completed in {duration:.2f}s, success: {result['success']}"
        )

        return MermaidRenderResponse(**response_data)

    except Exception as e:
        logger.error(f"[MERMAID RENDER] Unexpected error: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Internal server error during Mermaid rendering: {str(e)}",
        )


@router.post("/validate", response_model=MermaidValidationResponse)
async def validate_mermaid(
    request: MermaidValidationRequest,
    mermaid_service: MermaidRenderService = Depends(get_mermaid_service)
):
    """
    Validate Mermaid code without rendering

    This endpoint validates Mermaid syntax and optionally attempts to auto-fix errors.
    Useful for quick syntax checking in editors or before rendering.
    """
    logger.info(f"[MERMAID VALIDATE] Received validation request")
    safe_log_mermaid_code(request.code)

    try:
        is_valid, error_msg = mermaid_service.validate_mermaid_code(request.code)

        response_data = {
            "is_valid": is_valid,
            "error": error_msg if not is_valid else None,
            "code_length": len(request.code),
            "auto_fixed": False,
            "fixed_code": None,
            "fix_message": None
        }

        # Try auto-fix if validation failed and auto_fix is enabled
        if not is_valid and request.auto_fix:
            logger.info("[MERMAID VALIDATE] Attempting auto-fix...")
            from mvp_diagram_generator.mermaid_cli_validator import validate_and_fix_mermaid_with_cli

            is_fixed, fixed_code, fix_message = validate_and_fix_mermaid_with_cli(request.code)

            if is_fixed:
                response_data["is_valid"] = True
                response_data["auto_fixed"] = True
                response_data["fixed_code"] = fixed_code
                response_data["fix_message"] = fix_message
                response_data["error"] = None
                logger.info(f"[MERMAID VALIDATE] Auto-fix successful: {fix_message}")
            else:
                logger.info(f"[MERMAID VALIDATE] Auto-fix failed")

        logger.info(f"[MERMAID VALIDATE] Validation completed, valid: {response_data['is_valid']}")

        return MermaidValidationResponse(**response_data)

    except Exception as e:
        logger.error(f"[MERMAID VALIDATE] Unexpected error: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Internal server error during Mermaid validation: {str(e)}",
        )


@router.get("/info", response_model=MermaidInfoResponse)
async def get_mermaid_info(mermaid_service: MermaidRenderService = Depends(get_mermaid_service)):
    """
    Get information about the Mermaid CLI installation

    Returns version, availability, and other useful information.
    """
    try:
        info = mermaid_service.get_mermaid_info()
        return MermaidInfoResponse(**info)
    except Exception as e:
        logger.error(f"[MERMAID INFO] Unexpected error: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Internal server error retrieving Mermaid info: {str(e)}",
        )


@router.get("/health")
async def mermaid_health_check(mermaid_service: MermaidRenderService = Depends(get_mermaid_service)):
    """
    Health check endpoint for Mermaid rendering service

    Returns simple status information for monitoring.
    """
    try:
        info = mermaid_service.get_mermaid_info()
        return {
            "status": "healthy" if info["available"] else "unhealthy",
            "mermaid_available": info["available"],
            "timestamp": datetime.now().isoformat(),
        }
    except Exception as e:
        logger.error(f"[MERMAID HEALTH] Health check failed: {str(e)}")
        return {
            "status": "unhealthy",
            "mermaid_available": False,
            "error": str(e),
            "timestamp": datetime.now().isoformat(),
        }


@router.get("/download/{filename}")
async def download_mermaid_diagram(filename: str):
    """
    Download a pre-rendered Mermaid diagram file

    This endpoint serves SVG/PNG files that were generated during the chat conversation.
    Files are stored in backend/static/mermaid_diagrams/ directory.

    Args:
        filename: The diagram filename to download (e.g., mermaid_diagram_20251018_123456_abc123.svg)

    Returns:
        FileResponse: The diagram file for download
    """
    # Validate filename to prevent directory traversal attacks
    if ".." in filename or "/" in filename or "\\" in filename:
        logger.warning(f"[MERMAID DOWNLOAD] Attempted directory traversal: {filename}")
        raise HTTPException(
            status_code=400,
            detail="Invalid filename"
        )

    # Ensure filename ends with .svg or .png
    if not (filename.endswith(".svg") or filename.endswith(".png")):
        raise HTTPException(
            status_code=400,
            detail="Only SVG and PNG files can be downloaded"
        )

    # Construct file path
    diagram_dir = Path("backend") / "static" / "mermaid_diagrams"
    file_path = diagram_dir / filename

    # Check if file exists
    if not file_path.exists() or not file_path.is_file():
        logger.warning(f"[MERMAID DOWNLOAD] File not found: {file_path}")
        raise HTTPException(
            status_code=404,
            detail=f"Diagram file '{filename}' not found"
        )

    logger.info(f"[MERMAID DOWNLOAD] Serving file: {filename}")

    # Determine media type
    media_type = "image/svg+xml" if filename.endswith(".svg") else "image/png"

    # Return the file
    return FileResponse(
        path=str(file_path),
        media_type=media_type,
        filename=filename,
        headers={
            "Content-Disposition": f'attachment; filename="{filename}"'
        }
    )
