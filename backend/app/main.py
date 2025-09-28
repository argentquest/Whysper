"""
Main FastAPI application for WhysperCode Web2 Backend.

This module serves as the entry point for the WhysperCode Web2 Backend API.
It creates and configures the FastAPI application with essential middleware,
routing, and lifecycle events.

Key Features:
- CORS middleware for cross-origin requests
- API versioning via /api/v1
- Structured logging and monitoring
- Graceful startup and shutdown handling
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from app.core.config import settings
from app.api.v1.api import api_router
from common.logger import get_logger
import os

# Initialize logger for this module
logger = get_logger(__name__)

# Create FastAPI application instance with configuration from settings
app = FastAPI(
    title=settings.api_title,              # API title for documentation
    description=settings.api_description,  # API description for documentation
    version=settings.api_version,          # API version for versioning
    debug=settings.debug,                  # Debug mode for development
)

# Configure CORS middleware to allow cross-origin requests from frontend
# This enables the React frontend to communicate with the FastAPI backend
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,   # Allowed frontend origins (localhost:5173, etc.)
    allow_credentials=True,                # Allow cookies and authentication headers
    allow_methods=["*"],                   # Allow all HTTP methods (GET, POST, PUT, DELETE, etc.)
    allow_headers=["*"],                   # Allow all headers in requests
)

# Include the main API router with versioned prefix
# All endpoints are exposed under /api/v1/*
app.include_router(api_router, prefix="/api/v1")

# ==================== Frontend Static File Serving ====================
# Mount static files for the React frontend
static_dir = os.path.join(os.path.dirname(__file__), "..", "static")
if os.path.exists(static_dir):
    # Mount the assets directory for CSS/JS files
    assets_dir = os.path.join(static_dir, "assets")
    if os.path.exists(assets_dir):
        app.mount("/assets", StaticFiles(directory=assets_dir), name="assets")
    
    # Mount the root static files (like vite.svg)
    app.mount("/static", StaticFiles(directory=static_dir), name="static")
    
    @app.get("/vite.svg")
    def serve_vite_svg():
        """Serve vite.svg from static directory."""
        return FileResponse(os.path.join(static_dir, "vite.svg"))
    
    @app.get("/")
    def serve_frontend():
        """Serve the main frontend application."""
        return FileResponse(os.path.join(static_dir, "index.html"))
    
    @app.get("/{full_path:path}")
    def catch_all(full_path: str):
        """Catch-all route for frontend SPA routing."""
        # Don't interfere with API routes
        if full_path.startswith("api/"):
            return {"error": "API endpoint not found"}
        
        # Don't interfere with assets
        if full_path.startswith("assets/") or full_path.startswith("static/"):
            return {"error": "Static file not found"}
        
        # Serve static files if they exist
        file_path = os.path.join(static_dir, full_path)
        if os.path.exists(file_path) and os.path.isfile(file_path):
            return FileResponse(file_path)
        
        # Otherwise serve the main index.html for SPA routing
        return FileResponse(os.path.join(static_dir, "index.html"))
else:
    logger.warning(f"Static directory not found: {static_dir}. Frontend serving disabled.")

@app.on_event("startup")
async def startup_event():
    """
    Application startup event handler.
    
    Called when the FastAPI application starts up. Logs essential
    configuration information for debugging and monitoring.
    """
    logger.info(f"Starting {settings.api_title} v{settings.api_version}")
    logger.info(f"Server running on {settings.host}:{settings.port}")
    logger.info(f"Debug mode: {settings.debug}")
    logger.info(f"CORS origins: {settings.cors_origins}")

@app.on_event("shutdown")
async def shutdown_event():
    """
    Application shutdown event handler.
    
    Called when the FastAPI application is shutting down. Logs
    shutdown information for monitoring and cleanup purposes.
    """
    logger.info("Shutting down WhysperCode Web2 Backend")


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
