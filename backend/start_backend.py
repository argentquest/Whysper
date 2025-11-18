#!/usr/bin/env python3

import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# Initialize FastAPI application with basic metadata for documentation
app = FastAPI(
    title="Whysper Backend",
    description="Minimal backend server for Whysper",
    version="1.0.0"
)

# Configure Cross-Origin Resource Sharing (CORS) to allow requests from any origin
# This is crucial for web applications to enable frontend-backend communication
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins for development
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Root endpoint to confirm backend is running and provide basic info
@app.get("/")
async def root():
    return {"message": "Whysper Backend is running", "port": 8003}

# Health check endpoint for monitoring and verifying backend availability
@app.get("/health")
async def health():
    return {"status": "healthy"}

# Main execution block to start the server when script is run directly
if __name__ == "__main__":
    # Start uvicorn server with specific configuration for local development
    print("Starting Whysper Backend on port 8003...")
    uvicorn.run(
        "start_backend:app",  # Module and FastAPI app instance to run
        host="0.0.0.0",       # Listen on all network interfaces
        port=8003,             # Specific port for backend service
        reload=True,           # Enable auto-reload for development
        log_level="info"       # Set logging verbosity
    )