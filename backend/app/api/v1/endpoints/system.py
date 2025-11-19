"""
System and health check endpoints.

This module handles system-level operations including:
- Health checks
- API status
- Version information
"""
from typing import Dict
from fastapi import APIRouter
from app.core.config import settings
from common.logger import get_logger
from common.logging_decorator import log_method_call
import sys
import platform
from datetime import datetime

# Initialize logger for tracking method calls and debugging
logger = get_logger(__name__)
# Create API router for defining endpoint routes
router = APIRouter()


@router.get("/")
@log_method_call
def root() -> Dict[str, str]:
    # Log debug info for root endpoint entry
    logger.debug("root endpoint started")
    # Return basic API metadata and navigation links
    return {
        "message": f"Welcome to {settings.api_title}",
        "version": settings.api_version,
        "description": settings.api_description,
        "docs": "/docs",
        "redoc": "/redoc",
        "health": "/health"
    }


@router.get("/health")
@log_method_call
def health_check() -> Dict[str, str]:
    # Log debug info for health check endpoint entry
    logger.debug("health_check endpoint started")
    # Provide comprehensive system status for monitoring
    return {
        "status": "healthy",
        "service": settings.api_title,
        "version": settings.api_version,
        # Use UTC timestamp for consistent time reporting
        "timestamp": datetime.utcnow().isoformat(),
        # Include Python and system details for diagnostic purposes
        "python_version": sys.version,
        "platform": platform.platform(),
        "uptime": "running"  # Could be enhanced with actual uptime tracking
    }


@router.get("/version")
@log_method_call
def get_version() -> Dict[str, str]:
    # Return detailed version information about the API and environment
    return {
        "api_version": settings.api_version,
        "api_title": settings.api_title,
        # Include Python version and platform for compatibility checks
        "python_version": sys.version,
        "platform": platform.platform()
    }
