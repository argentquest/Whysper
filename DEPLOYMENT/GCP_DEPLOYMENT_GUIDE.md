# Google Cloud Platform Deployment Guide
## Step-by-Step Instructions for Whysper Web2

---

## Table of Contents
1. [Prerequisites](#prerequisites)
2. [Option 1: Cloud Run Deployment (Recommended)](#option-1-cloud-run-deployment-recommended)
3. [Option 2: Compute Engine Deployment](#option-2-compute-engine-deployment)
4. [Post-Deployment Configuration](#post-deployment-configuration)
5. [Monitoring and Maintenance](#monitoring-and-maintenance)
6. [Troubleshooting](#troubleshooting)

---

## Prerequisites

### 1. Google Cloud Account Setup

```bash
# Install Google Cloud SDK
# Visit: https://cloud.google.com/sdk/docs/install

# Verify installation
gcloud version

# Login to Google Cloud
gcloud auth login

# Set your project ID (replace with your project)
export PROJECT_ID="whysper-prod"
gcloud config set project $PROJECT_ID

# Enable required APIs
gcloud services enable \
    cloudbuild.googleapis.com \
    run.googleapis.com \
    artifactregistry.googleapis.com \
    secretmanager.googleapis.com \
    cloudresourcemanager.googleapis.com \
    logging.googleapis.com \
    monitoring.googleapis.com \
    storage.googleapis.com
```

### 2. Create Environment Variables

```bash
# Project Configuration
export PROJECT_ID="whysper-prod"
export REGION="us-central1"
export SERVICE_NAME="whysper-app"
export REPOSITORY_NAME="whysper-repo"
export IMAGE_NAME="whysper-web2"

# Set defaults
gcloud config set project $PROJECT_ID
gcloud config set compute/region $REGION
```

### 3. Create Artifact Registry Repository

```bash
# Create a Docker repository in Artifact Registry
gcloud artifacts repositories create $REPOSITORY_NAME \
    --repository-format=docker \
    --location=$REGION \
    --description="Whysper Web2 container images"

# Configure Docker authentication
gcloud auth configure-docker ${REGION}-docker.pkg.dev
```

### 4. Store Secrets in Secret Manager

```bash
# Create secrets for API keys and configuration
# Replace with your actual API key from OpenRouter

# Create API_KEY secret
echo -n "your-openrouter-api-key-here" | \
gcloud secrets create WHYSPER_API_KEY \
    --data-file=- \
    --replication-policy="automatic"

# Create ACCESS_KEY secret
echo -n "your-access-key-here" | \
gcloud secrets create WHYSPER_ACCESS_KEY \
    --data-file=- \
    --replication-policy="automatic"

# Verify secrets were created
gcloud secrets list
```

---

## Option 1: Cloud Run Deployment (Recommended)

### Step 1: Build the Docker Image

```bash
# Navigate to your project root
cd /path/to/Whysper

# Build the image using Cloud Build
gcloud builds submit \
    --tag ${REGION}-docker.pkg.dev/${PROJECT_ID}/${REPOSITORY_NAME}/${IMAGE_NAME}:latest \
    --timeout=30m

# Alternative: Build locally and push
docker build -t ${REGION}-docker.pkg.dev/${PROJECT_ID}/${REPOSITORY_NAME}/${IMAGE_NAME}:latest .
docker push ${REGION}-docker.pkg.dev/${PROJECT_ID}/${REPOSITORY_NAME}/${IMAGE_NAME}:latest
```

### Step 2: Create Service Account

```bash
# Create service account for Cloud Run
gcloud iam service-accounts create whysper-cloudrun-sa \
    --display-name="Whysper Cloud Run Service Account"

# Grant Secret Manager access
gcloud projects add-iam-policy-binding $PROJECT_ID \
    --member="serviceAccount:whysper-cloudrun-sa@${PROJECT_ID}.iam.gserviceaccount.com" \
    --role="roles/secretmanager.secretAccessor"

# Grant Cloud Storage access (optional)
gcloud projects add-iam-policy-binding $PROJECT_ID \
    --member="serviceAccount:whysper-cloudrun-sa@${PROJECT_ID}.iam.gserviceaccount.com" \
    --role="roles/storage.objectAdmin"
```

### Step 3: Deploy to Cloud Run

```bash
# Deploy the service
gcloud run deploy $SERVICE_NAME \
    --image=${REGION}-docker.pkg.dev/${PROJECT_ID}/${REPOSITORY_NAME}/${IMAGE_NAME}:latest \
    --platform=managed \
    --region=$REGION \
    --allow-unauthenticated \
    --service-account=whysper-cloudrun-sa@${PROJECT_ID}.iam.gserviceaccount.com \
    --memory=2Gi \
    --cpu=1 \
    --timeout=300 \
    --concurrency=80 \
    --min-instances=0 \
    --max-instances=10 \
    --port=8080 \
    --set-env-vars="PROVIDER=openrouter,DEFAULT_MODEL=google/gemini-2.5-flash-preview-09-2025,PORT=8080,API_HOST=0.0.0.0" \
    --set-secrets="API_KEY=WHYSPER_API_KEY:latest,ACCESS_KEY=WHYSPER_ACCESS_KEY:latest"

# Get the service URL
SERVICE_URL=$(gcloud run services describe $SERVICE_NAME \
    --platform=managed \
    --region=$REGION \
    --format='value(status.url)')

echo "Service deployed at: $SERVICE_URL"
```

### Step 4: Configure Custom Domain (Optional)

```bash
# Map a custom domain to your Cloud Run service
gcloud run domain-mappings create \
    --service=$SERVICE_NAME \
    --domain=whysper.example.com \
    --region=$REGION

# Follow instructions to update DNS records
gcloud run domain-mappings describe \
    --domain=whysper.example.com \
    --region=$REGION
```

### Step 5: Set Up Continuous Deployment

Create `cloudbuild.yaml` in your project root:

```yaml
steps:
  # Build the container image
  - name: 'gcr.io/cloud-builders/docker'
    args: ['build', '-t', '${_REGION}-docker.pkg.dev/${PROJECT_ID}/${_REPOSITORY}/${_IMAGE}:${SHORT_SHA}', '.']

  # Push the container image to Artifact Registry
  - name: 'gcr.io/cloud-builders/docker'
    args: ['push', '${_REGION}-docker.pkg.dev/${PROJECT_ID}/${_REPOSITORY}/${_IMAGE}:${SHORT_SHA}']

  # Deploy container image to Cloud Run
  - name: 'gcr.io/google.com/cloudsdktool/cloud-sdk'
    entrypoint: gcloud
    args:
      - 'run'
      - 'deploy'
      - '${_SERVICE_NAME}'
      - '--image=${_REGION}-docker.pkg.dev/${PROJECT_ID}/${_REPOSITORY}/${_IMAGE}:${SHORT_SHA}'
      - '--region=${_REGION}'
      - '--platform=managed'

substitutions:
  _REGION: us-central1
  _REPOSITORY: whysper-repo
  _IMAGE: whysper-web2
  _SERVICE_NAME: whysper-app

images:
  - '${_REGION}-docker.pkg.dev/${PROJECT_ID}/${_REPOSITORY}/${_IMAGE}:${SHORT_SHA}'

options:
  logging: CLOUD_LOGGING_ONLY
  machineType: 'E2_HIGHCPU_8'
  timeout: '1800s'
```

Create a Cloud Build trigger:

```bash
# Connect your repository (GitHub, GitLab, Bitbucket)
gcloud builds triggers create github \
    --name="whysper-deploy-trigger" \
    --repo-name="Whysper" \
    --repo-owner="your-github-username" \
    --branch-pattern="^main$" \
    --build-config="cloudbuild.yaml"
```

---

## Option 2: Compute Engine Deployment

### Step 1: Create Instance Template

```bash
# Create a VM instance template
gcloud compute instance-templates create-with-container whysper-template \
    --machine-type=e2-medium \
    --image-family=cos-stable \
    --image-project=cos-cloud \
    --boot-disk-size=20GB \
    --boot-disk-type=pd-standard \
    --container-image=${REGION}-docker.pkg.dev/${PROJECT_ID}/${REPOSITORY_NAME}/${IMAGE_NAME}:latest \
    --container-restart-policy=always \
    --container-privileged \
    --container-env=PROVIDER=openrouter,PORT=8080,API_HOST=0.0.0.0 \
    --container-env-file=<(echo "API_KEY=$(gcloud secrets versions access latest --secret=WHYSPER_API_KEY)") \
    --tags=http-server,https-server \
    --service-account=whysper-gce-sa@${PROJECT_ID}.iam.gserviceaccount.com \
    --scopes=cloud-platform
```

### Step 2: Create Managed Instance Group

```bash
# Create managed instance group
gcloud compute instance-groups managed create whysper-mig \
    --template=whysper-template \
    --size=1 \
    --region=$REGION \
    --health-check=whysper-health-check

# Set up autoscaling
gcloud compute instance-groups managed set-autoscaling whysper-mig \
    --region=$REGION \
    --max-num-replicas=5 \
    --min-num-replicas=1 \
    --target-cpu-utilization=0.60 \
    --cool-down-period=90
```

### Step 3: Create Health Check

```bash
# Create health check
gcloud compute health-checks create http whysper-health-check \
    --port=8080 \
    --request-path=/api/v1/ \
    --check-interval=10s \
    --timeout=5s \
    --unhealthy-threshold=3 \
    --healthy-threshold=2
```

### Step 4: Create Load Balancer

```bash
# Reserve static IP
gcloud compute addresses create whysper-ip \
    --ip-version=IPV4 \
    --global

# Create backend service
gcloud compute backend-services create whysper-backend \
    --protocol=HTTP \
    --health-checks=whysper-health-check \
    --global

# Add instance group to backend
gcloud compute backend-services add-backend whysper-backend \
    --instance-group=whysper-mig \
    --instance-group-region=$REGION \
    --balancing-mode=UTILIZATION \
    --max-utilization=0.8 \
    --global

# Create URL map
gcloud compute url-maps create whysper-lb \
    --default-service=whysper-backend

# Create HTTP proxy
gcloud compute target-http-proxies create whysper-http-proxy \
    --url-map=whysper-lb

# Create forwarding rule
gcloud compute forwarding-rules create whysper-http-rule \
    --address=whysper-ip \
    --global \
    --target-http-proxy=whysper-http-proxy \
    --ports=80

# Get static IP
gcloud compute addresses describe whysper-ip \
    --format="get(address)" \
    --global
```

### Step 5: Set Up SSL/HTTPS (Recommended)

```bash
# Create managed SSL certificate
gcloud compute ssl-certificates create whysper-ssl \
    --domains=whysper.example.com

# Create HTTPS proxy
gcloud compute target-https-proxies create whysper-https-proxy \
    --url-map=whysper-lb \
    --ssl-certificates=whysper-ssl

# Create HTTPS forwarding rule
gcloud compute forwarding-rules create whysper-https-rule \
    --address=whysper-ip \
    --global \
    --target-https-proxy=whysper-https-proxy \
    --ports=443
```

---

## Post-Deployment Configuration

### 1. Verify Deployment

```bash
# For Cloud Run
curl $SERVICE_URL/api/v1/

# Expected response: {"message": "Welcome to Whysper API"}

# Test health endpoint
curl $SERVICE_URL/api/v1/health

# Expected response: {"status": "healthy"}
```

### 2. Configure CORS (if needed)

Update [backend/app/main.py](../backend/app/main.py:28) to add your frontend domain:

```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://your-domain.com"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

### 3. Set Up Cloud Storage for Diagrams (Optional)

```bash
# Create a bucket for diagram storage
gsutil mb -l $REGION gs://${PROJECT_ID}-diagrams

# Set bucket permissions
gsutil iam ch \
    serviceAccount:whysper-cloudrun-sa@${PROJECT_ID}.iam.gserviceaccount.com:objectAdmin \
    gs://${PROJECT_ID}-diagrams
```

Update environment variables:

```bash
gcloud run services update $SERVICE_NAME \
    --region=$REGION \
    --update-env-vars="DIAGRAM_STORAGE_BUCKET=${PROJECT_ID}-diagrams"
```

### 4. Configure Cloud SQL (Optional)

```bash
# Create PostgreSQL instance
gcloud sql instances create whysper-db \
    --database-version=POSTGRES_14 \
    --tier=db-f1-micro \
    --region=$REGION

# Create database
gcloud sql databases create whysper \
    --instance=whysper-db

# Create user
gcloud sql users create whysper-user \
    --instance=whysper-db \
    --password=YOUR_SECURE_PASSWORD

# Get connection name
gcloud sql instances describe whysper-db \
    --format='value(connectionName)'


---

## Monitoring and Maintenance

### 1. Set Up Cloud Monitoring Alerts

```bash
# Create alert for high error rate
gcloud alpha monitoring policies create \
    --notification-channels=CHANNEL_ID \
    --display-name="High Error Rate Alert" \
    --condition-display-name="Error rate > 5%" \
    --condition-threshold-value=0.05 \
    --condition-threshold-duration=300s
```

### 2. View Logs

```bash
# View Cloud Run logs
gcloud logging read "resource.type=cloud_run_revision \
    AND resource.labels.service_name=$SERVICE_NAME" \
    --limit=50 \
    --format=json

# Stream logs in real-time
gcloud logging tail "resource.type=cloud_run_revision \
    AND resource.labels.service_name=$SERVICE_NAME"
```

### 3. Monitor Performance

```bash
# View service metrics
gcloud run services describe $SERVICE_NAME \
    --region=$REGION \
    --format=yaml
```

Access Cloud Console for detailed metrics:
```
https://console.cloud.google.com/run/detail/$REGION/$SERVICE_NAME/metrics
```

### 4. Update Application

```bash
# Build new version
gcloud builds submit \
    --tag ${REGION}-docker.pkg.dev/${PROJECT_ID}/${REPOSITORY_NAME}/${IMAGE_NAME}:v2

# Deploy update (gradual rollout)
gcloud run services update $SERVICE_NAME \
    --region=$REGION \
    --image=${REGION}-docker.pkg.dev/${PROJECT_ID}/${REPOSITORY_NAME}/${IMAGE_NAME}:v2

# Rollback if needed
gcloud run services update $SERVICE_NAME \
    --region=$REGION \
    --to-latest
```

### 5. Backup and Disaster Recovery

```bash
# Export container images
gcloud artifacts docker images list \
    ${REGION}-docker.pkg.dev/${PROJECT_ID}/${REPOSITORY_NAME}

# Backup secrets
gcloud secrets versions list WHYSPER_API_KEY

# Create snapshot (for Compute Engine)
gcloud compute disks snapshot whysper-disk \
    --snapshot-names=whysper-snapshot-$(date +%Y%m%d) \
    --zone=$REGION-a
```

---

## Troubleshooting

### Issue 1: Container Fails to Start

```bash
# Check Cloud Build logs
gcloud builds list --limit=5

# Check Cloud Run logs
gcloud logging read "resource.type=cloud_run_revision" \
    --limit=50

# Test container locally
docker run -p 8080:8080 \
    -e API_KEY=test-key \
    -e PROVIDER=openrouter \
    ${REGION}-docker.pkg.dev/${PROJECT_ID}/${REPOSITORY_NAME}/${IMAGE_NAME}:latest
```

**Common Fixes:**
- Ensure Playwright dependencies are installed
- Check D2 binary is included in container
- Verify Python dependencies are correct

### Issue 2: "Permission Denied" Errors

```bash
# Grant Cloud Run service account permissions
gcloud projects add-iam-policy-binding $PROJECT_ID \
    --member="serviceAccount:whysper-cloudrun-sa@${PROJECT_ID}.iam.gserviceaccount.com" \
    --role="roles/secretmanager.secretAccessor"
```

### Issue 3: Slow Performance

```bash
# Increase CPU and memory
gcloud run services update $SERVICE_NAME \
    --region=$REGION \
    --memory=4Gi \
    --cpu=2

# Set minimum instances to avoid cold starts
gcloud run services update $SERVICE_NAME \
    --region=$REGION \
    --min-instances=1
```

### Issue 4: Playwright Browser Issues

**Solution:** Ensure the Dockerfile includes:
```dockerfile
RUN playwright install --with-deps chromium
```

### Issue 5: D2 Diagrams Not Rendering

```bash
# Check if D2 binary is in PATH
docker exec <container-id> which d2

# Verify D2 binary is executable
docker exec <container-id> d2 --version
```

---

## Cleanup

```bash
# Delete Cloud Run service
gcloud run services delete $SERVICE_NAME --region=$REGION

# Delete container images
gcloud artifacts docker images delete \
    ${REGION}-docker.pkg.dev/${PROJECT_ID}/${REPOSITORY_NAME}/${IMAGE_NAME}:latest

# Delete secrets
gcloud secrets delete WHYSPER_API_KEY
gcloud secrets delete WHYSPER_ACCESS_KEY

# Delete repository
gcloud artifacts repositories delete $REPOSITORY_NAME --location=$REGION
```

---

## Next Steps

1. Set up monitoring dashboards
2. Configure custom domain
3. Implement backup strategy
4. Set up staging environment
5. Configure CI/CD pipeline

For more information, see:
- [GCP Architecture Document](GCP_ARCHITECTURE.md)
- [Dockerfile](../Dockerfile)
- [Main Application](../backend/app/main.py)
