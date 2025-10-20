"""
Mermaid CLI Validator

This module provides validation for Mermaid diagrams using the official Mermaid CLI (mmdc).
This is the most reliable way to validate Mermaid syntax as it uses the actual Mermaid parser.
"""

import subprocess
import os
import tempfile
import logging
from typing import Tuple, Optional

logger = logging.getLogger(__name__)

def validate_mermaid_with_cli(mermaid_code: str, mermaid_executable: str = "mmdc") -> Tuple[bool, str]:
    """
    Validates Mermaid code syntax by running the mmdc executable as a subprocess.

    Args:
        mermaid_code (str): The Mermaid code to validate
        mermaid_executable (str): Path to the mmdc executable (default: "mmdc")

    Returns:
        Tuple[bool, str]: A tuple containing:
            - bool: True if valid, False if invalid
            - str: Success message or error message
    """
    # Create temporary files for input and output
    with tempfile.NamedTemporaryFile(mode='w', suffix='.mmd', delete=False) as temp_input:
        temp_input_name = temp_input.name
        temp_input.write(mermaid_code)
        temp_input.flush()

    # Create a temporary output file
    temp_output_name = temp_input_name.replace('.mmd', '.svg')

    try:
        # Command to run mmdc (Mermaid CLI) - just try to compile to SVG
        # If compilation succeeds, the syntax is valid
        result = subprocess.run(
            [mermaid_executable, '-i', temp_input_name, '-o', temp_output_name],
            capture_output=True,
            text=True,
            check=True,  # Raise an error if the return code is non-zero
            timeout=30,  # Increased timeout for mmdc (can be slow on first run)
            shell=True  # Use shell on Windows to find .cmd files
        )

        # If check=True doesn't raise an exception, the validation succeeded
        logger.debug("Mermaid validation successful")
        return (True, "Mermaid Syntax is Valid.")

    except subprocess.CalledProcessError as e:
        # A non-zero return code means a syntax or parsing error occurred
        error_message = e.stderr.strip() or e.stdout.strip() or "Unknown Mermaid syntax error"
        logger.debug(f"Mermaid validation failed: {error_message}")

        # Clean up error message to extract useful info
        cleaned_error = clean_mermaid_error(error_message)
        return (False, f"Mermaid Syntax Error:\n{cleaned_error}")

    except subprocess.TimeoutExpired:
        error_message = "Mermaid validation timed out (10s limit)"
        logger.warning(error_message)
        return (False, error_message)

    except FileNotFoundError:
        # The 'mmdc' command wasn't found in PATH
        error_message = "Error: Mermaid CLI (mmdc) not found. Please install @mermaid-js/mermaid-cli."
        logger.error(error_message)
        return (False, error_message)

    except Exception as e:
        # Any other unexpected error
        error_message = f"Unexpected error during Mermaid validation: {str(e)}"
        logger.error(error_message)
        return (False, error_message)

    finally:
        # Clean up the temporary files
        try:
            if os.path.exists(temp_input_name):
                os.unlink(temp_input_name)
        except Exception as e:
            logger.warning(f"Failed to clean up temp input file {temp_input_name}: {e}")

        try:
            if os.path.exists(temp_output_name):
                os.unlink(temp_output_name)
        except Exception as e:
            logger.warning(f"Failed to clean up temp output file {temp_output_name}: {e}")

def clean_mermaid_error(error_message: str) -> str:
    """
    Clean up Mermaid CLI error messages to extract the most useful information.

    Args:
        error_message (str): Raw error message from mmdc

    Returns:
        str: Cleaned error message
    """
    # Remove ANSI color codes
    import re
    ansi_escape = re.compile(r'\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])')
    cleaned = ansi_escape.sub('', error_message)

    # Extract the most relevant lines (skip generic stack traces)
    lines = cleaned.split('\n')
    relevant_lines = []

    for line in lines:
        # Skip empty lines and common unhelpful lines
        if not line.strip():
            continue
        if 'at Object.' in line or 'at Function.' in line:
            continue
        if line.strip().startswith('at ') and '(' in line:
            continue

        relevant_lines.append(line)

    # Return first few relevant lines (most informative)
    if relevant_lines:
        return '\n'.join(relevant_lines[:10])

    return error_message

def is_mermaid_cli_available(mermaid_executable: str = "mmdc") -> bool:
    """
    Check if the Mermaid CLI (mmdc) executable is available.

    Args:
        mermaid_executable (str): Path to the mmdc executable (default: "mmdc")

    Returns:
        bool: True if Mermaid CLI is available, False otherwise
    """
    try:
        result = subprocess.run(
            [mermaid_executable, "--version"],
            capture_output=True,
            text=True,
            check=True,
            timeout=5,
            shell=True  # Use shell on Windows to find .cmd files
        )
        logger.debug(f"Mermaid CLI version: {result.stdout.strip()}")
        return True
    except (subprocess.CalledProcessError, FileNotFoundError, subprocess.TimeoutExpired) as e:
        logger.debug(f"Mermaid CLI check failed: {e}")
        return False

