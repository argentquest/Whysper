"""
Unified Diagram Provider API Endpoint
Uses the new modular provider system (backend/diagrams/)
Supports Mermaid, D2, and future diagram types
"""

from fastapi import APIRouter, HTTPException, BackgroundTasks, Depends
from fastapi.responses import Response, FileResponse
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, List
import logging
from common.logging_decorator import log_method_call
from pathlib import Path
from datetime import datetime
import os

from diagrams.provider_registry import get_registry, ProviderRegistry
from diagrams.base_diagram import BaseDiagramProvider
from diagrams.models import ProviderCapability

logger = logging.getLogger(__name__)
router = APIRouter()


# ===================================================================
# Request/Response Models
# ===================================================================

class DiagramRenderRequest(BaseModel):
    """Request model for diagram rendering"""

    code: str = Field(..., description="Diagram code to render", min_length=1)
    diagram_type: str = Field(..., description="Diagram type (mermaid, d2, etc.)")
    provider_id: Optional[str] = Field(None, description="Specific provider ID (optional)")
    output_format: str = Field("svg", description="Output format: 'svg', 'png', or native")
    metadata: Optional[Dict[str, Any]] = Field(None, description="Optional metadata")
    save_to_file: bool = Field(False, description="Whether to save output to file")

    class Config:
        schema_extra = {
            "example": {
                "code": "flowchart TD\n  A[Start] --> B[End]",
                "diagram_type": "mermaid",
                "output_format": "svg"
            }
        }


class DiagramRenderResponse(BaseModel):
    """Response model for diagram rendering"""

    success: bool = Field(..., description="Whether rendering was successful")
    content: Optional[str] = Field(None, description="Rendered diagram content")
    output_format: str = Field(..., description="Output format used")
    validation: Dict[str, Any] = Field(..., description="Validation results")
    metadata: Dict[str, Any] = Field(..., description="Render metadata")
    error: Optional[str] = Field(None, description="Error message if failed")
    file_path: Optional[str] = Field(None, description="Path to saved file if save_to_file=True")
    provider_id: str = Field(..., description="Provider that handled the request")


class DiagramValidationRequest(BaseModel):
    """Request model for diagram validation"""

    code: str = Field(..., description="Diagram code to validate", min_length=1)
    diagram_type: str = Field(..., description="Diagram type (mermaid, d2, etc.)")
    provider_id: Optional[str] = Field(None, description="Specific provider ID (optional)")
    auto_fix: bool = Field(True, description="Attempt pattern-based auto-fix")
    use_llm: bool = Field(False, description="Use LLM correction if pattern fix fails")


class DiagramValidationResponse(BaseModel):
    """Response model for diagram validation"""

    is_valid: bool = Field(..., description="Whether the diagram code is valid")
    error: Optional[str] = Field(None, description="Error message if invalid")
    code_length: int = Field(..., description="Length of the provided code")
    auto_fixed: bool = Field(False, description="Whether code was auto-fixed")
    llm_corrected: bool = Field(False, description="Whether LLM correction was used")
    fixed_code: Optional[str] = Field(None, description="Fixed code if applicable")
    correction_method: Optional[str] = Field(None, description="Method used for correction")
    provider_id: str = Field(..., description="Provider that handled validation")


class DiagramGenerationRequest(BaseModel):
    """Request model for LLM-based diagram generation"""

    prompt: str = Field(..., description="Natural language description of diagram to generate", min_length=1)
    diagram_type: str = Field(..., description="Diagram type (mermaid, d2, etc.)")
    system_prompt: Optional[str] = Field(None, description="Optional system prompt override")
    output_format: str = Field("svg", description="Output format: 'svg', 'png', or native")
    provider_id: Optional[str] = Field(None, description="Specific provider ID (optional)")

    class Config:
        schema_extra = {
            "example": {
                "prompt": "Create a simple architecture showing frontend connecting to backend",
                "diagram_type": "mermaid",
                "output_format": "svg"
            }
        }


class DiagramGenerationResponse(BaseModel):
    """Response model for diagram generation"""

    success: bool = Field(..., description="Whether generation was successful")
    content: Optional[str] = Field(None, description="Rendered diagram content (base64 encoded SVG)")
    diagram_code: Optional[str] = Field(None, description="Generated diagram code")
    output_format: str = Field(..., description="Output format used")
    error: Optional[str] = Field(None, description="Error message if failed")
    provider_id: str = Field(..., description="Provider that handled the request")


