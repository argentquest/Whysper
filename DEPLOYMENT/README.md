# Google Cloud Deployment Guide for Whysper Web2

## Overview

This document provides a complete guide for deploying Whysper Web2 application to Google Cloud Platform using a single container image with Red Hat Enterprise Linux 8.1 as the base OS, hosted on Google Cloud Run.

## Architecture Summary

The deployment consists of the following key components:

### 🏗️ **Architecture Documents**
- **[GCP_ARCHITECTURE.md](GCP_ARCHITECTURE.md)** - Complete system architecture with Mermaid diagrams
- **[DOCKERFILE.md](DOCKERFILE.md)** - Multi-stage Docker container configuration
- **[CLOUD_RUN_DEPLOYMENT.md](CLOUD_RUN_DEPLOYMENT.md)** - Cloud Run service configuration
- **[NETWORKING_SECURITY.md](NETWORKING_SECURITY.md)** - VPC, networking, and security setup
- **[SEcrets_MANAGEMENT.md](SECRETS_MANAGEMENT.md)** - Environment variables and secrets management
- **[CICD_PIPELINE.md](CICD_PIPELINE.md)** - CI/CD pipeline with Cloud Build
- **[MONITORING_LOGGING.md](MONITORING_LOGGING.md)** - Monitoring and logging configuration
- **[BACKUP_DISASTER_RECOVERY.md](BACKUP_DISASTER_RECOVERY.md)** - Backup and disaster recovery
- **[DEPLOYMENT_SCRIPTS.md](DEPLOYMENT_SCRIPTS.md)** - Deployment scripts and automation
- **[COST_OPTIMIZATION.md](COST_OPTIMIZATION.md)** - Cost optimization and scaling

### 🎯 **Key Features**
- **Single Container Image**: All components in one Docker container using RHEL 8.1 base
- **Google Cloud Run**: Serverless deployment with automatic scaling
- **Node.js for Frontend Only**: Used only for building, not runtime
- **Comprehensive Security**: Multi-layer security with IAM, Secret Manager, and network controls
- **Full CI/CD**: Automated pipeline with testing, security scanning, and deployment
- **Complete Monitoring**: Cloud Operations integration with custom dashboards and alerting
- **Disaster Recovery**: Automated backups, failover procedures, and recovery testing

## Quick Start Guide

### Prerequisites
1. **Google Cloud Account** with billing enabled
2. **Google Cloud SDK** installed and authenticated
3. **Docker** installed locally
4. **Git** for version control

### Initial Setup
```bash
# 1. Clone the repository
git clone https://github.com/your-org/whysper-web2.git
cd whysper-web2

# 2. Set up the project
./setup-project.sh your-gcp-project-id

# 3. Configure secrets
./setup-secrets.sh your-gcp-project-id

# 4. Set up environment variables
./configure-environment.sh production your-gcp-project-id
```

### Deployment Options

#### Development Environment
```bash
./deploy-development.sh
```

#### Staging Environment
```bash
./deploy-staging.sh
```

#### Production Environment
```bash
# Build and deploy
./deploy-production.sh

# Or with specific build ID
./deploy-production.sh build-20241213-143022
```

### Monitoring and Management

#### Health Checks
```bash
# Check service health
./health-check.sh https://whysper.example.com
```

#### Performance Monitoring
```bash
# Monitor performance
./monitor-performance.sh https://whysper.example.com
```

#### Cost Management
```bash
# Monitor costs
./cost-monitor.sh
```

#### Backup Operations
```bash
# Create backup
./backup.sh your-gcp-project-id

# Restore from backup
./restore.sh your-gcp-project-id backup-id-12345
```

## Service URLs

After deployment, your service will be available at:

### Development
- **Service**: `https://whysper-web2-dev-xxxxx.a.run.app`
- **Monitoring**: https://console.cloud.google.com/run/detail/us-central1/whysper-web2-dev

### Staging
- **Service**: `https://whysper-web2-staging-xxxxx.a.run.app`
- **Monitoring**: https://console.cloud.google.com/run/detail/us-central1/whysper-web2-staging

### Production
- **Service**: `https://whysper.example.com`
- **Monitoring**: https://console.cloud.google.com/run/detail/us-central1/whysper-web2

## Configuration Files

### Environment Variables
Key configuration files:
- `backend/.env` - Backend environment variables
- `frontend/.env` - Frontend environment variables
- `keys/` - Service account keys (never commit to version control)

### Secrets Management
All sensitive data is stored in Google Secret Manager:
- `API_KEY` - OpenRouter API key
- `ACCESS_KEY` - Application access key
- Database credentials (if using Cloud SQL)

### Docker Configuration
- `Dockerfile` - Multi-stage build configuration
- `.dockerignore` - Build optimization
- `docker-compose.yml` - Local development setup

## Security Best Practices

### 🔐 **Secret Management**
- Never commit secrets to version control
- Use Secret Manager for production secrets
- Rotate keys regularly (every 90 days)
- Use principle of least privilege for service accounts

### 🛡️ **Network Security**
- Use HTTPS for all communications
- Configure firewall rules appropriately
- Enable VPC Service Controls for sensitive operations
- Monitor access logs and set up alerts

### 📊 **Monitoring**
- Set up comprehensive dashboards in Cloud Monitoring
- Configure alerting for all critical metrics
- Implement structured logging with correlation IDs
- Regular performance testing and optimization

### 💰 **Cost Optimization**
- Set up budget alerts in Google Cloud Billing
- Use appropriate storage classes (STANDARD, COLDLINE, ARCHIVE)
- Implement lifecycle policies for automatic cleanup
- Right-size resources based on actual usage
- Use auto-scaling to optimize costs during variable load

## Troubleshooting

### Common Issues

1. **Build Failures**
   - Check build logs: `gcloud builds log --project=PROJECT_ID BUILD_ID`
   - Verify configuration: `gcloud builds describe --project=PROJECT_ID BUILD_ID`

2. **Deployment Failures**
   - Check service logs: `gcloud run services logs read SERVICE_NAME`
   - Verify service status: `gcloud run services describe SERVICE_NAME`
   - Check resource quotas: `gcloud compute project-info describe PROJECT_ID`

3. **Performance Issues**
   - Monitor metrics in Cloud Console
   - Check resource utilization
   - Review scaling settings

### Support Resources

- **Documentation**: See individual documentation files
- **Google Cloud Console**: https://console.cloud.google.com/
- **Support**: support@whysper.example.com
- **Monitoring Dashboard**: https://console.cloud.google.com/monitoring/

## Next Steps

1. **Review all documentation** before deployment
2. **Test in staging environment** before production
3. **Set up monitoring and alerting** immediately after deployment
4. **Regular cost reviews** to optimize spending
5. **Keep documentation updated** with any changes to procedures

## Compliance and Governance

This deployment architecture follows Google Cloud best practices for:
- **Security**: IAM controls, secret management, network security
- **Reliability**: Backup procedures, disaster recovery, health monitoring
- **Performance**: Resource optimization, scaling, monitoring
- **Cost Management**: Budget controls, cost optimization, resource rightsizing
- **Compliance**: Data protection, audit logging, access controls

For detailed information on any specific aspect of the deployment, refer to the specialized documentation files linked above.