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

logger = get_logger(__name__)
router = APIRouter()


@router.post("/extract")
def extract_code_blocks(request: dict) -> Dict[str, Any]:
    logger.debug("extract_code_blocks endpoint started")
    """
    Extract code blocks from a message with real parsing.
    
    This endpoint extracts code blocks from text content using regex patterns
    that match the web1 implementation exactly. It supports both Markdown
    fenced code blocks and HTML code elements as fallback.
    
    Request format:
    {
        "messageId": "unique-message-id",
        "content": "optional-direct-content"
    }
    
    If content is not provided, the endpoint will attempt to find the message
    in the conversation history using the messageId.
    """
    message_id = request.get("messageId")
    message_content = request.get("content")
    
    if not message_id:
        raise HTTPException(status_code=400, detail="messageId is required")
    
    try:
        # If content is provided, use it directly; otherwise try to find the message
        if not message_content:
            message_content = find_message_content(message_id, conversation_manager)
        
        if not message_content:
            return {
                "success": True,
                "data": [],
                "message": "No content found for message"
            }
        
        # Extract code blocks using the utility function
        code_blocks = extract_code_blocks_from_content(message_content, message_id)
        
        logger.info(f"Extracted {len(code_blocks)} code blocks from message {message_id}")
        
        return {
            "success": True,
            "data": code_blocks,
            "message": f"Successfully extracted {len(code_blocks)} code blocks"
        }
        
    except Exception as e:
        logger.error(f"Error extracting code blocks: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to extract code blocks: {str(e)}"
        )