class ProviderInfoResponse(BaseModel):
    """Response model for provider information"""

    provider_id: str
    provider_name: str
    diagram_type: str
    description: Optional[str]
    supported_output_formats: List[str]
    capabilities: List[str]
    version: Optional[str]
    available: bool
    requires_llm: bool


class ProvidersListResponse(BaseModel):
    """Response model for listing all providers"""

    total_providers: int
    available_providers: int
    unavailable_providers: int
    providers: List[ProviderInfoResponse]


# ===================================================================
# Helper Functions
# ===================================================================

def get_provider_for_request(
    diagram_type: str,
    provider_id: Optional[str] = None,
    registry: ProviderRegistry = None
) -> BaseDiagramProvider:
    """
    Get appropriate provider for the request

    Args:
        diagram_type: Type of diagram (mermaid, d2, etc.)
        provider_id: Optional specific provider ID
        registry: Provider registry instance

    Returns:
        BaseDiagramProvider instance

    Raises:
        HTTPException if provider not found or not available
    """
    if registry is None:
        registry = get_registry()

    # If specific provider requested
    if provider_id:
        provider = registry.get(provider_id)
        if not provider:
            raise HTTPException(
                status_code=404,
                detail=f"Provider '{provider_id}' not found"
            )
        if not provider.is_available():
            raise HTTPException(
                status_code=503,
                detail=f"Provider '{provider_id}' is not available. Check CLI installation."
            )
        return provider

    # Get default provider for diagram type
    provider = registry.get_default_provider(diagram_type)
    if not provider:
        raise HTTPException(
            status_code=404,
            detail=f"No provider found for diagram type '{diagram_type}'"
        )

    if not provider.is_available():
        raise HTTPException(
            status_code=503,
            detail=f"Default provider for '{diagram_type}' is not available. Check CLI installation."
        )

    return provider


def save_diagram_to_file(
    content: str,
    output_format: str,
    diagram_type: str,
    code_hash: int
) -> str:
    """
    Save diagram content to file

    Returns:
        str: Path to saved file
    """
    # Create output directory
    output_dir = Path("backend") / "static" / "diagrams"
    output_dir.mkdir(parents=True, exist_ok=True)

    # Generate unique filename
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"{diagram_type}_{timestamp}_{code_hash % 10000}.{output_format}"
    file_path = output_dir / filename

    # Save file
    if output_format == "png":
        import base64
        with open(file_path, "wb") as f:
            f.write(base64.b64decode(content))
    else:
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(content)

    logger.info(f"Saved {output_format.upper()} to: {file_path}")
    return str(file_path)


# ===================================================================
# API Endpoints
# ===================================================================

@router.post("/render", response_model=DiagramRenderResponse)
@log_method_call
async def render_diagram(
    request: DiagramRenderRequest,
    background_tasks: BackgroundTasks
):
    """
    Render a diagram using the provider system

    This unified endpoint supports multiple diagram types (Mermaid, D2, PlantUML, etc.)
    through the modular provider system. Each provider handles validation, auto-fix,
    and rendering for its specific diagram type.

    Example:
        POST /api/v1/diagrams/render
        {
            "code": "flowchart TD\\n  A --> B",
            "diagram_type": "mermaid",
            "output_format": "svg"
        }
    """
    start_time = datetime.now()

    logger.info(f"[DIAGRAM RENDER] Request: type={request.diagram_type}, format={request.output_format}")
    logger.debug(f"[DIAGRAM RENDER] Code length: {len(request.code)} chars")

    try:
        # Get provider registry
        registry = get_registry()

        # Get appropriate provider
        provider = get_provider_for_request(
            request.diagram_type,
            request.provider_id,
            registry
        )

        logger.info(f"[DIAGRAM RENDER] Using provider: {provider.provider_id}")

        # Render diagram
        result = provider.render(
            request.code,
            output_format=request.output_format
        )

        # Save to file if requested
        file_path = None
        if request.save_to_file and result.success and result.content:
            try:
                file_path = save_diagram_to_file(
                    result.content,
                    result.output_format,
                    request.diagram_type,
                    hash(request.code)
                )
            except Exception as save_error:
                logger.error(f"Failed to save file: {save_error}")

        # Build response
        duration = (datetime.now() - start_time).total_seconds()

        response = DiagramRenderResponse(
            success=result.success,
            content=result.content,
            output_format=result.output_format,
            validation={
                "is_valid": result.validation.is_valid,
                "error": result.validation.error,
                "auto_fixed": result.validation.auto_fixed,
                "llm_corrected": result.validation.llm_corrected,
                "correction_method": result.validation.correction_method
            },
            metadata={
                "provider_id": provider.provider_id,
                "provider_name": provider.provider_name,
                "render_time": duration,
                "timestamp": datetime.now().isoformat(),
                "code_length": len(request.code),
                **(request.metadata or {}),
                **(result.metadata or {})
            },
            error=result.error,
            file_path=file_path,
            provider_id=provider.provider_id
        )

        logger.info(f"[DIAGRAM RENDER] Completed in {duration:.2f}s, success: {result.success}")

        return response

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"[DIAGRAM RENDER] Unexpected error: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Internal server error during diagram rendering: {str(e)}"
        )


