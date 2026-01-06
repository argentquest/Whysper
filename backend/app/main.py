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

from common.env_manager import env_manager
import os
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.api.v1.api import api_router
from mcp_server.fastmcp_server import get_diagram_router
from app.utils.ssl_utils import build_ssl_kwargs
from common.logger import get_logger

from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from fastapi import HTTPException

# Initialize logger for centralized logging and tracking
logger = get_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup logging to provide context about the application's initialization
    logger.info(f"Starting {settings.api_title} v{settings.api_version}")
    logger.info(f"Server running on {settings.host}:{settings.port}")
    logger.info(f"Debug mode: {settings.debug}")
    logger.info(f"CORS origins: {settings.cors_origins}")

    # Initialize real-time log broadcasting for monitoring and debugging
    from common.log_broadcaster import setup_log_broadcasting

    setup_log_broadcasting()
    logger.info("Real-time log broadcasting enabled - connect to GET /api/v1/logs/stream")

    # Log diagram API integration details for system observability
    logger.info("Diagram API initialized")
    logger.info("Diagram endpoints available at /api/v1/diagrams/*")
    logger.info("Available endpoints: /generate, /render, /generate-and-render")

    yield  # Application runs here with managed resources

    # Graceful shutdown logging to track application lifecycle
    logger.info("Shutting down Whysper Web2 Backend")


# Create FastAPI application with comprehensive configuration
app = FastAPI(
    title=settings.api_title,  # API title for documentation
    description=settings.api_description,  # API description for documentation
    version=settings.api_version,  # API version for versioning
    debug=settings.debug,  # Debug mode for development
    lifespan=lifespan,  # Lifespan context manager
)

# Configure CORS middleware to enable cross-origin communication
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,  # Allowed frontend origins
    allow_credentials=True,  # Allow cookies and auth headers
    allow_methods=["*"],  # Allow all HTTP methods
    allow_headers=["*"],  # Allow all headers
)

# Include main API router with versioned prefix for structured routing
app.include_router(api_router, prefix="/api/v1")

# Include diagram router for diagram generation and rendering
diagram_router = get_diagram_router()
app.include_router(diagram_router)

# Mount static files with flexible directory configuration

def resolve_static_dir() -> str:
    env_vars = env_manager.load_env_file()
    env_override = os.environ.get("STATIC_DIR", "").strip()
    static_dir = (env_override or env_vars.get("STATIC_DIR", "").strip())
    if not static_dir:
        return os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "static")
    if not os.path.isabs(static_dir):
        static_dir = os.path.abspath(static_dir)
    return static_dir


static_dir = resolve_static_dir()

logger.info(f"Static files directory: {static_dir}")

# Mount /assets if it exists (Vite build output)
assets_dir = os.path.join(static_dir, "assets")
if os.path.exists(assets_dir):
    app.mount("/assets", StaticFiles(directory=assets_dir), name="assets")

# Mount /fonts if it exists (Vite build output for fonts)
fonts_dir = os.path.join(static_dir, "fonts")
if os.path.exists(fonts_dir):
    app.mount("/fonts", StaticFiles(directory=fonts_dir), name="fonts")

# Mount /static for backward compatibility or direct access
if os.path.exists(static_dir):
    app.mount("/static", StaticFiles(directory=static_dir), name="static")

# SPA Fallback Route
# This must be defined last to allow API routes to take precedence
@app.get("/{full_path:path}")
async def serve_spa(full_path: str):
    # Check if file exists in static root (e.g., vite.svg, favicon.ico)
    # Prevent directory traversal is handled by os.path.join usually, but be careful
    # secure_filename checks might be needed in strict envs, but here we trust local static dir.

    # Simple check to avoid serving hidden files
    if full_path.startswith("."):
         raise HTTPException(status_code=404)

    # Do not serve SPA fallback for API routes
    if full_path.startswith("api"):
        raise HTTPException(status_code=404)

    file_path = os.path.join(static_dir, full_path)
    if os.path.exists(file_path) and os.path.isfile(file_path):
        return FileResponse(file_path)

    # Fallback to index.html for SPA routing
    index_path = os.path.join(static_dir, "index.html")
    if os.path.exists(index_path):
        return FileResponse(index_path)

    # If index.html doesn't exist (backend only mode), return 404
    raise HTTPException(status_code=404, detail="Not Found")

# Enable direct execution for development server
if __name__ == "__main__":
    # Import uvicorn dynamically to optimize module loading
    import uvicorn

    ssl_kwargs = build_ssl_kwargs(settings)
    protocol = "https" if ssl_kwargs else "http"
    logger.info("Starting Whysper Backend on %s://%s:%s", protocol, settings.host, settings.port)

    # Launch development server with configurable parameters
    uvicorn.run(
        "app.main:app",  # Application module and instance
        host=settings.host,  # Server host (default: 0.0.0.0)
        port=settings.port,  # Server port (default: 8001)
        reload=settings.reload,  # Auto-reload on code changes (development)
        log_level="info",  # Logging level for uvicorn
        **ssl_kwargs,
    )
