from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List
from app.services.documentation_service import documentation_service, DocumentationRequest
from fastapi.responses import StreamingResponse
import io

router = APIRouter()

class GenerateDocumentationRequest(BaseModel):
    file_paths: List[str]
    documentation_type: str = "all"
    output_format: str = "markdown"
    include_examples: bool = True
    include_diagrams: bool = True
    target_audience: str = "developers"

@router.post("/generate")
async def generate_documentation(request: GenerateDocumentationRequest):
    """
    Generate documentation for a list of files.
    """
    try:
        doc_request = DocumentationRequest(
            file_paths=request.file_paths,
            documentation_type=request.documentation_type,
            output_format=request.output_format,
            include_examples=request.include_examples,
            include_diagrams=request.include_diagrams,
            target_audience=request.target_audience,
        )
        result = documentation_service.generate_documentation_with_guid(doc_request)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/download/{session_guid}")
async def download_documentation(session_guid: str):
    """
    Download the documentation as a zip file.
    """
    try:
        if session_guid not in documentation_service.cache:
            raise HTTPException(status_code=404, detail="Documentation session not found.")

        documentation_results, file_paths = documentation_service.cache[session_guid]
        
        zip_bytes = documentation_service.create_documentation_zip(
            documentation_results=documentation_results,
            file_paths=file_paths,
            session_guid=session_guid,
            include_source_files=True,
        )
        
        return StreamingResponse(
            io.BytesIO(zip_bytes),
            media_type="application/zip",
            headers={"Content-Disposition": f"attachment; filename={session_guid}-documentation.zip"},
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
