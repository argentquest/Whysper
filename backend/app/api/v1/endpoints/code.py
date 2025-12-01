"""
Code extraction endpoints.

This module handles code block extraction from AI responses,
supporting both direct content extraction and conversation history lookup.
"""
from fastapi import APIRouter, HTTPException
from typing import Dict, Any, List, Optional
from app.utils.code_extraction import (
    extract_code_blocks_from_content,
    find_message_content
)
from app.services.conversation_service import conversation_manager
from common.logger import get_logger
from common.logging_decorator import log_method_call
from schemas import CodeExtractionRequest, CodeExtractionResponse

logger = get_logger(__name__)
router = APIRouter()


@router.post(
    "/extract",
    response_model=CodeExtractionResponse,
    summary="Extract code blocks",
    description="Extract code blocks from a message content or by message ID."
)
@log_method_call
def extract_code_blocks(request: CodeExtractionRequest):
    """
    Extract code blocks from a message content or by message ID.

    Args:
        request (CodeExtractionRequest): The request containing messageId and optional content.

    Returns:
        CodeExtractionResponse: The extracted code blocks.

    Raises:
        HTTPException: If messageId is missing or extraction fails.
    """
    # Start logging the method call for debugging purposes
    logger.debug("extract_code_blocks endpoint started")

    # Extract messageId and content from the incoming request
    message_id = request.messageId
    message_content = request.content
    
    # Validate that messageId is provided, raising an error if missing
    if not message_id:
        raise HTTPException(status_code=400, detail="messageId is required")
    
    try:
        # Attempt to find message content if not directly provided
        # This allows searching through conversation history
        if not message_content:
            message_content = find_message_content(message_id, conversation_manager)
        
        # Return empty result if no content is found
        if not message_content:
            return {
                "success": True,
                "data": [],
                "message": "No content found for message"
            }
        
        # Extract code blocks using a specialized utility function
        # This handles different code block formats like Markdown and HTML
        code_blocks = extract_code_blocks_from_content(message_content, message_id)
        
        # Log the number of extracted code blocks for monitoring
        logger.info(f"Extracted {len(code_blocks)} code blocks from message {message_id}")
        
        # Return successful response with extracted code blocks
        return {
            "success": True,
            "data": code_blocks,
            "message": f"Successfully extracted {len(code_blocks)} code blocks"
        }
        
    except Exception as e:
        # Log and re-raise any unexpected errors to provide detailed error information
        logger.info(f"Error extracting code blocks: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to extract code blocks: {str(e)}"
        )
