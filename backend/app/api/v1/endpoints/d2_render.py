"""
D2 Rendering API Endpoint
Handles D2 diagram rendering requests using the CLI service
"""

from fastapi import APIRouter, HTTPException, BackgroundTasks, Depends
from fastapi.responses import Response, FileResponse
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, List
import logging
from common.logging_decorator import log_method_call
import asyncio
import os
from datetime import datetime
from pathlib import Path

from app.services.d2_render_service import get_d2_service, D2RenderService
from security_utils import SecurityUtils

logger = logging.getLogger(__name__)
router = APIRouter()


# Request/Response Models
class D2RenderRequest(BaseModel):
    """Request model for D2 rendering"""

    code: str = Field(..., description="D2 diagram code to render", min_length=1)
    metadata: Optional[Dict[str, Any]] = Field(
        None, description="Optional metadata to include with the render"
    )
    return_svg: bool = Field(
        True, description="Whether to return SVG content in response"
    )
    save_to_file: bool = Field(False, description="Whether to save the SVG to a file")


class D2RenderResponse(BaseModel):
    """Response model for D2 rendering"""

    success: bool = Field(..., description="Whether rendering was successful")
    svg_content: Optional[str] = Field(
        None, description="SVG content if successful and return_svg=True"
    )
    validation: Dict[str, Any] = Field(..., description="Validation results")
    metadata: Dict[str, Any] = Field(..., description="Render metadata")
    error: Optional[str] = Field(None, description="Error message if rendering failed")
    file_path: Optional[str] = Field(
        None, description="Path to saved file if save_to_file=True"
    )


class D2ValidationRequest(BaseModel):
    """Request model for D2 validation only"""

    code: str = Field(..., description="D2 code to validate", min_length=1)


class D2ValidationResponse(BaseModel):
    """Response model for D2 validation"""

    is_valid: bool = Field(..., description="Whether the D2 code is valid")
    error: Optional[str] = Field(None, description="Error message if invalid")
    code_length: int = Field(..., description="Length of the provided code")


class D2BatchRenderRequest(BaseModel):
    """Request model for batch D2 rendering"""

    codes: List[str] = Field(
        ..., description="List of D2 codes to render", min_items=1, max_items=50
    )
    metadata: Optional[Dict[str, Any]] = Field(
        None, description="Optional metadata to include with all renders"
    )


class D2BatchRenderResponse(BaseModel):
    """Response model for batch D2 rendering"""

    results: List[D2RenderResponse] = Field(..., description="List of render results")
    summary: Dict[str, Any] = Field(..., description="Batch summary statistics")
    batch_id: str = Field(..., description="Unique identifier for this batch")


class D2InfoResponse(BaseModel):
    """Response model for D2 CLI info"""

    available: bool = Field(..., description="Whether D2 CLI is available")
    executable: Optional[str] = Field(None, description="Path to D2 executable")
    version: Optional[str] = Field(None, description="D2 version")
    error: Optional[str] = Field(None, description="Error message if not available")


# Helper function to safely log D2 code
@log_method_call
def safe_log_d2_code(code: str, max_length: int = 200):
    """Safely log D2 code without exposing sensitive data"""
    if len(code) <= max_length:
        return SecurityUtils.safe_debug_info({"d2_code": code})
    else:
        truncated = code[:max_length] + "...[truncated]"
        return SecurityUtils.safe_debug_info({"d2_code": truncated})


