"""
Diagram Event Logging Endpoint

This endpoint receives diagram detection and rendering events from the frontend
and logs them to the backend structured logs for monitoring and debugging.
"""

from fastapi import APIRouter
from pydantic import BaseModel
from typing import Literal, Optional
from common.logger import get_logger

router = APIRouter()
logger = get_logger(__name__)


class DiagramEventRequest(BaseModel):
    """Request model for diagram event logging"""
    event_type: Literal['detection', 'render_start', 'render_success', 'render_error']
    diagram_type: Literal['mermaid', 'd2', 'c4']
    code_preview: Optional[str] = None
    code_length: Optional[int] = None
    error_message: Optional[str] = None
    detection_method: Optional[str] = None  # e.g., 'language_marker', 'syntax_pattern', 'c4_keyword:C4Context'
    conversation_id: Optional[str] = None


@router.post("/log-diagram-event")
async def log_diagram_event(event: DiagramEventRequest):
    """
    Log diagram detection and rendering events from frontend

    This endpoint allows the frontend to send diagram-related events
    to be logged in the backend structured logs for debugging and monitoring.
    """

    # Build log message based on event type
    if event.event_type == 'detection':
        message = f"🔍 Diagram detected: {event.diagram_type.upper()}"
        logger.info(
            message,
            extra={
                'diagram_type': event.diagram_type,
                'detection_method': event.detection_method,
                'code_length': event.code_length,
                'code_preview': event.code_preview,
                'conversation_id': event.conversation_id
            }
        )

    elif event.event_type == 'render_start':
        message = f"🎨 Rendering {event.diagram_type.upper()} diagram..."
        logger.info(
            message,
            extra={
                'diagram_type': event.diagram_type,
                'code_length': event.code_length,
                'conversation_id': event.conversation_id
            }
        )

    elif event.event_type == 'render_success':
        message = f"✅ Successfully rendered {event.diagram_type.upper()} diagram"
        logger.info(
            message,
            extra={
                'diagram_type': event.diagram_type,
                'code_length': event.code_length,
                'conversation_id': event.conversation_id
            }
        )

    elif event.event_type == 'render_error':
        # Include error message in main log message for visibility
        error_detail = f": {event.error_message}" if event.error_message else ""
        message = f"❌ Error rendering {event.diagram_type.upper()} diagram{error_detail}"
        logger.error(
            message,
            extra={
                'diagram_type': event.diagram_type,
                'error_message': event.error_message,
                'code_length': event.code_length,
                'code_preview': event.code_preview,
                'conversation_id': event.conversation_id
            }
        )

    return {
        "status": "logged",
        "event_type": event.event_type,
        "diagram_type": event.diagram_type
    }


@router.get("/health")
async def health_check():
    """Health check endpoint for diagram event logging service"""
    return {"status": "healthy", "service": "diagram_events"}
