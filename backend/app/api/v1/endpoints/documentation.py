```python
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List
from app.services.documentation_service import documentation_service, DocumentationRequest
from common.logging_decorator import log_method_call
from fastapi.responses import StreamingResponse
import io

# Create a FastAPI router for documentation-related endpoints
router = APIRouter()

# Define a Pydantic model for documentation generation request
# Provides type hints and validation for input parameters
class GenerateDocumentationRequest(BaseModel):
    file_paths: List[str]
    documentation_type: str = "all"
    output_format: str = "markdown"
    include_examples: bool = True
    include_diagrams: bool = True
    target_audience: str = "developers"

@router.post("/generate")
@log_method_call
async def generate_documentation(request: GenerateDocumentationRequest):
    # Convert the incoming request to a documentation service request
    # This allows standardized processing across different service layers
    try:
        doc_request = DocumentationRequest(
            file_paths=request.file_paths,
            documentation_type=request.documentation_type,
            output_format=request.output_format,
            include_examples=request.include_examples,
            include_diagrams=request.include_diagrams,
            target_audience=request.target_audience,
        )
        
        # Generate documentation and return the result
        # Uses a service method that caches the results with a GUID
        result = documentation_service.generate_documentation_with_guid(doc_request)
        return result
    except Exception as e:
        # Catch and convert any errors to an HTTP 500 server error
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/download/{session_guid}")
@log_method_call
async def download_documentation(session_guid: str):
    # Retrieve and download documentation for a specific session
    # Uses the session GUID to fetch cached documentation results
    try:
        # Check if the session exists in the cache
        if session_guid not in documentation_service.cache:
            raise HTTPException(status_code=404, detail="Documentation session not found.")

        # Retrieve cached documentation and file paths
        documentation_results, file_paths = documentation_service.cache[session_guid]
        
        # Create a zip file of the documentation
        # Includes option to include source files
        zip_bytes = documentation_service.create_documentation_zip(
            documentation_results=documentation_results,
            file_paths=file_paths,
            session_guid=session_guid,
            include_source_files=True,
        )
        
        # Stream the zip file as a downloadable response
        # Sets appropriate headers for file download
        return StreamingResponse(
            io.BytesIO(zip_bytes),
            media_type="application/zip",
            headers={"Content-Disposition": f"attachment; filename={session_guid}-documentation.zip"},
        )
    except Exception as e:
        # Catch and convert any errors to an HTTP 500 server error
        raise HTTPException(status_code=500, detail=str(e))