@router.post("/render", response_model=D2RenderResponse)
@log_method_call
async def render_d2(
    request: D2RenderRequest,
    background_tasks: BackgroundTasks,
    d2_service: D2RenderService = Depends(get_d2_service),
):
    """
    Render a D2 diagram to SVG using the CLI

    This endpoint takes D2 code and renders it to SVG using the D2 CLI.
    It includes validation, error handling, and optional file saving.
    """
    start_time = datetime.now()

    logger.info(f"[D2 RENDER] Received render request")
    safe_log_d2_code(request.code)

    try:
        # Render with metadata
        render_metadata = {
            "endpoint": "/render",
            "return_svg": request.return_svg,
            "save_to_file": request.save_to_file,
            **(request.metadata or {}),
        }

        result = d2_service.render_d2_with_metadata(request.code, render_metadata)

        # Prepare response
        response_data = {
            "success": result["success"],
            "svg_content": result["svg_content"] if request.return_svg else None,
            "validation": result["validation"],
            "metadata": result["metadata"],
            "error": result["error"],
            "file_path": None,
        }

        # Save to file if requested
        if request.save_to_file and result["success"] and result["svg_content"]:
            try:
                # Create output directory
                output_dir = "backend/generated_svgs"
                import os

                os.makedirs(output_dir, exist_ok=True)

                # Generate unique filename
                timestamp = start_time.strftime("%Y%m%d_%H%M%S")
                filename = f"d2_render_{timestamp}_{hash(request.code) % 10000}.svg"
                file_path = os.path.join(output_dir, filename)

                # Save file
                with open(file_path, "w", encoding="utf-8") as f:
                    f.write(result["svg_content"])

                response_data["file_path"] = file_path
                logger.info(f"[D2 RENDER] Saved SVG to: {file_path}")

            except Exception as save_error:
                logger.error(f"[D2 RENDER] Failed to save file: {save_error}")
                # Don't fail the request, just log the error

        # Log completion
        duration = (datetime.now() - start_time).total_seconds()
        logger.info(
            f"[D2 RENDER] Render completed in {duration:.2f}s, success: {result['success']}"
        )

        return D2RenderResponse(**response_data)

    except Exception as e:
        logger.error(f"[D2 RENDER] Unexpected error: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Internal server error during D2 rendering: {str(e)}",
        )


@router.post("/validate", response_model=D2ValidationResponse)
@log_method_call
async def validate_d2(
    request: D2ValidationRequest, d2_service: D2RenderService = Depends(get_d2_service)
):
    """
    Validate D2 code without rendering

    This endpoint only validates D2 syntax without generating SVG.
    Useful for quick syntax checking in editors.
    """
    logger.info(f"[D2 VALIDATE] Received validation request")
    safe_log_d2_code(request.code)

    try:
        is_valid, error_msg = d2_service.validate_d2_code(request.code)

        response_data = {
            "is_valid": is_valid,
            "error": error_msg if not is_valid else None,
            "code_length": len(request.code),
        }

        logger.info(f"[D2 VALIDATE] Validation completed, valid: {is_valid}")

        return D2ValidationResponse(**response_data)

    except Exception as e:
        logger.error(f"[D2 VALIDATE] Unexpected error: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Internal server error during D2 validation: {str(e)}",
        )


@router.post("/render/batch", response_model=D2BatchRenderResponse)
@log_method_call
async def render_d2_batch(
    request: D2BatchRenderRequest, d2_service: D2RenderService = Depends(get_d2_service)
):
    """
    Render multiple D2 diagrams in a batch

    This endpoint processes multiple D2 codes and returns all results.
    Maximum 50 diagrams per batch.
    """
    if len(request.codes) > 50:
        raise HTTPException(
            status_code=400, detail="Maximum 50 diagrams allowed per batch"
        )

    start_time = datetime.now()
    batch_id = f"batch_{start_time.strftime('%Y%m%d_%H%M%S')}_{hash(str(request.codes)) % 10000}"

    logger.info(
        f"[D2 BATCH] Received batch render request with {len(request.codes)} diagrams, batch_id: {batch_id}"
    )

    results = []
    success_count = 0

    try:
        for i, code in enumerate(request.codes):
            logger.info(f"[D2 BATCH] Processing diagram {i+1}/{len(request.codes)}")

            # Render each diagram
            render_metadata = {
                "batch_id": batch_id,
                "diagram_index": i,
                "endpoint": "/render/batch",
                **(request.metadata or {}),
            }

            result = d2_service.render_d2_with_metadata(code, render_metadata)

            # Convert to response model
            response_data = {
                "success": result["success"],
                "svg_content": result["svg_content"],
                "validation": result["validation"],
                "metadata": result["metadata"],
                "error": result["error"],
                "file_path": None,
            }

            results.append(D2RenderResponse(**response_data))

            if result["success"]:
                success_count += 1

        # Calculate summary
        duration = (datetime.now() - start_time).total_seconds()
        summary = {
            "total_diagrams": len(request.codes),
            "successful": success_count,
            "failed": len(request.codes) - success_count,
            "success_rate": (success_count / len(request.codes)) * 100,
            "total_time": duration,
            "average_time_per_diagram": duration / len(request.codes),
        }

        logger.info(
            f"[D2 BATCH] Batch completed, success: {success_count}/{len(request.codes)} in {duration:.2f}s"
        )

        return D2BatchRenderResponse(
            results=results, summary=summary, batch_id=batch_id
        )

    except Exception as e:
        logger.error(f"[D2 BATCH] Unexpected error: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Internal server error during batch D2 rendering: {str(e)}",
        )


