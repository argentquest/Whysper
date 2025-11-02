"""
Shared models for diagram providers

Defines common data structures used across all providers.
"""

from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from enum import Enum
from datetime import datetime


class ProviderCapability(str, Enum):
    """Capabilities that a provider can support"""
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
    """Result of diagram validation"""
    is_valid: bool
    error: Optional[str] = None
    warnings: List[str] = Field(default_factory=list)
    auto_fixed: bool = False
    llm_corrected: bool = False
    fixed_code: Optional[str] = None
    code_length: int = 0
    correction_method: Optional[str] = None  # "pattern", "llm", "cli"


class RenderResult(BaseModel):
    """Result of diagram rendering"""
    success: bool
    content: Optional[str] = None          # SVG/PNG content or converted code
    output_format: str                     # Format of the content
    validation: ValidationResult
    metadata: Dict[str, Any] = Field(default_factory=dict)
    error: Optional[str] = None
    file_path: Optional[str] = None


class ProviderMetadata(BaseModel):
    """Metadata about a diagram provider"""
    provider_id: str                       # e.g., "mermaidv1", "d2v1"
    provider_name: str                     # Human-readable name
    diagram_type: str                      # Primary diagram type (mermaid, d2, etc.)
    supported_output_formats: List[str]    # Formats this provider can output
    capabilities: List[ProviderCapability]
    version: Optional[str]                 # Provider version
    available: bool                        # Is provider available/installed
    description: Optional[str]             # Description of the provider
    requires_llm: bool = False             # Does this provider require LLM access?


class CorrectionAttemptType(str, Enum):
    """Type of correction attempt"""
    PATTERN = "pattern"
    LLM = "llm"
    USER = "user"
    ORIGINAL = "original"


class CorrectionAttempt(BaseModel):
    """Record of a single correction attempt"""
    attempt_number: int
    attempt_type: CorrectionAttemptType
    code: str
    timestamp: datetime
    is_valid: bool
    error: Optional[str] = None
    success: bool
