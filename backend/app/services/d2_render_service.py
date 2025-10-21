"""
D2 Rendering Service using CLI
Handles D2 diagram compilation and rendering using the D2 CLI tool
"""

import os
import subprocess
import tempfile
import uuid
from typing import Tuple, Optional, Dict, Any
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

class D2RenderService:
    """Service for rendering D2 diagrams using the D2 CLI"""

    # Maximum D2 code length (500KB should be more than enough for any diagram)
    MAX_D2_CODE_LENGTH = 500 * 1024  # 500KB

    def __init__(self):
        self.d2_executable = self._find_d2_executable()
        if not self.d2_executable:
            raise RuntimeError("D2 CLI not found. Please install D2 from https://d2lang.com/")

    def _find_d2_executable(self) -> Optional[str]:
        """Find the D2 executable using environment variable or known locations"""
        from common.env_manager import env_manager

        # Get D2 executable path from environment
        env_vars = env_manager.load_env_file()
        d2_path = env_vars.get('D2_EXECUTABLE_PATH', '').strip()

        if d2_path:
            # Use configured path from environment
            if not os.path.isabs(d2_path):
                d2_path = os.path.abspath(d2_path)

            # Verify the configured path works
            try:
                result = subprocess.run([d2_path, '--version'],
                                      capture_output=True,
                                      text=True,
                                      timeout=5)
                if result.returncode == 0:
                    logger.info(f"Found D2 executable at: {d2_path} (from environment)")
                    logger.info(f"D2 version: {result.stdout.strip()}")
                    return d2_path
                else:
                    logger.warning(f"D2 executable configured in environment at {d2_path} but not working, falling back to auto-detection")
            except (subprocess.TimeoutExpired, FileNotFoundError, subprocess.CalledProcessError) as e:
                logger.warning(f"D2 executable configured in environment at {d2_path} but failed: {e}, falling back to auto-detection")

        # Auto-detect in common locations
        possible_paths = [
            'd2',  # In PATH
            os.path.join(os.getcwd(), 'bin', 'd2.exe'),  # Windows local (project root)
            os.path.join(os.getcwd(), 'bin', 'd2'),  # Linux/Mac local (project root)
            os.path.join(os.getcwd(), 'D2', 'd2-v0.7.1', 'bin', 'd2.exe'),  # Windows project
            '/usr/local/bin/d2',  # macOS/Linux
            '/usr/bin/d2',  # Linux
        ]

        for path in possible_paths:
            try:
                result = subprocess.run([path, '--version'],
                                      capture_output=True,
                                      text=True,
                                      timeout=5)
                if result.returncode == 0:
                    logger.info(f"Found D2 executable at: {path}")
                    logger.info(f"D2 version: {result.stdout.strip()}")
                    return path
            except (subprocess.TimeoutExpired, FileNotFoundError, subprocess.CalledProcessError):
                continue

        return None
    
    def validate_d2_code(self, d2_code: str) -> Tuple[bool, str]:
        """
        Validate D2 code using the CLI

        Args:
            d2_code (str): The D2 code to validate

        Returns:
            Tuple[bool, str]: (is_valid, error_message)
        """
        if not d2_code or not d2_code.strip():
            return False, "D2 code is empty"

        # Check code length to prevent excessive memory usage
        if len(d2_code) > self.MAX_D2_CODE_LENGTH:
            return False, f"D2 code too large ({len(d2_code)} bytes). Maximum allowed: {self.MAX_D2_CODE_LENGTH} bytes"
        
        # Create temporary input file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.d2', delete=False) as temp_file:
            temp_file_name = temp_file.name
            temp_file.write(d2_code)
            temp_file.flush()
        
        try:
            # Run D2 to validate by attempting to render to stdout
            # Don't use -t flag to ensure validation matches actual rendering
            result = subprocess.run(
                [self.d2_executable, temp_file_name, '-'],
                capture_output=True,
                text=True,
                check=True,
                timeout=10
            )

            # Log validation success with output info
            logger.debug(f"D2 validation successful - output size: {len(result.stdout)} bytes")
            return True, "D2 Syntax is Valid."
            
        except subprocess.CalledProcessError as e:
            error_msg = e.stderr.strip() or e.stdout.strip() or "D2 validation failed"
            logger.error(f"D2 validation error: {error_msg}")
            return False, error_msg
            
        except subprocess.TimeoutExpired:
            error_msg = "D2 validation timed out"
            logger.error(error_msg)
            return False, error_msg
            
        except FileNotFoundError:
            error_msg = "D2 executable not found"
            logger.error(error_msg)
            return False, error_msg
            
        except Exception as e:
            error_msg = f"Unexpected error: {str(e)}"
            logger.error(error_msg)
            return False, error_msg
            
        finally:
            # Clean up temporary file
            try:
                if os.path.exists(temp_file_name):
                    os.unlink(temp_file_name)
            except Exception:
                pass
    
    def render_d2_to_svg(self, d2_code: str, output_dir: Optional[str] = None) -> Tuple[bool, str, Optional[str]]:
        """
        Render D2 code to SVG using the CLI

        Args:
            d2_code (str): The D2 code to render
            output_dir (Optional[str]): Directory to save the SVG. If None, uses temp directory.

        Returns:
            Tuple[bool, str, Optional[str]]: (success, error_message, svg_path_or_svg_content)
        """
        if not d2_code or not d2_code.strip():
            return False, "D2 code is empty", None

        # Check code length
        if len(d2_code) > self.MAX_D2_CODE_LENGTH:
            return False, f"D2 code too large ({len(d2_code)} bytes). Maximum allowed: {self.MAX_D2_CODE_LENGTH} bytes", None
        
        # Create temporary input file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.d2', delete=False) as temp_file:
            temp_file_name = temp_file.name
            temp_file.write(d2_code)
            temp_file.flush()
        
        # Determine output path
        if output_dir:
            os.makedirs(output_dir, exist_ok=True)
            svg_filename = f"{uuid.uuid4()}.svg"
            svg_path = os.path.join(output_dir, svg_filename)
        else:
            # Use temporary file
            svg_path = temp_file_name.replace('.d2', '.svg')
        
        try:
            # Run D2 to generate SVG
            result = subprocess.run(
                [self.d2_executable, temp_file_name, svg_path],
                capture_output=True,
                text=True,
                check=True,
                timeout=30
            )

            # Log rendering success
            if result.stdout:
                logger.debug(f"D2 render output: {result.stdout.strip()}")
            if result.stderr:
                logger.debug(f"D2 render stderr: {result.stderr.strip()}")

            # Check if output file was created
            if os.path.exists(svg_path) and os.path.getsize(svg_path) > 0:
                # Read the SVG content
                with open(svg_path, 'r', encoding='utf-8') as f:
                    svg_content = f.read()
                
                # Clean up temporary files if not using output_dir
                if not output_dir:
                    try:
                        os.unlink(svg_path)
                    except Exception:
                        pass
                
                return True, "", svg_content
            else:
                return False, "D2 produced no output", None
                
        except subprocess.CalledProcessError as e:
            error_msg = e.stderr.strip() or e.stdout.strip() or "D2 rendering failed"
            logger.error(f"D2 rendering error: {error_msg}")
            return False, f"D2 rendering error: {error_msg}", None
            
        except subprocess.TimeoutExpired:
            error_msg = "D2 rendering timed out"
            logger.error(error_msg)
            return False, error_msg, None
            
        except FileNotFoundError:
            error_msg = "D2 executable not found"
            logger.error(error_msg)
            return False, error_msg, None
            
        except Exception as e:
            error_msg = f"Unexpected error: {str(e)}"
            logger.error(error_msg)
            return False, error_msg, None
            
        finally:
            # Clean up temporary input file
            try:
                if os.path.exists(temp_file_name):
                    os.unlink(temp_file_name)
            except Exception:
                pass
    
    def render_d2_with_metadata(self, d2_code: str, metadata: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Render D2 code and return comprehensive result with metadata
        
        Args:
            d2_code (str): The D2 code to render
            metadata (Optional[Dict]): Additional metadata to include in the result
            
        Returns:
            Dict[str, Any]: Comprehensive render result
        """
        start_time = datetime.now()
        
        # Validate first
        is_valid, validation_error = self.validate_d2_code(d2_code)
        
        result = {
            "success": False,
            "svg_content": None,
            "validation": {
                "is_valid": is_valid,
                "error": validation_error if not is_valid else None
            },
            "metadata": {
                "render_time": None,
                "code_length": len(d2_code) if d2_code else 0,
                "timestamp": start_time.isoformat(),
                **(metadata or {})
            },
            "error": None
        }
        
        if not is_valid:
            result["error"] = validation_error
            return result
        
        # Render to SVG
        success, error_msg, svg_content = self.render_d2_to_svg(d2_code)
        
        end_time = datetime.now()
        render_time = (end_time - start_time).total_seconds()
        
        result["metadata"]["render_time"] = render_time
        result["success"] = success
        result["svg_content"] = svg_content
        
        if not success:
            result["error"] = error_msg
        
        return result
    
    def get_d2_info(self) -> Dict[str, Any]:
        """Get information about the D2 CLI installation"""
        try:
            result = subprocess.run(
                [self.d2_executable, '--version'],
                capture_output=True,
                text=True,
                timeout=5
            )
            
            return {
                "available": True,
                "executable": self.d2_executable,
                "version": result.stdout.strip(),
                "error": None
            }
        except Exception as e:
            return {
                "available": False,
                "executable": None,
                "version": None,
                "error": str(e)
            }

# Singleton instance
_d2_service = None

def get_d2_service() -> D2RenderService:
    """Get the singleton D2 service instance"""
    global _d2_service
    if _d2_service is None:
        _d2_service = D2RenderService()
    return _d2_service