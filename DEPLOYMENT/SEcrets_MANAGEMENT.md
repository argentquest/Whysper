# Environment Variables and Secrets Management Strategy

## Overview

This document outlines a comprehensive strategy for managing environment variables and secrets for the Whysper Web2 application on Google Cloud Platform, ensuring security, scalability, and maintainability.

## Secret Management Architecture

```mermaid
graph TB
    subgraph "Development Environment"
        DEV_ENV[.env.local]
        GITIGNORE[.gitignore]
        LOCAL_SECRETS[Local Secrets]
    end
    
    subgraph "Google Cloud Platform"
        subgraph "Secret Manager"
            PROD_SECRETS[Production Secrets]
            STAGING_SECRETS[Staging Secrets]
            DEV_SECRETS[Development Secrets]
        end
        
        subgraph "Environment Configuration"
            CLOUD_RUN[Cloud Run Environment]
            CLOUD_BUILD[Cloud Build Variables]
            ARTIFACT_REGISTRY[Artifact Registry]
        end
        
        subgraph "Access Control"
            IAM_ROLES[IAM Roles]
            SERVICE_ACCOUNTS[Service Accounts]
            ACCESS_POLICIES[Access Policies]
        end
    end
    
    subgraph "CI/CD Pipeline"
        GITHUB[GitHub Repository]
        CLOUD_BUILD_TRIGGER[Build Triggers]
        DEPLOYMENT_STAGES[Deployment Stages]
    end
    
    %% Connections
    DEV_ENV --> GITHUB
    GITHUB --> CLOUD_BUILD_TRIGGER
    CLOUD_BUILD_TRIGGER --> CLOUD_BUILD
    CLOUD_BUILD --> ARTIFACT_REGISTRY
    ARTIFACT_REGISTRY --> CLOUD_RUN
    
    PROD_SECRETS --> IAM_ROLES
    STAGING_SECRETS --> IAM_ROLES
    DEV_SECRETS --> IAM_ROLES
    IAM_ROLES --> SERVICE_ACCOUNTS
    SERVICE_ACCOUNTS --> ACCESS_POLICIES
    ACCESS_POLICIES --> CLOUD_RUN
    
    CLOUD_RUN --> DEPLOYMENT_STAGES
    DEPLOYMENT_STAGES --> PROD_SECRETS
    DEPLOYMENT_STAGES --> STAGING_SECRETS
```

## Secret Manager Configuration

### Secret Categories and Structure

#### 1. API Keys and Authentication
```bash
# API Provider Secrets
echo "Creating API provider secrets..."

# OpenRouter API Key
echo "sk-or-v1-your-openrouter-api-key" | gcloud secrets create openrouter-api-key \
    --project=$PROJECT_ID \
    --data-file=-

# Access Key for Application
echo "your-secret-access-key" | gcloud secrets create app-access-key \
    --project=$PROJECT_ID \
    --data-file=-

# Custom Provider API Key (if used)
echo "your-custom-provider-key" | gcloud secrets create custom-provider-api-key \
    --project=$PROJECT_ID \
    --data-file=-
```

#### 2. External Service Configuration
```bash
# External Service URLs and Configuration
echo "https://openrouter.ai/api/v1/chat/completions" | gcloud secrets create openrouter-api-url \
    --project=$PROJECT_ID \
    --data-file=-

echo "https://your-api.com/v1/chat" | gcloud secrets create custom-provider-url \
    --project=$PROJECT_ID \
    --data-file=-

echo "https://kroki.io" | gcloud secrets create kroki-url \
    --project=$PROJECT_ID \
    --data-file=-
```

#### 3. Database and Storage Credentials
```bash
# Database Connection (if using Cloud SQL)
echo "postgresql://username:password@host:port/database" | gcloud secrets create database-url \
    --project=$PROJECT_ID \
    --data-file=-

# Storage Access Keys (if using external storage)
echo "your-storage-access-key" | gcloud secrets create storage-access-key \
    --project=$PROJECT_ID \
    --data-file=-

echo "your-storage-secret-key" | gcloud secrets create storage-secret-key \
    --project=$PROJECT_ID \
    --data-file=-
```

