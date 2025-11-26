from fastapi import APIRouter, HTTPException, Body
from fastapi.responses import StreamingResponse
import asyncio
import json
import logging

from app.services.diagram_factory_service import (
    DiagramFactoryService,
    DiagramSessionStore,
    DiagramSession,
)
from common.logging_decorator import log_method_call

logger = logging.getLogger(__name__)
router = APIRouter()


@router.post("/start")
@log_method_call
async def start_diagram_generation(
    initial_prompt: str = Body(..., embed=True),
    diagram_type: str = Body("Mermaid", embed=True),
    model_id: str = Body(None, embed=True),
    session_id: str = Body(None, embed=True),
):
    """
    Initialize a new diagram generation session.

    Args:
        initial_prompt (str): The initial description of the system.
        diagram_type (str): The desired diagram type (default: "Mermaid").
        model_id (str, optional): The AI model ID to use.
        session_id (str, optional): A specific session ID to use (e.g. from frontend).

    Returns:
        dict: Session details including session_id, status, and message.

    Raises:
        HTTPException: If an error occurs during initialization.
    """
    # Initialize a new diagram generation session with optional model selection
    try:
        logger.info(f"🚀 Starting diagram generation with prompt: {initial_prompt[:100]}... (session_id provided: {session_id is not None})")
        # Create a unique session for tracking diagram generation progress
        # If session_id is provided (from frontend tab), use it; otherwise generate a new one
        session = DiagramSessionStore.create_session(session_id=session_id)
        logger.info(f"✅ Session created: {session.session_id}")
        # Instantiate service to manage diagram generation workflow
        service = DiagramFactoryService(session)
        # Pass model_id to the service if provided
        await service.start_generation(initial_prompt, diagram_type, model_id)

        # Return session details for client tracking
        logger.info(f"✅ Diagram generation started for session {session.session_id}")
        return {
            "session_id": session.session_id,
            "status": service.get_status(),
            "message": "Diagram generation started"
        }
    except Exception as e:
        # Log and re-raise any errors during session initialization
        logger.error(f"Error starting diagram generation: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/stream/{session_id}")
@log_method_call
async def stream_diagram_updates(session_id: str):
    """
    Stream real-time updates for a diagram generation session.

    Args:
        session_id (str): The ID of the session to stream updates for.

    Returns:
        StreamingResponse: A Server-Sent Events (SSE) stream of updates.

    Raises:
        HTTPException: If the session is not found.
    """
    # Stream real-time updates for a diagram generation session
    logger.info(f"📡 Received stream request for session: {session_id}")
    session = DiagramSessionStore.get_session(session_id)
    if not session:
        logger.error(f"❌ Session not found: {session_id}")
        raise HTTPException(status_code=404, detail="Session not found")
    logger.info(f"✅ Found session: {session_id}, starting stream...")

    async def event_generator():
        try:
            while True:
                try:
                    # Wait for an update with a short timeout for responsiveness
                    update = await asyncio.wait_for(session.update_queue.get(), timeout=3)
                    # Serialize and yield update as Server-Sent Event
                    yield f"data: {json.dumps(update)}\n\n"

                    # Terminate streaming if generation is complete
                    if update.get("status") in ["completed", "error"]:
                        break

                except asyncio.TimeoutError:
                    # Send periodic "waiting" status to keep client informed
                    waiting_status = {
                        "type": "status",
                        "status": "waiting",
                        "message": "AI is processing your request... (no response yet)",
                        "session_id": session_id,
                    }
                    logger.info(f"[SSE] Sending waiting status for session {session_id}")
                    yield f"data: {json.dumps(waiting_status)}\n\n"
                except asyncio.CancelledError:
                    # Handle potential client disconnection
                    logger.info(f"Client disconnected from stream: {session_id}")
                    break
        except Exception as e:
            # Handle and report any streaming errors
            logger.error(f"Error in event generator: {e}")
            error_data = {"type": "error", "message": str(e)}
            yield f"data: {json.dumps(error_data)}\n\n"

    return StreamingResponse(event_generator(), media_type="text/event-stream")


