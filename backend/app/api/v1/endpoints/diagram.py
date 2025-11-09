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

logger = logging.getLogger(__name__)
router = APIRouter()


@router.post("/diagram/start")
async def start_diagram_generation(
    initial_prompt: str = Body(..., embed=True),
    diagram_type: str = Body("Mermaid", embed=True),
):
    """
    Starts a new diagram generation session.
    
    Returns:
        - session_id: Unique session identifier
        - status: Initial session status
    """
    try:
        session = DiagramSessionStore.create_session()
        service = DiagramFactoryService(session)
        await service.start_generation(initial_prompt, diagram_type)
        
        return {
            "session_id": session.session_id,
            "status": service.get_status(),
            "message": "Diagram generation started"
        }
    except Exception as e:
        logger.error(f"Error starting diagram generation: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/diagram/stream/{session_id}")
async def stream_diagram_updates(session_id: str):
    """
    Streams real-time updates for a diagram generation session via Server-Sent Events.
    """
    session = DiagramSessionStore.get_session(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

    async def event_generator():
        try:
            while True:
                try:
                    # Wait for an update from the service with 30 second timeout
                    update = await asyncio.wait_for(session.update_queue.get(), timeout=30)
                    # Serialize to JSON
                    yield f"data: {json.dumps(update)}\n\n"

                    # Check if generation is complete
                    if update.get("status") in ["completed", "error"]:
                        break

                except asyncio.TimeoutError:
                    # Send keep-alive message
                    yield 'data: {"type": "keep-alive"}\n\n'
                except asyncio.CancelledError:
                    # Handle client disconnection
                    logger.info(f"Client disconnected from stream: {session_id}")
                    break
        except Exception as e:
            logger.error(f"Error in event generator: {e}")
            error_data = {"type": "error", "message": str(e)}
            yield f"data: {json.dumps(error_data)}\n\n"

    return StreamingResponse(event_generator(), media_type="text/event-stream")


@router.post("/diagram/clarify")
async def submit_clarification(
    session_id: str = Body(..., embed=True),
    response: str = Body(..., embed=True),
):
    """
    Submits a response to a clarification question.
    
    Args:
        session_id: The session to respond to
        response: User's response to the clarification
    """
    session = DiagramSessionStore.get_session(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

    try:
        service = DiagramFactoryService(session)
        await service.handle_clarification(response)
        return service.get_status()
    except Exception as e:
        logger.error(f"Error handling clarification: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/diagram/render")
async def render_diagram(
    session_id: str = Body(..., embed=True),
    code: str = Body(None, embed=True),
):
    """
    Renders a diagram from the provided code or the code in the session.
    
    Args:
        session_id: The session to render for
        code: Optional custom diagram code to render
    """
    session = DiagramSessionStore.get_session(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

    try:
        service = DiagramFactoryService(session)
        await service.render_diagram(code)
        return service.get_status()
    except Exception as e:
        logger.error(f"Error rendering diagram: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/diagram/{session_id}")
async def get_diagram_status(session_id: str):
    """
    Gets the current status of a diagram generation session.
    
    Args:
        session_id: The session ID
        
    Returns:
        Current session status including code, SVG output, and errors
    """
    session = DiagramSessionStore.get_session(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

    try:
        service = DiagramFactoryService(session)
        return service.get_status()
    except Exception as e:
        logger.error(f"Error getting status: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/diagram/{session_id}")
async def delete_session(session_id: str):
    """
    Deletes a diagram generation session.
    
    Args:
        session_id: The session to delete
    """
    session = DiagramSessionStore.get_session(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

    try:
        DiagramSessionStore.delete_session(session_id)
        return {"message": f"Session {session_id} deleted"}
    except Exception as e:
        logger.error(f"Error deleting session: {e}")
        raise HTTPException(status_code=500, detail=str(e))
