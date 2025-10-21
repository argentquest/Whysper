"""
FastAPI application for Whysper Web2 Backend API.

This module creates the core FastAPI application with API endpoints only.
It includes CORS middleware, API routing, and lifecycle events.

Key Features:
- CORS middleware for cross-origin requests
- API versioning via /api/v1
- Structured logging and monitoring
- Graceful startup and shutdown handling

Note: This is the API-only version. For full application with frontend serving,
use backend/main.py instead.
"""
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.api.v1.api import api_router
from mcp_server.fastmcp_server import get_mcp_router
from common.logger import get_logger

from fastapi.staticfiles import StaticFiles

# Initialize logger for this module
logger = get_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Lifespan context manager for the FastAPI application.

    Handles startup and shutdown events in a modern, non-deprecated way.
    This replaces the deprecated @app.on_event() decorators.
    """
    # Startup code - equivalent to the old startup_event()
    logger.info(f"Starting {settings.api_title} v{settings.api_version}")
    logger.info(f"Server running on {settings.host}:{settings.port}")
    logger.info(f"Debug mode: {settings.debug}")
    logger.info(f"CORS origins: {settings.cors_origins}")

    # Initialize real-time log broadcasting
    from common.log_broadcaster import setup_log_broadcasting
    setup_log_broadcasting()
    logger.info("Real-time log broadcasting enabled - connect to GET /api/v1/logs/stream")

    # Log MCP server integration
    logger.info("FastMCP server integration initialized")
    logger.info("MCP endpoints available at /mcp/*")
    logger.info(
        "MCP tools: generate_diagram, render_diagram, generate_and_render"
    )
    logger.info("MCP WebSocket endpoint: /mcp/ws")

    yield  # Application runs here

    # Shutdown code - equivalent to the old shutdown_event()
    logger.info("Shutting down Whysper Web2 Backend")


# Create FastAPI application instance with configuration from settings
app = FastAPI(
    title=settings.api_title,              # API title for documentation
    description=settings.api_description,  # API description for documentation
    version=settings.api_version,          # API version for versioning
    debug=settings.debug,                  # Debug mode for development
    lifespan=lifespan,                     # Lifespan context manager
)

# Configure CORS middleware to allow cross-origin requests from frontend
# This enables the React frontend to communicate with the FastAPI backend
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,   # Allowed frontend origins
    allow_credentials=True,                # Allow cookies and auth headers
    allow_methods=["*"],                   # Allow all HTTP methods
    allow_headers=["*"],                   # Allow all headers
)

# Include the main API router with versioned prefix
# All endpoints are exposed under /api/v1/*
app.include_router(api_router, prefix="/api/v1")

# Include the MCP router for FastMCP integration
# MCP endpoints are exposed under /mcp/*
mcp_router = get_mcp_router()
app.include_router(mcp_router)

# Mount static files directory
# This allows serving files from the backend/static directory
import os
from common.env_manager import env_manager

# Get static directory from environment or use default
env_vars = env_manager.load_env_file()
static_dir = env_vars.get('STATIC_DIR', '').strip()
if not static_dir:
    # Default: backend/static directory
    static_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "static")
else:
    # Use configured path (can be absolute or relative)
    if not os.path.isabs(static_dir):
        # If relative, make it relative to the project root
        static_dir = os.path.abspath(static_dir)

logger.info(f"Static files directory: {static_dir}")
app.mount("/static", StaticFiles(directory=static_dir), name="static")

# Direct execution entry point for development
if __name__ == "__main__":
    # Import uvicorn dynamically to avoid import overhead when used as module
    import uvicorn
    
    # Run the FastAPI application with uvicorn ASGI server
    uvicorn.run(
        "app.main:app",           # Application module and instance
        host=settings.host,       # Server host (default: 0.0.0.0)
        port=settings.port,       # Server port (default: 8001)
        reload=settings.reload,   # Auto-reload on code changes (development)
        log_level="info"          # Logging level for uvicorn
    )