#### 4. Application Configuration
```bash
# Application-specific secrets
echo "your-jwt-secret-key" | gcloud secrets create jwt-secret \
    --project=$PROJECT_ID \
    --data-file=-

echo "your-encryption-key" | gcloud secrets create encryption-key \
    --project=$PROJECT_ID \
    --data-file=-

echo "your-webhook-secret" | gcloud secrets create webhook-secret \
    --project=$PROJECT_ID \
    --data-file=-
```

## Environment-Specific Configuration

### Development Environment
```bash
#!/bin/bash
# setup-dev-secrets.sh

PROJECT_ID="your-gcp-project-dev"
ENVIRONMENT="development"

echo "🔧 Setting up development environment secrets..."

# Create development versions of secrets
echo "dev-api-key-value" | gcloud secrets create dev-openrouter-api-key \
    --project=$PROJECT_ID \
    --data-file=-

echo "dev-access-key-value" | gcloud secrets create dev-app-access-key \
    --project=$PROJECT_ID \
    --data-file=-

# Environment-specific labels
gcloud secrets update dev-openrouter-api-key \
    --project=$PROJECT_ID \
    --update-labels=environment=development,team=backend

gcloud secrets update dev-app-access-key \
    --project=$PROJECT_ID \
    --update-labels=environment=development,team=backend
```

### Staging Environment
```bash
#!/bin/bash
# setup-staging-secrets.sh

PROJECT_ID="your-gcp-project-staging"
ENVIRONMENT="staging"

echo "🧪 Setting up staging environment secrets..."

# Create staging versions of secrets
echo "staging-api-key-value" | gcloud secrets create staging-openrouter-api-key \
    --project=$PROJECT_ID \
    --data-file=-

echo "staging-access-key-value" | gcloud secrets create staging-app-access-key \
    --project=$PROJECT_ID \
    --data-file=-

# Environment-specific labels
gcloud secrets update staging-openrouter-api-key \
    --project=$PROJECT_ID \
    --update-labels=environment=staging,team=backend

gcloud secrets update staging-app-access-key \
    --project=$PROJECT_ID \
    --update-labels=environment=staging,team=backend
```

### Production Environment
```bash
#!/bin/bash
# setup-prod-secrets.sh

PROJECT_ID="your-gcp-project-prod"
ENVIRONMENT="production"

echo "🚀 Setting up production environment secrets..."

# Create production versions of secrets
echo "prod-api-key-value" | gcloud secrets create prod-openrouter-api-key \
    --project=$PROJECT_ID \
    --data-file=-

echo "prod-access-key-value" | gcloud secrets create prod-app-access-key \
    --project=$PROJECT_ID \
    --data-file=-

# Environment-specific labels
gcloud secrets update prod-openrouter-api-key \
    --project=$PROJECT_ID \
    --update-labels=environment=production,team=backend,critical=true

gcloud secrets update prod-app-access-key \
    --project=$PROJECT_ID \
    --update-labels=environment=production,team=backend,critical=true
```

## IAM Access Control

### Service Account Configuration
```bash
#!/bin/bash
# configure-service-account-access.sh

PROJECT_ID="your-gcp-project-id"

echo "👤 Configuring service account access..."

# Cloud Run service account
SERVICE_ACCOUNT="whysper-web2@$PROJECT_ID.iam.gserviceaccount.com"

# Grant access to specific secrets with environment-based conditions
gcloud secrets add-iam-policy-binding openrouter-api-key \
    --project=$PROJECT_ID \
    --member="serviceAccount:$SERVICE_ACCOUNT" \
    --role="roles/secretmanager.secretAccessor" \
    --condition="title=ProductionAccess,expression=resource.name.startsWith('projects/$PROJECT_ID/secrets/prod-')"

gcloud secrets add-iam-policy-binding app-access-key \
    --project=$PROJECT_ID \
    --member="serviceAccount:$SERVICE_ACCOUNT" \
    --role="roles/secretmanager.secretAccessor" \
    --condition="title=ProductionAccess,expression=resource.name.startsWith('projects/$PROJECT_ID/secrets/prod-')"

# Grant access to staging secrets for staging service account
STAGING_SERVICE_ACCOUNT="whysper-web2-staging@$PROJECT_ID.iam.gserviceaccount.com"

gcloud secrets add-iam-policy-binding staging-openrouter-api-key \
    --project=$PROJECT_ID \
    --member="serviceAccount:$STAGING_SERVICE_ACCOUNT" \
    --role="rolesmanager.secretAccessor"

# Grant access to development secrets for development service account
DEV_SERVICE_ACCOUNT="whysper-web2-dev@$PROJECT_ID.iam.gserviceaccount.com"

gcloud secrets add-iam-policy-binding dev-openrouter-api-key \
    --project=$PROJECT_ID \
    --member="serviceAccount:$DEV_SERVICE_ACCOUNT" \
    --role="roles/secretmanager.secretAccessor"
```

