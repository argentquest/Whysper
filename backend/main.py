#!/usr/bin/env python3
"""
Main entry point for WhysperCode Web2 Application.

This simplified main.py file makes it easy to run the entire application
(backend API + frontend) from a single command.

Usage:
    python main.py

The application will start on http://localhost:8001 and serve both:
- API endpoints at /api/v1/* and /api/*
- Frontend React application at /
"""

import uvicorn
import os
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from app.main import app
from app.core.config import settings

def setup_frontend():
    """Mount frontend static files if available."""
    frontend_dist = os.path.join(os.path.dirname(__file__), "..", "frontend", "dist")
    
    if os.path.exists(frontend_dist):
        # Mount static assets (JS, CSS, images)
        app.mount("/assets", StaticFiles(directory=os.path.join(frontend_dist, "assets")), name="assets")
        
        # Serve index.html for root and catch-all routes
        @app.get("/")
        def serve_frontend_root():
            return FileResponse(os.path.join(frontend_dist, "index.html"))
        
        @app.get("/{full_path:path}")
        def serve_frontend_catchall(full_path: str):
            # Don't interfere with API routes
            if full_path.startswith("api/") or full_path.startswith("docs"):
                return {"error": "Endpoint not found"}
            
            # Check if it's a static file request
            file_path = os.path.join(frontend_dist, full_path)
            if os.path.exists(file_path) and os.path.isfile(file_path):
                return FileResponse(file_path)
            
            # For SPA routing, serve index.html
            return FileResponse(os.path.join(frontend_dist, "index.html"))
        
        print(f"[boot] Frontend mounted from: {frontend_dist}")
    else:
        print(f"[boot] Frontend dist not found at: {frontend_dist}")
        print(f"[boot] Run 'npm run build' in frontend directory to build frontend")

if __name__ == "__main__":
    print("[boot] Starting WhysperCode Web2 Application...")
    
    # Setup frontend static file serving
    setup_frontend()
    
    print(f"[boot] Frontend: http://{settings.host}:{settings.port}")
    print(f"[boot] API: http://{settings.host}:{settings.port}/api/v1")
    print(f"[boot] Docs: http://{settings.host}:{settings.port}/docs")
    print("=" * 50)

    reload_target = "app.main:app" if settings.reload else app

    uvicorn.run(
        reload_target,
        host=settings.host,
        port=settings.port,
        reload=settings.reload,
        log_level="info"
    )
