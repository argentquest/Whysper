import os
import time
from fastapi import APIRouter, UploadFile, File, HTTPException, status
from pydantic import BaseModel
from app.services.image_analysis_service import ImageAnalysisService
from app.core.config import settings
from common.logger import get_logger

router = APIRouter()
logger = get_logger(__name__)

class ImageAnalysisResponse(BaseModel):
    description: str

@router.post("/analyze", response_model=ImageAnalysisResponse)
async def analyze_image(file: UploadFile = File(...)):
    """
    Upload an infrastructure diagram image and get a text description 
    of its architecture components and flows.
    """
    if not file.content_type.startswith("image/"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="File must be an image"
        )
    
    try:
        contents = await file.read()
        
        # Save file to history directory
        timestamp = time.strftime("%Y%m%d-%H%M%S")
        filename = f"{timestamp}_{file.filename}"
        history_path = os.path.join(settings.history_dir, "uploads")
        os.makedirs(history_path, exist_ok=True)
        file_path = os.path.join(history_path, filename)
        
        with open(file_path, "wb") as f:
            f.write(contents)
            
        logger.info(f"Saved uploaded image to {file_path}")

        description = await ImageAnalysisService.analyze_infra_image(contents, file.content_type)
        return ImageAnalysisResponse(description=description)
    except Exception as e:
        logger.error(f"Failed to analyze image: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to analyze image: {str(e)}"
        )