@router.post("/validate", response_model=DiagramValidationResponse)
@log_method_call
async def validate_diagram(request: DiagramValidationRequest):
    """
    Validate diagram code without rendering

    Supports pattern-based auto-fix and optional LLM correction.
    """
    logger.info(f"[DIAGRAM VALIDATE] Request: type={request.diagram_type}")

    try:
        # Get provider
        registry = get_registry()
        provider = get_provider_for_request(
            request.diagram_type,
            request.provider_id,
            registry
        )

        logger.info(f"[DIAGRAM VALIDATE] Using provider: {provider.provider_id}")

        # Validate code
        validation_result = provider.validate_code(request.code)

        # Try auto-fix if validation failed and requested
        if not validation_result.is_valid and request.auto_fix:
            logger.info("[DIAGRAM VALIDATE] Attempting auto-fix...")

            fix_result = provider.auto_fix_pattern_based(
                request.code,
                validation_result.error or "Syntax error"
            )

            if fix_result.is_valid and fix_result.auto_fixed:
                validation_result = fix_result
                logger.info("[DIAGRAM VALIDATE] Auto-fix successful")
            elif request.use_llm and ProviderCapability.LLM_CORRECTION in provider.capabilities:
                logger.info("[DIAGRAM VALIDATE] Pattern fix failed, trying LLM correction...")
                # LLM correction would go here
                # For now, just log that it's available
                logger.info("[DIAGRAM VALIDATE] LLM correction available but not yet implemented in endpoint")

        response = DiagramValidationResponse(
            is_valid=validation_result.is_valid,
            error=validation_result.error,
            code_length=len(request.code),
            auto_fixed=validation_result.auto_fixed,
            llm_corrected=validation_result.llm_corrected,
            fixed_code=validation_result.fixed_code,
            correction_method=validation_result.correction_method,
            provider_id=provider.provider_id
        )

        logger.info(f"[DIAGRAM VALIDATE] Completed, valid: {validation_result.is_valid}")

        return response

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"[DIAGRAM VALIDATE] Unexpected error: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Internal server error during validation: {str(e)}"
        )


@router.get("/providers", response_model=ProvidersListResponse)
@log_method_call
async def list_providers():
    """
    List all available diagram providers

    Returns information about all registered providers including their
    capabilities, supported formats, and availability status.
    """
    try:
        registry = get_registry()
        all_providers = registry.list_all()

        providers_info = []
        for metadata in all_providers:
            providers_info.append(ProviderInfoResponse(
                provider_id=metadata.provider_id,
                provider_name=metadata.provider_name,
                diagram_type=metadata.diagram_type,
                description=metadata.description,
                supported_output_formats=metadata.supported_output_formats,
                capabilities=[cap.value for cap in metadata.capabilities],
                version=metadata.version,
                available=metadata.available,
                requires_llm=metadata.requires_llm
            ))

        stats = registry.get_statistics()

        return ProvidersListResponse(
            total_providers=stats["total_providers"],
            available_providers=stats["available_providers"],
            unavailable_providers=stats["unavailable_providers"],
            providers=providers_info
        )

    except Exception as e:
        logger.error(f"[PROVIDERS LIST] Error: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Error retrieving providers: {str(e)}"
        )


