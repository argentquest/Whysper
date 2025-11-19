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
from common.logging_decorator import log_method_call

# Configure logger for tracking diagram events
logger = logging.getLogger(__name__)

# Create API router for diagram logging endpoints
router = APIRouter()


class DiagramEventPayload(BaseModel):
    """Event payload structure for diagram operations"""
    event_type: str  # Track type of diagram event
    diagram_type: str  # Specify diagram rendering technology
    code_length: Optional[int] = None  # Track complexity of diagram code
    code_preview: Optional[str] = None  # Capture preview of diagram code
    provider: Optional[str] = None  # Log rendering service/provider
    render_time: Optional[float] = None  # Measure rendering performance
    error_message: Optional[str] = None  # Capture any rendering errors
    validation_errors: Optional[list] = None  # Store validation issue details
    detection_method: Optional[str] = None  # Track how diagram was processed
    extra_data: Optional[Dict[str, Any]] = None  # Flexible additional metadata


@router.post(
    "/log-diagram-event",
    tags=["diagrams", "logging"],
    summary="Log a diagram event",
    description="Log diagram-related events for debugging and analytics"
)
@log_method_call
def log_diagram_event(event: DiagramEventPayload):
    """
    Log a diagram event from the frontend.

    This endpoint captures diagram rendering, validation, and error events
    for debugging and analytics purposes.
    """
    try:
        # Construct a comprehensive log message with key event details
        log_message = f"[{event.event_type.upper()}] {event.diagram_type} diagram"

        # Optionally append code length to provide context
        if event.code_length:
            log_message += f" ({event.code_length} chars)"

        # Include rendering provider if available
        if event.provider:
            log_message += f" via {event.provider}"

        # Add rendering performance timing
        if event.render_time:
            log_message += f" in {event.render_time:.3f}s"

        # Log errors as warnings, successful events as info
        if event.error_message:
            logger.warning(f"{log_message}: {event.error_message}")
        else:
            logger.info(log_message)

        # Log any supplementary event data for detailed tracking
        if event.extra_data:
            logger.debug(f"Event extra data: {event.extra_data}")

        # Return success response with key event metadata
        return {
            "success": True,
            "message": "Event logged successfully",
            "event_type": event.event_type,
            "diagram_type": event.diagram_type
        }

    except Exception as e:
        # Catch and log any unexpected errors during event logging
        logger.error(f"Error logging diagram event: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to log event: {str(e)}"
        )
