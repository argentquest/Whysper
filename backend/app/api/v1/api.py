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
- /diagrams/v2: Unified diagram provider API (Mermaid, D2, PlantUML, etc.)
- /diagrams: MVP diagram generator endpoints
- /documentation: Documentation generation
- /auth: Authentication endpoints
"""
from fastapi import APIRouter
from .endpoints import (
    chat, code, files, settings, system, documentation, auth, diagram_provider, diagram_events, diagram as diagram_wizard
)
from mvp_diagram_generator import (
    rendering_api as diagram_generator_api
)

# Create the main API router to aggregate all endpoint routers
# Serves as a centralized routing mechanism for the entire application
api_router = APIRouter()

# =============================================================================
# Whysper Core API Endpoints
# Systematically include routers for different functional domains
# Each router is added with a specific prefix and tagged for documentation
# =============================================================================

# Include chat-related endpoints with '/chat' prefix for conversational features
api_router.include_router(
    chat.router,
    prefix="/chat",
    tags=["chat"]
)

# Include code-related endpoints for code processing and analysis
api_router.include_router(
    code.router,
    prefix="/code",
    tags=["code"]
)

# Include file system endpoints for file management operations
api_router.include_router(
    files.router,
    prefix="/files",
    tags=["files"]
)

# Include application settings endpoints for user configuration
api_router.include_router(
    settings.router,
    prefix="/settings",
    tags=["settings"]
)

# Include system-level endpoints for health checks and system information
api_router.include_router(
    system.router,
    prefix="/system",
    tags=["system"]
)

# Include diagram wizard endpoints for creating and managing diagrams
api_router.include_router(
    diagram_wizard.router,
    prefix="/diagram",
    tags=["diagram-wizard"],
)

# Include diagram event logging endpoints for tracking diagram-related activities
api_router.include_router(
    diagram_events.router,
    prefix="/diagrams",
    tags=["diagrams", "logging"],
)

# Include modern diagram provider endpoints with versioned prefix
# Supports multiple diagram rendering providers and formats
api_router.include_router(
    diagram_provider.router,
    prefix="/diagrams/v2",  # v2 to avoid conflict with existing
    tags=["diagrams-v2", "providers"],
)

# Include MVP diagram generator endpoints for basic diagram generation
api_router.include_router(
    diagram_generator_api.router,
    prefix="/diagrams",
    tags=["diagrams"],
)

# Include documentation generation endpoints
api_router.include_router(
    documentation.router,
    prefix="/documentation",
    tags=["documentation"],
)

# Include authentication endpoints for user management
api_router.include_router(
    auth.router,
    prefix="/auth",
    tags=["auth"],
)
