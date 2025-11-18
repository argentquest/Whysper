"""
Shared models for diagram providers

Defines common data structures used across all providers.
"""

from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from enum import Enum
from datetime import datetime


class ProviderCapability(str, Enum):
    # Enumerate possible capabilities that a diagram provider can support
    VALIDATE = "validate"              # Can validate syntax
    RENDER_SVG = "render_svg"          # Can render to SVG
    RENDER_PNG = "render_png"          # Can render to PNG
    RENDER_PDF = "render_pdf"          # Can render to PDF
    AUTO_FIX = "auto_fix"              # Can auto-fix syntax (pattern-based)
    LLM_CORRECTION = "llm_correction"  # Supports LLM-based correction
    BATCH = "batch"                    # Supports batch rendering
    CONVERT = "convert"                # Converts between formats
    STREAMING = "streaming"            # Supports streaming output


class ValidationResult(BaseModel):
    # Model to represent the result of diagram validation
    is_valid: bool  # Whether the diagram passed validation
    error: Optional[str] = None  # Optional error message if validation fails
    warnings: List[str] = Field(default_factory=list)  # List of warnings
    auto_fixed: bool = False  # Whether auto-fix was applied
    llm_corrected: bool = False  # Whether LLM correction was used
    fixed_code: Optional[str] = None  # Corrected code if fixes applied
    code_length: int = 0  # Length of the original/corrected code
    correction_method: Optional[str] = None  # Method used for correction


class RenderResult(BaseModel):
    # Model to represent the result of diagram rendering
    success: bool  # Whether rendering was successful
    content: Optional[str] = None          # SVG/PNG content or converted code
    output_format: str                     # Format of the rendered content
    validation: ValidationResult  # Validation details for the render
    metadata: Dict[str, Any] = Field(default_factory=dict)  # Additional metadata
    error: Optional[str] = None  # Error message if rendering failed
    file_path: Optional[str] = None  # Path to rendered file if applicable


class ProviderMetadata(BaseModel):
    # Model to store metadata about a diagram provider
    provider_id: str                       # Unique identifier for provider
    provider_name: str                     # Human-readable name
    diagram_type: str                      # Type of diagram (mermaid, d2, etc.)
    supported_output_formats: List[str]    # Possible output formats
    capabilities: List[ProviderCapability]  # List of provider capabilities
    version: Optional[str]                 # Provider version
    available: bool                        # Is provider installed/available
    description: Optional[str]             # Description of the provider
    requires_llm: bool = False             # Needs LLM access to function


class CorrectionAttemptType(str, Enum):
    # Enumerate possible types of correction attempts
    PATTERN = "pattern"  # Correction using pattern matching
    LLM = "llm"          # Correction using language model
    USER = "user"        # Manual user correction
    ORIGINAL = "original"  # No correction attempted


class CorrectionAttempt(BaseModel):
    # Model to track individual correction attempts
    attempt_number: int  # Which attempt number this is
    attempt_type: CorrectionAttemptType  # Type of correction attempt
    code: str  # The code being corrected
    timestamp: datetime  # When the correction was attempted
    is_valid: bool  # Whether the correction was successful
    error: Optional[str] = None  # Error message if correction failed
    success: bool  # Overall success of the correction attempt