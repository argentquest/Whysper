# Google Cloud Run Deployment Configuration

## Overview

This document provides detailed configuration for deploying Whysper Web2 on Google Cloud Run with optimal settings for performance, security, and scalability.

## Cloud Run Service Configuration

### Service YAML Configuration
```yaml
apiVersion: serving.knative.dev/v1
kind: Service
metadata:
  name: whysper-web2
  annotations:
    run.googleapis.com/ingress: all
    run.googleapis.com/execution-environment: gen2
    run.googleapis.com/cpu-throttling: "false"
    run.googleapis.com/launch-stage: BETA
spec:
  template:
    metadata:
      annotations:
        run.googleapis.com/cpu-boost: "true"
        run.googleapis.com/execution-environment: gen2
        autoscaling.knative.dev/maxScale: "100"
        autoscaling.knative.dev/minScale: "0"
        autoscaling.knative.dev/scaleDownDelay: "300s"
        autoscaling.knative.dev/target: "60"
        autoscaling.knative.dev/targetUtilizationPercentage: "70"
    spec:
      containerConcurrency: 80
      timeoutSeconds: 300
      containers:
      - image: gcr.io/PROJECT_ID/whysper-web2:latest
        ports:
        - containerPort: 8080
          protocol: TCP
        resources:
          limits:
            cpu: "2000m"
            memory: "4Gi"
          requests:
            cpu: "1000m"
            memory: "2Gi"
        env:
        - name: PORT
          value: "8080"
        - name: HOST
          value: "0.0.0.0"
        - name: API_KEY
          valueFrom:
            secretKeyRef:
              name: whysper-secrets
              key: API_KEY
        - name: PROVIDER
          value: "openrouter"
        - name: DEFAULT_MODEL
          value: "google/gemini-2.5-flash-preview-09-2025"
        - name: STATIC_DIR
          value: "/app/static"
        - name: LOG_LEVEL
          value: "INFO"
        startupProbe:
          httpGet:
            path: /health
            port: 8080
          initialDelaySeconds: 10
          periodSeconds: 5
          timeoutSeconds: 5
          failureThreshold: 3
        livenessProbe:
          httpGet:
            path: /health
            port: 8080
          initialDelaySeconds: 15
          periodSeconds: 10
          timeoutSeconds: 5
          failureThreshold: 3
        readinessProbe:
          httpGet:
            path: /ready
            port: 8080
          initialDelaySeconds: 5
          periodSeconds: 5
          timeoutSeconds: 3
          failureThreshold: 3
```

## Deployment Scripts

### gcloud Deployment Script
```bash
#!/bin/bash
# deploy.sh - Cloud Run deployment script

set -e

# Configuration
PROJECT_ID="your-gcp-project-id"
REGION="us-central1"
SERVICE_NAME="whysper-web2"
IMAGE_NAME="whysper-web2"
REPO_NAME="whysper-repo"

echo "🚀 Deploying Whysper Web2 to Cloud Run..."

# Set project
gcloud config set project $PROJECT_ID

# Enable required APIs
echo "📋 Enabling required APIs..."
gcloud services enable run.googleapis.com
gcloud services enable cloudbuild.googleapis.com
gcloud services enable artifactregistry.googleapis.com
gcloud services enable secretmanager.googleapis.com

# Create Artifact Registry repository
echo "📦 Creating Artifact Registry repository..."
gcloud artifacts repositories create $REPO_NAME \
    --repository-format=docker \
    --location=$REGION \
    --description="Whysper Web2 Docker images"

# Build and push container image
echo "🔨 Building container image..."
gcloud builds submit --tag gcr.io/$PROJECT_ID/$IMAGE_NAME:latest .

# Deploy to Cloud Run
echo "🌐 Deploying to Cloud Run..."
gcloud run deploy $SERVICE_NAME \
    --image gcr.io/$PROJECT_ID/$IMAGE_NAME:latest \
    --region $REGION \
    --platform managed \
    --allow-unauthenticated \
    --cpu 2 \
    --memory 4Gi \
    --max-instances 100 \
    --min-instances 0 \
    --concurrency 80 \
    --timeout 300s \
    --set-env-vars PORT=8080,HOST=0.0.0.0,PROVIDER=openrouter,DEFAULT_MODEL=google/gemini-2.5-flash-preview-09-2025,STATIC_DIR=/app/static,LOG_LEVEL=INFO \
    --set-secrets API_KEY=whysper-secrets:API_KEY \
    --ingress all \
    --execution-environment gen2

# Get service URL
SERVICE_URL=$(gcloud run services describe $SERVICE_NAME \
    --region $REGION \
    --format 'value(status.url)')

echo "✅ Deployment complete!"
echo "🌍 Service URL: $SERVICE_URL"
echo "📊 Monitor: https://console.cloud.google.com/run/detail/$REGION/$SERVICE_NAME"
```

