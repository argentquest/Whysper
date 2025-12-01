"""Environment and theme helpers for the web backend."""

from __future__ import annotations

import os
import json
from typing import Dict, Tuple, List, Any, Optional

from common.env_manager import env_manager
from common.logger import get_logger
from common.logging_decorator import log_method_call
from security_utils import SecurityUtils
from .theme_service import theme_manager

logger = get_logger(__name__)


class SettingsService:
    """
    Manages application settings, environment variables, theme preferences,
    agent prompts, and subagent commands for the web backend.
    """

    @log_method_call
    def get_settings(self) -> Dict[str, Any]:
        """
        Retrieve current application settings and configuration.

        Returns:
            Dict[str, Any]: A dictionary containing:
                - values: Current environment variables.
                - masked: Environment variables with sensitive keys masked.
                - descriptions: Descriptions for environment variables.
                - theme: Current active theme.
                - availableThemes: List of available themes.
                - timeout: Frontend timeout value.
                - activeBrand: Active brand code.
        """
        env_vars = env_manager.load_env_file()
        masked = {key: SecurityUtils.mask_api_key(value) if "KEY" in key else value for key, value in env_vars.items()}

        # Get frontend timeout (default to 120 seconds if not set)
        frontend_timeout = int(env_vars.get("FRONT_END_TIMEOUT", "120"))

        # Get active brand (default to WF if not set)
        active_brand = env_vars.get("ACTIVE_BRAND", "WF")

        return {
            "values": env_vars,
            "masked": masked,
            "descriptions": env_manager.get_env_descriptions(),
            "theme": theme_manager.current_theme_name,
            "availableThemes": theme_manager.get_available_themes(),
            "timeout": frontend_timeout,  # Add timeout to settings response
            "activeBrand": active_brand,  # Active brand for frontend branding
        }

    @log_method_call
    def _parse_yaml_frontmatter(self, content: str) -> Optional[Dict[str, Any]]:
        """
        Parse YAML frontmatter from markdown content.

        Args:
            content: The markdown content string.

        Returns:
            Optional[Dict[str, Any]]: Parsed metadata dictionary or None if no frontmatter found.
        """
        if not content.startswith("---"):
            return None

        try:
            # Find the end of frontmatter
            end_pos = content.find("---", 3)
            if end_pos == -1:
                return None

            frontmatter = content[3:end_pos].strip()
            # Simple YAML parsing for basic key-value pairs
            metadata = {}
            for line in frontmatter.split("\n"):
                line = line.strip()
                if ":" in line and not line.startswith("#"):
                    key, value = line.split(":", 1)
                    key = key.strip()
                    value = value.strip()
                    # Handle arrays like [item1, item2]
                    if value.startswith("[") and value.endswith("]"):
                        # Simple array parsing
                        items = [item.strip().strip('"').strip("'") for item in value[1:-1].split(",") if item.strip()]
                        metadata[key] = items
                    else:
                        # Remove quotes if present
                        value = value.strip('"').strip("'")
                        metadata[key] = value
            return metadata
        except Exception:
            return None

    @log_method_call
    def get_agent_prompts(self) -> List[Dict[str, str]]:
        """
        Load available agent prompts from the prompts/coding/agent directory.

        Returns:
            List[Dict[str, str]]: List of agent prompt metadata dictionaries containing:
                - name: The agent name (filename without extension).
                - title: The display title.
                - description: The description.
                - category: List of categories.
                - filename: The filename.
        """
        try:
            prompts_dir = os.path.join(os.path.dirname(__file__), "..", "..", "..", "prompts", "coding", "agent")
            agent_prompts = []

            if os.path.exists(prompts_dir):
                for filename in os.listdir(prompts_dir):
                    if filename.endswith(".md"):
                        file_path = os.path.join(prompts_dir, filename)
                        name = filename[:-3]  # Remove .md extension

                        # Try to parse YAML frontmatter
                        metadata = None
                        try:
                            with open(file_path, "r", encoding="utf-8") as f:
                                content = f.read()
                                metadata = self._parse_yaml_frontmatter(content)
                        except Exception:
                            pass

                        if metadata and "title" in metadata:
                            title = metadata["title"]
                            description = metadata.get("description", "")
                            category = metadata.get("category", [])
                        else:
                            # Fallback to filename-based title
                            title = name.replace("-", " ").replace("_", " ").title()
                            description = ""
                            category = []

                        agent_prompts.append(
                            {
                                "name": name,
                                "title": title,
                                "description": description,
                                "category": category,
                                "filename": filename,
                            }
                        )

            # Sort by title for consistent ordering
            agent_prompts.sort(key=lambda x: x["title"])
            return agent_prompts

        except Exception as e:
            logger.info(f"Error loading agent prompts: {e}")
            return []

    @log_method_call
    def get_subagent_commands(self) -> List[Dict[str, str]]:
        """
        Load subagent commands from the prompts/coding/subagent/master.json file.

        Returns:
            List[Dict[str, str]]: List of subagent commands.
        """
        try:
            commands_file = os.path.join(
                os.path.dirname(__file__), "..", "..", "..", "prompts", "coding", "subagent", "master.json"
            )

            if os.path.exists(commands_file):
                with open(commands_file, "r", encoding="utf-8") as f:
                    commands = json.load(f)
                return commands
            else:
                logger.info(f"Subagent commands file not found: {commands_file}")
                return []

        except Exception as e:
            logger.info(f"Error loading subagent commands: {e}")
            return []

    @log_method_call
    def get_agent_prompt_content(self, filename: str) -> str:
        """
        Load the content of a specific agent prompt file.

        Args:
            filename: The name of the prompt file (e.g., 'agent.md').

        Returns:
            str: The content of the file, or empty string if not found/error.
        """
        try:
            prompts_dir = os.path.join(os.path.dirname(__file__), "..", "..", "..", "prompts", "coding", "agent")
            file_path = os.path.join(prompts_dir, filename)

            if os.path.exists(file_path) and filename.endswith(".md"):
                with open(file_path, "r", encoding="utf-8") as f:
                    return f.read()
            else:
                logger.info(f"Agent prompt file not found: {file_path}")
                return ""

        except Exception as e:
            logger.info(f"Error loading agent prompt content: {e}")
            return ""

    @log_method_call
    def update_env(self, changes: Dict[str, str]) -> Dict[str, Any]:
        """
        Update multiple environment variables and persist changes.

        Args:
            changes: A dictionary of {key: value} pairs to update.

        Returns:
            Dict[str, Any]: Response containing:
                - success: Boolean indicating overall success
                - updated: List of successfully updated variables
                - errors: List of failed updates with error details
        """
        updated = []
        errors = []

        for key, value in changes.items():
            try:
                success = env_manager.update_single_var(key, value)
                if success:
                    updated.append(key)
                else:
                    errors.append({"key": key, "error": "Update failed"})
            except Exception as e:
                errors.append({"key": key, "error": str(e)})

        return {"success": len(errors) == 0, "updated": updated, "errors": errors}

    @log_method_call
    def set_theme(self, theme_name: str) -> Tuple[bool, str]:
        """
        Set the application theme.

        Args:
            theme_name: The theme to set ('light' or 'dark').

        Returns:
            Tuple[bool, str]: Success status and the active theme name.
        """
        success = theme_manager.switch_theme(theme_name)
        if success:
            env_manager.update_single_var("UI_THEME", theme_name)
            return True, theme_name
        return False, theme_manager.current_theme_name

    @log_method_call
    def toggle_theme(self) -> Tuple[str, str]:
        """
        Toggle the current application theme between light and dark mode.

        Persists the new theme setting.

        Returns:
            Tuple[str, str]: The new theme name and a status message.
        """
        theme_manager.toggle_theme()
        new_theme = theme_manager.current_theme_name
        env_manager.update_single_var("UI_THEME", new_theme)
        return new_theme, "Theme updated"

    @log_method_call
    def get_architecture_agents(self) -> List[Dict[str, str]]:
        """
        Load only agents with 'architecture' in name or metadata.

        Returns:
            List[Dict[str, str]]: List of architecture-related agent prompts.
        """
        try:
            all_agents = self.get_agent_prompts()
            architecture_agents = []

            for agent in all_agents:
                name = agent.get("name", "").lower()
                title = agent.get("title", "").lower()
                description = agent.get("description", "").lower()
                category = agent.get("category", [])

                # Check if 'architecture' is in name, title, description, or category
                has_architecture = (
                    "architecture" in name
                    or "architecture" in title
                    or "architecture" in description
                    or any("architecture" in str(cat).lower() for cat in category)
                )

                if has_architecture:
                    architecture_agents.append(agent)

            return architecture_agents

        except Exception as e:
            logger.info(f"Error loading architecture agents: {e}")
            return []

    @log_method_call
    def get_agent_options(self, agent_id: str) -> List[Dict[str, Any]]:
        """
        Load agent options from agentoption.json file for a specific agent.

        Args:
            agent_id: The agent identifier (folder name).

        Returns:
            List[Dict[str, Any]]: List of options or empty list if not found.
        """
        try:
            # Build path to agentoption.json
            agentoption_dir = os.path.join(
                os.path.dirname(__file__), "..", "..", "..", "prompts", "coding", "agentoption", agent_id
            )
            agentoption_file = os.path.join(agentoption_dir, "agentoption.json")

            if os.path.exists(agentoption_file):
                with open(agentoption_file, "r", encoding="utf-8") as f:
                    options = json.load(f)
                    logger.debug(f"Loaded {len(options)} options for agent '{agent_id}'")
                    return options
            else:
                logger.info(f"Agent options file not found: {agentoption_file}")
                return []

        except json.JSONDecodeError as e:
            logger.info(f"Failed to parse agent options JSON for '{agent_id}': {e}")
            return []
        except Exception as e:
            logger.info(f"Error loading agent options for '{agent_id}': {e}")
            return []


settings_service = SettingsService()
