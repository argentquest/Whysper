from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
import os

router = APIRouter()

class VerifyAccessKeyRequest(BaseModel):
    access_key: str

@router.post("/verify")
async def verify_access_key(request: VerifyAccessKeyRequest):
    """
    Verify the access key.
    """
    correct_key = os.getenv("ACCESS_KEY")
    if not correct_key:
        raise HTTPException(status_code=500, detail="Access key not configured on the server.")

    if request.access_key == correct_key:
        return {"success": True}
    else:
        raise HTTPException(status_code=401, detail="Invalid access key.")
