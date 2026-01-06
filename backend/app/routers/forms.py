from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Dict, Any
from app.services.form_service import FormService
from common.logging_decorator import log_method_call

router = APIRouter()


class PublishFormRequest(BaseModel):
    model_config = {"protected_namespaces": ()}

    form_name: str
    form_description: str
    form_type: str
    version: str
    form_schema: Dict[str, Any]
    ui_schema: Dict[str, Any]
    form_data: Dict[str, Any]  # Sample data


class SubmitFormRequest(BaseModel):
    form_id: str
    form_data: Dict[str, Any]
    session_id: str


class EditFormRequest(BaseModel):
    form_id: str
    form_data: Dict[str, Any]
    session_id: str


@router.post("/publish")
@log_method_call
async def publish_form(request: PublishFormRequest):
    """Publish a new form definition"""
    service = FormService()
    try:
        # Map form_schema back to schema for internal storage
        form_data = request.model_dump()
        form_data['schema'] = form_data.pop('form_schema')

        form_id = service.publish_form(form_data)
        return {"form_id": form_id, "message": "Form published successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/published")
@log_method_call
async def get_published_forms():
    """List all published forms with metadata"""
    service = FormService()
    try:
        return service.get_published_forms()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/submit")
@log_method_call
async def submit_form(request: SubmitFormRequest):
    """Submit a form with user data"""
    service = FormService()
    try:
        submission_id = service.submit_form(request.model_dump())
        return {"submission_id": submission_id, "message": "Form submitted successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/submissions")
@log_method_call
async def get_submissions():
    """List all form submissions"""
    service = FormService()
    try:
        return service.get_submissions()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/submissions/{submission_id}")
@log_method_call
async def get_submission(submission_id: str):
    """Get a single submission by ID"""
    service = FormService()
    try:
        return service.get_submission(submission_id)
    except FileNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/edit/{submission_id}")
@log_method_call
async def edit_submission(submission_id: str, request: EditFormRequest):
    """Edit an existing submission (creates new version)"""
    service = FormService()
    try:
        new_submission_id = service.edit_submission(submission_id, request.model_dump())
        return {"submission_id": new_submission_id, "message": "Submission edited successfully"}
    except FileNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/submissions/history/{submission_id}")
@log_method_call
async def get_submission_history(submission_id: str):
    """Get version history for a submission"""
    service = FormService()
    try:
        return service.get_submission_history(submission_id)
    except FileNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
