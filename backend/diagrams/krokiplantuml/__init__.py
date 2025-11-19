"""
Kroki PlantUML Provider

PlantUML diagrams via Kroki service.
"""

from .kroki_renderer import KrokiPlantUMLProvider  # Import the KrokiPlantUMLProvider from local module

# Expose only KrokiPlantUMLProvider in module's public interface
__all__ = ['KrokiPlantUMLProvider']
