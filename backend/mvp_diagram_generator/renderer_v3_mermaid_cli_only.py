"""
Mermaid CLI-Only Renderer - Version 3

This renderer uses ONLY the Mermaid CLI (mmdc) for all diagram rendering.
No fallbacks, no Playwright, pure Mermaid CLI approach.

Supported diagram types:
- mermaid: Uses mmdc CLI directly
- d2: Converted to mermaid syntax then rendered via mmdc
- c4: Converted to mermaid syntax then rendered via mmdc

This is the most reliable and stable approach for Windows environments.
"""

import subprocess
import tempfile
import os
import base64
from pathlib import Path
from typing import Literal
from common.logger import get_logger

logger = get_logger(__name__)

# Mermaid CLI executable name
MMDC_EXECUTABLE = "mmdc"
MMDC_TIMEOUT = 120  # seconds


def render_diagram(
    diagram_code: str,
    diagram_type: str,
    output_format: str = "svg",
    **kwargs
) -> str:
    """
    Render a diagram using Mermaid CLI (mmdc) only.

    Args:
        diagram_code: The diagram source code
        diagram_type: Type of diagram ('mermaid', 'd2', or 'c4')
        output_format: Output format ('svg' or 'png')
        **kwargs: Additional arguments (ignored, for compatibility)

    Returns:
        str: Rendered diagram (SVG string or base64-encoded PNG)

    Raises:
        Exception: If rendering fails
    """
    logger.info(f"Rendering {diagram_type} diagram to {output_format} using Mermaid CLI")

    # Validate output format
    if output_format not in ("svg", "png"):
        raise ValueError(f"Unsupported output format: {output_format}")

    # Normalize diagram code to Mermaid syntax
    if diagram_type in ("d2", "c4"):
        logger.info(f"Converting {diagram_type} to Mermaid syntax")
        diagram_code = convert_to_mermaid(diagram_code, diagram_type)
    elif diagram_type != "mermaid":
        raise ValueError(f"Unsupported diagram type: {diagram_type}")

    # Render using Mermaid CLI
    return render_with_mmdc(diagram_code, output_format)


def convert_to_mermaid(diagram_code: str, diagram_type: str) -> str:
    """
    Convert D2 or C4 diagrams to Mermaid syntax.

    For now, returns the code as-is. In production, this would:
    - Parse D2 syntax and convert to Mermaid flowchart
    - Parse C4 syntax and convert to Mermaid diagram

    Args:
        diagram_code: The diagram code
        diagram_type: 'd2' or 'c4'

    Returns:
        str: Mermaid-compatible diagram code
    """
    logger.debug(f"Converting {diagram_type} to Mermaid (currently returns as-is)")
    # TODO: Implement actual D2->Mermaid and C4->Mermaid conversion
    # For now, assume input is already valid Mermaid or compatible
    return diagram_code


def render_with_mmdc(diagram_code: str, output_format: str) -> str:
    """
    Render using Mermaid CLI (mmdc) executable.

    Args:
        diagram_code: The Mermaid diagram code
        output_format: 'svg' or 'png'

    Returns:
        str: SVG string or base64-encoded PNG

    Raises:
        Exception: If mmdc is not available or rendering fails
    """

    # Check if mmdc is available
    if not is_mmdc_available():
        raise Exception(
            "Mermaid CLI (mmdc) is not available on this system. "
            "Please install with: npm install -g @mermaid-js/mermaid-cli"
        )

    # Create temporary files
    with tempfile.TemporaryDirectory() as tmpdir:
        input_file = Path(tmpdir) / "diagram.mmd"
        output_file = Path(tmpdir) / f"diagram.{output_format}"

        try:
            # Write diagram code to input file
            input_file.write_text(diagram_code, encoding="utf-8")
            logger.debug(f"Wrote diagram to: {input_file}")

            # Run mmdc command
            cmd = [
                MMDC_EXECUTABLE,
                "-i", str(input_file),
                "-o", str(output_file),
                "-f", output_format.upper(),  # mmdc expects SVG or PNG
            ]

            logger.debug(f"Running command: {' '.join(cmd)}")

            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=MMDC_TIMEOUT,
                shell=True  # Use shell on Windows to find .cmd files
            )

            if result.returncode != 0:
                error_msg = result.stderr or result.stdout or "Unknown error"
                raise Exception(f"mmdc rendering failed: {error_msg}")

            logger.debug(f"mmdc completed successfully")

            # Read output file
            if not output_file.exists():
                raise Exception(f"Output file not created: {output_file}")

            output_data = output_file.read_bytes()

            # Return based on format
            if output_format == "svg":
                # Return SVG as string
                return output_data.decode("utf-8")
            elif output_format == "png":
                # Return PNG as base64
                return base64.b64encode(output_data).decode("utf-8")

        except subprocess.TimeoutExpired:
            raise Exception(f"mmdc timed out after {MMDC_TIMEOUT} seconds")
        except Exception as e:
            logger.error(f"Error rendering diagram: {str(e)}")
            raise


def is_mmdc_available() -> bool:
    """
    Check if Mermaid CLI (mmdc) is available on the system.

    Returns:
        bool: True if mmdc is available, False otherwise
    """
    try:
        result = subprocess.run(
            [MMDC_EXECUTABLE, "--version"],
            capture_output=True,
            text=True,
            timeout=5,
            shell=True  # Use shell on Windows
        )
        available = result.returncode == 0
        if available:
            logger.debug(f"mmdc is available: {result.stdout.strip()}")
        else:
            logger.warning(f"mmdc check failed: {result.stderr}")
        return available
    except Exception as e:
        logger.warning(f"Could not check mmdc availability: {str(e)}")
        return False
