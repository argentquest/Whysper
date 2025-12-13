# Deploying Whysper on Google Cloud Platform (GCP)

This guide details the architecture and step-by-step instructions to deploy Whysper as a single containerized application on Google Cloud.

## Architecture Overview

The application is packaged as a "One Image" solution, containing both the React Frontend (compiled to static files) and the FastAPI Backend. This simplifies deployment to a single service.

### Google Cloud Architecture Diagram

```mermaid
graph TD
    User[User / Client] -->|HTTPS| LB[Cloud Load Balancing]
    LB -->|Traffic| CR[Cloud Run Service]

    subgraph "Google Cloud Platform"
        subgraph "Cloud Run Container (The One Image)"
            FE[React Frontend (Static)]
            BE[FastAPI Backend]
            FE -->|Served by| BE
        end

        AR[Artifact Registry] -->|Deploys Image| CR
    end

    BE -->|API Calls| ExtAI[External AI Provider (OpenRouter)]

    style CR fill:#4285F4,stroke:#fff,stroke-width:2px,color:white
    style AR fill:#EA4335,stroke:#fff,stroke-width:2px,color:white
    style LB fill:#34A853,stroke:#fff,stroke-width:2px,color:white
```

### Components
1.  **Google Artifact Registry**: Stores the Docker image.
2.  **Google Cloud Run**: Runs the stateless container (Serverless). This is the recommended service for this "One Image" architecture as it scales automatically and charges only for usage.
    *   *Alternative*: **Google Compute Engine** (VM) if you prefer managing a VM with Docker/Podman installed, effectively mimicking an "OCP Node".
3.  **The "One Image"**:
    *   **Base**: Red Hat UBI 8 with Python 3.9.
    *   **Content**: React Static Files + FastAPI App.
    *   **No Database**: As requested, the app runs statelessly.

---

## Step-by-Step Deployment Instructions

### Prerequisites
1.  **Google Cloud Project** created.
2.  **gcloud CLI** installed and authenticated (`gcloud auth login`).
3.  **Docker** installed locally (for building).

### 1. Enable Required GCP Services
```bash
gcloud services enable artifactregistry.googleapis.com run.googleapis.com cloudbuild.googleapis.com
```

### 2. Create an Artifact Registry Repository
Create a Docker repository named `whysper-repo` in your preferred region (e.g., `us-central1`).
```bash
gcloud artifacts repositories create whysper-repo \
    --repository-format=docker \
    --location=us-central1 \
    --description="Whysper App Repository"
```

### 3. Build the "One Image"
You can build the image using Cloud Build (recommended) or locally.

**Option A: Cloud Build (Easiest)**
This builds the image directly in the cloud, so you don't need to worry about local Docker setup or uploading large layers.
```bash
gcloud builds submit --tag us-central1-docker.pkg.dev/YOUR_PROJECT_ID/whysper-repo/whysper-app:v1 .
```
*(Replace `YOUR_PROJECT_ID` with your actual GCP project ID)*

**Option B: Local Build**
```bash
docker build -t us-central1-docker.pkg.dev/YOUR_PROJECT_ID/whysper-repo/whysper-app:v1 .
docker push us-central1-docker.pkg.dev/YOUR_PROJECT_ID/whysper-repo/whysper-app:v1
```

### 4. Deploy to Cloud Run
Deploy the image as a service.
```bash
gcloud run deploy whysper-service \
    --image us-central1-docker.pkg.dev/YOUR_PROJECT_ID/whysper-repo/whysper-app:v1 \
    --platform managed \
    --region us-central1 \
    --allow-unauthenticated \
    --port 8080 \
    --set-env-vars API_KEY="your-openrouter-key",PROVIDER="openrouter"
```

*   **--allow-unauthenticated**: Makes the app publicly accessible. Remove this if you want internal-only access.
*   **--set-env-vars**: Set your `API_KEY` here.

### 5. Access the Application
The command will output a URL (e.g., `https://whysper-service-xyz-uc.a.run.app`). Open this URL in your browser.
-   The **React Frontend** will load.
-   It talks to the **FastAPI Backend** on the same URL (e.g., `/api/v1/...`).

## Alternative: Deploying on Compute Engine (VM)
If you need to simulate an OCP Node more closely:

1.  Create a VM instance with a Container-Optimized OS or RHEL 8.
2.  SSH into the VM.
3.  Pull the image from Artifact Registry.
4.  Run it with Docker/Podman:
    ```bash
    docker run -d -p 80:8080 -e API_KEY="your-key" us-central1-docker.pkg.dev/.../whysper-app:v1
    ```