@router.get("/providers/{provider_id}", response_model=ProviderInfoResponse)
@log_method_call
async def get_provider_info(provider_id: str):
    """
    Get information about a specific provider
    """
    try:
        registry = get_registry()
        provider = registry.get(provider_id)

        if not provider:
            raise HTTPException(
                status_code=404,
                detail=f"Provider '{provider_id}' not found"
            )

        metadata = provider.get_metadata()

        return ProviderInfoResponse(
            provider_id=metadata.provider_id,
            provider_name=metadata.provider_name,
            diagram_type=metadata.diagram_type,
            description=metadata.description,
            supported_output_formats=metadata.supported_output_formats,
            capabilities=[cap.value for cap in metadata.capabilities],
            version=metadata.version,
            available=metadata.available,
            requires_llm=metadata.requires_llm
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"[PROVIDER INFO] Error: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Error retrieving provider info: {str(e)}"
        )


@router.get("/health")
@log_method_call
async def health_check():
    """
    Health check endpoint for diagram provider system
    """
    try:
        registry = get_registry()
        stats = registry.get_statistics()

        return {
            "status": "healthy" if stats["available_providers"] > 0 else "degraded",
            "total_providers": stats["total_providers"],
            "available_providers": stats["available_providers"],
            "diagram_types": stats["diagram_types"],
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"[HEALTH] Health check failed: {e}")
        return {
            "status": "unhealthy",
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }


@router.get("/download/{filename}")
@log_method_call
async def download_diagram(filename: str):
    """
    Download a pre-rendered diagram file

    Files are stored in backend/static/diagrams/ directory.
    """
    # Validate filename to prevent directory traversal
    if ".." in filename or "/" in filename or "\\" in filename:
        logger.warning(f"[DOWNLOAD] Attempted directory traversal: {filename}")
        raise HTTPException(status_code=400, detail="Invalid filename")

    # Ensure filename has valid extension
    valid_extensions = [".svg", ".png", ".d2", ".mmd"]
    if not any(filename.endswith(ext) for ext in valid_extensions):
        raise HTTPException(
            status_code=400,
            detail=f"Only {', '.join(valid_extensions)} files can be downloaded"
        )

    # Construct file path
    diagram_dir = Path("backend") / "static" / "diagrams"
    file_path = diagram_dir / filename

    # Check if file exists
    if not file_path.exists() or not file_path.is_file():
        logger.warning(f"[DOWNLOAD] File not found: {file_path}")
        raise HTTPException(
            status_code=404,
            detail=f"Diagram file '{filename}' not found"
        )

    logger.info(f"[DOWNLOAD] Serving file: {filename}")

    # Determine media type
    if filename.endswith(".svg"):
        media_type = "image/svg+xml"
    elif filename.endswith(".png"):
        media_type = "image/png"
    elif filename.endswith(".d2"):
        media_type = "text/plain"
    elif filename.endswith(".mmd"):
        media_type = "text/plain"
    else:
        media_type = "application/octet-stream"

    return FileResponse(
        path=str(file_path),
        media_type=media_type,
        filename=filename,
        headers={"Content-Disposition": f'attachment; filename="{filename}"'}
    )


# ===================================================================
# Diagram Generation Endpoint (for ArchStudio)
# ===================================================================

class GenerateDiagramRequest(BaseModel):
    """Request model for diagram generation using an agent"""
    agentId: str = Field(..., description="Agent ID to use for generation")
    prompt: str = Field(..., description="User prompt for the agent", min_length=1)
    diagramType: Optional[str] = Field("mermaid", description="Diagram type (mermaid, d2, plantuml, etc.)")


class GenerateDiagramResponse(BaseModel):
    """Response model for diagram generation"""
    requestId: str = Field(..., description="Unique request ID for tracking")
    diagram: Optional[DiagramRenderResponse] = Field(None, description="Initial diagram response if available")