@router.post("/clarify")
@log_method_call
async def submit_clarification(
    session_id: str = Body(..., embed=True),
    response: str = Body(..., embed=True),
):
    """
    Submit a user response to a clarification question.

    Args:
        session_id (str): The session ID.
        response (str): The user's response to the clarification question.

    Returns:
        dict: The updated session status.

    Raises:
        HTTPException: If the session is not found or an error occurs.
    """
    # Process user's response to a clarification request
    session = DiagramSessionStore.get_session(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

    try:
        # Create service to handle clarification workflow
        service = DiagramFactoryService(session)
        # Process user's clarification response
        await service.handle_clarification(response)
        return service.get_status()
    except Exception as e:
        # Log and handle any clarification processing errors
        logger.error(f"Error handling clarification: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/confirm_ready")
@log_method_call
async def confirm_ready(
    session_id: str = Body(..., embed=True),
):
    """
    Confirm that the user is ready to proceed with diagram generation.

    Args:
        session_id (str): The session ID.

    Returns:
        dict: The updated session status.

    Raises:
        HTTPException: If the session is not found or an error occurs.
    """
    # Confirm user is ready to proceed with diagram generation
    session = DiagramSessionStore.get_session(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

    try:
        # Create service to manage generation workflow
        service = DiagramFactoryService(session)
        # Signal that user has confirmed readiness
        await service.confirm_ready()
        return service.get_status()
    except Exception as e:
        # Log and handle any readiness confirmation errors
        logger.error(f"Error confirming ready: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/select_diagram_type")
@log_method_call
async def select_diagram_type(
    session_id: str = Body(..., embed=True),
    diagram_type: str = Body(..., embed=True),
):
    """
    Select the preferred diagram type for generation.

    Args:
        session_id (str): The session ID.
        diagram_type (str): The selected diagram type (e.g., "Mermaid", "D2").

    Returns:
        dict: The updated session status.

    Raises:
        HTTPException: If the session is not found or an error occurs.
    """
    # Process user's selection of diagram type (Mermaid, D2, PlantUML, Structurizr)
    session = DiagramSessionStore.get_session(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

    try:
        # Create service to handle diagram type selection workflow
        service = DiagramFactoryService(session)
        # Process user's diagram type selection and resume workflow
        await service.select_diagram_type(diagram_type)
        return service.get_status()
    except Exception as e:
        # Log and handle any diagram type selection errors
        logger.error(f"Error selecting diagram type: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/approve_render")
@log_method_call
async def approve_render(
    session_id: str = Body(..., embed=True),
):
    """
    Approve the current diagram for rendering.

    Args:
        session_id (str): The session ID.

    Returns:
        dict: The updated session status.

    Raises:
        HTTPException: If the session is not found or an error occurs.
    """
    # Approve diagram for rendering
    session = DiagramSessionStore.get_session(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

    try:
        # Create service to manage rendering workflow
        service = DiagramFactoryService(session)
        # Signal approval to proceed with rendering
        await service.approve_render()
        return service.get_status()
    except Exception as e:
        # Log and handle any rendering approval errors
        logger.error(f"Error approving render: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/render")
@log_method_call
async def render_diagram(
    session_id: str = Body(..., embed=True),
    code: str = Body(None, embed=True),
):
    """
    Render a diagram from the session's code or provided code.

    Args:
        session_id (str): The session ID.
        code (str, optional): Custom diagram code to render. If not provided, uses session code.

    Returns:
        dict: The updated session status.

    Raises:
        HTTPException: If the session is not found or an error occurs.
    """
    # Render a diagram from session or provided code
    session = DiagramSessionStore.get_session(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

    try:
        # Create service to manage rendering process
        service = DiagramFactoryService(session)
        # Render diagram with optional custom code
        await service.render_diagram(code)
        return service.get_status()
    except Exception as e:
        # Log and handle any rendering errors
        logger.error(f"Error rendering diagram: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{session_id}")
@log_method_call
async def get_diagram_status(session_id: str):
    """
    Get the current status of a diagram generation session.

    Args:
        session_id (str): The session ID.

    Returns:
        dict: The current session status.

    Raises:
        HTTPException: If the session is not found or an error occurs.
    """
    # Retrieve the current status of a diagram generation session
    session = DiagramSessionStore.get_session(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

    try:
        # Create service to fetch session status
        service = DiagramFactoryService(session)
        return service.get_status()
    except Exception as e:
        # Log and handle any status retrieval errors
        logger.error(f"Error getting status: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/{session_id}")
@log_method_call
async def delete_session(session_id: str):
    """
    Delete a diagram generation session.

    Args:
        session_id (str): The session ID to delete.

    Returns:
        dict: A confirmation message.

    Raises:
        HTTPException: If the session is not found or an error occurs.
    """
    # Delete a specific diagram generation session
    session = DiagramSessionStore.get_session(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

    try:
        # Remove session from session store
        DiagramSessionStore.delete_session(session_id)
        return {"message": f"Session {session_id} deleted"}
    except Exception as e:
        # Log and handle any session deletion errors
        logger.error(f"Error deleting session: {e}")
        raise HTTPException(status_code=500, detail=str(e))
