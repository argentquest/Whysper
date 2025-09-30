"""
Settings and configuration management endpoints.

This module handles application settings including:
- Environment variable management
- Theme configuration
- System message management
"""
from typing import Dict, Any, List
from fastapi import APIRouter, HTTPException
from app.services.settings_service import settings_service
from schemas import (
    SettingsUpdateRequest,
    ThemeToggleResponse,
    ThemeSetRequest,
)
from common.logger import get_logger

logger = get_logger(__name__)
router = APIRouter()


# ---------------------------------------------------------------------------
# Application Settings
# ---------------------------------------------------------------------------

@router.get("/")
def get_settings() -> Dict[str, Any]:
    """
    Retrieve current application settings and configuration.

    Returns the complete set of application settings including environment
    variables, theme preferences, system configuration, and agent prompts.
    Used by the frontend to display and manage user preferences.

    Returns:
        Dict[str, Any]: Complete application settings including:
            - Environment variables and their current values
            - Theme settings (light/dark/auto)
            - System message configurations
            - Available agent prompts and their metadata

    Raises:
        HTTPException: If there are issues accessing configuration data
    """
    logger.debug("get_settings endpoint started")

    try:
        settings_data = settings_service.get_settings()
        logger.debug(f"Retrieved settings with {len(settings_data) if isinstance(settings_data, dict) else 'unknown'} configuration items")
        return settings_data
    except Exception as e:
        logger.error(f"Failed to retrieve settings: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to retrieve settings: {str(e)}")


@router.get("/agent-prompts/{filename}")
def get_agent_prompt(filename: str) -> Dict[str, str]:
    """
    Retrieve the content of a specific agent prompt file.

    Used by the frontend to display and potentially edit agent prompts.
    Agent prompts are predefined instruction sets for different AI agent
    behaviors (coding, debugging, documentation, etc.).

    Args:
        filename: Name of the agent prompt file to retrieve (e.g., 'debugging.md',
                 'code_review.md')

    Returns:
        Dict[str, str]: Dictionary containing:
            - filename: The requested filename
            - content: Full text content of the agent prompt

    Raises:
        HTTPException: If the agent prompt file is not found (404) or
                      if there are issues reading the file (500)
    """
    logger.debug(f"get_agent_prompt endpoint called for file: {filename}")

    try:
        content = settings_service.get_agent_prompt_content(filename)
        if not content:
            logger.warning(f"Agent prompt not found: {filename}")
            raise HTTPException(status_code=404, detail="Agent prompt not found")

        logger.debug(f"Successfully retrieved agent prompt '{filename}' with {len(content)} characters")
        return {"filename": filename, "content": content}

    except HTTPException:
        # Re-raise HTTP exceptions as-is
        raise
    except Exception as e:
        logger.error(f"Failed to retrieve agent prompt '{filename}': {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to retrieve agent prompt: {str(e)}")


@router.put("/env")
def update_env(request: SettingsUpdateRequest) -> Dict[str, Any]:
    """
    Update environment variables and application configuration.

    Allows the frontend to modify environment variables that control
    application behavior. Changes are validated and applied atomically.
    Some changes may require application restart to take effect.

    Args:
        request: SettingsUpdateRequest containing:
            - updates: Dictionary of environment variable key-value pairs to update

    Returns:
        Dict[str, Any]: Update result containing:
            - success: Boolean indicating if update was successful
            - updated: List of environment variables that were updated
            - errors: List of any validation errors that occurred

    Raises:
        HTTPException: If validation fails or update operation encounters errors

    Note:
        Changes to API keys, model configurations, and server settings
        may require application restart.
    """
    logger.debug("update_env endpoint called")

    try:
        update_data = request.updates
        logger.debug(f"Processing {len(update_data) if update_data else 0} environment variable updates")

        result = settings_service.update_env(update_data)
        logger.debug(f"Environment update completed: {len(result.get('updated', []))} variables updated")

        if result.get('errors'):
            logger.warning(f"Environment update had {len(result['errors'])} validation errors")

        return result

    except Exception as e:
        logger.error(f"Failed to update environment variables: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to update environment: {str(e)}")


# ---------------------------------------------------------------------------
# Theme Management
# ---------------------------------------------------------------------------

@router.put("/theme", response_model=ThemeToggleResponse)
def set_theme(request: ThemeSetRequest):
    """
    Set the application theme to a specific value.

    Changes the UI theme for all users of the application. The theme setting
    is persisted and affects all interface elements throughout the application.

    Args:
        request: ThemeSetRequest containing:
            - theme: Theme name ('light', 'dark', or 'auto')

    Returns:
        ThemeToggleResponse: Response containing:
            - theme: The current theme setting
            - message: Confirmation message

    Raises:
        HTTPException: If the requested theme is invalid or unsupported
    """
    logger.debug(f"set_theme endpoint called with theme: {request.theme}")

    try:
        success, theme = settings_service.set_theme(request.theme)
        if success:
            logger.info(f"Theme successfully changed to: {theme}")
            return ThemeToggleResponse(theme=theme, message="Theme updated")
        else:
            logger.warning(f"Failed to set theme to: {request.theme}")
            raise HTTPException(status_code=400, detail="Invalid theme")

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error setting theme to '{request.theme}': {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to set theme: {str(e)}")


@router.post("/theme/toggle", response_model=ThemeToggleResponse)
def toggle_theme():
    """
    Toggle between light and dark themes.

    Switches the theme from the current setting to the opposite mode.
    Light becomes dark, dark becomes light. Auto mode may be affected
    by system preferences.

    Returns:
        ThemeToggleResponse: Response containing:
            - theme: The new theme setting after toggle
            - message: Status message about the theme change

    Raises:
        HTTPException: If theme toggle operation fails
    """
    logger.debug("toggle_theme endpoint called")

    try:
        theme, message = settings_service.toggle_theme()
        logger.info(f"Theme toggled to: {theme}")
        return ThemeToggleResponse(theme=theme, message=message)

    except Exception as e:
        logger.error(f"Error toggling theme: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to toggle theme: {str(e)}")


# ---------------------------------------------------------------------------
# Agents and Subagents
# ---------------------------------------------------------------------------

@router.get("/agents")
def list_agents() -> List[Dict[str, Any]]:
    """List all available agent prompts."""
    logger.debug("list_agents endpoint called")
    result = settings_service.get_agent_prompts()
    logger.debug(f"Returning {len(result)} agent prompts")
    return result


@router.get("/subagents")
def list_subagents() -> List[Dict[str, Any]]:
    """List all available subagent commands."""
    logger.debug("list_subagents endpoint called")
    result = settings_service.get_subagent_commands()
    logger.debug(f"Returning {len(result)} subagent commands")
    return result




