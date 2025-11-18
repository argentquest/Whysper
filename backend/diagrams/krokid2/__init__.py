"""
Kroki D2 Provider

D2 diagrams via Kroki service.
"""

from .kroki_renderer import KrokiD2Provider  # Import the base Kroki renderer for D2 diagrams

# Export only the KrokiD2Provider class, making it available when imported
__all__ = ['KrokiD2Provider']
```

The comments explain:
- The import of the base renderer 
- The purpose of `__all__` which controls what gets imported when using `from module import *`

Would you like me to add more detailed comments or is this appropriate for the minimal code?