### Terraform Configuration
```hcl
# main.tf - Terraform configuration for Cloud Run

terraform {
  required_providers {
    google = {
      source  = "hashicorp/google"
      version = "~> 4.0"
    }
  }
}

provider "google" {
  project = var.project_id
  region  = var.region
}

# Cloud Run Service
resource "google_cloud_run_service" "whysper_web2" {
  name     = "whysper-web2"
  location = var.region
  
  template {
    metadata {
      annotations = {
        "run.googleapis.com/ingress"                      = "all"
        "run.googleapis.com/execution-environment"         = "gen2"
        "run.googleapis.com/cpu-throttling"              = "false"
        "autoscaling.knative.dev/maxScale"               = "100"
        "autoscaling.knative.dev/minScale"               = "0"
        "autoscaling.knative.dev/target"                 = "60"
        "autoscaling.knative.dev/targetUtilizationPercentage" = "70"
        "run.googleapis.com/cpu-boost"                  = "true"
      }
    }

    spec {
      container_concurrency = 80
      timeout_seconds      = 300

      containers {
        image = "gcr.io/${var.project_id}/whysper-web2:latest"
        
        ports {
          container_port = 8080
        }

        resources {
          limits = {
            cpu    = "2000m"
            memory = "4Gi"
          }
          requests = {
            cpu    = "1000m"
            memory = "2Gi"
          }
        }

        env {
          name  = "PORT"
          value = "8080"
        }

        env {
          name  = "HOST"
          value = "0.0.0.0"
        }

        env {
          name  = "PROVIDER"
          value = "openrouter"
        }

        env {
          name  = "DEFAULT_MODEL"
          value = "google/gemini-2.5-flash-preview-09-2025"
        }

        env {
          name  = "STATIC_DIR"
          value = "/app/static"
        }

        env {
          name  = "LOG_LEVEL"
          value = "INFO"
        }

        env {
          name = "API_KEY"
          value_from {
            secret_key_ref {
              name = google_secret_manager_secret.whysper_secrets.secret_id
              key  = "API_KEY"
            }
          }
        }

        startup_probe {
          http_get {
            path = "/health"
            port = 8080
          }
          initial_delay_seconds = 10
          period_seconds        = 5
          timeout_seconds      = 5
          failure_threshold    = 3
        }

        liveness_probe {
          http_get {
            path = "/health"
            port = 8080
          }
          initial_delay_seconds = 15
          period_seconds        = 10
          timeout_seconds      = 5
          failure_threshold    = 3
        }

        readiness_probe {
          http_get {
            path = "/ready"
            port = 8080
          }
          initial_delay_seconds = 5
          period_seconds        = 5
          timeout_seconds      = 3
          failure_threshold    = 3
        }
      }
    }
  }

  traffic {
    percent         = 100
    latest_revision = true
  }
}

# IAM Policy for public access
resource "google_cloud_run_service_iam_member" "public_access" {
  location = google_cloud_run_service.whysper_web2.location
  project  = google_cloud_run_service.whysper_web2.project
  service  = google_cloud_run_service.whysper_web2.name
  role     = "roles/run.invoker"
  member   = "allUsers"
}

# Variables
variable "project_id" {
  description = "GCP Project ID"
  type        = string
}

variable "region" {
  description = "GCP Region"
  type        = string
  default     = "us-central1"
}
```

## Environment Configuration

