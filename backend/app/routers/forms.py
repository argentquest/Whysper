from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Dict, Any
from app.services.form_service import FormService

router = APIRouter()

class PublishFormRequest(BaseModel):
    form_name: str
    form_description: str
    form_type: str
    version: str
    schema: Dict[str, Any]
    ui_schema: Dict[str, Any]
    form_data: Dict[str, Any]  # Sample data

@router.post("/publish")
async def publish_form(request: PublishFormRequest):
    """Publish a new form definition"""
    service = FormService()
    try:
        form_id = service.publish_form(request.model_dump())
        return {"form_id": form_id, "message": "Form published successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/published")
async def get_published_forms():
    """List all published forms with metadata"""
    service = FormService()
    try:
        return service.get_published_forms()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
