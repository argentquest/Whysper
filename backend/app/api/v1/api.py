"""
API v1 router aggregation for Whysper Web2 Backend.

This module serves as the central router aggregator for API version 1. It combines
all individual endpoint routers into a single cohesive API router that can be
included in the main FastAPI application.

Architecture:
- Each functional area has its own endpoint module (chat, code, files, etc.)
- This module aggregates them with proper URL prefixes and OpenAPI tags
- Provides consistent error responses and documentation structures

Router Organization:
- /system: Health checks, version info, root endpoint
- /chat & /conversations: AI chat and conversation management
- /code: Code extraction and language detection
- /files: File upload, download, and management
- /settings: User preferences and configuration
"""
from fastapi import APIRouter
from .endpoints import (
    chat, code, files, settings, system, diagram_events, d2_render, documentation, auth
)
from mvp_diagram_generator import (
    rendering_api as diagram_generator_api
)

# Main API router for the application
# This router includes all other routers for different functionalities
api_router = APIRouter()

# =============================================================================
# Whysper Core API Endpoints
# =============================================================================

# Include routers from the different endpoint modules
# These are organized by their functionality (chat, code, files, etc.)

# Chat-related endpoints
api_router.include_router(
    chat.router,
    prefix="/chat",
    tags=["chat"]
)

# Code-related endpoints (e.g., code extraction)
api_router.include_router(
    code.router,
    prefix="/code",
    tags=["code"]
)

# File system endpoints
api_router.include_router(
    files.router,
    prefix="/files",
    tags=["files"]
)

# Application settings endpoints
api_router.include_router(
    settings.router,
    prefix="/settings",
    tags=["settings"]
)

# System-level endpoints (e.g., health checks)
api_router.include_router(
    system.router,
    prefix="/system",
    tags=["system"]
)

# ==================== Diagram Events Endpoints ====================
# Diagram detection and rendering event logging from frontend
# Available at: /api/v1/diagrams/* (log-diagram-event, health)
api_router.include_router(
    diagram_events.router,
    prefix="/diagrams",  # URL prefix for diagram event operations
    tags=["diagrams"],
)

# ==================== MVP Diagram Generator Endpoints ====================
api_router.include_router(
    diagram_generator_api.router,
    prefix="/diagrams",
    tags=["diagrams"],
)

# ==================== D2 Rendering Endpoints ====================
# D2 diagram rendering using CLI
# Available at: /api/v1/d2/* (render, validate, batch, info, health)
api_router.include_router(
    d2_render.router,
    prefix="/d2",
    tags=["d2"],
)

# ==================== Documentation Generator Endpoints ====================
api_router.include_router(
    documentation.router,
    prefix="/documentation",
    tags=["documentation"],
)

# ==================== Auth Endpoints ====================
api_router.include_router(
    auth.router,
    prefix="/auth",
    tags=["auth"],
)