### Principle of Least Privilege
```yaml
# iam-policy.yaml - Least privilege access configuration

# Production service account - only production secrets
bindings:
  - members:
      - serviceAccount:whysper-web2-prod@project-id.iam.gserviceaccount.com
    role: roles/secretmanager.secretAccessor
    condition:
        title: ProductionSecretsOnly
        expression: >
          resource.name.startsWith('projects/project-id/secrets/prod-') &&
          !resource.name.matches('projects/project-id/secrets/.*-test-.*')

# Staging service account - staging and shared secrets
bindings:
  - members:
      - serviceAccount:whysper-web2-staging@project-id.iam.gserviceaccount.com
    role: roles/secretmanager.secretAccessor
    condition:
        title: StagingSecretsOnly
        expression: >
          resource.name.startsWith('projects/project-id/secrets/staging-') ||
          resource.name.startsWith('projects/project-id/secrets/shared-')

# Development service account - development and shared secrets
bindings:
  - members:
      - serviceAccount:whysper-web2-dev@project-id.iam.gserviceaccount.com
    role: roles/secretmanager.secretAccessor
    condition:
        title: DevelopmentSecretsOnly
        expression: >
          resource.name.startsWith('projects/project-id/secrets/dev-') ||
          resource.name.startsWith('projects/project-id/secrets/shared-') ||
          resource.name.matches('projects/project-id/secrets/.*-test-.*')
```

## Environment Variables Management

### Cloud Run Environment Variables
```bash
#!/bin/bash
# deploy-with-env-vars.sh

PROJECT_ID="your-gcp-project-id"
SERVICE_NAME="whysper-web2"
REGION="us-central1"

echo "🌍 Deploying with environment variables..."

# Deploy with secret references
gcloud run deploy $SERVICE_NAME \
    --project=$PROJECT_ID \
    --region=$REGION \
    --image gcr.io/$PROJECT_ID/whysper-web2:latest \
    --set-secrets \
        API_KEY=openrouter-api-key:latest, \
        ACCESS_KEY=app-access-key:latest, \
        DATABASE_URL=database-url:latest, \
        JWT_SECRET=jwt-secret:latest \
        ENCRYPTION_KEY=encryption-key:latest \
    --set-env-vars \
        PORT=8080, \
        HOST=0.0.0.0, \
        PROVIDER=openrouter, \
        DEFAULT_MODEL=google/gemini-2.5-flash-preview-09-2025, \
        STATIC_DIR=/app/static, \
        LOG_LEVEL=INFO, \
        MAX_TOKENS=10000, \
        TEMPERATURE=0.7, \
        AI_CONNECT_TIMEOUT=30, \
        AI_READ_TIMEOUT=120, \
        ENABLE_STREAMING=true, \
        DEBUG_LOGGING=false, \
        SHOW_TOKEN_USAGE=true, \
        AUTO_SAVE_CONVERSATIONS=true, \
        KROKI_URL=https://kroki.io, \
        OPENROUTER_API_URL=https://openrouter.ai/api/v1/chat/completions, \
        OPENROUTER_HTTP_REFERER=https://whysper.example.com, \
        OPENROUTER_TITLE=Whysper Web2
```

