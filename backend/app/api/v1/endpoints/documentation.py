"""
Documentation generation endpoints for Whysper.

This module provides endpoints for generating various types of documentation
from codebases, including API docs, README files, architecture diagrams, and usage examples.
"""

from fastapi import APIRouter, HTTPException, BackgroundTasks
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field
import uuid
from common.logger import get_logger

logger = get_logger(__name__)
router = APIRouter()

# Import documentation service
try:
    from app.services.documentation_service import DocumentationService, DocumentationRequest, DocumentationResult
    doc_service = DocumentationService()
except ImportError:
    logger.warning("DocumentationService not available, using placeholder")
    doc_service = None


# Request/Response Models
class DocumentationGenerateRequest(BaseModel):
    """Request model for documentation generation."""
    file_paths: List[str] = Field(..., description="List of file paths to analyze")
    documentation_type: str = Field(..., description="Type of documentation to generate")
    output_format: str = Field(default="markdown", description="Output format")
    template: Optional[str] = Field(None, description="Template to use")
    include_examples: bool = Field(default=True, description="Include usage examples")
    include_diagrams: bool = Field(default=True, description="Include diagrams")
    target_audience: str = Field(default="developers", description="Target audience")
    language: Optional[str] = Field(None, description="Force specific documentation language")


class DocumentationGenerateResponse(BaseModel):
    """Response model for documentation generation."""
    id: str = Field(..., description="Documentation ID")
    content: str = Field(..., description="Generated documentation content")
    metadata: Dict[str, Any] = Field(..., description="Documentation metadata")
    diagrams: List[Dict[str, Any]] = Field(default=[], description="Generated diagrams")
    examples: List[Dict[str, Any]] = Field(default=[], description="Generated examples")
    references: List[str] = Field(default=[], description="Cross-references")
    generated_at: str = Field(..., description="Generation timestamp")
    processing_time: float = Field(..., description="Processing time in seconds")
    token_usage: Dict[str, int] = Field(default={}, description="Token usage information")


class DocumentationTemplatesResponse(BaseModel):
    """Response model for documentation templates."""
    templates: List[Dict[str, Any]] = Field(..., description="Available templates")
    count: int = Field(..., description="Number of templates")


class DocumentationExportRequest(BaseModel):
    """Request model for documentation export."""
    documentation_id: str = Field(..., description="Documentation ID")
    export_format: str = Field(..., description="Export format")
    content: str = Field(..., description="Documentation content")
    filename: Optional[str] = Field(None, description="Export filename")
    options: Optional[Dict[str, Any]] = Field(default={}, description="Export options")


class DocumentationExportResponse(BaseModel):
    """Response model for documentation export."""
    content: str = Field(..., description="Exported content")
    format: str = Field(..., description="Export format")
    filename: str = Field(..., description="Export filename")
    content_type: str = Field(..., description="Content type")


@router.post("/generate", response_model=DocumentationGenerateResponse)
def generate_documentation(request: DocumentationGenerateRequest):
    """
    Generate documentation for selected files.
    
    This endpoint analyzes the provided code files and generates comprehensive
    documentation based on the specified type and format.
    
    Args:
        request: Documentation generation request with file paths and options
        
    Returns:
        Generated documentation with metadata and optional diagrams
    """
    logger.info(f"Generating {request.documentation_type} documentation for {len(request.file_paths)} files")
    
    if not doc_service:
        raise HTTPException(
            status_code=503, 
            detail="Documentation service not available"
        )
    
    try:
        # Create documentation request
        doc_request = DocumentationRequest(
            file_paths=request.file_paths,
            documentation_type=request.documentation_type,
            output_format=request.output_format,
            template=request.template,
            include_examples=request.include_examples,
            include_diagrams=request.include_diagrams,
            target_audience=request.target_audience,
            language=request.language
        )
        
        # Generate documentation
        result = doc_service.generate_documentation(doc_request)
        
        # Convert to response format
        response = DocumentationGenerateResponse(
            id=result.id,
            content=result.content,
            metadata=result.metadata,
            diagrams=result.diagrams,
            examples=result.examples,
            references=result.references,
            generated_at=result.generated_at.isoformat(),
            processing_time=result.processing_time,
            token_usage=result.token_usage
        )
        
        logger.info(f"Documentation generated successfully in {result.processing_time:.2f}s")
        return response
        
    except Exception as e:
        logger.error(f"Error generating documentation: {e}")
        raise HTTPException(
            status_code=500, 
            detail=f"Failed to generate documentation: {str(e)}"
        )


