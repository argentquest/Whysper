#!/usr/bin/env python3
"""
Minimal backend script to start a FastAPI server on port 8003.
This is a from-scratch implementation for basic backend functionality.
"""

import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# Create FastAPI app
app = FastAPI(
    title="Whysper Backend",
    description="Minimal backend server for Whysper",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins for development
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    """Root endpoint"""
    return {"message": "Whysper Backend is running", "port": 8003}


@app.get("/health")
async def health():
    """Health check endpoint"""
    return {"status": "healthy"}

if __name__ == "__main__":
    print("Starting Whysper Backend on port 8003...")
    uvicorn.run(
        "start_backend:app",
        host="0.0.0.0",
        port=8003,
        reload=True,
        log_level="info"
    )