### Environment-Specific Variable Files
```yaml
# environments/production.yaml
environment: production
project_id: your-gcp-project-prod
service_name: whysper-web2
region: us-central1

secrets:
  api_key: prod-openrouter-api-key
  access_key: prod-app-access-key
  database_url: prod-database-url
  jwt_secret: prod-jwt-secret
  encryption_key: prod-encryption-key

environment_variables:
  PORT: 8080
  HOST: 0.0.0.0
  PROVIDER: openrouter
  DEFAULT_MODEL: google/gemini-2.5-flash-preview-09-2025
  STATIC_DIR: /app/static
  LOG_LEVEL: INFO
  MAX_TOKENS: 10000
  TEMPERATURE: 0.7
  AI_CONNECT_TIMEOUT: 30
  AI_READ_TIMEOUT: 120
  ENABLE_STREAMING: true
  DEBUG_LOGGING: false
  SHOW_TOKEN_USAGE: true
  AUTO_SAVE_CONVERSATIONS: true

---

# environments/staging.yaml
environment: staging
project_id: your-gcp-project-staging
service_name: whysper-web2-staging
region: us-central1

secrets:
  api_key: staging-openrouter-api-key
  access_key: staging-app-access-key
  database_url: staging-database-url
  jwt_secret: staging-jwt-secret
  encryption_key: staging-encryption-key

environment_variables:
  PORT: 8080
  HOST: 0.0.0.0
  PROVIDER: openrouter
  DEFAULT_MODEL: google/gemini-2.5-flash-preview-09-2025
  STATIC_DIR: /app/static
  LOG_LEVEL: DEBUG
  MAX_TOKENS: 10000
  TEMPERATURE: 0.7
  AI_CONNECT_TIMEOUT: 30
  AI_READ_TIMEOUT: 120
  ENABLE_STREAMING: true
  DEBUG_LOGGING: true
  SHOW_TOKEN_USAGE: true
  AUTO_SAVE_CONVERSATIONS: true

---

# environments/development.yaml
environment: development
project_id: your-gcp-project-dev
service_name: whysper-web2-dev
region: us-central1

secrets:
  api_key: dev-openrouter-api-key
  access_key: dev-app-access-key
  database_url: dev-database-url
  jwt_secret: dev-jwt-secret
  encryption_key: dev-encryption-key

environment_variables:
  PORT: 8080
  HOST: 0.0.0.0
  PROVIDER: openrouter
  DEFAULT_MODEL: google/gemini-2.5-flash-preview-09-2025
  STATIC_DIR: /app/static
  LOG_LEVEL: DEBUG
  MAX_TOKENS: 10000
  TEMPERATURE: 0.7
  AI_CONNECT_TIMEOUT: 30
  AI_READ_TIMEOUT: 120
  ENABLE_STREAMING: true
  DEBUG_LOGGING: true
  SHOW_TOKEN_USAGE: true
  AUTO_SAVE_CONVERSATIONS: true
```

## Secret Rotation Strategy

### Automated Secret Rotation
```bash
#!/bin/bash
# rotate-secrets.sh

PROJECT_ID="your-gcp-project-id"

echo "🔄 Rotating secrets..."

# Function to rotate a secret
rotate_secret() {
    local secret_name=$1
    local new_value=$2
    
    echo "Rotating $secret_name..."
    
    # Create new version
    echo "$new_value" | gcloud secrets versions add $secret_name \
        --project=$PROJECT_ID \
        --data-file=-
    
    # Set as latest
    gcloud secrets versions enable $secret_name \
        --project=$PROJECT_ID \
        --version=$(gcloud secrets versions list $secret_name \
            --project=$PROJECT_ID \
            --limit=1 \
            --sort-by=~createTime \
            --format='value(name)' | cut -d/ -f3)
    
    echo "✅ $secret_name rotated successfully"
}

# Rotate API keys (example - in practice, these would come from your provider)
rotate_secret "openrouter-api-key" "sk-or-v1-new-api-key-here"
rotate_secret "app-access-key" "new-secret-access-key-here"

# Clean up old versions (keep last 5 versions)
for secret in openrouter-api-key app-access-key; do
    gcloud secrets versions list $secret \
        --project=$PROJECT_ID \
        --format='value(name)' \
        --sort-by=~createTime | \
    tail -n +6 | \
    xargs -I {} gcloud secrets versions delete $secret:{} --project=$PROJECT_ID --quiet
done

echo "🧹 Old secret versions cleaned up"
```

