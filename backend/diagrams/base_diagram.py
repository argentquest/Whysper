"""
Base Diagram Provider

Abstract base class for all diagram providers.
Provides common functionality and enforces provider interface.
"""

from abc import ABC, abstractmethod
from pathlib import Path
from typing import Optional, List, Dict, Any, Callable, Awaitable
from datetime import datetime
import logging
import asyncio

from .provider_config import ProviderConfig, load_provider_config
from .models import (
    ProviderCapability,
    ValidationResult,
    RenderResult,
    ProviderMetadata
)
from common.logging_decorator import log_method_call


class BaseDiagramProvider(ABC):
    """
    Abstract base class for all diagram providers.

    ARCHITECTURE OVERVIEW:
    The provider system is designed around concept of self-contained, pluggable
    diagram renderers. Each provider is a folder containing:
    - config.json: Provider configuration and overrides
    - {provider}_renderer.py: Implementation of BaseDiagramProvider
    - README.md: Documentation for adding/modifying provider

    PROVIDER RESPONSIBILITIES:
    1. Validation: Check if diagram code is syntactically correct
    2. Rendering: Convert diagram code to output formats (SVG, PNG, etc.)
    3. Auto-fixing: Attempt to correct syntax errors (pattern-based and LLM-based)
    4. Metadata: Report capabilities, version, availability

    CORRECTION STRATEGY (Three-Tier):
    Tier 1 - Pattern-Based (Fast, Free, Deterministic):
        - Regex-based fixes for common errors
        - No network calls, instant results
        - Example: Add missing braces, fix arrow spacing

    Tier 2 - LLM-Based (Slower, Costs Tokens, Intelligent):
        - AI-powered correction for complex syntax issues
        - Uses provider-specific rules via get_llm_correction_rules()
        - Retries with feedback loop (validates corrected code)
        - Example: Restructure diagram logic, fix semantic issues

    Tier 3 - User Manual (Last Resort):
        - Show error message to user for manual fix
        - Used when both automated methods fail
        - Provides clear error descriptions from CLI

    RENDERING PIPELINE:
    The render_with_validation() method orchestrates full pipeline:

    1. Initial Validation → validate_code()
       ↓ (if invalid)
    2. Pattern-Based Fix → auto_fix_pattern_based()
       ↓ (if still invalid)
    3. LLM Correction → _attempt_llm_correction()
       ↓ (with retry loop up to max_retries)
    4. Final Render → render()
       ↓
    5. Return RenderResult with metadata

    PROVIDER IDENTIFICATION:
    Each provider is identified by its folder name (provider_id).
    Example folder structure:
        backend/diagrams/
        ├── mermaidv1/           # provider_id = "mermaidv1"
        │   ├── config.json
        │   └── mermaid_renderer.py
        ├── d2v1/                # provider_id = "d2v1"
        │   ├── config.json
        │   └── d2_renderer.py
        └── base_diagram.py      # This file

    CONFIGURATION HIERARCHY:
    Root config (backend/diagrams/config.json)
        ↓ (provides defaults)
    Provider config (backend/diagrams/{provider}/config.json)
        ↓ (overrides specific settings)
    Runtime options (**options parameter)

    DESIGN PATTERNS USED:
    - Template Method: render_with_validation() defines skeleton, subclasses fill steps
    - Strategy: Different correction strategies (pattern vs LLM)
    - Factory: ProviderRegistry creates provider instances
    - Singleton: Each provider is instantiated once per registry
    """

    @log_method_call
    def __init__(self, provider_folder: Path):
        """
        Initialize provider.

        Args:
            provider_folder: Path to the provider's folder (contains config.json)
        """
        logging.getLogger(__name__).info(
            "Initializing BaseDiagramProvider",
            extra={"provider_folder": str(provider_folder)}
        )
        self.provider_folder = provider_folder
        self.config = self._load_config()
        self.logger = self._setup_logging()
        self._llm_correction_service = None

        if not self.config:
            raise RuntimeError(f"Failed to load config for provider in {provider_folder}")

        self._validate_config()

        self.logger.info(
            f"✅ Initialized {self.config.provider_name} "
            f"(LLM retries: {self.config.llm_correction.max_retries}, "
            f"strategy: {self.config.correction_strategy})"
        )
        self.logger.info("Completed BaseDiagramProvider initialization")

    @log_method_call
    def _load_config(self) -> Optional[ProviderConfig]:
        """Load configuration from config.json in provider folder"""
        logging.getLogger(__name__).info(
            "Loading provider config",
            extra={"provider_folder": str(self.provider_folder)}
        )
        config = load_provider_config(self.provider_folder)

        if config:
            self.logger = logging.getLogger(f"diagrams.{config.provider_id}")
            self.logger.info(f"Loaded config for {config.provider_name}")

        logging.getLogger(__name__).info(
            "Completed provider config load",
            extra={"provider_id": getattr(config, 'provider_id', None)}
        )
        return config

    @log_method_call
    def _validate_config(self):
        """Validate that config matches provider implementation"""
        self.logger.info(
            "Validating provider config",
            extra={
                "config_provider_id": self.config.provider_id,
                "impl_provider_id": self.provider_id
            }
        )
        if self.config.provider_id != self.provider_id:
            self.logger.info(
                f"Config provider_id '{self.config.provider_id}' does not match "
                f"implementation provider_id '{self.provider_id}'"
            )
        self.logger.info("Completed provider config validation")

    @log_method_call
    def _setup_logging(self):
        """Setup logging for this provider"""
        logging.getLogger(__name__).info(
            "Setting up provider logger",
            extra={"provider_id": getattr(self, 'provider_id', None)}
        )
        if hasattr(self, 'config') and self.config:
            return logging.getLogger(f"diagrams.{self.config.provider_id}")
        return logging.getLogger(f"diagrams.{self.provider_folder.name}")

    # =====================================================================
    # ABSTRACT PROPERTIES - Must be implemented by subclasses
    # =====================================================================

    @property
    @abstractmethod
    def provider_id(self) -> str:
        """
        Unique identifier for this provider (same as folder name).
        Example: "mermaidv1", "d2v1", "mermaid-playwright"
        """
        pass

    @property
    @abstractmethod
    def provider_name(self) -> str:
        """
        Human-readable name for this provider.
        Example: "Mermaid CLI Renderer v1", "D2 CLI Renderer v1"
        """
        pass

    @property
    @abstractmethod
    def diagram_type(self) -> str:
        """
        Primary diagram type this provider handles.
        Example: "mermaid", "d2", "plantuml"
        """
        pass

    @property
    @abstractmethod
    def supported_output_formats(self) -> List[str]:
        """
        List of output formats this provider supports.
        Example: ["mermaid", "svg", "png"]
        """
        pass

    @property
    @abstractmethod
    def capabilities(self) -> List[ProviderCapability]:
        """
        List of capabilities this provider supports.
        Example: [VALIDATE, RENDER_SVG, RENDER_PNG, AUTO_FIX, LLM_CORRECTION]
        """
        pass

    # =====================================================================
    # ABSTRACT METHODS - Must be implemented by subclasses
    # =====================================================================

    @abstractmethod
    def validate_code(self, code: str, **options) -> ValidationResult:
        """
        Validate diagram code.

        Args:
            code: The diagram code to validate
            **options: Provider-specific options

        Returns:
            ValidationResult with validation status and errors
        """
        pass

    @abstractmethod
    def render(
        self,
        code: str,
        output_format: str = "svg",
        **options
    ) -> RenderResult:
        """
        Render diagram code to specified format.

        Args:
            code: The diagram code to render
            output_format: Desired output format (svg, png, pdf, or diagram type)
            **options: Provider-specific options

        Returns:
            RenderResult with rendered content and metadata
        """
        pass

    @abstractmethod
    def get_version(self) -> Optional[str]:
        """Get version of underlying tool/library"""
        pass

    @abstractmethod
    def is_available(self) -> bool:
        """Check if provider is available and properly configured"""
        pass

    # =====================================================================
    # OPTIONAL METHODS - Can be overridden for pattern-based auto-fix
    # =====================================================================

    @log_method_call
    def auto_fix_pattern_based(self, code: str, error_message: str, **options) -> ValidationResult:
        """
        Attempt pattern-based auto-fix (override in subclass for custom logic).

        This is for simple, deterministic fixes like:
        - Adding missing diagram type declarations
        - Fixing arrow spacing
        - Fixing quote syntax
        - etc.

        Args:
            code: The invalid code
            error_message: The error message from validation
            **options: Provider-specific options

        Returns:
            ValidationResult with fixed code if successful
        """
        self.logger.info(
            "Starting default auto_fix_pattern_based",
            extra={"code_length": len(code)}
        )
        # Default implementation: no pattern-based fixing
        result = ValidationResult(
            is_valid=False,
            error=error_message,
            auto_fixed=False,
            code_length=len(code)
        )
        self.logger.info(
            "Completed default auto_fix_pattern_based",
            extra={"auto_fixed": result.auto_fixed}
        )
        return result

    @log_method_call
    def get_llm_correction_rules(self) -> Optional[str]:
        """
        Get provider-specific rules for LLM correction.
        Override in subclass to provide custom rules.

        Returns:
            String with provider-specific correction rules
        """
        self.logger.info("Retrieving LLM correction rules (base default)")
        return None

    # =====================================================================
    # CONCRETE METHODS - Provided by base class
    # =====================================================================

    async def _send_progress(
        self,
        progress_callback: Optional[Callable[[Dict[str, Any]], Awaitable[None]]],
        update: Dict[str, Any]
    ):
        """
        Send progress update via callback if provided.

        Args:
            progress_callback: Optional async callback function
            update: Progress update data to send
        """
        if progress_callback:
            await progress_callback(update)

    @log_method_call
    def set_llm_correction_service(self, service):
        """Set LLM correction service for this provider"""
        self._llm_correction_service = service

    @log_method_call
    def get_config(self) -> ProviderConfig:
        """Get current configuration"""
        return self.config

    @log_method_call
    def reload_config(self) -> bool:
        """
        Reload configuration from config.json.
        Useful for runtime config updates.

        Returns:
            True if reload successful, False otherwise
        """
        self.logger.info("Starting config reload", extra={"provider_id": self.provider_id})
        try:
            new_config = load_provider_config(self.provider_folder)
            if new_config:
                self.config = new_config
                self.logger.info(f"Config reloaded for {self.provider_id}")
                return True
            return False
        except Exception as e:
            self.logger.info(f"Failed to reload config: {e}")
            return False
        finally:
            self.logger.info("Completed config reload attempt", extra={"provider_id": self.provider_id})

    @log_method_call
    def get_metadata(self) -> ProviderMetadata:
        """Get comprehensive metadata about this provider"""
        self.logger.info("Gathering provider metadata", extra={"provider_id": self.provider_id})
        return ProviderMetadata(
            provider_id=self.provider_id,
            provider_name=self.provider_name,
            diagram_type=self.diagram_type,
            supported_output_formats=self.supported_output_formats,
            capabilities=self.capabilities,
            version=self.get_version(),
            available=self.is_available(),
            description=self.config.description or self.__doc__,
            requires_llm=ProviderCapability.LLM_CORRECTION in self.capabilities
        )

    @log_method_call
    def supports_capability(self, capability: ProviderCapability) -> bool:
        """Check if this provider supports a specific capability"""
        self.logger.info(
            "Checking capability support",
            extra={"provider_id": self.provider_id, "capability": capability.name}
        )
        return capability in self.capabilities

    @log_method_call
    def supports_output_format(self, output_format: str) -> bool:
        """Check if this provider supports a specific output format"""
        self.logger.info(
            "Checking output format support",
            extra={"provider_id": self.provider_id, "format": output_format}
        )
        return output_format.lower() in [fmt.lower() for fmt in self.supported_output_formats]

    @log_method_call
    async def render_with_validation(
        self,
        code: str,
        output_format: str = "svg",
        auto_fix: Optional[bool] = None,
        llm_correction: Optional[bool] = None,
        max_retries: Optional[int] = None,
        model: Optional[str] = None,
        progress_callback: Optional[Callable[[Dict[str, Any]], Awaitable[None]]] = None,
        **options
    ) -> RenderResult:
        """
        Render with automatic validation and correction (template method pattern).

        THIS IS THE CORE METHOD OF THE PROVIDER SYSTEM.
        It orchestrates complete rendering pipeline with error correction.

        PIPELINE FLOW:
        ┌─────────────────────────────────────────────────────────────────┐
        │ 1. VALIDATE CODE                                                │
        │    - Check syntax using provider's validate_code()             │
        │    - Get error messages from CLI/parser                        │
        └─────────────────────────────────────────────────────────────────┘
                              ↓
                       [Code Valid?] ──Yes──> Skip to Step 4
                              ↓ No
        ┌─────────────────────────────────────────────────────────────────┐
        │ 2. PATTERN-BASED AUTO-FIX (if enabled)                          │
        │    - Fast, deterministic corrections                            │
        │    - Regex-based rules (e.g., fix spacing, add braces)         │
        │    - No network calls or AI required                            │
        │    - Validate fixed code                                        │
        └─────────────────────────────────────────────────────────────────┘
                              ↓
                       [Code Valid?] ──Yes──> Skip to Step 4
                              ↓ No
        ┌─────────────────────────────────────────────────────────────────┐
        │ 3. LLM-BASED CORRECTION (if enabled)                            │
        │    - AI-powered intelligent correction                          │
        │    - Uses provider-specific correction rules                    │
        │    - Retry loop with validation feedback                        │
        │    - Max retries configurable (default: 8)                      │
        │    - Each iteration validates and provides new errors           │
        └─────────────────────────────────────────────────────────────────┘
                              ↓
                       [Code Valid?] ──Yes──> Continue
                              ↓ No
                        Return error to user
                              ↓
        ┌─────────────────────────────────────────────────────────────────┐
        │ 4. RENDER DIAGRAM                                                │
        │    - Call provider's render() with validated code               │
        │    - Generate requested output format (SVG/PNG/etc.)           │
        │    - Track metadata (timing, size, corrections applied)         │
        └─────────────────────────────────────────────────────────────────┘

        CONFIGURATION PRECEDENCE:
        Runtime parameters > Provider config > Root config

        Example:
            render_with_validation(
                code="x -> y",
                auto_fix=True,        # Override config
                llm_correction=False  # Override config
            )

        PERFORMANCE CHARACTERISTICS:
        - No correction: ~100-300ms (validation + rendering)
        - Pattern-based: +10-50ms (regex operations)
        - LLM correction: +2-10s per attempt (network + AI processing)

        ERROR HANDLING:
        - Validation errors: Returns RenderResult with error details
        - CLI not available: Returns immediate error
        - LLM timeout: Falls back to showing validation error
        - Rendering failure: Returns error with successful validation

        Args:
            code: Diagram code to render
            output_format: Desired output format ('svg', 'png', diagram type)
            auto_fix: Enable pattern-based auto-fix (None = use config default)
            llm_correction: Enable LLM-based correction (None = use config default)
            max_retries: Maximum LLM correction attempts (None = use config default)
            model: LLM model to use (None = use config default)
            progress_callback: Optional callback for progress updates
            **options: Provider-specific rendering options

        Returns:
            RenderResult with:
                - success: True if rendered successfully
                - content: Rendered output (SVG string, PNG base64, etc.)
                - validation: ValidationResult with correction details
                - metadata: Timing, provider info, correction method used
                - error: Error message if unsuccessful

        Example Usage:
            >>> provider = registry.get_provider("d2v1")
            >>> result = provider.render_with_validation(
            ...     code="x -> y",
            ...     output_format="svg",
            ...     auto_fix=True
            ... )
            >>> if result.success:
            ...     print(f"Rendered {len(result.content)} bytes")
            ...     if result.validation.auto_fixed:
            ...         print("Code was auto-fixed")
        """
        start_time = datetime.now()

        # ===== Configuration Resolution =====
        # Use runtime parameters if provided, otherwise fall back to config
        # This allows per-request overrides while respecting global config
        auto_fix = auto_fix if auto_fix is not None else self.config.pattern_correction.enabled
        llm_correction = llm_correction if llm_correction is not None else self.config.llm_correction.enabled
        max_retries = max_retries if max_retries is not None else self.config.llm_correction.max_retries

        self.logger.info(
            f"[{self.provider_id}] Starting render pipeline for {output_format} "
            f"(auto_fix={auto_fix}, llm={llm_correction}, max_retries={max_retries})"
        )
        self.logger.debug(f"[{self.provider_id}] Code length: {len(code)} chars")

        # Check output format support
        if not self.supports_output_format(output_format):
            return RenderResult(
                success=False,
                content=None,
                output_format=output_format,
                validation=ValidationResult(
                    is_valid=False,
                    error=f"Output format '{output_format}' not supported by {self.provider_id}",
                    code_length=len(code)
                ),
                metadata=self._create_metadata(start_time),
                error=f"Unsupported output format: {output_format}"
            )

        # Step 1: Initial validation
        self.logger.info(f"[{self.provider_id}] Step 1/4: Validating code...")
        await self._send_progress(progress_callback, {
            "status": "validating",
            "message": f"Validating {self.diagram_type} code...",
            "step": "1/4"
        })

        validation_result = self.validate_code(code, **options)
        current_code = code

        # Step 2: Pattern-based auto-fix
        if not validation_result.is_valid and auto_fix and self.supports_capability(ProviderCapability.AUTO_FIX):
            self.logger.info(f"[{self.provider_id}] Step 2/4: Attempting pattern-based auto-fix...")
            await self._send_progress(progress_callback, {
                "status": "auto_fixing",
                "message": f"Attempting pattern-based auto-fix for {self.diagram_type}...",
                "step": "2/4"
            })

            validation_result = self.auto_fix_pattern_based(
                current_code, validation_result.error, **options
            )

            if validation_result.auto_fixed and validation_result.fixed_code:
                current_code = validation_result.fixed_code
                self.logger.info(f"[{self.provider_id}] ✅ Pattern-based fix successful")
                await self._send_progress(progress_callback, {
                    "status": "auto_fixed",
                    "message": f"✅ Pattern-based fix successful",
                    "step": "2/4"
                })

        # Step 3: LLM-based correction
        if not validation_result.is_valid and llm_correction and self.supports_capability(ProviderCapability.LLM_CORRECTION):
            self.logger.info(f"[{self.provider_id}] Step 3/4: Attempting LLM-based correction...")
            await self._send_progress(progress_callback, {
                "status": "llm_correcting",
                "message": f"Attempting AI-powered correction for {self.diagram_type}...",
                "step": "3/4",
                "max_retries": max_retries
            })

            validation_result = await self._attempt_llm_correction(
                current_code, validation_result.error, max_retries, model, progress_callback, **options
            )

            if validation_result.llm_corrected and validation_result.fixed_code:
                current_code = validation_result.fixed_code
                self.logger.info(f"[{self.provider_id}] ✅ LLM correction successful")
                await self._send_progress(progress_callback, {
                    "status": "llm_corrected",
                    "message": f"✅ AI correction successful",
                    "step": "3/4"
                })

        # If still invalid, try to render anyway as best attempt
        if not validation_result.is_valid:
            duration = (datetime.now() - start_time).total_seconds()
            self.logger.info(
                f"[{self.provider_id}] ⚠️  Validation failed after all "
                f"attempts ({duration:.2f}s). Attempting render anyway..."
            )

            # Try to render the best-attempt code even if validation failed
            # This allows users to see what was attempted
            try:
                render_result = self.render(
                    current_code, output_format, **options
                )
                render_result.validation = validation_result
                render_result.metadata.update(
                    self._create_metadata(start_time)
                )
                # Mark as failed even if render succeeded, since validation
                # failed
                render_result.success = False
                render_result.error = (
                    f"Validation failed: {validation_result.error}. "
                    f"Rendered best attempt."
                )
                return render_result
            except Exception as e:
                self.logger.info(
                    f"[{self.provider_id}] Render of invalid code "
                    f"also failed: {e}"
                )
                return RenderResult(
                    success=False,
                    content=current_code,  # Return code for debugging
                    output_format="text",
                    validation=validation_result,
                    metadata=self._create_metadata(start_time),
                    error=validation_result.error
                )

        # Step 4: Render
        self.logger.info(f"[{self.provider_id}] Step 4/4: Rendering to {output_format}...")
        await self._send_progress(progress_callback, {
            "status": "rendering",
            "message": f"Rendering {self.diagram_type} to {output_format.upper()}...",
            "step": "4/4"
        })

        render_result = self.render(current_code, output_format, **options)

        if render_result.success:
            await self._send_progress(progress_callback, {
                "status": "render_complete",
                "message": f"? {self.diagram_type} rendered successfully",
                "step": "4/4"
            })
            if render_result.output_format.lower() == "svg" and render_result.content:
                self.logger.info(
                    "SVG output",
                    extra={"svg": render_result.content}
                )

        # Update metadata
        duration = (datetime.now() - start_time).total_seconds()
        render_result.metadata.update(self._create_metadata(start_time))
        render_result.validation = validation_result

        if render_result.success:
            self.logger.info(f"[{self.provider_id}] ? Render successful ({duration:.2f}s)")
        else:
            self.logger.info(f"[{self.provider_id}] ? Render failed ({duration:.2f}s)")

        self.logger.info(
            "Completed render_with_validation",
            extra={"provider_id": self.provider_id, "duration_sec": duration, "success": render_result.success}
        )
        return render_result

    @log_method_call
    async def _attempt_llm_correction(
        self,
        code: str,
        error_message: str,
        max_retries: int,
        model: Optional[str] = None,
        progress_callback: Optional[Callable[[Dict[str, Any]], Awaitable[None]]] = None,
        **options
    ) -> ValidationResult:
        """Attempt LLM-based correction with retries"""
        self.logger.info(
            "Starting _attempt_llm_correction",
            extra={"provider_id": self.provider_id, "max_retries": max_retries}
        )

        if not self._llm_correction_service or not self._llm_correction_service.is_available():
            self.logger.info(f"[{self.provider_id}] LLM correction service not available")
            return ValidationResult(
                is_valid=False,
                error=error_message,
                llm_corrected=False,
                code_length=len(code)
            )

        current_code = code
        current_error = error_message

        for attempt in range(1, max_retries + 1):
            self.logger.info(f"[{self.provider_id}] LLM correction attempt {attempt}/{max_retries}")

            # Send progress update for retry attempt
            await self._send_progress(progress_callback, {
                "status": "llm_correcting",
                "message": f"AI correction attempt {attempt}/{max_retries}...",
                "step": "3/4",
                "attempt": attempt,
                "max_retries": max_retries
            })

            # Request correction from LLM
            # Use session model if provided, otherwise fall back to config
            llm_model = model or self.config.llm_correction.model_override
            success, corrected_code, message = self._llm_correction_service.correct_diagram_code(
                diagram_type=self.diagram_type,
                invalid_code=current_code,
                error_message=current_error,
                provider_specific_rules=self.get_llm_correction_rules(),
                max_tokens=self.config.llm_correction.max_tokens,
                temperature=self.config.llm_correction.temperature,
                model=llm_model
            )

            if not success:
                self.logger.info(f"[{self.provider_id}] LLM correction failed: {message}")
                continue

            # Validate corrected code
            validation_result = self.validate_code(corrected_code, **options)

            if validation_result.is_valid:
                # Success!
                validation_result.llm_corrected = True
                validation_result.fixed_code = corrected_code
                validation_result.correction_method = "llm"
                self.logger.info(f"[{self.provider_id}] ✅ LLM correction succeeded on attempt {attempt}")
                self.logger.info(
                    "Completed _attempt_llm_correction",
                    extra={"provider_id": self.provider_id, "attempt": attempt, "success": True}
                )
                return validation_result
            else:
                # Try again with new error
                current_code = corrected_code
                current_error = validation_result.error
                self.logger.info(
                    f"[{self.provider_id}] LLM correction attempt {attempt} still invalid: "
                    f"{current_error[:100] if current_error else 'Unknown error'}"
                )

        # All attempts failed
        self.logger.info(f"[{self.provider_id}] ❌ LLM correction failed after {max_retries} attempts")
        result = ValidationResult(
            is_valid=False,
            error=current_error,
            llm_corrected=False,
            code_length=len(current_code)
        )
        self.logger.info(
            "Completed _attempt_llm_correction",
            extra={"provider_id": self.provider_id, "success": result.is_valid}
        )
        return result

    @log_method_call
    def _create_metadata(self, start_time: datetime) -> Dict[str, Any]:
        """Create standard metadata dictionary"""
        self.logger.info(
            "Creating metadata",
            extra={"provider_id": self.provider_id}
        )
        return {
            "provider": self.provider_id,
            "provider_name": self.provider_name,
            "render_time": (datetime.now() - start_time).total_seconds(),
            "timestamp": datetime.now().isoformat()
        }

    # =====================================================================
    # BATCH RENDERING - Optional override
    # =====================================================================

    @log_method_call
    def render_batch(
        self,
        codes: List[str],
        output_format: str = "svg",
        **options
    ) -> List[RenderResult]:
        """
        Render multiple diagrams (override for optimized batch processing).

        Default implementation renders one by one.
        Subclasses can override for more efficient batch processing.
        """
        self.logger.info(
            "Starting batch render",
            extra={"provider_id": self.provider_id, "count": len(codes), "format": output_format}
        )
        if not self.supports_capability(ProviderCapability.BATCH):
            raise NotImplementedError(
                f"Provider {self.provider_id} does not support batch rendering"
            )

        results = []
        for i, code in enumerate(codes):
            self.logger.info(f"[{self.provider_id}] Batch render {i+1}/{len(codes)}")
            result = self.render_with_validation(code, output_format, **options)
            results.append(result)

        self.logger.info(
            "Completed batch render",
            extra={"provider_id": self.provider_id, "count": len(results)}
        )
        return results
