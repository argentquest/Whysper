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

logger = get_logger(__name__)
router = APIRouter()


@router.get("/")
@log_method_call
def root() -> Dict[str, str]:
    logger.debug("root endpoint started")
    """Root endpoint with API information."""
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
    logger.debug("health_check endpoint started")
    """
    Health check endpoint for monitoring and load balancers.
    
    Returns system status and basic metrics.
    """
    return {
        "status": "healthy",
        "service": settings.api_title,
        "version": settings.api_version,
        "timestamp": datetime.utcnow().isoformat(),
        "python_version": sys.version,
        "platform": platform.platform(),
        "uptime": "running"  # Could be enhanced with actual uptime tracking
    }


@router.get("/version")
@log_method_call
def get_version() -> Dict[str, str]:
    """Get API version information."""
    return {
        "api_version": settings.api_version,
        "api_title": settings.api_title,
        "python_version": sys.version,
        "platform": platform.platform()
    }