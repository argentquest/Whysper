"""
Main entry point for Whysper Web2 Backend API Server.

This is a pure API server that only serves backend endpoints.
The frontend runs separately on its own port (typically 5173).

Usage:
    python main.py

The backend API server will start on http://localhost:8001 and serve:
- API endpoints at /api/v1/*
- OpenAPI documentation at /docs

Frontend should be started separately with:
    cd frontend && npm run dev
"""

import uvicorn
import os
from app.main import app
from app.core.config import settings
from common.logger import get_logger, configure_logging

# Configure logging based on environment variables
configure_logging()

# Initialize logger for main application boot
logger = get_logger(__name__)

# Test console output immediately
print("=" * 60)
print("BACKEND API SERVER STARTING - Console output working!")
print("LOG_LEVEL from env:", os.getenv('LOG_LEVEL', 'NOT_SET'))
print("=" * 60)

# Test debug logging immediately
logger.debug("DEBUG LOGGING TEST - This should appear in console if LOG_LEVEL=DEBUG")
logger.info("INFO LOGGING TEST - This should always appear")
logger.error("ERROR LOGGING TEST - This should always appear")

# No frontend serving - this is a pure API server

if __name__ == "__main__":
    """
    Main entry point when script is executed directly.

    This block:
    1. Logs application startup
    2. Displays API access URLs  
    3. Starts the uvicorn server

    The backend API server runs on port 8001 by default and serves:
    - FastAPI backend endpoints at /api/v1 paths
    - OpenAPI documentation at /docs
    """
    logger.info("Starting Whysper Web2 Backend API Server boot process")
    print("[boot] Starting Whysper Web2 Backend API Server...")

    # Display access information
    base_url = f"http://{settings.host}:{settings.port}"
    api_url = f"{base_url}/api/v1"
    docs_url = f"{base_url}/docs"

    print(f"[boot] API Server: {base_url}")
    print(f"[boot] API Endpoints: {api_url}")
    print(f"[boot] API Documentation: {docs_url}")
    print(f"[boot] Frontend: Run separately with 'cd frontend && npm run dev'")
    print("=" * 60)

    logger.info(f"Backend API Server configured - Base: {base_url}")
    logger.info(f"Backend API Server configured - API: {api_url}")
    logger.info(f"Backend API Server configured - Docs: {docs_url}")

    # Determine reload target based on settings
    reload_target = "app.main:app" if settings.reload else app
    logger.debug(f"Reload target: {reload_target}")
    logger.debug(f"Host: {settings.host}, Port: {settings.port}, Reload: {settings.reload}")

    # Start uvicorn server
    logger.info("Starting uvicorn server...")
    # Get log level from environment for uvicorn
    import os
    uvicorn_log_level = os.getenv('LOG_LEVEL', 'INFO').lower()
    
    uvicorn.run(
        reload_target,
        host=settings.host,
        port=settings.port,
        reload=settings.reload,
        log_level=uvicorn_log_level
    )
# trigger reload
