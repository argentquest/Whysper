"""
Mermaid Rendering Service
Handles Mermaid diagram validation and rendering using the Mermaid CLI (mmdc)
"""

import logging
from typing import Dict, Any, Tuple, Optional
from datetime import datetime

from mvp_diagram_generator.mermaid_cli_validator import (
    validate_mermaid_with_cli,
    is_mermaid_cli_available,
    validate_and_fix_mermaid_with_cli,
    validate_mermaid_and_render
)

logger = logging.getLogger(__name__)


class MermaidRenderService:
    """Service for validating and rendering Mermaid diagrams"""

    def __init__(self, mermaid_executable: str = "mmdc"):
        """
        Initialize the Mermaid render service

        Args:
            mermaid_executable: Path to mmdc executable
        """
        self.mermaid_executable = mermaid_executable
        self._cli_available = None
        logger.info(f"Initialized MermaidRenderService with executable: {mermaid_executable}")

    def validate_mermaid_code(self, mermaid_code: str) -> Tuple[bool, Optional[str]]:
        """
        Validate Mermaid code syntax

        Args:
            mermaid_code: The Mermaid code to validate

        Returns:
            Tuple of (is_valid, error_message)
        """
        logger.info(f"[MERMAID VALIDATE] Starting validation for {len(mermaid_code)} character code")
        logger.debug(f"[MERMAID VALIDATE] Code preview (first 100 chars): {mermaid_code[:100]}")

        try:
            is_valid, message = validate_mermaid_with_cli(mermaid_code, self.mermaid_executable)

            if is_valid:
                logger.info(f"[MERMAID VALIDATE] ✅ Validation successful")
            else:
                logger.warning(f"[MERMAID VALIDATE] ❌ Validation failed")
                logger.warning(f"[MERMAID VALIDATE] Error: {message[:200] if message else 'Unknown error'}")

            return (is_valid, None if is_valid else message)
        except Exception as e:
            logger.error(f"[MERMAID VALIDATE] Exception during validation: {e}", exc_info=True)
            return (False, f"Validation failed: {str(e)}")

    def render_mermaid_with_metadata(
        self,
        mermaid_code: str,
        metadata: Optional[Dict[str, Any]] = None,
        output_format: str = "svg"
    ) -> Dict[str, Any]:
        """
        Render Mermaid diagram with metadata tracking

        Args:
            mermaid_code: The Mermaid code to render
            metadata: Optional metadata to track
            output_format: Output format ('svg' or 'png')

        Returns:
            Dictionary containing render results
        """
        start_time = datetime.now()
        logger.info(f"[MERMAID RENDER] Starting render request for {output_format.upper()}")
        logger.info(f"[MERMAID RENDER] Code length: {len(mermaid_code)} characters")
        logger.debug(f"[MERMAID RENDER] Metadata: {metadata}")

        # First validate
        logger.info(f"[MERMAID RENDER] Step 1/3: Validating syntax...")
        is_valid, error_message = self.validate_mermaid_code(mermaid_code)

        validation_result = {
            "is_valid": is_valid,
            "error": error_message,
            "code_length": len(mermaid_code)
        }

        if not is_valid:
            # Try to auto-fix
            logger.info(f"[MERMAID RENDER] Step 2/3: Validation failed, attempting auto-fix...")
            logger.info(f"[MERMAID RENDER] Original error: {error_message[:200] if error_message else 'Unknown'}")

            is_fixed, fixed_code, fix_message = validate_and_fix_mermaid_with_cli(
                mermaid_code, max_attempts=3
            )

            if is_fixed:
                logger.info(f"[MERMAID RENDER] ✅ Auto-fix successful!")
                logger.info(f"[MERMAID RENDER] Fix message: {fix_message}")
                logger.debug(f"[MERMAID RENDER] Code changes: {len(mermaid_code)} → {len(fixed_code)} chars")

                mermaid_code = fixed_code
                validation_result["is_valid"] = True
                validation_result["auto_fixed"] = True
                validation_result["fix_message"] = fix_message
                validation_result["error"] = None
            else:
                logger.error(f"[MERMAID RENDER] ❌ Auto-fix failed after 3 attempts")
                logger.error(f"[MERMAID RENDER] Final error: {error_message}")

                return {
                    "success": False,
                    "svg_content": None,
                    "validation": validation_result,
                    "metadata": {
                        "render_time": 0,
                        "timestamp": datetime.now().isoformat(),
                        "attempted_auto_fix": True,
                        "auto_fix_failed": True,
                        **(metadata or {})
                    },
                    "error": error_message
                }

        # Render the diagram
        logger.info(f"[MERMAID RENDER] Step 3/3: Rendering diagram to {output_format.upper()}...")

        try:
            is_valid_render, render_message, rendered_output = validate_mermaid_and_render(
                mermaid_code,
                output_format=output_format,
                mermaid_executable=self.mermaid_executable
            )

            if is_valid_render:
                duration = (datetime.now() - start_time).total_seconds()
                output_size = len(rendered_output) if rendered_output else 0

                logger.info(f"[MERMAID RENDER] ✅ Rendering successful!")
                logger.info(f"[MERMAID RENDER] Duration: {duration:.2f}s")
                logger.info(f"[MERMAID RENDER] Output size: {output_size} bytes ({output_size/1024:.1f} KB)")

                return {
                    "success": True,
                    "svg_content": rendered_output if output_format == "svg" else None,
                    "png_content": rendered_output if output_format == "png" else None,
                    "validation": validation_result,
                    "metadata": {
                        "render_time": duration,
                        "timestamp": datetime.now().isoformat(),
                        "output_format": output_format,
                        "code_length": len(mermaid_code),
                        "output_size_bytes": output_size,
                        **(metadata or {})
                    },
                    "error": None
                }
            else:
                duration = (datetime.now() - start_time).total_seconds()
                logger.error(f"[MERMAID RENDER] ❌ Rendering failed after {duration:.2f}s")
                logger.error(f"[MERMAID RENDER] Error: {render_message[:300] if render_message else 'Unknown error'}")

                return {
                    "success": False,
                    "svg_content": None,
                    "validation": validation_result,
                    "metadata": {
                        "render_time": duration,
                        "timestamp": datetime.now().isoformat(),
                        **(metadata or {})
                    },
                    "error": render_message
                }

        except Exception as e:
            duration = (datetime.now() - start_time).total_seconds()
            logger.error(f"[MERMAID RENDER] ❌ Exception during rendering after {duration:.2f}s")
            logger.error(f"[MERMAID RENDER] Exception: {str(e)}", exc_info=True)

            return {
                "success": False,
                "svg_content": None,
                "validation": validation_result,
                "metadata": {
                    "render_time": duration,
                    "timestamp": datetime.now().isoformat(),
                    "exception": str(e),
                    **(metadata or {})
                },
                "error": f"Rendering failed: {str(e)}"
            }

    def get_mermaid_info(self) -> Dict[str, Any]:
        """
        Get information about Mermaid CLI installation

        Returns:
            Dictionary with Mermaid CLI information
        """
        try:
            available = is_mermaid_cli_available(self.mermaid_executable)

            if available:
                # Try to get version
                import subprocess
                try:
                    result = subprocess.run(
                        [self.mermaid_executable, "--version"],
                        capture_output=True,
                        text=True,
                        timeout=5,
                        shell=True
                    )
                    version = result.stdout.strip()
                except Exception:
                    version = "Unknown"

                return {
                    "available": True,
                    "executable": self.mermaid_executable,
                    "version": version,
                    "error": None
                }
            else:
                return {
                    "available": False,
                    "executable": self.mermaid_executable,
                    "version": None,
                    "error": "Mermaid CLI (mmdc) not found. Install with: npm install -g @mermaid-js/mermaid-cli"
                }

        except Exception as e:
            logger.error(f"Error getting Mermaid info: {e}")
            return {
                "available": False,
                "executable": self.mermaid_executable,
                "version": None,
                "error": str(e)
            }


# Singleton instance
_mermaid_service_instance = None


def get_mermaid_service() -> MermaidRenderService:
    """Get the singleton Mermaid render service instance"""
    global _mermaid_service_instance

    if _mermaid_service_instance is None:
        _mermaid_service_instance = MermaidRenderService()

    return _mermaid_service_instance
