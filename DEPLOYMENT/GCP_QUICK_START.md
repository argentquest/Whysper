# Google Cloud Platform - Quick Start Guide
## Deploy Whysper Web2 in 10 Minutes

---

## Prerequisites

- Google Cloud account with billing enabled
- `gcloud` CLI installed
- OpenRouter API key (get from https://openrouter.ai/keys)

---

## Quick Deploy to Cloud Run (Recommended)

### Step 1: Set Up GCP Project (2 minutes)

```bash
# Set your project ID
export PROJECT_ID="whysper-prod"  # Change this to your project
export REGION="us-central1"

# Create project (if new)
gcloud projects create $PROJECT_ID --name="Whysper Production"

# Set active project
gcloud config set project $PROJECT_ID

# Enable billing (must be done via console if first time)
# Visit: https://console.cloud.google.com/billing

# Enable required APIs
gcloud services enable \
    cloudbuild.googleapis.com \
    run.googleapis.com \
    artifactregistry.googleapis.com \
    secretmanager.googleapis.com
```

### Step 2: Create Secrets (1 minute)

```bash
# Store your OpenRouter API key
echo -n "YOUR_OPENROUTER_API_KEY_HERE" | \
gcloud secrets create WHYSPER_API_KEY \
    --data-file=- \
    --replication-policy="automatic"

# Create access key (optional, for authentication)
echo -n "your-secure-access-key" | \
gcloud secrets create WHYSPER_ACCESS_KEY \
    --data-file=- \
    --replication-policy="automatic"
```

### Step 3: Create Artifact Registry (1 minute)

```bash
# Create container repository
gcloud artifacts repositories create whysper-repo \
    --repository-format=docker \
    --location=$REGION \
    --description="Whysper Web2 container images"

# Configure Docker authentication
gcloud auth configure-docker ${REGION}-docker.pkg.dev
```

### Step 4: Build and Deploy (5-6 minutes)

```bash
# Navigate to your project directory
cd /path/to/Whysper

# Build and deploy in one command
gcloud run deploy whysper-app \
    --source=. \
    --region=$REGION \
    --allow-unauthenticated \
    --memory=2Gi \
    --cpu=1 \
    --timeout=300 \
    --min-instances=0 \
    --max-instances=10 \
    --port=8080 \
    --set-env-vars="PROVIDER=openrouter,DEFAULT_MODEL=google/gemini-2.5-flash-preview-09-2025,PORT=8080,API_HOST=0.0.0.0" \
    --set-secrets="API_KEY=WHYSPER_API_KEY:latest,ACCESS_KEY=WHYSPER_ACCESS_KEY:latest"
```

### Step 5: Get Your URL and Test (30 seconds)

```bash
# Get service URL
SERVICE_URL=$(gcloud run services describe whysper-app \
    --region=$REGION \
    --format='value(status.url)')

echo "🚀 Your app is live at: $SERVICE_URL"

# Test the API
curl $SERVICE_URL/api/v1/

# Expected response: {"message": "Welcome to Whysper API"}
```

---

## Alternative: Build Separately (For More Control)

### Step 1-3: Same as above

### Step 4a: Build Container Image

```bash
# Build using Cloud Build
gcloud builds submit \
    --tag ${REGION}-docker.pkg.dev/${PROJECT_ID}/whysper-repo/whysper-web2:latest \
    --timeout=30m
```

### Step 4b: Deploy Pre-built Image

```bash
# Create service account
gcloud iam service-accounts create whysper-cloudrun-sa \
    --display-name="Whysper Cloud Run Service Account"

# Grant secret access
gcloud projects add-iam-policy-binding $PROJECT_ID \
    --member="serviceAccount:whysper-cloudrun-sa@${PROJECT_ID}.iam.gserviceaccount.com" \
    --role="roles/secretmanager.secretAccessor"

# Deploy
gcloud run deploy whysper-app \
    --image=${REGION}-docker.pkg.dev/${PROJECT_ID}/whysper-repo/whysper-web2:latest \
    --region=$REGION \
    --service-account=whysper-cloudrun-sa@${PROJECT_ID}.iam.gserviceaccount.com \
    --allow-unauthenticated \
    --memory=2Gi \
    --cpu=1 \
    --timeout=300 \
    --min-instances=0 \
    --max-instances=10 \
    --port=8080 \
    --set-env-vars="PROVIDER=openrouter,DEFAULT_MODEL=google/gemini-2.5-flash-preview-09-2025,PORT=8080,API_HOST=0.0.0.0" \
    --set-secrets="API_KEY=WHYSPER_API_KEY:latest,ACCESS_KEY=WHYSPER_ACCESS_KEY:latest"
```

---

## Post-Deployment

### View Logs

```bash
# Stream live logs
gcloud logging tail "resource.type=cloud_run_revision \
    AND resource.labels.service_name=whysper-app" \
    --format=json

# View in Cloud Console
echo "https://console.cloud.google.com/run/detail/${REGION}/whysper-app/logs"
```

### Monitor Performance

```bash
# View metrics in Cloud Console
echo "https://console.cloud.google.com/run/detail/${REGION}/whysper-app/metrics"
```

### Update Deployment

```bash
# After making code changes
gcloud run deploy whysper-app \
    --source=. \
    --region=$REGION
```

---

## Cost Optimization Tips

1. **Set minimum instances to 0** (default) - Pay only when in use
2. **Use --cpu-boost** flag for faster cold starts
3. **Monitor usage** in Cloud Console to adjust resources
4. **Set up budget alerts** to avoid surprises

```bash
# Example: Set budget alert
gcloud billing budgets create \
    --billing-account=BILLING_ACCOUNT_ID \
    --display-name="Whysper Monthly Budget" \
    --budget-amount=50USD \
    --threshold-rule=percent=50 \
    --threshold-rule=percent=90 \
    --threshold-rule=percent=100
```

---

## Troubleshooting

### Build Fails

```bash
# Check build logs
gcloud builds list --limit=5

# View specific build
gcloud builds log BUILD_ID
```

### Deployment Fails

```bash
# Check service status
gcloud run services describe whysper-app --region=$REGION

# Check revisions
gcloud run revisions list --service=whysper-app --region=$REGION
```

### App Not Responding

```bash
# Check logs for errors
gcloud logging read "resource.type=cloud_run_revision" \
    --limit=50 \
    --format=json

# Test locally
docker build -t whysper-test .
docker run -p 8080:8080 -e API_KEY=test whysper-test
```

---

## Next Steps

- [ ] Set up custom domain
- [ ] Configure CI/CD pipeline
- [ ] Add Cloud Storage for diagrams
- [ ] Set up monitoring alerts
- [ ] Configure backup strategy

See detailed guides:
- [Full Architecture](GCP_ARCHITECTURE.md)
- [Deployment Guide](GCP_DEPLOYMENT_GUIDE.md)
- [Security Best Practices](GCP_SECURITY.md)

---

## Cleanup

```bash
# Delete everything (when done testing)
gcloud run services delete whysper-app --region=$REGION
gcloud secrets delete WHYSPER_API_KEY
gcloud secrets delete WHYSPER_ACCESS_KEY
gcloud artifacts repositories delete whysper-repo --location=$REGION
```

---

## Support

- GCP Documentation: https://cloud.google.com/run/docs
- Cloud Run Pricing: https://cloud.google.com/run/pricing
- OpenRouter Docs: https://openrouter.ai/docs