### Production Environment Variables
```bash
# Core Configuration
PORT=8080
HOST=0.0.0.0
PROVIDER=openrouter
DEFAULT_MODEL=google/gemini-2.5-flash-preview-09-2025
STATIC_DIR=/app/static
LOG_LEVEL=INFO

# Performance Tuning
MAX_TOKENS=10000
TEMPERATURE=0.7
AI_CONNECT_TIMEOUT=30
AI_READ_TIMEOUT=120
REQUEST_TIMEOUT=60

# Feature Flags
ENABLE_STREAMING=true
DEBUG_LOGGING=false
SHOW_TOKEN_USAGE=true
AUTO_SAVE_CONVERSATIONS=true

# External Services
KROKI=https://kroki.io
OPENROUTER_API_URL=https://openrouter.ai/api/v1/chat/completions
OPENROUTER_HTTP_REFERER=https://whysper.example.com
OPENROUTER_TITLE=Whysper Web2
```

### Development Environment Variables
```bash
# Development Configuration
PORT=8080
HOST=0.0.0.0
PROVIDER=openrouter
DEFAULT_MODEL=google/gemini-2.5-flash-preview-09-2025
STATIC_DIR=/app/static
LOG_LEVEL=DEBUG

# Development Features
DEBUG_LOGGING=true
ENABLE_STREAMING=true
SHOW_TOKEN_USAGE=true
RELOAD=true

# Testing Configuration
FRONT_END_TIMEOUT=120
RETRY_ATTEMPTS=3
VALIDATE_SSL=true
```

## Service Configuration Options

### Scaling Configuration
```yaml
# Automatic Scaling
autoscaling.knative.dev/maxScale: "100"      # Maximum instances
autoscaling.knative.dev/minScale: "0"       # Minimum instances (scale to zero)
autoscaling.knative.dev/target: "60"         # Target concurrent requests per instance
autoscaling.knative.dev/targetUtilizationPercentage: "70"  # Target CPU utilization

# Scale Down Configuration
autoscaling.knative.dev/scaleDownDelay: "300s"  # Delay before scaling down
```

### Performance Configuration
```yaml
# CPU and Memory
run.googleapis.com/cpu: "2000m"              # 2 vCPUs
run.googleapis.com/memory: "4Gi"               # 4GB RAM
run.googleapis.com/cpu-throttling: "false"     # Disable CPU throttling
run.googleapis.com/cpu-boost: "true"          # Enable CPU boost

# Execution Environment
run.googleapis.com/execution-environment: "gen2"  # Use 2nd generation
run.googleapis.com/launch-stage: "BETA"        # Enable beta features
```

### Networking Configuration
```yaml
# Ingress Settings
run.googleapis.com/ingress: "all"             # Allow all traffic types
run.googleapis.com/ingress-status: "all"      # Internal and external

# VPC Connector (for private services)
run.googleapis.com/vpc-access-connector: "projects/PROJECT_ID/locations/REGION/connectors/CONNECTOR_NAME"
```

## Health Check Configuration

### Application Health Endpoints
```python
# Add to backend/app/main.py
from fastapi import FastAPI
from datetime import datetime
import psutil
import os

@app.get("/health")
async def health_check():
    """Basic health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "version": "2.0.0",
        "uptime": os.getenv("UPTIME", "unknown")
    }

@app.get("/ready")
async def readiness_check():
    """Readiness check endpoint"""
    try:
        # Check critical dependencies
        # Add checks for database, external APIs, etc.
        return {
            "status": "ready",
            "checks": {
                "api_key_configured": bool(os.getenv("API_KEY")),
                "static_dir_accessible": os.path.exists(os.getenv("STATIC_DIR", "/app/static")),
                "memory_usage": f"{psutil.virtual_memory().percent}%"
            }
        }
    except Exception as e:
        return {"status": "not_ready", "error": str(e)}, 503

@app.get("/live")
async def liveness_check():
    """Liveness check endpoint"""
    return {"status": "alive", "timestamp": datetime.utcnow().isoformat()}
```

## Deployment Strategies

