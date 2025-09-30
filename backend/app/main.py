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
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.api.v1.api import api_router
from common.logger import get_logger

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
    logger.info("Shutting down Whysper Web2 Backend")


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