@router.post("/api-docs", response_model=DocumentationGenerateResponse)
def generate_api_docs(request: Dict[str, Any]):
    """
    Generate API documentation from code signatures.
    
    This endpoint specializes in generating API documentation, including endpoints,
    request/response schemas, authentication, and error handling.
    
    Args:
        request: API documentation generation request
        
    Returns:
        API documentation with endpoint details and examples
    """
    logger.info("Generating API documentation")
    
    if not doc_service:
        raise HTTPException(
            status_code=503, 
            detail="Documentation service not available"
        )
    
    try:
        # Extract file paths from request
        file_paths = request.get("file_paths", [])
        
        # Create documentation request with API-specific settings
        doc_request = DocumentationRequest(
            file_paths=file_paths,
            documentation_type="api",
            output_format=request.get("output_format", "markdown"),
            template="api_documentation",
            include_examples=True,
            include_diagrams=True,
            target_audience=request.get("target_audience", "developers"),
            language=request.get("language")
        )
        
        # Generate documentation
        result = doc_service.generate_documentation(doc_request)
        
        # Convert to response format
        response = DocumentationGenerateResponse(
            id=result.id,
            content=result.content,
            metadata=result.metadata,
            diagrams=result.diagrams,
            examples=result.examples,
            references=result.references,
            generated_at=result.generated_at.isoformat(),
            processing_time=result.processing_time,
            token_usage=result.token_usage
        )
        
        logger.info(f"API documentation generated successfully in {result.processing_time:.2f}s")
        return response
        
    except Exception as e:
        logger.error(f"Error generating API documentation: {e}")
        raise HTTPException(
            status_code=500, 
            detail=f"Failed to generate API documentation: {str(e)}"
        )


@router.post("/readme", response_model=DocumentationGenerateResponse)
def generate_readme(request: Dict[str, Any]):
    """
    Generate project README file.
    
    This endpoint generates a comprehensive README file with project description,
    installation instructions, usage examples, and contribution guidelines.
    
    Args:
        request: README generation request
        
    Returns:
        Generated README content with project information
    """
    logger.info("Generating README file")
    
    if not doc_service:
        raise HTTPException(
            status_code=503, 
            detail="Documentation service not available"
        )
    
    try:
        # Extract file paths from request
        file_paths = request.get("file_paths", [])
        
        # Create documentation request with README-specific settings
        doc_request = DocumentationRequest(
            file_paths=file_paths,
            documentation_type="readme",
            output_format=request.get("output_format", "markdown"),
            template="readme_template",
            include_examples=True,
            include_diagrams=False,
            target_audience="mixed",
            language=request.get("language")
        )
        
        # Generate documentation
        result = doc_service.generate_documentation(doc_request)
        
        # Convert to response format
        response = DocumentationGenerateResponse(
            id=result.id,
            content=result.content,
            metadata=result.metadata,
            diagrams=result.diagrams,
            examples=result.examples,
            references=result.references,
            generated_at=result.generated_at.isoformat(),
            processing_time=result.processing_time,
            token_usage=result.token_usage
        )
        
        logger.info(f"README generated successfully in {result.processing_time:.2f}s")
        return response
        
    except Exception as e:
        logger.error(f"Error generating README: {e}")
        raise HTTPException(
            status_code=500, 
            detail=f"Failed to generate README: {str(e)}"
        )


@router.get("/templates", response_model=DocumentationTemplatesResponse)
def get_documentation_templates():
    """
    Get available documentation templates.
    
    This endpoint returns a list of available documentation templates
    with their descriptions and supported formats.
    
    Returns:
        List of available documentation templates
    """
    logger.info("Retrieving documentation templates")
    
    if not doc_service:
        raise HTTPException(
            status_code=503, 
            detail="Documentation service not available"
        )
    
    try:
        # Get available templates
        templates = doc_service.templates
        
        # Convert to response format
        template_list = []
        for name, template in templates.items():
            template_list.append({
                "name": name,
                "title": template.get("metadata", {}).get("title", name),
                "description": template.get("metadata", {}).get("description", ""),
                "supported_formats": ["markdown", "html"],
                "instructions": template.get("instructions", "")
            })
        
        response = DocumentationTemplatesResponse(
            templates=template_list,
            count=len(template_list)
        )
        
        logger.info(f"Retrieved {len(template_list)} documentation templates")
        return response
        
    except Exception as e:
        logger.error(f"Error retrieving documentation templates: {e}")
        raise HTTPException(
            status_code=500, 
            detail=f"Failed to retrieve templates: {str(e)}"
        )


