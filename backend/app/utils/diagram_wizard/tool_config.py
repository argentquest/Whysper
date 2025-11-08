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

    CONFIGS: Dict[str, Dict[str, Any]] = {
        "D2": {
            "tool_name": "d2",
            "validator_cmd": ["d2", "--check"],  # args format, not shell
            "renderer_cmd": ["d2"],  # render to SVG
            "extension": ".d2",
        },
        "Mermaid": {
            "tool_name": "mmdc",
            "validator_cmd": ["mmdc", "--validate"],
            "renderer_cmd": ["mmdc", "-i", "{input}", "-o", "{output}"],
            "extension": ".mmd",
        },
        "PlantUML": {
            "tool_name": "plantuml",
            "validator_cmd": None,  # PlantUML validates on render
            "renderer_cmd": ["plantuml", "-tsvg"],
            "extension": ".puml",
        },
    }

    @staticmethod
    def get_config(diagram_type: str) -> Dict[str, Any]:
        """Get configuration for a specific diagram type."""
        if diagram_type not in DiagramToolConfig.CONFIGS:
            raise ValueError(f"Unknown diagram type: {diagram_type}")
        return DiagramToolConfig.CONFIGS[diagram_type]


class DiagramToolRunner:
    """Safely executes diagram rendering tools."""

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
            tool_name: Tool name (d2, mmdc, plantuml)

        Returns:
            True if tool is available and executable
        """
        try:
            result = subprocess.run(
                [tool_name, "--version"],
                capture_output=True,
                timeout=5,
            )
            return result.returncode == 0
        except (FileNotFoundError, subprocess.TimeoutExpired):
            return False

    @staticmethod
    def validate_arguments(args: List[str]) -> bool:
        """
        Validate that arguments don't contain shell metacharacters.

        Args:
            args: List of command arguments

        Returns:
            True if all arguments are safe
        """
        forbidden_chars = ["$", "`", "|", ";", "&", ">", "<", "\n", "\r"]
        for arg in args:
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
            tool: Tool name (d2, mmdc, plantuml)
            args: List of command arguments
            input_file: Optional input file path
            output_file: Optional output file path
            timeout: Execution timeout in seconds

        Returns:
            Tuple of (success: bool, output: str)
        """
        # Validate arguments
        if not DiagramToolRunner.validate_arguments(args):
            return False, "Invalid characters in arguments"

        # Check tool is available
        if not DiagramToolRunner.is_tool_available(tool):
            return False, f"Tool not available: {tool}"

        # Determine timeout
        if timeout is None:
            timeout = DiagramToolRunner.TOOL_TIMEOUTS.get(tool, 30)

        # Build command
        command = [tool] + args

        try:
            result = subprocess.run(
                command,
                capture_output=True,
                text=True,
                timeout=timeout,
                cwd=tempfile.gettempdir(),
            )

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
