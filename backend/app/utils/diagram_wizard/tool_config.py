"""
Diagram tool configuration and safe execution.

Handles tool configuration for D2, Mermaid, and PlantUML with:
- Safe subprocess execution (no shell=True)
- Tool availability detection
- Timeout enforcement
- Proper file cleanup
"""

import subprocess
import tempfile
import os
from pathlib import Path
from typing import Tuple, List, Dict, Any
from enum import Enum


class DiagramTool(str, Enum):
    """Supported diagram tools."""

    D2 = "d2"
    MERMAID = "mmdc"
    PLANTUML = "plantuml"


class DiagramToolConfig:
    """Configuration for diagram rendering tools."""

    # Centralized configuration dictionary for different diagram tools
    CONFIGS: Dict[str, Dict[str, Any]] = {
        "D2": {
            "tool_name": "d2",
            "validator_cmd": ["d2", "--check"],  # Command to check D2 tool validity
            "renderer_cmd": ["d2"],  # Render to SVG
            "extension": ".d2",
        },
        "Mermaid": {
            "tool_name": "mmdc",
            "validator_cmd": ["mmdc", "--validate"],  # Validate Mermaid file
            "renderer_cmd": ["mmdc", "-i", "{input}", "-o", "{output}"],  # Render with input/output
            "extension": ".mmd",
        },
        "PlantUML": {
            "tool_name": "plantuml",
            "validator_cmd": None,  # PlantUML validates on render
            "renderer_cmd": ["plantuml", "-tsvg"],  # Render to SVG
            "extension": ".puml",
        },
    }

    @staticmethod
    def get_config(diagram_type: str) -> Dict[str, Any]:
        """
        Get configuration for a specific diagram type.

        Args:
            diagram_type (str): The diagram type (e.g., 'D2', 'Mermaid').

        Returns:
            Dict[str, Any]: The tool configuration.

        Raises:
            ValueError: If the diagram type is unknown.
        """
        # Validate and retrieve tool configuration
        if diagram_type not in DiagramToolConfig.CONFIGS:
            raise ValueError(f"Unknown diagram type: {diagram_type}")
        return DiagramToolConfig.CONFIGS[diagram_type]


class DiagramToolRunner:
    """Safely executes diagram rendering tools."""

    # Predefined timeout values for different tools
    TOOL_TIMEOUTS = {
        "d2": 30,
        "mmdc": 30,
        "plantuml": 45,
    }

    @staticmethod
    def is_tool_available(tool_name: str) -> bool:
        """
        Check if a tool is available in the system PATH.

        Args:
            tool_name (str): The name of the tool executable.

        Returns:
            bool: True if available, False otherwise.
        """
        try:
            # Attempt to run tool with version check
            result = subprocess.run(
                [tool_name, "--version"],
                capture_output=True,
                timeout=5,  # Short timeout for availability check
            )
            return result.returncode == 0  # Success if return code is 0
        except (FileNotFoundError, subprocess.TimeoutExpired):
            return False  # Tool not found or timeout occurred

    @staticmethod
    def validate_arguments(args: List[str]) -> bool:
        """
        Validate that arguments don't contain shell metacharacters.

        Args:
            args (List[str]): List of command arguments.

        Returns:
            bool: True if valid, False if forbidden characters found.
        """
        # List of forbidden characters to prevent shell injection
        forbidden_chars = ["$", "`", "|", ";", "&", ">", "<", "\n", "\r"]
        for arg in args:
            # Check if any forbidden character is in the argument
            if any(char in arg for char in forbidden_chars):
                return False
        return True

    @staticmethod
    def run_tool(
        tool: str,
        args: List[str],
        input_file: str = None,
        output_file: str = None,
        timeout: int = None,
    ) -> Tuple[bool, str]:
        """
        Safely execute a diagram tool.

        Args:
            tool (str): The tool executable name.
            args (List[str]): Command line arguments.
            input_file (str, optional): Path to input file.
            output_file (str, optional): Path to output file.
            timeout (int, optional): Execution timeout in seconds.

        Returns:
            Tuple[bool, str]: A tuple containing (success, output/error message).
        """
        # Validate arguments to prevent shell injection
        if not DiagramToolRunner.validate_arguments(args):
            return False, "Invalid characters in arguments"

        # Check if tool is available before execution
        if not DiagramToolRunner.is_tool_available(tool):
            return False, f"Tool not available: {tool}"

        # Determine timeout, use default if not specified
        if timeout is None:
            timeout = DiagramToolRunner.TOOL_TIMEOUTS.get(tool, 30)

        # Build the full command
        command = [tool] + args

        try:
            # Run subprocess with controlled environment
            result = subprocess.run(
                command,
                capture_output=True,
                text=True,
                timeout=timeout,
                cwd=tempfile.gettempdir(),  # Run in temp directory
            )

            # Check execution status
            if result.returncode == 0:
                return True, result.stdout
            else:
                return False, result.stderr or result.stdout

        except subprocess.TimeoutExpired:
            return False, f"Tool timeout after {timeout}s"
        except Exception as e:
            return False, f"Execution error: {str(e)}"


class ToolValidationError(Exception):
    """Raised when tool validation fails."""

    pass
