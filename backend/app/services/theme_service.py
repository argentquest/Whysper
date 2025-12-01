"""Theme management service for web backend."""

from __future__ import annotations

import os
from typing import List

from common.logger import get_logger
from common.logging_decorator import log_method_call

logger = get_logger(__name__)


class ThemeManager:
    """
    Simple theme manager for web backend that handles light/dark themes.

    This is a simplified version of tkinter theme manager, adapted for
    web use without GUI dependencies.
    """

    @log_method_call
    def __init__(self) -> None:
        """
        Initialize the ThemeManager.

        Sets up available themes and loads the user's theme preference from environment variables.
        """
        # Define the list of available themes for the application
        self.themes = ["light", "dark"]

        # Set a default theme to ensure the application always starts with a theme
        self.current_theme_name = "light"

        # Load user's saved theme preference from environment variable
        self._load_theme_preference()

    @log_method_call
    def _load_theme_preference(self) -> None:
        """
        Load theme preference from environment variable 'UI_THEME'.

        Defaults to 'light' if not set or invalid.
        """
        # Retrieve theme preference from environment variable, defaulting to 'light'
        theme_pref = os.getenv("UI_THEME", "light")

        # Validate and set the theme preference if it's in the available themes
        if theme_pref in self.themes:
            self.current_theme_name = theme_pref

    @log_method_call
    def switch_theme(self, theme_name: str) -> bool:
        """
        Switch the current theme to the specified theme.

        Args:
            theme_name: The name of the theme to switch to (e.g., 'light', 'dark').

        Returns:
            bool: True if the theme was successfully switched, False if the theme name is invalid.
        """
        # Check if the requested theme is valid before switching
        if theme_name in self.themes:
            self.current_theme_name = theme_name
            return True
        return False

    @log_method_call
    def get_current_theme(self) -> str:
        """
        Get the currently active theme name.

        Returns:
            str: The name of the current theme.
        """
        # Return the currently active theme name
        return self.current_theme_name

    @log_method_call
    def get_available_themes(self) -> List[str]:
        """
        Get a list of available themes.

        Returns:
            List[str]: A list of available theme names.
        """
        # Return a copy of available themes to prevent direct modification
        return self.themes.copy()

    @log_method_call
    def toggle_theme(self) -> bool:
        """
        Toggle between 'light' and 'dark' themes.

        Returns:
            bool: True if the theme was successfully toggled.
        """
        # Determine the opposite theme based on current theme
        new_theme = "dark" if self.current_theme_name == "light" else "light"

        # Switch to the new theme and return the result
        return self.switch_theme(new_theme)


# Create a global theme manager instance for easy access across the application
theme_manager = ThemeManager()
