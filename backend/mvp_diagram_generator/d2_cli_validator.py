"""
D2 CLI Validator

This module provides validation for D2 diagrams using the official D2 CLI executable.
This is the most reliable way to validate D2 syntax as it uses the actual D2 parser.
"""

import subprocess
import os
import tempfile
import logging
from typing import Tuple, Optional

logger = logging.getLogger(__name__)

def _get_d2_executable_path() -> str:
    """
    Get the D2 executable path from environment or use default.

    Returns:
        str: Path to D2 executable
    """
    try:
        from common.env_manager import env_manager
        env_vars = env_manager.load_env_file()
        d2_path = env_vars.get('D2_EXECUTABLE_PATH', '').strip()
        if d2_path:
            if not os.path.isabs(d2_path):
                d2_path = os.path.abspath(d2_path)
            return d2_path
    except Exception as e:
        logger.debug(f"Could not load D2 path from environment: {e}")

    # Default to 'd2' in PATH
    return "d2"

def validate_d2_with_cli(d2_code: str, d2_executable: str = None) -> Tuple[bool, str]:
    """
    Validates D2 code syntax by running the d2 executable as a subprocess.

    Args:
        d2_code (str): The D2 code to validate
        d2_executable (str): Path to the d2 executable (default: from environment or "d2")

    Returns:
        Tuple[bool, str]: A tuple containing:
            - bool: True if valid, False if invalid
            - str: Success message or error message
    """
    # Get D2 executable path from environment if not provided
    if d2_executable is None:
        d2_executable = _get_d2_executable_path()

    # Create a temporary file to write the D2 code for the executable
    with tempfile.NamedTemporaryFile(mode='w', suffix='.d2', delete=False) as temp_file:
        temp_file_name = temp_file.name
        temp_file.write(d2_code)
        temp_file.flush()

    try:
        # Command to run D2 executable (suppressing image output with -t)
        # We use check_output to capture any error messages
        result = subprocess.run(
            [d2_executable, temp_file_name, '-t', '1'],  # -t 1 is for text layout engine (fastest check)
            capture_output=True,
            text=True,
            check=True,  # Raise an error if the return code is non-zero
            timeout=10  # Add timeout to prevent hanging
        )
        
        # If check=True, an exception is only raised on syntax error.
        logger.debug("D2 validation successful")
        return (True, "D2 Syntax is Valid.")
        
    except subprocess.CalledProcessError as e:
        # A non-zero return code means a syntax or parsing error occurred
        error_message = e.stderr.strip() or e.stdout.strip() or "Unknown D2 syntax error"
        logger.debug(f"D2 validation failed: {error_message}")
        return (False, f"D2 Syntax Error:\n{error_message}")
        
    except subprocess.TimeoutExpired:
        error_message = "D2 validation timed out (10s limit)"
        logger.warning(error_message)
        return (False, error_message)
        
    except FileNotFoundError:
        # The 'd2' command wasn't found in PATH
        error_message = "Error: D2 executable not found. Please install D2 CLI."
        logger.error(error_message)
        return (False, error_message)
        
    except Exception as e:
        # Any other unexpected error
        error_message = f"Unexpected error during D2 validation: {str(e)}"
        logger.error(error_message)
        return (False, error_message)
        
    finally:
        # Clean up the temporary file
        try:
            if os.path.exists(temp_file_name):
                os.unlink(temp_file_name)
        except Exception as e:
            logger.warning(f"Failed to clean up temp file {temp_file_name}: {e}")

def is_d2_cli_available(d2_executable: str = None) -> bool:
    """
    Check if the D2 CLI executable is available.

    Args:
        d2_executable (str): Path to the d2 executable (default: from environment or "d2")

    Returns:
        bool: True if D2 CLI is available, False otherwise
    """
    # Get D2 executable path from environment if not provided
    if d2_executable is None:
        d2_executable = _get_d2_executable_path()

    try:
        result = subprocess.run(
            [d2_executable, "--version"],
            capture_output=True,
            text=True,
            check=True,
            timeout=120
        )
        logger.debug(f"D2 CLI version: {result.stdout.strip()}")
        return True
    except (subprocess.CalledProcessError, FileNotFoundError, subprocess.TimeoutExpired):
        return False

def validate_and_fix_d2_with_cli(d2_code: str, max_attempts: int = 3) -> Tuple[bool, str, str]:
    """
    Validates D2 code using CLI and attempts to fix common issues.
    
    This function tries to validate the D2 code, and if it fails, it applies
    some common fixes and tries again (up to max_attempts times).
    
    Args:
        d2_code (str): The D2 code to validate and potentially fix
        max_attempts (int): Maximum number of fix attempts
        
    Returns:
        Tuple[bool, str, str]: A tuple containing:
            - bool: True if valid, False if invalid
            - str: The (potentially) corrected D2 code
            - str: Success message or error message
    """
    from .d2_syntax_fixer import fix_d2_syntax
    
    current_code = d2_code
    
    for attempt in range(max_attempts):
        # Try to validate the current code
        is_valid, message = validate_d2_with_cli(current_code)
        
        if is_valid:
            if attempt > 0:
                message = f"D2 syntax fixed after {attempt} attempt(s). {message}"
            return (True, current_code, message)
        
        # If this is the last attempt, don't try to fix anymore
        if attempt == max_attempts - 1:
            return (False, current_code, message)
        
        # Apply syntax fixes and try again
        logger.debug(f"D2 validation failed on attempt {attempt + 1}, applying fixes...")
        fix_result = fix_d2_syntax(current_code)
        current_code = fix_result.corrected_code
        
        # If no corrections were made, don't try again
        if not fix_result.corrections:
            logger.debug("No corrections applied, stopping fix attempts")
            return (False, current_code, message)
    
    return (False, current_code, "Failed to validate D2 syntax after multiple attempts")