### Scheduled Rotation with Cloud Scheduler
```yaml
# cloud-scheduler-job.yaml

apiVersion: batch.cnrm.cloud.google.com/v1
kind: Job
metadata:
  name: secret-rotation-job
spec:
  template:
    spec:
      template:
        spec:
          containers:
          - name: secret-rotator
            image: gcr.io/google.com/cloudsdktool/cloud-sdk:latest
            script: |
              #!/bin/bash
              gcloud secrets versions add openrouter-api-key \
                  --project=$PROJECT_ID \
                  --data-file=<(echo "new-api-key-here")
              
              # Update Cloud Run service with new secret version
              gcloud run services update whysper-web2 \
                  --project=$PROJECT_ID \
                  --region=us-central1 \
                  --update-secrets API_KEY=openrouter-api-key:latest
            env:
            - name: PROJECT_ID
              value: "your-gcp-project-id"
          restartPolicy: OnFailure
  schedule: "0 2 * * 0"  # Every Sunday at 2 AM
  timeZone: "UTC"
```

## Configuration Validation

### Secret Validation Script
```bash
#!/bin/bash
# validate-secrets.sh

PROJECT_ID="your-gcp-project-id"
ENVIRONMENT=$1

echo "🔍 Validating secrets for $ENVIRONMENT environment..."

# Function to validate secret exists and is accessible
validate_secret() {
    local secret_name=$1
    local expected_prefix=$2
    
    echo "Validating $secret_name..."
    
    # Check if secret exists
    if ! gcloud secrets describe $secret_name --project=$PROJECT_ID >/dev/null 2>&1; then
        echo "❌ Secret $secret_name does not exist"
        return 1
    fi
    
    # Check if secret has correct prefix
    if [[ ! $secret_name =~ ^$expected_prefix ]]; then
        echo "❌ Secret $secret_name does not have expected prefix $expected_prefix"
        return 1
    fi
    
    # Check if service account has access
    SERVICE_ACCOUNT="whysper-web2-$ENVIRONMENT@$PROJECT_ID.iam.gserviceaccount.com"
    if ! gcloud secrets versions list $secret_name \
        --project=$PROJECT_ID \
        --filter="state:ENABLED" >/dev/null 2>&1; then
        echo "❌ Service account does not have access to $secret_name"
        return 1
    fi
    
    echo "✅ Secret $secret_name is valid"
    return 0
}

# Validate based on environment
case $ENVIRONMENT in
    "production")
        validate_secret "prod-openrouter-api-key" "prod-"
        validate_secret "prod-app-access-key" "prod-"
        validate_secret "prod-jwt-secret" "prod-"
        ;;
    "staging")
        validate_secret "staging-openrouter-api-key" "staging-"
        validate_secret "staging-app-access-key" "staging-"
        validate_secret "staging-jwt-secret" "staging-"
        ;;
    "development")
        validate_secret "dev-openrouter-api-key" "dev-"
        validate_secret "dev-app-access-key" "dev-"
        validate_secret "dev-jwt-secret" "dev-"
        ;;
    *)
        echo "❌ Unknown environment: $ENVIRONMENT"
        exit 1
        ;;
esac

echo "✅ All secrets validated successfully!"
```

## Security Best Practices

### Secret Security Guidelines
1. **Never commit secrets to version control**
2. **Use unique secrets per environment**
3. **Implement regular rotation schedules**
4. **Monitor secret access patterns**
5. **Use principle of least privilege**
6. **Encrypt sensitive data at rest**
7. **Audit secret access regularly**

### Environment Variable Security
1. **Separate configuration from code**
2. **Use environment-specific configurations**
3. **Validate all required variables**
4. **Default to secure values**
5. **Document all configuration options**
6. **Use type-safe configuration loading**

### Access Control Policies
1. **Role-based access control**
2. **Environment-based permissions**
3. **Time-limited access tokens**
4. **IP-based restrictions**
5. **Multi-factor authentication**
6. **Regular access reviews**

## Monitoring and Auditing

### Secret Access Monitoring
```yaml
# secret-access-monitoring.yaml

apiVersion: monitoring.cnrm.cloud.google.com/v1
kind: AlertPolicy
metadata:
  name: secret-access-alerts
spec:
  displayName: "Secret Access Alerts"
  combiner: "OR"
  conditions:
    - displayName: "Unexpected secret access"
      conditionThreshold:
        filter: >
          resource.type="secretmanager_secret" AND
          protoPayload.methodName="google.cloud.secretmanager.v1.SecretManagerService.AccessSecretVersion" AND
          protoPayload.authenticationInfo.principalEmail!~"whysper-web2-.*@.*.iam.gserviceaccount.com"
        aggregations:
          - alignmentPeriod: "300s"
            perSeriesAligner: "ALIGN_COUNT"
        comparison: "COMPARISON_GT"
        duration: "300s"
        trigger:
          count: 1
        thresholdValue: 0
  notificationChannels:
    - projects/PROJECT_ID/notificationChannels/1234567890123456789
```

