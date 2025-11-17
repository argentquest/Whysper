from fastapi import APIRouter, HTTPException
from common.logging_decorator import log_method_call
from pydantic import BaseModel
import os

router = APIRouter()

class VerifyAccessKeyRequest(BaseModel):
    access_key: str

@router.post("/verify")
@log_method_call
async def verify_access_key(request: VerifyAccessKeyRequest):
    """
    Verify the access key.
    If ACCESS_KEY is not configured (blank), authentication is disabled.
    """
    correct_key = os.getenv("ACCESS_KEY", "").strip()

    # If ACCESS_KEY is blank or not set, authentication is disabled - allow all
    if not correct_key:
        return {"success": True, "auth_disabled": True}

    if request.access_key == correct_key:
        return {"success": True, "auth_disabled": False}
    else:
        raise HTTPException(status_code=401, detail="Invalid access key.")

@router.get("/check")
@log_method_call
async def check_auth_required():
    """
    Check if authentication is required.
    Returns whether ACCESS_KEY is configured.
    """
    correct_key = os.getenv("ACCESS_KEY", "").strip()
    return {
        "auth_required": bool(correct_key),
        "auth_disabled": not bool(correct_key)
    }
