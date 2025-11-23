"""
Kroki C4 Provider

C4 diagrams via Kroki service using PlantUML engine.
"""

from .kroki_renderer import KrokiC4Provider  # Import Kroki renderer from local module

# Expose only KrokiC4Provider class for external imports
__all__ = ['KrokiC4Provider']