### Environment Variable Validation
```python
# config_validator.py - Configuration validation utility

import os
from typing import Dict, Any, List
from pydantic import BaseModel, validator

class AppConfig(BaseModel):
    """Application configuration with validation"""
    
    # Required API configuration
    api_key: str
    provider: str = "openrouter"
    default_model: str = "google/gemini-2.5-flash-preview-09-2025"
    
    # Server configuration
    port: int = 8080
    host: str = "0.0.0.0"
    
    # Feature flags
    enable_streaming: bool = True
    debug_logging: bool = False
    show_token_usage: bool = True
    
    # Performance settings
    max_tokens: int = 10000
    temperature: float = 0.7
    ai_connect_timeout: int = 30
    ai_read_timeout: int = 120
    
    @validator('api_key')
    def validate_api_key(cls, v):
        if not v or len(v) < 10:
            raise ValueError('API key must be at least 10 characters long')
        return v
    
    @validator('port')
    def validate_port(cls, v):
        if not 1 <= v <= 65535:
            raise ValueError('Port must be between 1 and 65535')
        return v
    
    @validator('temperature')
    def validate_temperature(cls, v):
        if not 0.0 <= v <= 2.0:
            raise ValueError('Temperature must be between 0.0 and 2.0')
        return v

def load_config() -> AppConfig:
    """Load and validate configuration from environment"""
    try:
        config = AppConfig(
            api_key=os.getenv('API_KEY', ''),
            provider=os.getenv('PROVIDER', 'openrouter'),
            default_model=os.getenv('DEFAULT_MODEL', 'google/gemini-2.5-flash-preview-09-2025'),
            port=int(os.getenv('PORT', '8080')),
            host=os.getenv('HOST', '0.0.0.0'),
            enable_streaming=os.getenv('ENABLE_STREAMING', 'true').lower() == 'true',
            debug_logging=os.getenv('DEBUG_LOGGING', 'false').lower() == 'true',
            show_token_usage=os.getenv('SHOW_TOKEN_USAGE', 'true').lower() == 'true',
            max_tokens=int(os.getenv('MAX_TOKENS', '10000')),
            temperature=float(os.getenv('TEMPERATURE', '0.7')),
            ai_connect_timeout=int(os.getenv('AI_CONNECT_TIMEOUT', '30')),
            ai_read_timeout=int(os.getenv('AI_READ_TIMEOUT', '120'))
        )
        return config
    except Exception as e:
        print(f"Configuration validation failed: {e}")
        raise

# Usage in application
config = load_config()
print(f"Loaded configuration for provider: {config.provider}")
```

## Emergency Procedures

### Secret Compromise Response
```bash
#!/bin/bash
# emergency-secret-rotation.sh

PROJECT_ID="your-gcp-project-id"
COMPROMISED_SECRET=$1

echo "🚨 Emergency rotation for compromised secret: $COMPROMISED_SECRET"

# Immediately disable the compromised secret
gcloud secrets versions add $COMPROMISED_SECRET \
    --project=$PROJECT_ID \
    --data-file=<(echo "COMPROMISED-DO-NOT-USE") \
    --ttl=0s

# Create new secret with new name
NEW_SECRET_NAME="${COMPROMISED_SECRET}-emergency-$(date +%s)"
echo "new-emergency-value" | gcloud secrets create $NEW_SECRET_NAME \
    --project=$PROJECT_ID \
    --data-file=-

# Update all services to use new secret
gcloud run services update whysper-web2 \
    --project=$PROJECT_ID \
    --region=us-central1 \
    --update-secrets "${COMPROMISED_SECRET}=${NEW_SECRET_NAME}:latest"

# Notify security team
echo "📧 Sending emergency notification..."
# Add your notification logic here

echo "✅ Emergency rotation completed"
```

This comprehensive strategy ensures secure management of all environment variables and secrets across different environments while maintaining operational efficiency and security compliance.