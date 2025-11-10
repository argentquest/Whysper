"""
Kroki Base Provider - Common functionality for all Kroki-based diagram providers

This module provides shared functionality for all Kroki diagram providers:
- krokid2 (D2 diagrams)
- krokimermaid (Mermaid diagrams)
- krokistructurizr (Structurizr diagrams)
- krokic4 (C4 model diagrams)
- krokiplantuml (PlantUML diagrams)

All Kroki providers use the same HTTP-based API to communicate with a
local Kroki server, so this base class eliminates code duplication.
"""

from pathlib import Path
from typing import Optional, List
import requests
import logging

from diagrams.base_diagram import BaseDiagramProvider
from diagrams.models import (
    ProviderCapability,
    ValidationResult,
    RenderResult
)

from common.logging_decorator import log_method_call

logger = logging.getLogger(__name__)


class KrokiBaseProvider(BaseDiagramProvider):
    """
    Base class for all Kroki-based diagram providers.

    Subclasses should override:
    - provider_id: Unique identifier (e.g., 'krokid2')
    - provider_name: Human-readable name (e.g., 'Kroki D2 Renderer')
    - diagram_type: Primary diagram type (e.g., 'd2')
    - diagram_endpoint: Kroki API endpoint (e.g., 'd2', 'mermaid')
    - get_llm_correction_rules(): Language-specific rules

    Configuration (from config.json custom settings):
    - server_url: Kroki server URL (default: http://localhost:8000)
    - diagram_endpoint: API endpoint for diagram type
    - timeout_seconds: Request timeout (default: 30)
    - max_retries: Max retries for failed requests (default: 3)
    """

    @property
    def diagram_endpoint(self) -> str:
        """Kroki API endpoint for this diagram type (e.g., 'd2', 'mermaid')"""
        raise NotImplementedError(
            "Subclasses must define diagram_endpoint property"
        )

    @property
    def supported_output_formats(self) -> List[str]:
        """Output formats: SVG (fast, vector) and PNG (rasterized)"""
        return ["svg", "png"]

    @property
    def capabilities(self) -> List[ProviderCapability]:
        """All Kroki providers support: validation, rendering, auto-fix, LLM correction"""
        return [
            ProviderCapability.VALIDATE,
            ProviderCapability.RENDER_SVG,
            ProviderCapability.RENDER_PNG,
            ProviderCapability.AUTO_FIX,
            ProviderCapability.LLM_CORRECTION
        ]

    @log_method_call
    def __init__(self, provider_folder: Path):
        """
        Initialize Kroki base provider.

        Args:
            provider_folder: Path to provider folder containing config.json
        """
        super().__init__(provider_folder)

        # Get server configuration from config.json custom settings
        custom_settings = self.config.custom or {}
        self.server_url = custom_settings.get(
            "server_url", "http://localhost:8000"
        )
        self.timeout = custom_settings.get("timeout_seconds", 30)
        self.max_retries = custom_settings.get("max_retries", 3)

        # Cache server availability
        self._server_available = None

        self.logger.info(
            f"{self.provider_name} configured: "
            f"{self.server_url}/{self.diagram_endpoint}"
        )

    @log_method_call
    def is_available(self) -> bool:
        """Check if Kroki server is available"""
        if self._server_available is None:
            try:
                response = requests.get(
                    f"{self.server_url}/health",
                    timeout=5
                )

                self._server_available = response.status_code == 200
                if self._server_available:
                    self.logger.info(
                        f"Kroki server is available at {self.server_url}"
                    )
                else:
                    self.logger.warning(
                        f"Kroki server health check failed: "
                        f"{response.status_code}"
                    )
            except Exception as e:
                self.logger.warning(f"Kroki server not reachable: {e}")
                self._server_available = False

        return self._server_available

    @log_method_call
    def get_version(self) -> Optional[str]:
        """Get Kroki service version"""
        if not self.is_available():
            return None

        try:
            response = requests.get(
                f"{self.server_url}/version",
                timeout=5
            )

            if response.status_code == 200:
                return response.text.strip()
            return "Unknown"
        except Exception:
            return "Unknown"

    @log_method_call
    def validate_code(self, code: str, **options) -> ValidationResult:
        """
        Validate diagram code using Kroki service.

        This is the same across all Kroki providers - they all use
        the same HTTP endpoint validation mechanism.
        """
        if not self.is_available():
            return ValidationResult(
                is_valid=False,
                error="Kroki server not available",
                code_length=len(code)
            )

        self.logger.debug(
            f"Validating {self.diagram_type} code ({len(code)} chars)"
        )

        try:
            # Try to render to SVG for validation
            # Kroki will return error in response if syntax is invalid
            response = requests.post(
                f"{self.server_url}/{self.diagram_endpoint}/svg",
                data=code,
                headers={'Content-Type': 'text/plain'},
                timeout=self.timeout
            )

            if response.status_code == 200:
                return ValidationResult(
                    is_valid=True,
                    code_length=len(code)
                )
            else:
                # Extract error message from response
                error_msg = response.text
                if response.status_code == 400:
                    error_msg = (
                        f"{self.diagram_type.upper()} syntax error: {error_msg}"
                    )
                else:
                    error_msg = (
                        f"Kroki error ({response.status_code}): {error_msg}"
                    )

                return ValidationResult(
                    is_valid=False,
                    error=error_msg,
                    code_length=len(code)
                )
        except requests.exceptions.Timeout:
            return ValidationResult(
                is_valid=False,
                error="Validation request timed out",
                code_length=len(code)
            )
        except Exception as e:
            error_msg = f"Validation exception: {str(e)}"
            self.logger.error(error_msg, exc_info=True)
            return ValidationResult(
                is_valid=False,
                error=error_msg,
                code_length=len(code)
            )

    @log_method_call
    def auto_fix_pattern_based(
        self, code: str, error_message: str, **options
    ) -> ValidationResult:
        """
        Attempt pattern-based auto-fix for common syntax errors.

        This implements general fixes that work across all Kroki diagram types.
        Subclasses can override this to add diagram-specific fixes.

        Args:
            code: The invalid code
            error_message: The error message from validation
            **options: Provider-specific options

        Returns:
            ValidationResult with fixed code if successful
        """
        self.logger.info(
            f"Attempting pattern-based auto-fix for {self.diagram_type}..."
        )

        fixed_code = code
        corrections = []

        # General fix: Add missing braces for containers
        if '{' in fixed_code:
            open_count = fixed_code.count('{')
            close_count = fixed_code.count('}')
            if open_count > close_count:
                missing_braces = open_count - close_count
                fixed_code += '}' * missing_braces
                corrections.append(
                    f'Added {missing_braces} missing closing brace(s)'
                )

        # Validate fixed code
        validation_result = self.validate_code(fixed_code, **options)

        if validation_result.is_valid:
            validation_result.auto_fixed = True
            validation_result.fixed_code = fixed_code
            validation_result.correction_method = "pattern"
            if corrections:
                self.logger.info(
                    f"Pattern-based fixes applied: {', '.join(corrections)}"
                )
        else:
            self.logger.debug("Pattern-based fix did not resolve errors")

        return validation_result

    @log_method_call
    def render(
        self, code: str, output_format: str = "svg", **options
    ) -> RenderResult:
        """
        Render diagram to specified format using Kroki.

        This is the same across all Kroki providers - they all use
        the same HTTP rendering mechanism.
        """
        if not self.is_available():
            return RenderResult(
                success=False,
                content=None,
                output_format=output_format,
                validation=ValidationResult(
                    is_valid=False,
                    error="Kroki server not available",
                    code_length=len(code)
                ),
                metadata={},
                error="Kroki server not available"
            )

        # Validate supported format
        if output_format.lower() not in ["svg", "png"]:
            return RenderResult(
                success=False,
                content=None,
                output_format=output_format,
                validation=ValidationResult(
                    is_valid=False,
                    error=f"Unsupported output format: {output_format}",
                    code_length=len(code)
                ),
                metadata={},
                error=f"Unsupported output format: {output_format}"
            )

        self.logger.debug(
            f"Rendering {self.diagram_type} to {output_format.upper()}..."
        )

        try:
            # Render via Kroki API
            response = requests.post(
                f"{self.server_url}/{self.diagram_endpoint}/{output_format}",
                data=code,
                headers={'Content-Type': 'text/plain'},
                timeout=self.timeout
            )

            if response.status_code == 200:
                # SVG is text, PNG is binary
                if output_format == 'svg':
                    content = response.text
                    output_size = len(content)
                else:
                    content = response.content
                    output_size = len(content)

                return RenderResult(
                    success=True,
                    content=content,
                    output_format=output_format,
                    validation=ValidationResult(
                        is_valid=True, code_length=len(code)
                    ),
                    metadata={
                        "provider": self.provider_id,
                        "output_size_bytes": output_size,
                        "server_url": self.server_url,
                        "render_time": (
                            response.elapsed.total_seconds()
                            if hasattr(response, 'elapsed') else None
                        )
                    }
                )
            else:
                error_msg = response.text
                self.logger.error(f"Rendering failed: {error_msg[:200]}")
                return RenderResult(
                    success=False,
                    content=None,
                    output_format=output_format,
                    validation=ValidationResult(
                        is_valid=False,
                        error=error_msg,
                        code_length=len(code)
                    ),
                    metadata={"server_url": self.server_url},
                    error=error_msg
                )
        except requests.exceptions.Timeout:
            error_msg = (
                f"Rendering request timed out after {self.timeout} seconds"
            )
            self.logger.error(error_msg)
            return RenderResult(
                success=False,
                content=None,
                output_format=output_format,
                validation=ValidationResult(
                    is_valid=False,
                    error=error_msg,
                    code_length=len(code)
                ),
                metadata={"server_url": self.server_url},
                error=error_msg
            )
        except Exception as e:
            error_msg = f"Rendering exception: {str(e)}"
            self.logger.error(error_msg, exc_info=True)
            return RenderResult(
                success=False,
                content=None,
                output_format=output_format,
                validation=ValidationResult(
                    is_valid=False,
                    error=error_msg,
                    code_length=len(code)
                ),
                metadata={"server_url": self.server_url},
                error=error_msg
            )