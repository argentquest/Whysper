from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Dict, Any
from app.services.form_submission_service import FormSubmissionService

router = APIRouter()

class SubmitFormRequest(BaseModel):
    form_id: str
    form_data: Dict[str, Any]
    session_id: str

@router.post("/submit")
async def submit_form(request: SubmitFormRequest):
    """Submit a new filled form"""
    service = FormSubmissionService()
    try:
        submission_id = service.submit_form(request.dict())
        return {"submission_id": submission_id, "message": "Form submitted successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.put("/edit/{submission_id}")
async def edit_form_submission(submission_id: str, request: SubmitFormRequest):
    """Edit an existing form submission (creates new version)"""
    service = FormSubmissionService()
    try:
        new_submission_id = service.edit_form_submission(submission_id, request.dict())
        return {"submission_id": new_submission_id, "message": "Form updated successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/submissions")
async def get_form_submissions():
    """List all form submissions with metadata"""
    service = FormSubmissionService()
    try:
        return service.get_all_submissions()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/submissions/{submission_id}")
async def get_form_submission(submission_id: str):
    """Get specific form submission"""
    service = FormSubmissionService()
    return service.get_submission(submission_id)
