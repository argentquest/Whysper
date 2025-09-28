"""Environment and theme helpers for the web backend."""
from __future__ import annotations

import os
import json
from typing import Dict, Tuple, List

from common.env_manager import env_manager
from common.logger import get_logger
from security_utils import SecurityUtils
from .theme_service import theme_manager

logger = get_logger(__name__)


class SettingsService:
    """Expose environment configuration and theme controls via REST."""

    def get_settings(self) -> Dict[str, object]:
        env_vars = env_manager.load_env_file()
        masked = {
            key: SecurityUtils.mask_api_key(value) if "KEY" in key else value
            for key, value in env_vars.items()
        }
        return {
            "values": env_vars,
            "masked": masked,
            "descriptions": env_manager.get_env_descriptions(),
            "theme": theme_manager.current_theme_name,
            "availableThemes": theme_manager.get_available_themes(),
            "agentPrompts": self.get_agent_prompts(),
            "subagentCommands": self.get_subagent_commands(),
        }

    def get_agent_prompts(self) -> List[Dict[str, str]]:
        """Load available agent prompts from the prompts/coding/agent directory."""
        try:
            prompts_dir = os.path.join(os.path.dirname(__file__), "..", "..", "..", "prompts", "coding", "agent")
            agent_prompts = []
            
            if os.path.exists(prompts_dir):
                for filename in os.listdir(prompts_dir):
                    if filename.endswith('.md'):
                        name = filename[:-3]  # Remove .md extension
                        title = name.replace('-', ' ').replace('_', ' ').title()
                        agent_prompts.append({
                            "name": name,
                            "title": title,
                            "filename": filename
                        })
            
            # Sort by title for consistent ordering
            agent_prompts.sort(key=lambda x: x['title'])
            return agent_prompts
            
        except Exception as e:
            logger.error(f"Error loading agent prompts: {e}")
            return []

    def get_subagent_commands(self) -> List[Dict[str, str]]:
        """Load subagent commands from the prompts/coding/subagent/master.json file."""
        try:
            commands_file = os.path.join(os.path.dirname(__file__), "..", "..", "..", "prompts", "coding", "subagent", "master.json")
            
            if os.path.exists(commands_file):
                with open(commands_file, 'r', encoding='utf-8') as f:
                    commands = json.load(f)
                return commands
            else:
                logger.warning(f"Subagent commands file not found: {commands_file}")
                return []
                
        except Exception as e:
            logger.error(f"Error loading subagent commands: {e}")
            return []

    def get_agent_prompt_content(self, filename: str) -> str:
        """Load the content of a specific agent prompt file."""
        try:
            prompts_dir = os.path.join(os.path.dirname(__file__), "..", "..", "..", "prompts", "coding", "agent")
            file_path = os.path.join(prompts_dir, filename)
            
            if os.path.exists(file_path) and filename.endswith('.md'):
                with open(file_path, 'r', encoding='utf-8') as f:
                    return f.read()
            else:
                logger.warning(f"Agent prompt file not found: {file_path}")
                return ""
                
        except Exception as e:
            logger.error(f"Error loading agent prompt content: {e}")
            return ""

    def update_env(self, changes: Dict[str, str]) -> Dict[str, bool]:
        results: Dict[str, bool] = {}
        for key, value in changes.items():
            results[key] = env_manager.update_single_var(key, value)
        return results

    def set_theme(self, theme_name: str) -> Tuple[bool, str]:
        success = theme_manager.switch_theme(theme_name)
        if success:
            env_manager.update_single_var("UI_THEME", theme_name)
            return True, theme_name
        return False, theme_manager.current_theme_name

    def toggle_theme(self) -> Tuple[str, str]:
        theme_manager.toggle_theme()
        new_theme = theme_manager.current_theme_name
        env_manager.update_single_var("UI_THEME", new_theme)
        return new_theme, "Theme updated"


settings_service = SettingsService()
