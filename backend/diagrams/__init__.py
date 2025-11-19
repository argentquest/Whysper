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

# Import critical models defining the core data structures and types for diagram providers
from .models import (
    ProviderCapability,
    ValidationResult,
    RenderResult,
    ProviderMetadata,
    CorrectionAttemptType,
    CorrectionAttempt
)

# Import configuration management modules for loading and managing provider settings
from .provider_config import (
    ProviderConfig,
    RootConfig,
    CorrectionStrategy,
    load_provider_config,
    get_config_loader
)

# Import base abstract class for defining common diagram provider interface
from .base_diagram import BaseDiagramProvider

# Explicitly define the public API for this module, controlling what can be imported
__all__ = [
    # Models exposed for external use
    'ProviderCapability',
    'ValidationResult',
    'RenderResult',
    'ProviderMetadata',
    'CorrectionAttemptType',
    'CorrectionAttempt',

    # Configuration classes and utility functions
    'ProviderConfig',
    'RootConfig',
    'CorrectionStrategy',
    'load_provider_config',
    'get_config_loader',

    # Base provider class for inheritance
    'BaseDiagramProvider',
]

# Semantic versioning for the module, allowing version tracking and compatibility checks
__version__ = "1.0.0"
