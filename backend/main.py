"""
Main entry point for the Whysper Web2 Backend API.

This module sets up the Windows event loop policy before importing
any other modules to fix Playwright subprocess issues on Windows.
"""

import asyncio
import sys
import platform

# Detect if running on Windows and set a special event loop policy
# This resolves compatibility issues with Playwright subprocesses
if platform.system() == "Windows":
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

# Import the main FastAPI application after setting Windows event loop
from app.main import app

# Check if script is being run directly (not imported)
# This ensures the server only starts when script is main entry point
if __name__ == "__main__":
    import uvicorn
    from app.core.config import settings
    
    # Launch the FastAPI application using Uvicorn ASGI server
    # Uses configuration settings for host, port, and reload behavior
    uvicorn.run(
        "app.main:app",
        host=settings.host,
        port=settings.port,
        reload=settings.reload,
        log_level="info"
    )