@router.get("/info", response_model=D2InfoResponse)
@log_method_call
async def get_d2_info(d2_service: D2RenderService = Depends(get_d2_service)):
    """
    Get information about the D2 CLI installation

    Returns version, availability, and other useful information.
    """
    try:
        info = d2_service.get_d2_info()
        return D2InfoResponse(**info)
    except Exception as e:
        logger.error(f"[D2 INFO] Unexpected error: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Internal server error retrieving D2 info: {str(e)}",
        )


@router.get("/health")
@log_method_call
async def d2_health_check(d2_service: D2RenderService = Depends(get_d2_service)):
    """
    Health check endpoint for D2 rendering service

    Returns simple status information for monitoring.
    """
    try:
        info = d2_service.get_d2_info()
        return {
            "status": "healthy" if info["available"] else "unhealthy",
            "d2_available": info["available"],
            "timestamp": datetime.now().isoformat(),
        }
    except Exception as e:
        logger.error(f"[D2 HEALTH] Health check failed: {str(e)}")
        return {
            "status": "unhealthy",
            "d2_available": False,
            "error": str(e),
            "timestamp": datetime.now().isoformat(),
        }


@router.get("/download/{filename}")
@log_method_call
async def download_d2_svg(filename: str):
    """
    Download a pre-rendered D2 SVG file

    This endpoint serves SVG files that were generated during the chat conversation.
    Files are stored in backend/static/d2_diagrams/ directory.

    Args:
        filename: The SVG filename to download (e.g., d2_diagram_20251018_123456_abc123.svg)

    Returns:
        FileResponse: The SVG file for download
    """
    # Validate filename to prevent directory traversal attacks
    if ".." in filename or "/" in filename or "\\" in filename:
        logger.warning(f"[D2 DOWNLOAD] Attempted directory traversal: {filename}")
        raise HTTPException(
            status_code=400,
            detail="Invalid filename"
        )

    # Ensure filename ends with .svg
    if not filename.endswith(".svg"):
        raise HTTPException(
            status_code=400,
            detail="Only SVG files can be downloaded"
        )

    # Construct file path
    svg_dir = Path("backend") / "static" / "d2_diagrams"
    file_path = svg_dir / filename

    # Check if file exists
    if not file_path.exists() or not file_path.is_file():
        logger.warning(f"[D2 DOWNLOAD] File not found: {file_path}")
        raise HTTPException(
            status_code=404,
            detail=f"SVG file '{filename}' not found"
        )

    logger.info(f"[D2 DOWNLOAD] Serving file: {filename}")

    # Return the file
    return FileResponse(
        path=str(file_path),
        media_type="image/svg+xml",
        filename=filename,
        headers={
            "Content-Disposition": f'attachment; filename="{filename}"'
        }
    )
