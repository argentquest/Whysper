"""
Kroki D2 Provider

D2 diagrams via Kroki service.
"""

from .kroki_renderer import KrokiD2Provider  # Import the base Kroki renderer for D2 diagrams

# Export only the KrokiD2Provider class, making it available when imported
__all__ = ['KrokiD2Provider']
