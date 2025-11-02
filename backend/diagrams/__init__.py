"""
Diagram Provider System

New modular architecture for diagram rendering with:
- Provider-based design (folder = provider)
- Hierarchical configuration (root defaults + provider overrides)
- LLM-based error correction
- User correction workflow
- Multiple providers for same diagram type

This runs in parallel with existing mermaid/d2 services.
"""

from .models import (
    ProviderCapability,
    ValidationResult,
    RenderResult,
    ProviderMetadata,
    CorrectionAttemptType,
    CorrectionAttempt
)

from .provider_config import (
    ProviderConfig,
    RootConfig,
    CorrectionStrategy,
    load_provider_config,
    get_config_loader
)

from .base_diagram import BaseDiagramProvider

__all__ = [
    # Models
    'ProviderCapability',
    'ValidationResult',
    'RenderResult',
    'ProviderMetadata',
    'CorrectionAttemptType',
    'CorrectionAttempt',

    # Config
    'ProviderConfig',
    'RootConfig',
    'CorrectionStrategy',
    'load_provider_config',
    'get_config_loader',

    # Base
    'BaseDiagramProvider',
]

__version__ = "1.0.0"
