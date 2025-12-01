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
import base64
from pathlib import Path
from common.logger import get_logger

# Initialize logger for tracking and debugging rendering process
logger = get_logger(__name__)

# Define constants for Mermaid CLI executable and timeout
MMDC_EXECUTABLE = "mmdc"
MMDC_TIMEOUT = 120  # seconds


def render_diagram(
    diagram_code: str,
    diagram_type: str,
    output_format: str = "svg",
    **kwargs
) -> str:
    # Log the start of diagram rendering with type and format
    logger.info(f"Rendering {diagram_type} diagram to {output_format} using Mermaid CLI")

    # Validate that output format is either SVG or PNG
    if output_format not in ("svg", "png"):
        raise ValueError(f"Unsupported output format: {output_format}")

    # Convert non-mermaid diagram types to mermaid syntax
    if diagram_type in ("d2", "c4"):
        logger.info(f"Converting {diagram_type} to Mermaid syntax")
        diagram_code = convert_to_mermaid(diagram_code, diagram_type)
    elif diagram_type != "mermaid":
        raise ValueError(f"Unsupported diagram type: {diagram_type}")

    # Render the diagram using Mermaid CLI and return the result
    return render_with_mmdc(diagram_code, output_format)


def convert_to_mermaid(diagram_code: str, diagram_type: str) -> str:
    # Placeholder for future conversion logic from D2 or C4 to Mermaid syntax
    logger.debug(f"Converting {diagram_type} to Mermaid (currently returns as-is)")
    # TODO: Implement actual D2->Mermaid and C4->Mermaid conversion
    return diagram_code


def render_with_mmdc(diagram_code: str, output_format: str) -> str:
    # Verify Mermaid CLI is available before attempting to render
    if not is_mmdc_available():
        raise Exception(
            "Mermaid CLI (mmdc) is not available on this system. "
            "Please install with: npm install -g @mermaid-js/mermaid-cli"
        )

    # Use temporary directory to store input and output files
    with tempfile.TemporaryDirectory() as tmpdir:
        input_file = Path(tmpdir) / "diagram.mmd"
        output_file = Path(tmpdir) / f"diagram.{output_format}"

        try:
            # Write diagram code to temporary input file
            input_file.write_text(diagram_code, encoding="utf-8")
            logger.debug(f"Wrote diagram to: {input_file}")

            # Prepare mmdc command with input and output file specifications
            cmd = [
                MMDC_EXECUTABLE,
                "-i", str(input_file),
                "-o", str(output_file),
                "-f", output_format.upper(),  # mmdc expects uppercase format
            ]

            logger.debug(f"Running command: {' '.join(cmd)}")

            # Execute mmdc command with timeout and shell support for Windows
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=MMDC_TIMEOUT,
                shell=True  # Use shell on Windows to find .cmd files
            )

            # Check if command execution was successful
            if result.returncode != 0:
                error_msg = result.stderr or result.stdout or "Unknown error"
                raise Exception(f"mmdc rendering failed: {error_msg}")

            logger.debug(f"mmdc completed successfully")

            # Verify output file was created
            if not output_file.exists():
                raise Exception(f"Output file not created: {output_file}")

            # Read output file contents
            output_data = output_file.read_bytes()

            # Return diagram based on output format
            if output_format == "svg":
                return output_data.decode("utf-8")  # Return SVG as string
            elif output_format == "png":
                return base64.b64encode(output_data).decode("utf-8")  # Return PNG as base64

        except subprocess.TimeoutExpired:
            raise Exception(f"mmdc timed out after {MMDC_TIMEOUT} seconds")
        except Exception as e:
            logger.info(f"Error rendering diagram: {str(e)}")
            raise


def is_mmdc_available() -> bool:
    # Check if Mermaid CLI is installed and accessible
    try:
        result = subprocess.run(
            [MMDC_EXECUTABLE, "--version"],
            capture_output=True,
            text=True,
            timeout=5,
            shell=True  # Use shell on Windows
        )
        # Determine availability based on return code
        available = result.returncode == 0
        if available:
            logger.debug(f"mmdc is available: {result.stdout.strip()}")
        else:
            logger.info(f"mmdc check failed: {result.stderr}")
        return available
    except Exception as e:
        logger.info(f"Could not check mmdc availability: {str(e)}")
        return False
