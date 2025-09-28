#!/usr/bin/env python3
"""
Simplified WhysperCode Web2 Application for demonstration.

This version serves the frontend and provides basic API endpoints
without the complex AI integration for testing purposes.
"""

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
import os
import uvicorn

# Create FastAPI application
app = FastAPI(
    title="WhysperCode Web2",
    description="AI-Powered Code Analysis & Development Assistant",
    version="2.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files for the React frontend
static_dir = "static"
if os.path.exists(static_dir):
    app.mount("/static", StaticFiles(directory=static_dir), name="static")
    
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
        
        # Serve static files if they exist
        file_path = os.path.join(static_dir, full_path)
        if os.path.exists(file_path) and os.path.isfile(file_path):
            return FileResponse(file_path)
        
        # Otherwise serve the main index.html for SPA routing
        return FileResponse(os.path.join(static_dir, "index.html"))

# Simple API endpoints
@app.get("/api/v1/")
def api_health():
    """API health check."""
    return {
        "message": "Welcome to WhysperCode Web2 Backend",
        "version": "2.0.0",
        "status": "running"
    }

@app.get("/api/v1/files/")
def get_files():
    """Simple files endpoint."""
    return {
        "success": True,
        "data": [
            {"path": "./example.py", "name": "example.py", "size": 1024, "isSelected": False, "type": "file"},
            {"path": "./README.md", "name": "README.md", "size": 2048, "isSelected": False, "type": "file"}
        ]
    }

@app.post("/api/v1/chat/")
def chat():
    """Simple chat endpoint."""
    return {
        "success": True,
        "data": {
            "message": {
                "id": "msg-demo-123",
                "role": "assistant",
                "content": "🎉 **WhysperCode Web2 is working!**\n\nThis is a demonstration response from the integrated FastAPI backend. The frontend and backend are successfully communicating!\n\n### Features Available:\n- ✅ Frontend serving via FastAPI\n- ✅ API endpoints\n- ✅ Static file serving\n- ✅ SPA routing support\n\n### Next Steps:\n1. Configure your AI provider API keys\n2. Enable full AI integration\n3. Add file system integration\n\nThe application is ready for development and deployment! 🚀",
                "timestamp": "2024-01-01T00:00:00Z",
                "metadata": {
                    "tokens": 50,
                    "model": "demo-model"
                }
            },
            "conversationId": "demo-conv-123"
        }
    }

@app.get("/api/v1/settings/")
def get_settings():
    """Simple settings endpoint."""
    return {
        "success": True,
        "data": {
            "theme": "light",
            "provider": "demo",
            "model": "demo-model",
            "systemPrompt": "You are a helpful AI assistant."
        }
    }

if __name__ == "__main__":
    print("Starting WhysperCode Web2 (Demo Mode)...")
    print("Frontend: http://localhost:8001")
    print("API: http://localhost:8001/api/v1")
    print("Docs: http://localhost:8001/docs")
    print("=" * 50)
    
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8001,
        reload=False,
        log_level="info"
    )