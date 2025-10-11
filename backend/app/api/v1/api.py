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
from .endpoints import chat, code, files, settings, system, shell, diagram_events
from typing import Dict, Any

# Create the main API router for version 1
# This router will be included in the main app with /api/v1 prefix
api_router = APIRouter()

# ==================== System Endpoints ====================
# Root endpoints for health checks, version info, and system status
# Available at: /api/v1/, /api/v1/health, /api/v1/version
api_router.include_router(
    system.router,
    tags=["system"],  # OpenAPI documentation tag
    responses={404: {"description": "Not found"}},  # Common error response
)  # Added missing closing parenthesis

# ==================== Chat Endpoints ====================
# AI conversation management under /api/v1/chat/*
api_router.include_router(
    chat.router,
    prefix="/chat",      # URL prefix for chat operations
    tags=["chat"],       # OpenAPI documentation tag
    responses={404: {"description": "Not found"}},
)

# ==================== Code Extraction Endpoints ====================
# Code block extraction and language detection services
# Available at: /api/v1/code/* (extract, languages, detect-language)
api_router.include_router(
    code.router,
    prefix="/code",      # URL prefix for code operations
    tags=["code"],       # OpenAPI documentation tag
    responses={404: {"description": "Not found"}},
)

# ==================== File Management Endpoints ====================
# File upload, download, and conversation attachment services
# Available at: /api/v1/files/* (upload, download, list, delete)
api_router.include_router(
    files.router,
    prefix="/files",     # URL prefix for file operations
    tags=["files"],      # OpenAPI documentation tag
    responses={404: {"description": "Not found"}},
)

# ==================== Settings Endpoints ====================
# User preferences, AI model configuration, and application settings
# Available at: /api/v1/settings/* (get, update, models, providers)
api_router.include_router(
    settings.router,
    prefix="/settings",  # URL prefix for settings operations
    tags=["settings"],   # OpenAPI documentation tag
    responses={404: {"description": "Not found"}},
)

# ==================== Shell Endpoints ====================
# Real-time shell access and command execution via WebSocket
# Available at: /api/v1/shell/* (sessions, ws, security)
api_router.include_router(
    shell.router,
    prefix="/shell",     # URL prefix for shell operations
    tags=["shell"],      # OpenAPI documentation tag
    responses={404: {"description": "Not found"}},
)

# ==================== Diagram Events Endpoints ====================
# Diagram detection and rendering event logging from frontend
# Available at: /api/v1/diagrams/* (log-diagram-event, health)
api_router.include_router(
    diagram_events.router,
    prefix="/diagrams",  # URL prefix for diagram event operations
    tags=["diagrams"],   # OpenAPI documentation tag
    responses={404: {"description": "Not found"}},
)
