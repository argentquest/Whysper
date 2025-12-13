# Deployment (Compute Engine + Docker, UBI 8.1)

This project deploys as a single container image based on Red Hat UBI 8.1. Node.js is used only during the build to produce the React frontend; FastAPI serves both the API and the built static assets at runtime. No database servers are required.

## High-Level Architecture
- Client → HTTPS (optional Cloud CDN) → External HTTP(S) Load Balancer (managed SSL) → Compute Engine VM running Docker → UBI 8.1 container (FastAPI + built React).
- Services used: Compute Engine, Artifact Registry, Secret Manager, Cloud Logging and Monitoring (Ops Agent), optional Cloud CDN and Cloud Storage (assets/backups).

### Text Diagram
- Client (Browser)  
  ↓ HTTPS (Cloud CDN optional)  
  External HTTP(S) Load Balancer (managed SSL)  
  ↓  
  Compute Engine VM (Docker: UBI 8.1 container serving API + static React)  
  ↓  
  - Secret Manager (env/secrets)  
  - Cloud Storage (optional)  
  - Cloud Logging/Monitoring (Ops Agent)

## Dockerfile Pattern (multi-stage on UBI 8.1)
Use UBI 8.1 for both build and runtime. Node.js is only in the build stage.

```Dockerfile
# Build stage
FROM registry.access.redhat.com/ubi8/nodejs-18:1-101 as build
WORKDIR /app
COPY package*.json ./
RUN npm ci
COPY . .
RUN npm run build                   # produces frontend build (e.g., dist/)
# Optionally cache Python deps here if desired:
# RUN pip install --user -r requirements.txt

# Runtime stage
FROM registry.access.redhat.com/ubi8/ubi:8.1
WORKDIR /app
RUN yum install -y python3 python3-pip && yum clean all
COPY --from=build /app /app
RUN pip3 install -r requirements.txt
EXPOSE 8080
CMD ["uvicorn", "backend.app.main:app", "--host", "0.0.0.0", "--port", "8080"]
```

## GCP Setup (brand-new project)
1) Enable APIs: Compute Engine, Artifact Registry, Secret Manager, Cloud Logging, Cloud Monitoring.
2) Artifact Registry repo:
   - `gcloud artifacts repositories create whysper-repo --repository-format=docker --location=us-central1`
3) Build and push image (recommended off-VM):
   - `gcloud auth configure-docker us-central1-docker.pkg.dev`
   - `docker build -t us-central1-docker.pkg.dev/PROJECT_ID/whysper-repo/whysper:latest .`
   - `docker push us-central1-docker.pkg.dev/PROJECT_ID/whysper-repo/whysper:latest`
4) Secrets/config:
   - Store sensitive values in Secret Manager.
   - Non-secret config via env vars. Optionally fetch secrets at boot and write an env file.

## VM Provisioning
1) Create VM:
   - Machine type: e2-medium (adjust as needed).
   - OS: minimal Debian/Ubuntu or COS; Docker will run the UBI 8.1 container (host OS need not be UBI).
   - Firewall: allow HTTPS (443) and optionally HTTP (80) for redirect.
   - Service account: grant Artifact Registry Reader, Secret Manager Access (if used), Logging/Monitoring agent writer.
2) Install Docker (if not using COS):
   - Debian/Ubuntu: `sudo apt-get update && sudo apt-get install -y docker.io`
   - Add your user to docker group: `sudo usermod -aG docker $USER` (re-login).
3) Optional: install Ops Agent for Logging/Monitoring.

## Run the Container on the VM
Pull and run the image, loading env vars from a file produced locally or from Secret Manager.

```bash
gcloud auth configure-docker us-central1-docker.pkg.dev
docker pull us-central1-docker.pkg.dev/PROJECT_ID/whysper-repo/whysper:latest
docker run -d --name whysper -p 8080:8080 --env-file /etc/whysper.env \
  us-central1-docker.pkg.dev/PROJECT_ID/whysper-repo/whysper:latest
```

### Systemd unit (auto-start on boot)
Create `/etc/systemd/system/whysper.service`:
```
[Unit]
Description=Whysper container
After=network-online.target docker.service
Wants=network-online.target docker.service

[Service]
Restart=always
ExecStartPre=/usr/bin/docker pull us-central1-docker.pkg.dev/PROJECT_ID/whysper-repo/whysper:latest
ExecStart=/usr/bin/docker run --rm --name whysper -p 8080:8080 --env-file /etc/whysper.env \
  us-central1-docker.pkg.dev/PROJECT_ID/whysper-repo/whysper:latest
ExecStop=/usr/bin/docker stop whysper

[Install]
WantedBy=multi-user.target
```
Enable and start:
```bash
sudo systemctl daemon-reload
sudo systemctl enable whysper
sudo systemctl start whysper
```

## HTTPS and Domain
Two options:
- Minimal: point DNS A record to VM external IP. Run a reverse proxy on the VM (NGINX/Caddy) on 443, terminate TLS (Let’s Encrypt), and proxy to `localhost:8080`.
- Managed: use External HTTP(S) Load Balancer with managed SSL, optional Cloud CDN, backend pointing to an instance group containing this VM.

## Updates
- Rebuild/push new image → SSH or use a small script/CI job to `docker pull` latest and `docker restart whysper` (or systemd will restart after pull).
- Keep the env file stable; rotate secrets via Secret Manager and refresh the env file before restart.

## Notes and Practices
- Container base remains `registry.access.redhat.com/ubi8/ubi:8.1` to satisfy UBI 8.1 requirement.
- Node.js is only used in the build stage; not required at runtime unless SSR is added.
- If using Cloud Storage for assets/backups, mount via signed URLs or client SDK; no DB services are provisioned.
- Consider setting health checks (e.g., `/health`) if fronted by a Load Balancer.
