"""
D2 CLI Validator

This module provides validation for D2 diagrams using the official D2 CLI executable.
This is the most reliable way to validate D2 syntax as it uses the actual D2 parser.
"""

import subprocess
import os
import tempfile
import logging
from typing import Tuple

logger = logging.getLogger(__name__)

def _get_d2_executable_path() -> str:
    """
    Retrieve the path to the D2 executable.

    Tries to get the path from the D2_EXECUTABLE_PATH environment variable.
    Falls back to "d2" (assuming it's in the system PATH).

    Returns:
        str: The path to the D2 executable.
    """
    # Attempt to retrieve D2 executable path from environment variables
    # Provides flexibility in executable location configuration
    try:
        from common.env_manager import env_manager
        env_vars = env_manager.load_env_file()
        d2_path = env_vars.get('D2_EXECUTABLE_PATH', '').strip()
        if d2_path:
            # Convert to absolute path if relative path is provided
            if not os.path.isabs(d2_path):
                d2_path = os.path.abspath(d2_path)
            return d2_path
    except Exception as e:
        logger.debug(f"Could not load D2 path from environment: {e}")

    # Fallback to default 'd2' command in system PATH
    return "d2"

def validate_d2_with_cli(d2_code: str, d2_executable: str = None) -> Tuple[bool, str]:
    """
    Validate D2 code syntax using the D2 CLI.

    Args:
        d2_code: The D2 diagram code to validate.
        d2_executable: Optional path to the D2 executable.

    Returns:
        Tuple[bool, str]: A tuple containing a boolean indicating validity and a message (validation success message or error details).
    """
    # Validate D2 code syntax by executing the D2 CLI as a subprocess
    # This method uses the official parser to check syntax reliability

    # Determine the D2 executable path if not explicitly provided
    if d2_executable is None:
        d2_executable = _get_d2_executable_path()

    # Create a temporary file to store the D2 code for CLI validation
    with tempfile.NamedTemporaryFile(mode='w', suffix='.d2', delete=False) as temp_file:
        temp_file_name = temp_file.name
        temp_file.write(d2_code)
        temp_file.flush()

    try:
        # Run D2 executable with text layout engine for fastest syntax check
        # Capture output and set a timeout to prevent hanging
        subprocess.run(
            [d2_executable, temp_file_name, '-t', '1'],  # -t 1 is for text layout engine (fastest check)
            capture_output=True,
            text=True,
            check=True,  # Raise an error if the return code is non-zero
            timeout=10  # Add timeout to prevent hanging
        )
        
        # Successful validation returns a positive result
        logger.debug("D2 validation successful")
        return (True, "D2 Syntax is Valid.")
        
    except subprocess.CalledProcessError as e:
        # Capture and return specific syntax error messages
        error_message = e.stderr.strip() or e.stdout.strip() or "Unknown D2 syntax error"
        logger.debug(f"D2 validation failed: {error_message}")
        return (False, f"D2 Syntax Error:\n{error_message}")
        
    except subprocess.TimeoutExpired:
        # Handle cases where validation takes too long
        error_message = "D2 validation timed out (10s limit)"
        logger.warning(error_message)
        return (False, error_message)
        
    except FileNotFoundError:
        # Provide clear feedback if D2 CLI is not installed
        error_message = "Error: D2 executable not found. Please install D2 CLI."
        logger.error(error_message)
        return (False, error_message)
        
    except Exception as e:
        # Catch-all for unexpected errors during validation
        error_message = f"Unexpected error during D2 validation: {str(e)}"
        logger.error(error_message)
        return (False, error_message)
        
    finally:
        # Ensure temporary file is always cleaned up
        try:
            if os.path.exists(temp_file_name):
                os.unlink(temp_file_name)
        except Exception as e:
            logger.warning(f"Failed to clean up temp file {temp_file_name}: {e}")

def is_d2_cli_available(d2_executable: str = None) -> bool:
    """
    Check if the D2 CLI is available on the system.

    Args:
        d2_executable: Optional path to the D2 executable.

    Returns:
        bool: True if the D2 CLI is available, False otherwise.
    """
    # Check if the D2 CLI is installed and accessible
    # Useful for pre-flight checks before validation

    # Determine the D2 executable path if not explicitly provided
    if d2_executable is None:
        d2_executable = _get_d2_executable_path()

    try:
        # Attempt to run version check with timeout
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
    Validate D2 code and attempt to automatically fix syntax errors.

    Args:
        d2_code: The D2 diagram code.
        max_attempts: Maximum number of fix attempts (default: 3).

    Returns:
        Tuple[bool, str, str]: A tuple containing:
            - is_valid (bool): Whether the final code is valid.
            - code (str): The (potentially fixed) D2 code.
            - message (str): Validation/fix status message.
    """
    # Validate D2 code and attempt automatic fixes for common syntax issues
    # Provides multiple attempts to correct and validate the code
    
    from .d2_syntax_fixer import fix_d2_syntax
    
    current_code = d2_code
    
    for attempt in range(max_attempts):
        # Validate the current iteration of the code
        is_valid, message = validate_d2_with_cli(current_code)
        
        # Return successful validation with optional fix information
        if is_valid:
            if attempt > 0:
                message = f"D2 syntax fixed after {attempt} attempt(s). {message}"
            return (True, current_code, message)
        
        # Stop attempts if at maximum retries
        if attempt == max_attempts - 1:
            return (False, current_code, message)
        
        # Log and attempt to fix syntax issues
        logger.debug(f"D2 validation failed on attempt {attempt + 1}, applying fixes...")
        fix_result = fix_d2_syntax(current_code)
        current_code = fix_result.corrected_code
        
        # Stop if no corrections were possible
        if not fix_result.corrections:
            logger.debug("No corrections applied, stopping fix attempts")
            return (False, current_code, message)
    
    # Final fallback if all attempts fail
    return (False, current_code, "Failed to validate D2 syntax after multiple attempts")