@router.post("/export", response_model=DocumentationExportResponse)
def export_documentation(request: DocumentationExportRequest):
    """
    Export generated documentation to various formats.
    
    This endpoint takes generated documentation and exports it to the specified
    format, with optional styling and formatting options.
    
    Args:
        request: Documentation export request
        
    Returns:
        Exported documentation in the specified format
    """
    logger.info(f"Exporting documentation to {request.export_format}")
    
    try:
        # Get documentation content
        documentation_id = request.documentation_id
        
        # This would typically retrieve from a database or cache
        # For now, we'll assume the content is provided in the request
        content = request.content
        
        # Export based on format
        if request.export_format == "pdf":
            # This would require PDF export functionality
            exported_content = content  # Placeholder
            content_type = "application/pdf"
        elif request.export_format == "html":
            # This would require HTML export functionality
            exported_content = content  # Placeholder
            content_type = "text/html"
        elif request.export_format == "docx":
            # This would require Word export functionality
            exported_content = content  # Placeholder
            content_type = "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
        else:
            # Default to markdown
            exported_content = content
            content_type = "text/markdown"
        
        response = DocumentationExportResponse(
            content=exported_content,
            format=request.export_format,
            filename=request.filename or f"documentation.{request.export_format}",
            content_type=content_type
        )
        
        logger.info(f"Documentation exported to {request.export_format} successfully")
        return response
        
    except Exception as e:
        logger.error(f"Error exporting documentation: {e}")
        raise HTTPException(
            status_code=500, 
            detail=f"Failed to export documentation: {str(e)}"
        )


@router.post("/generate-bulk")
def generate_bulk_documentation(request: Dict[str, Any]):
    """
    Generate comprehensive documentation for all context files and create a zip package.
    
    This endpoint generates multiple types of documentation (API, README, Architecture)
    for all provided files, creates GUID-prefixed output files, and packages everything
    including source files into a downloadable zip file.
    
    Args:
        request: Bulk documentation generation request with file paths and options
        
    Returns:
        Zip file containing all documentation, source files, and metadata
    """
    logger.info(f"Generating bulk documentation for {len(request.get('file_paths', []))} files")
    
    if not doc_service:
        raise HTTPException(
            status_code=503,
            detail="Documentation service not available"
        )
    
    try:
        # Extract parameters
        file_paths = request.get("file_paths", [])
        include_source_files = request.get("include_source_files", True)
        documentation_types = request.get("documentation_types", ["api", "readme", "architecture"])
        
        if not file_paths:
            raise HTTPException(
                status_code=400,
                detail="No file paths provided"
            )
        
        # Generate session GUID
        session_guid = str(uuid.uuid4())[:8]
        logger.info(f"Starting bulk documentation session {session_guid}")
        
        # Generate documentation for each type
        documentation_results = []
        for doc_type in documentation_types:
            logger.info(f"Generating {doc_type} documentation")
            
            doc_request = DocumentationRequest(
                file_paths=file_paths,
                documentation_type=doc_type,
                output_format="markdown",
                include_examples=True,
                include_diagrams=True,
                target_audience="developers"
            )
            
            result = doc_service.generate_documentation_with_guid(doc_request)
            documentation_results.append(result)
        
        # Create zip file with all documentation and source files
        zip_bytes = doc_service.create_documentation_zip(
            documentation_results=documentation_results,
            file_paths=file_paths,
            session_guid=session_guid,
            include_source_files=include_source_files
        )
        
        # Return zip file for download
        from fastapi.responses import Response
        filename = f"documentation-{session_guid}.zip"
        
        return Response(
            content=zip_bytes,
            media_type="application/zip",
            headers={
                "Content-Disposition": f"attachment; filename={filename}"
            }
        )
        
    except Exception as e:
        logger.error(f"Error generating bulk documentation: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to generate bulk documentation: {str(e)}"
        )


@router.get("/health")
def health_check():
    """
    Health check endpoint for documentation service.
    
    Returns:
        Health status of the documentation service
    """
    return {
        "status": "healthy",
        "service": "documentation",
        "available": doc_service is not None
    }