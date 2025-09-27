#!/usr/bin/env python3
"""
Main entry point for WhisperCode Web2 Application.

This simplified main.py file makes it easy to run the entire application
(backend API + frontend) from a single command.

Usage:
    python main.py

The application will start on http://localhost:8001 and serve both:
- API endpoints at /api/v1/* and /api/*
- Frontend React application at /
"""

import uvicorn
from app.main import app
from app.core.config import settings

if __name__ == "__main__":
    print("🚀 Starting WhisperCode Web2 Application...")
    print(f"📱 Frontend: http://{settings.host}:{settings.port}")
    print(f"🔌 API: http://{settings.host}:{settings.port}/api/v1")
    print(f"📚 Docs: http://{settings.host}:{settings.port}/docs")
    print("=" * 50)
    
    uvicorn.run(
        app,
        host=settings.host,
        port=settings.port,
        reload=settings.reload,
        log_level="info"
    )