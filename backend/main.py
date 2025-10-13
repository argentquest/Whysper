"""
Main entry point for the Whysper Web2 Backend API.

This module sets up the Windows event loop policy before importing
any other modules to fix Playwright subprocess issues on Windows.
"""

import asyncio
import sys
import platform

# Fix Windows asyncio issue for Playwright BEFORE any other imports
if platform.system() == "Windows":
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

# Now import the main FastAPI app
from app.main import app

if __name__ == "__main__":
    import uvicorn
    from app.core.config import settings
    
    # Run the FastAPI application with uvicorn ASGI server
    uvicorn.run(
        "app.main:app",
        host=settings.host,
        port=settings.port,
        reload=settings.reload,
        log_level="info"
    )
