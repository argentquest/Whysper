"""
Shell WebSocket endpoints for Whysper Web2 Backend.

This module provides real-time shell access via WebSocket connections.
It handles command execution, output streaming, and session management
with proper security controls and cleanup.

WebSocket Protocol:
- Client sends: {"type": "command", "data": "ls -la"}
- Server sends: {"type": "output", "stream": "stdout", "data": "file listing..."}
- Server sends: {"type": "status", "data": "completed"}
"""
import asyncio
import json
from typing import Dict, Any
from fastapi import APIRouter, WebSocket, WebSocketDisconnect, HTTPException, Depends
from fastapi.responses import JSONResponse
from app.services.shell_service import shell_service, CommandStatus
from common.logger import get_logger

logger = get_logger(__name__)
router = APIRouter()

class WebSocketManager:
    """Manages WebSocket connections for shell sessions."""
    
    def __init__(self):
        # Maps session_id to WebSocket connection
        self.connections: Dict[str, WebSocket] = {}
    
    async def connect(self, websocket: WebSocket, session_id: str):
        """Accept a WebSocket connection and associate it with a session."""
        await websocket.accept()
        self.connections[session_id] = websocket
        logger.info(f"WebSocket connected for session {session_id}")
    
    def disconnect(self, session_id: str):
        """Remove WebSocket connection for a session."""
        if session_id in self.connections:
            del self.connections[session_id]
            logger.info(f"WebSocket disconnected for session {session_id}")
    
    async def send_message(self, session_id: str, message: Dict[str, Any]):
        """Send a message to the WebSocket for a session."""
        if session_id in self.connections:
            try:
                await self.connections[session_id].send_text(json.dumps(message))
            except Exception as e:
                logger.error(f"Error sending message to session {session_id}: {e}")
                self.disconnect(session_id)

# Global WebSocket manager
ws_manager = WebSocketManager()

@router.websocket("/ws/{session_id}")
async def shell_websocket(websocket: WebSocket, session_id: str):
    """
    WebSocket endpoint for shell interaction.
    
    Protocol:
    - Client connects with session_id
    - Client sends commands as JSON: {"type": "command", "data": "ls -la"}
    - Server streams output as JSON: {"type": "output", "stream": "stdout", "data": "..."}
    - Server sends status updates: {"type": "status", "data": "completed"}
    """
    # Verify session exists
    session_info = shell_service.get_session_info(session_id)
    if not session_info:
        await websocket.close(code=4004, reason="Session not found")
        return
    
    await ws_manager.connect(websocket, session_id)
    
    # Send welcome message
    await ws_manager.send_message(session_id, {
        "type": "status",
        "data": "connected",
        "session_info": session_info
    })
    
    try:
        while True:
            # Receive message from client
            data = await websocket.receive_text()
            
            try:
                message = json.loads(data)
                message_type = message.get("type")
                
                if message_type == "command":
                    command = message.get("data", "").strip()
                    if not command:
                        await ws_manager.send_message(session_id, {
                            "type": "error",
                            "data": "Empty command"
                        })
                        continue
                    
                    # Echo the command back to client
                    await ws_manager.send_message(session_id, {
                        "type": "echo",
                        "data": command
                    })
                    
                    # Define output callback for streaming
                    async def output_callback(data: str, stream_type: str):
                        await ws_manager.send_message(session_id, {
                            "type": "output",
                            "stream": stream_type,
                            "data": data
                        })
                    
                    # Execute command
                    status = await shell_service.execute_command(
                        session_id, 
                        command, 
                        output_callback
                    )
                    
                    # Send completion status
                    await ws_manager.send_message(session_id, {
                        "type": "status",
                        "data": status.value
                    })
                
                elif message_type == "ping":
                    # Handle ping for keepalive
                    await ws_manager.send_message(session_id, {
                        "type": "pong",
                        "data": message.get("data", "")
                    })
                
                else:
                    await ws_manager.send_message(session_id, {
                        "type": "error",
                        "data": f"Unknown message type: {message_type}"
                    })
                    
            except json.JSONDecodeError:
                await ws_manager.send_message(session_id, {
                    "type": "error",
                    "data": "Invalid JSON message"
                })
            except Exception as e:
                logger.error(f"Error processing message in session {session_id}: {e}")
                await ws_manager.send_message(session_id, {
                    "type": "error",
                    "data": f"Error processing message: {str(e)}"
                })
    
    except WebSocketDisconnect:
        logger.info(f"WebSocket disconnected for session {session_id}")
    except Exception as e:
        logger.error(f"WebSocket error for session {session_id}: {e}")
    finally:
        ws_manager.disconnect(session_id)

@router.post("/sessions")
async def create_shell_session(working_directory: str = None, shell_type: str = "auto"):
    """
    Create a new shell session.
    
    Args:
        working_directory: Optional working directory for the session
        shell_type: Shell type ("auto", "cmd", "powershell", "bash")
    
    Returns:
        dict: Session information including session_id
    """
    try:
        session_id = await shell_service.create_session(working_directory, shell_type)
        session_info = shell_service.get_session_info(session_id)
        
        return {
            "success": True,
            "data": {
                "session_id": session_id,
                "session_info": session_info
            }
        }
    except Exception as e:
        logger.error(f"Error creating shell session: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/sessions")
async def list_shell_sessions():
    """
    List all active shell sessions.
    
    Returns:
        dict: List of all active sessions
    """
    try:
        sessions = shell_service.list_sessions()
        return {
            "success": True,
            "data": sessions
        }
    except Exception as e:
        logger.error(f"Error listing shell sessions: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/sessions/{session_id}")
async def get_shell_session(session_id: str):
    """
    Get information about a specific shell session.
    
    Args:
        session_id: Session identifier
    
    Returns:
        dict: Session information
    """
    session_info = shell_service.get_session_info(session_id)
    if not session_info:
        raise HTTPException(status_code=404, detail="Session not found")
    
    return {
        "success": True,
        "data": session_info
    }

@router.delete("/sessions/{session_id}")
async def close_shell_session(session_id: str):
    """
    Close and clean up a shell session.
    
    Args:
        session_id: Session identifier
    
    Returns:
        dict: Success status
    """
    try:
        success = await shell_service.close_session(session_id)
        if not success:
            raise HTTPException(status_code=404, detail="Session not found")
        
        # Disconnect WebSocket if connected
        ws_manager.disconnect(session_id)
        
        return {
            "success": True,
            "message": "Session closed successfully"
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error closing shell session {session_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/security/allowed-commands")
async def get_allowed_commands():
    """
    Get list of explicitly allowed commands.
    
    Returns:
        dict: List of allowed commands and security info
    """
    from app.services.shell_service import ShellSecurityManager
    
    return {
        "success": True,
        "data": {
            "allowed_commands": list(ShellSecurityManager.ALLOWED_COMMANDS),
            "blocked_commands": list(ShellSecurityManager.BLOCKED_COMMANDS),
            "dangerous_patterns": list(ShellSecurityManager.DANGEROUS_PATTERNS)
        }
    }

@router.post("/security/validate-command")
async def validate_command(command: str):
    """
    Validate if a command is safe to execute.
    
    Args:
        command: Command to validate
    
    Returns:
        dict: Validation result with safety status and reason
    """
    try:
        from app.services.shell_service import ShellSecurityManager
        
        is_safe, reason = ShellSecurityManager.is_command_safe(command)
        
        return {
            "success": True,
            "data": {
                "command": command,
                "is_safe": is_safe,
                "reason": reason
            }
        }
    except Exception as e:
        logger.error(f"Error validating command: {e}")
        raise HTTPException(status_code=500, detail=str(e))