@router.post("/generate", response_model=GenerateDiagramResponse)
@log_method_call
def generate_diagram(request: GenerateDiagramRequest):
    """Generate a diagram using an agent and optional rendering.

    For the ArchStudio application, this endpoint:
    1. Calls the specified agent with the prompt
    2. Returns a request ID for SSE tracking
    3. Optionally returns an initial diagram response

    Args:
        request: GenerateDiagramRequest with agentId, prompt, and diagramType

    Returns:
        GenerateDiagramResponse with requestId and optional initial diagram
    """
    import uuid
    from datetime import datetime

    logger.debug(f"[GENERATE] Received diagram generation request for agent: {request.agentId}")

    # Generate a unique request ID for tracking
    request_id = str(uuid.uuid4())

    try:
        # Import the settings service
        from app.services.settings_service import settings_service

        # Log all request details for debugging
        logger.info(f"[GENERATE] =============== DIAGRAM GENERATION REQUEST ===============")
        logger.info(f"[GENERATE] Request ID: {request_id}")
        logger.info(f"[GENERATE] Agent ID: '{request.agentId}'")
        logger.info(f"[GENERATE] Diagram Type: '{request.diagramType}' (type={type(request.diagramType).__name__})")
        logger.info(f"[GENERATE] User Prompt Length: {len(request.prompt)} characters")
        logger.info(f"[GENERATE] User Prompt Preview: {request.prompt[:200] if len(request.prompt) > 200 else request.prompt}...")

        # Load the agent's system prompt
        agent_prompt_filename = f"{request.agentId}.md"
        agent_system_prompt = settings_service.get_agent_prompt_content(agent_prompt_filename)
        logger.info(f"[GENERATE] Agent System Prompt Length: {len(agent_system_prompt)} characters")
        logger.info(f"[GENERATE] Agent System Prompt Preview: {agent_system_prompt[:200] if len(agent_system_prompt) > 200 else agent_system_prompt}...")

        logger.info(f"[GENERATE] ========================================================")

        # TODO: Implement actual diagram generation using the agent
        # This would involve:
        # 1. ✓ Loading the agent prompt from prompts/coding/agent/{agentId}.md
        # 2. Call the AI model with the agent prompt + user prompt
        # 3. Parse the generated diagram code
        # 4. Render it based on the diagramType via SSE stream

        # For now, return a placeholder response with the request ID
        # The actual diagram generation would happen asynchronously
        # and be delivered via SSE connection

        return GenerateDiagramResponse(
            requestId=request_id,
            diagram=None  # Diagram will be sent via SSE when ready
        )

    except Exception as e:
        logger.error(f"[GENERATE] Error generating diagram: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to generate diagram: {str(e)}"
        )


# ===================================================================
# Diagram Streaming Endpoint (for ArchStudio SSE)
# ===================================================================

from fastapi.responses import StreamingResponse


@router.get("/stream")
@log_method_call
def stream_diagram(requestId: str):
    """Stream diagram generation updates via SSE for a specific request.

    This endpoint provides Server-Sent Events (SSE) for real-time updates
    on diagram generation progress. The frontend maintains an EventSource
    connection to receive updates as diagrams are generated.

    Args:
        requestId: The request ID returned from the /generate endpoint

    Yields:
        SSE formatted messages with diagram generation updates
    """
    import asyncio

    logger.debug(f"[STREAM] Client connected to stream for request: {requestId}")

    async def event_generator():
        """Generate SSE events for diagram updates"""
        try:
            # Send a connection confirmation
            yield f"event: connected\ndata: {{'requestId': '{requestId}', 'message': 'Connected to diagram stream'}}\n\n"

            # Simulate a brief delay before sending placeholder message
            await asyncio.sleep(1)

            # Send a placeholder update (in a real implementation, this would be populated
            # from a task queue or similar mechanism)
            yield f"event: status\ndata: {{'requestId': '{requestId}', 'status': 'processing'}}\n\n"

            # Keep connection alive for a reasonable time or until client disconnects
            for i in range(10):
                await asyncio.sleep(2)
                # Send keepalive pings
                yield f": keepalive\n\n"

        except asyncio.CancelledError:
            logger.debug(f"[STREAM] Client disconnected from stream for request: {requestId}")
        except Exception as e:
            logger.error(f"[STREAM] Error in stream for request {requestId}: {str(e)}")
            yield f"event: error\ndata: {{'requestId': '{requestId}', 'error': '{str(e)}'}}\n\n"

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no"
        }
    )
