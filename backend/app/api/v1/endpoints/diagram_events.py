"""
Diagram Event Logging Endpoints

Simple event logging for diagram rendering, validation, and other operations.
Used by the frontend to track diagram-related events for debugging and analytics.

Endpoints:
- POST /diagrams/log-diagram-event - Log a diagram event
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional, Any, Dict
import logging

logger = logging.getLogger(__name__)

router = APIRouter()


class DiagramEventPayload(BaseModel):
    """Event payload structure for diagram operations"""
    event_type: str  # render_start, render_success, render_error, validate_start, etc.
    diagram_type: str  # mermaid, d2, c4
    code_length: Optional[int] = None
    code_preview: Optional[str] = None
    provider: Optional[str] = None
    render_time: Optional[float] = None
    error_message: Optional[str] = None
    validation_errors: Optional[list] = None
    detection_method: Optional[str] = None
    extra_data: Optional[Dict[str, Any]] = None


@router.post(
    "/log-diagram-event",
    tags=["diagrams", "logging"],
    summary="Log a diagram event",
    description="Log diagram-related events for debugging and analytics"
)
def log_diagram_event(event: DiagramEventPayload):
    """
    Log a diagram event from the frontend.

    This endpoint captures diagram rendering, validation, and error events
    for debugging and analytics purposes.

    Args:
        event: The event payload containing event details

    Returns:
        Success response with event ID
    """
    try:
        # Log the event with appropriate level
        log_message = f"[{event.event_type.upper()}] {event.diagram_type} diagram"

        if event.code_length:
            log_message += f" ({event.code_length} chars)"

        if event.provider:
            log_message += f" via {event.provider}"

        if event.render_time:
            log_message += f" in {event.render_time:.3f}s"

        if event.error_message:
            logger.warning(f"{log_message}: {event.error_message}")
        else:
            logger.info(log_message)

        # Log additional data if provided
        if event.extra_data:
            logger.debug(f"Event extra data: {event.extra_data}")

        return {
            "success": True,
            "message": "Event logged successfully",
            "event_type": event.event_type,
            "diagram_type": event.diagram_type
        }

    except Exception as e:
        logger.error(f"Error logging diagram event: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to log event: {str(e)}"
        )