def validate_and_fix_mermaid_with_cli(mermaid_code: str, max_attempts: int = 3) -> Tuple[bool, str, str]:
    """
    Validates Mermaid code using CLI and attempts to fix common issues.

    This function tries to validate the Mermaid code, and if it fails, it applies
    some common fixes and tries again (up to max_attempts times).

    Args:
        mermaid_code (str): The Mermaid code to validate and potentially fix
        max_attempts (int): Maximum number of fix attempts

    Returns:
        Tuple[bool, str, str]: A tuple containing:
            - bool: True if valid, False if invalid
            - str: The (potentially) corrected Mermaid code
            - str: Success message or error message
    """
    from .mermaid_syntax_fixer import fix_mermaid_syntax

    logger.info(f"[MERMAID AUTO-FIX] Starting auto-fix process (max {max_attempts} attempts)")
    logger.debug(f"[MERMAID AUTO-FIX] Original code length: {len(mermaid_code)} chars")

    current_code = mermaid_code

    for attempt in range(max_attempts):
        logger.info(f"[MERMAID AUTO-FIX] Attempt {attempt + 1}/{max_attempts}")

        # Try to validate the current code
        is_valid, message = validate_mermaid_with_cli(current_code)

        if is_valid:
            if attempt > 0:
                logger.info(f"[MERMAID AUTO-FIX] ✅ Success on attempt {attempt + 1}!")
                message = f"Mermaid syntax fixed after {attempt} attempt(s). {message}"
            else:
                logger.info(f"[MERMAID AUTO-FIX] ✅ Code was already valid, no fixes needed")
            return (True, current_code, message)

        # If this is the last attempt, don't try to fix anymore
        if attempt == max_attempts - 1:
            logger.error(f"[MERMAID AUTO-FIX] ❌ All {max_attempts} attempts exhausted")
            logger.error(f"[MERMAID AUTO-FIX] Final error: {message[:200]}")
            return (False, current_code, message)

        # Apply syntax fixes and try again
        logger.info(f"[MERMAID AUTO-FIX] Validation failed, applying syntax fixes...")
        fix_result = fix_mermaid_syntax(current_code)

        if fix_result.corrections:
            logger.info(f"[MERMAID AUTO-FIX] Applied {len(fix_result.corrections)} correction(s):")
            for i, correction in enumerate(fix_result.corrections, 1):
                logger.info(f"[MERMAID AUTO-FIX]   {i}. {correction}")
        else:
            logger.warning(f"[MERMAID AUTO-FIX] No corrections could be applied")

        if fix_result.warnings:
            logger.warning(f"[MERMAID AUTO-FIX] {len(fix_result.warnings)} warning(s):")
            for warning in fix_result.warnings:
                logger.warning(f"[MERMAID AUTO-FIX]   - {warning}")

        current_code = fix_result.corrected_code
        logger.debug(f"[MERMAID AUTO-FIX] Code length after fixes: {len(current_code)} chars")

        # If no corrections were made, don't try again
        if not fix_result.corrections:
            logger.warning(f"[MERMAID AUTO-FIX] No corrections possible, stopping attempts")
            return (False, current_code, message)

    logger.error(f"[MERMAID AUTO-FIX] ❌ Failed to fix after all attempts")
    return (False, current_code, "Failed to validate Mermaid syntax after multiple attempts")

def validate_mermaid_and_render(
    mermaid_code: str,
    output_format: str = "svg",
    mermaid_executable: str = "mmdc"
) -> Tuple[bool, str, Optional[str]]:
    """
    Validates Mermaid code and renders it if valid.

    Args:
        mermaid_code (str): The Mermaid code to validate and render
        output_format (str): Output format ('svg' or 'png')
        mermaid_executable (str): Path to the mmdc executable

    Returns:
        Tuple[bool, str, Optional[str]]: A tuple containing:
            - bool: True if valid, False if invalid
            - str: Success/error message
            - Optional[str]: Rendered output (SVG string or base64 PNG) if successful
    """
    with tempfile.NamedTemporaryFile(mode='w', suffix='.mmd', delete=False) as temp_input:
        temp_input_name = temp_input.name
        temp_input.write(mermaid_code)
        temp_input.flush()

    # Create output filename
    output_ext = '.svg' if output_format == 'svg' else '.png'
    temp_output_name = temp_input_name.replace('.mmd', output_ext)

    try:
        # Run mmdc to render the diagram
        result = subprocess.run(
            [mermaid_executable, '-i', temp_input_name, '-o', temp_output_name],
            capture_output=True,
            text=True,
            check=True,
            timeout=15,
            shell=True  # Use shell on Windows to find .cmd files
        )

        # Read the output file
        with open(temp_output_name, 'rb' if output_format == 'png' else 'r') as f:
            if output_format == 'png':
                import base64
                rendered_output = base64.b64encode(f.read()).decode('utf-8')
            else:
                rendered_output = f.read()

        logger.info(f"Successfully rendered Mermaid diagram to {output_format}")
        return (True, "Mermaid diagram rendered successfully", rendered_output)

    except subprocess.CalledProcessError as e:
        error_message = e.stderr.strip() or e.stdout.strip() or "Unknown Mermaid error"
        cleaned_error = clean_mermaid_error(error_message)
        return (False, f"Mermaid Rendering Error:\n{cleaned_error}", None)

    except Exception as e:
        error_message = f"Unexpected error during Mermaid rendering: {str(e)}"
        logger.error(error_message)
        return (False, error_message, None)

    finally:
        # Clean up temporary files
        try:
            if os.path.exists(temp_input_name):
                os.unlink(temp_input_name)
        except Exception as e:
            logger.warning(f"Failed to clean up temp input file: {e}")

        try:
            if os.path.exists(temp_output_name):
                os.unlink(temp_output_name)
        except Exception as e:
            logger.warning(f"Failed to clean up temp output file: {e}")