### Blue-Green Deployment
```bash
#!/bin/bash
# blue-green-deploy.sh

CURRENT_VERSION=$(gcloud run services describe whysper-web2 --region=$REGION --format='value(template.spec.containers[0].image)' | cut -d: -f2)
NEW_VERSION="v$(date +%Y%m%d-%H%M%S)"

echo "Current version: $CURRENT_VERSION"
echo "New version: $NEW_VERSION"

# Deploy new version as green
gcloud run deploy whysper-web2-green \
    --image gcr.io/$PROJECT_ID/whysper-web2:$NEW_VERSION \
    --region $REGION \
    --no-traffic

# Test green deployment
echo "Testing green deployment..."
GREEN_URL=$(gcloud run services describe whysper-web2-green --region=$REGION --format='value(status.url)')
curl -f $GREEN_URL/health || exit 1

# Switch traffic to green
echo "Switching traffic to green..."
gcloud run services update-traffic whysper-web2 \
    --region $REGION \
    --to-revisions whysper-web2-green=100

# Clean up old blue deployment
echo "Cleaning up old deployment..."
gcloud run services delete whysper-web2-blue --region=$REGION --quiet || true
gcloud run services update whysper-web2-green --region=$REGION --new-revision-name=whysper-web2-blue
```

### Canary Deployment
```bash
#!/bin/bash
# canary-deploy.sh

NEW_VERSION="v$(date +%Y%m%d-%H%M%S)"

# Deploy new version
gcloud run deploy whysper-web2 \
    --image gcr.io/$PROJECT_ID/whysper-web2:$NEW_VERSION \
    --region $REGION \
    --no-traffic

# Gradual traffic shift
for percent in 5 10 25 50 100; do
    echo "Shifting $percent% traffic to new version..."
    gcloud run services update-traffic whysper-web2 \
        --region $REGION \
        --to-revisions whysper-web2=$percent,whysper-web2-$NEW_VERSION=$((100-percent))
    
    echo "Waiting for traffic shift..."
    sleep 60
    
    # Check metrics and health
    # Add monitoring checks here
done
```

## Monitoring and Observability

### Cloud Monitoring Integration
```yaml
# Service Monitoring Annotations
run.googleapis.com/monitoring: "true"
run.googleapis.com/logging: "true"
```

### Custom Metrics
```python
# Add to application for custom metrics
from prometheus_client import Counter, Histogram, generate_latest

REQUEST_COUNT = Counter('http_requests_total', 'Total HTTP requests', ['method', 'endpoint'])
REQUEST_DURATION = Histogram('http_request_duration_seconds', 'HTTP request duration')

@app.middleware("http")
async def metrics_middleware(request: Request, call_next):
    start_time = time.time()
    response = await call_next(request)
    duration = time.time() - start_time
    
    REQUEST_COUNT.labels(method=request.method, endpoint=request.url.path).inc()
    REQUEST_DURATION.observe(duration)
    
    return response
```

## Security Configuration

### IAM Roles
```bash
# Service Account Roles
gcloud projects add-iam-policy-binding $PROJECT_ID \
    --member="serviceAccount:whysper-web2@$PROJECT_ID.iam.gserviceaccount.com" \
    --role="roles/run.invoker"

gcloud projects add-iam-policy-binding $PROJECT_ID \
    --member="serviceAccount:whysper-web2@$PROJECT_ID.iam.gserviceaccount.com" \
    --role="roles/secretmanager.secretAccessor"

gcloud projects add-iam-policy-binding $PROJECT_ID \
    --member="serviceAccount:whysper-web2@$PROJECT_ID.iam.gserviceaccount.com" \
    --role="roles/logging.logWriter"

gcloud projects add-iam-policy-binding $PROJECT_ID \
    --member="serviceAccount:whysper-web2@$PROJECT_ID.iam.gserviceaccount.com" \
    --role="roles/monitoring.metricWriter"
```

### Security Headers
```python
# Add to FastAPI application
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware

app.add_middleware(
    TrustedHostMiddleware, 
    allowed_hosts=["*.run.app", "yourdomain.com"]
)

# Security headers middleware
@app.middleware("http")
async def security_headers_middleware(request: Request, call_next):
    response = await call_next(request)
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["X-XSS-Protection"] = "1; mode=block"
    response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
    return response