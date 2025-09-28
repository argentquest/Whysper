"""
Settings and configuration management endpoints.

This module handles application settings including:
- Environment variable management
- Theme configuration
- System message management
"""
from fastapi import APIRouter, HTTPException
from app.services.settings_service import settings_service
from app.services.system_service import system_message_service
from schemas import (
    SettingsUpdateRequest,
    ThemeToggleResponse,
    ThemeSetRequest,
    SystemMessageSetRequest,
    SystemMessageUpdateRequest,
)
import markdown2
from common.logger import get_logger

logger = get_logger(__name__)
router = APIRouter()


# ---------------------------------------------------------------------------
# Application Settings
# ---------------------------------------------------------------------------

@router.get("/")
def get_settings():
    """Get current application settings."""
    return settings_service.get_settings()


@router.get("/agent-prompts/{filename}")
def get_agent_prompt(filename: str):
    """Get the content of a specific agent prompt."""
    content = settings_service.get_agent_prompt_content(filename)
    if not content:
        raise HTTPException(status_code=404, detail="Agent prompt not found")
    return {"filename": filename, "content": content}


@router.put("/env")
def update_env(request: SettingsUpdateRequest):
    """Update environment variables and settings."""
    return settings_service.update_env(request.updates)


# ---------------------------------------------------------------------------
# Theme Management
# ---------------------------------------------------------------------------

@router.put("/theme", response_model=ThemeToggleResponse)
def set_theme(request: ThemeSetRequest):
    """Set the application theme."""
    success, theme = settings_service.set_theme(request.theme)
    if success:
        return ThemeToggleResponse(theme=theme, message="Theme updated")
    raise HTTPException(status_code=400, detail="Invalid theme")


@router.post("/theme/toggle", response_model=ThemeToggleResponse)
def toggle_theme():
    """Toggle between light and dark themes."""
    theme, message = settings_service.toggle_theme()
    return ThemeToggleResponse(theme=theme, message=message)


# ---------------------------------------------------------------------------
# System Messages
# ---------------------------------------------------------------------------

@router.get("/system-messages")
def list_system_messages():
    """List all available system messages."""
    return {
        "current": system_message_service.get_current_file(),
        "messages": system_message_service.list_messages(),
    }


@router.get("/system-messages/{filename}")
def get_system_message(filename: str):
    """Get a specific system message by filename."""
    content = system_message_service.load_message(filename)
    if content is None:
        raise HTTPException(status_code=404, detail="System message not found")
    html_content = markdown2.markdown(content)
    return {"filename": filename, "content": content, "htmlContent": html_content}


@router.put("/system-messages/current")
def set_current_system_message(request: SystemMessageSetRequest):
    """Set the current active system message."""
    if not system_message_service.set_current(request.filename):
        raise HTTPException(
            status_code=400,
            detail="Unable to set system message",
        )
    return {"current": request.filename}


@router.post("/system-messages")
def save_system_message(request: SystemMessageUpdateRequest):
    """Create or update a system message."""
    if not system_message_service.save(request.filename, request.content):
        raise HTTPException(
            status_code=400,
            detail="Unable to save system message",
        )
    return {"filename": request.filename}


@router.delete("/system-messages/{filename}")
def delete_system_message(filename: str):
    """Delete a system message."""
    if not system_message_service.delete(filename):
        raise HTTPException(
            status_code=400,
            detail="Unable to delete system message",
        )
    return {"filename": filename, "deleted": True}
