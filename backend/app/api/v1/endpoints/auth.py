from fastapi import APIRouter, HTTPException
from common.logging_decorator import log_method_call
from pydantic import BaseModel
import os

router = APIRouter()

# Pydantic model to define the structure of the access key verification request
class VerifyAccessKeyRequest(BaseModel):
    access_key: str

class VerifyAccessKeyResponse(BaseModel):
    success: bool
    auth_disabled: bool

class CheckAuthResponse(BaseModel):
    auth_required: bool
    auth_disabled: bool

@router.post(
    "/verify",
    response_model=VerifyAccessKeyResponse,
    summary="Verify access key",
    description="Verify the provided access key against the environment configuration."
)
@log_method_call
async def verify_access_key(request: VerifyAccessKeyRequest):
    """
    Verify the provided access key.

    Args:
        request (VerifyAccessKeyRequest): The request containing the access key.

    Returns:
        VerifyAccessKeyResponse: The verification result.

    Raises:
        HTTPException: If the key is invalid (401).
    """
    # Retrieve the correct access key from environment variables, stripping whitespace
    correct_key = os.getenv("ACCESS_KEY", "").strip()

    # If ACCESS_KEY is blank or not set, authentication is disabled - allow all
    if not correct_key:
        return {"success": True, "auth_disabled": True}

    # Compare the provided access key with the correct key
    if request.access_key == correct_key:
        return {"success": True, "auth_disabled": False}
    else:
        # Raise an HTTP 401 Unauthorized exception if the key is invalid
        raise HTTPException(status_code=401, detail="Invalid access key.")

@router.get(
    "/check",
    response_model=CheckAuthResponse,
    summary="Check auth requirements",
    description="Check if authentication is required by the server."
)
@log_method_call
async def check_auth_required():
    """
    Check if authentication is required.

    Returns:
        CheckAuthResponse: Flags indicating if auth is required or disabled.
    """
    # Retrieve the access key from environment variables
    correct_key = os.getenv("ACCESS_KEY", "").strip()
    
    # Return boolean flags indicating authentication requirements
    return {
        "auth_required": bool(correct_key),  # True if a key is set
        "auth_disabled": not bool(correct_key)  # True if no key is set
    }
