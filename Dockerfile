# ============================================================================
# Multi-Stage Dockerfile for Whysper Web2
# Base Image: Red Hat Universal Base Image (UBI) 8
# ============================================================================

# ============================================================================
# STAGE 1: Frontend Build
# Purpose: Compile React + TypeScript frontend using Node.js
# Output: Static files (HTML, JS, CSS) in /frontend/dist
# ============================================================================
FROM registry.access.redhat.com/ubi8/nodejs-18:latest AS frontend-builder

# Set working directory
WORKDIR /build

# Copy frontend package files
COPY frontend/package*.json ./

# Install frontend dependencies
RUN npm ci --only=production

# Copy frontend source code
COPY frontend/ ./

# Build frontend (TypeScript compilation + Vite bundling)
RUN npm run build

# Verify build output
RUN ls -la dist/

# ============================================================================
# STAGE 2: Python Runtime
# Purpose: Production container with Python, FastAPI, and compiled frontend
# Base: RHEL UBI 8 with Python 3.11
# ============================================================================
FROM registry.access.redhat.com/ubi8/python-311:latest

# Switch to root for system package installation
USER root

# ============================================================================
# System Dependencies Installation
# ============================================================================

# Update system and install required packages
RUN dnf update -y && \
    dnf install -y \
        # Build tools
        gcc \
        gcc-c++ \
        make \
        git \
        # Essential utilities
        wget \
        curl \
        unzip \
        ca-certificates \
        # Cleanup
    && dnf clean all \
    && rm -rf /var/cache/dnf

# ============================================================================
# Application Setup
# ============================================================================

# Set working directory
WORKDIR /app

# Copy Python requirements
COPY requirements.txt .

# Upgrade pip and install Python dependencies
RUN pip install --no-cache-dir --upgrade pip setuptools wheel && \
    pip install --no-cache-dir -r requirements.txt

# ============================================================================
# Install D2 CLI for Diagram Generation
# ============================================================================

# Download and install D2 binary
# D2 is used for generating D2 diagrams
RUN ARCH=$(uname -m) && \
    if [ "$ARCH" = "x86_64" ]; then \
        D2_ARCH="amd64"; \
    elif [ "$ARCH" = "aarch64" ]; then \
        D2_ARCH="arm64"; \
    else \
        echo "Unsupported architecture: $ARCH"; exit 1; \
    fi && \
    D2_VERSION="v0.6.3" && \
    wget -O /tmp/d2.tar.gz "https://github.com/terrastruct/d2/releases/download/${D2_VERSION}/d2-${D2_VERSION}-linux-${D2_ARCH}.tar.gz" && \
    tar -xzf /tmp/d2.tar.gz -C /tmp && \
    mv /tmp/d2-${D2_VERSION}/bin/d2 /usr/local/bin/d2 && \
    chmod +x /usr/local/bin/d2 && \
    rm -rf /tmp/d2* && \
    d2 --version

# ============================================================================
# Copy Application Code
# ============================================================================

# Copy backend application code
COPY backend/ ./backend/

# Copy compiled frontend from build stage
COPY --from=frontend-builder /build/dist ./backend/static

# Copy root-level files
COPY .envTemplate ./.envTemplate

# Verify static files were copied
RUN ls -la ./backend/static/

# ============================================================================
# Create Required Directories
# ============================================================================

RUN mkdir -p \
    /app/backend/diagrams/generated \
    /app/backend/logs \
    /app/results \
    /app/backend/prompts \
    /app/backend/prompts/coding/agent

# ============================================================================
# Security Configuration
# ============================================================================

# Create non-root user for running the application
RUN useradd -m -u 1001 -s /bin/bash whysper && \
    chown -R whysper:whysper /app

# Switch to non-root user
USER whysper

# ============================================================================
# Environment Variables
# ============================================================================

# Set Python environment
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# Application configuration
ENV PORT=8080 \
    API_HOST=0.0.0.0 \
    PROVIDER=openrouter \
    STATIC_DIR=/app/backend/static \
    PROMPTS_DIR=/app \
    D2_EXECUTABLE_PATH=/usr/local/bin/d2

# Working directory for Python
WORKDIR /app/backend

# ============================================================================
# Health Check
# ============================================================================

HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD curl -f http://localhost:${PORT}/api/v1/ || exit 1

# ============================================================================
# Expose Port
# ============================================================================

EXPOSE 8080

# ============================================================================
# Container Startup
# ============================================================================

# Run the application
# Note: main.py uses uvicorn to serve both API and static frontend
CMD ["python", "main.py"]

# ============================================================================
# Build and Run Instructions
# ============================================================================
#
# Build:
#   docker build -t whysper-web2:latest .
#
# Run locally:
#   docker run -p 8080:8080 \
#     -e API_KEY=your-openrouter-api-key \
#     -e PROVIDER=openrouter \
#     whysper-web2:latest
#
# Build for GCP:
#   gcloud builds submit --tag REGION-docker.pkg.dev/PROJECT_ID/REPO/whysper-web2:latest
#
# Deploy to Cloud Run:
#   gcloud run deploy whysper-app \
#     --image=REGION-docker.pkg.dev/PROJECT_ID/REPO/whysper-web2:latest \
#     --platform=managed \
#     --region=REGION \
#     --set-secrets="API_KEY=WHYSPER_API_KEY:latest"
#
# ============================================================================
