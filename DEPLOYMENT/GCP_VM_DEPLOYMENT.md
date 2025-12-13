# Google Compute Engine VM Deployment Guide
## Deploy Whysper Web2 on RHEL-Compatible VM

---

## Table of Contents
1. [VM Specifications](#vm-specifications)
2. [Initial VM Setup](#initial-vm-setup)
3. [Install System Dependencies](#install-system-dependencies)
4. [Install D2 CLI](#install-d2-cli)
5. [Deploy Application](#deploy-application)
6. [Configure Systemd Service](#configure-systemd-service)
7. [Set Up NGINX Reverse Proxy](#set-up-nginx-reverse-proxy)
8. [SSL/HTTPS Configuration](#sslhttps-configuration)
9. [Monitoring and Logs](#monitoring-and-logs)
10. [Maintenance and Updates](#maintenance-and-updates)

---

## VM Specifications

### Recommended VM Configuration

| Specification | Minimum | Recommended | High Traffic |
|---------------|---------|-------------|--------------|
| **Machine Type** | e2-small | e2-medium | e2-standard-2 |
| **vCPUs** | 2 | 2 | 2 |
| **Memory** | 2 GB | 4 GB | 8 GB |
| **Boot Disk** | 20 GB | 30 GB | 50 GB |
| **Disk Type** | Standard | SSD | SSD |
| **Operating System** | RHEL 8.1+ | RHEL 8.1+ | RHEL 8.1+ |
| **Monthly Cost** | ~$14 | ~$24 | ~$49 |

### Operating System Options

1. **Red Hat Enterprise Linux 8** (Recommended)
   - Subscription required
   - Enterprise support available
   - RHEL Universal Base Image 8.1+

2. **Rocky Linux 8** (Free RHEL Alternative)
   - 100% RHEL-compatible
   - Community-supported
   - No subscription fees

3. **AlmaLinux 8** (Free RHEL Alternative)
   - 100% RHEL-compatible
   - Community-supported
   - No subscription fees

---

## Initial VM Setup

### Step 1: Create Compute Engine VM

```bash
# Set project variables
export PROJECT_ID="whysper-prod"
export VM_NAME="whysper-vm"
export ZONE="us-central1-a"
export REGION="us-central1"

# Set project
gcloud config set project $PROJECT_ID

# Create VM with Rocky Linux 8 (RHEL-compatible, free)
gcloud compute instances create $VM_NAME \
    --zone=$ZONE \
    --machine-type=e2-medium \
    --image-family=rocky-linux-8 \
    --image-project=rocky-linux-cloud \
    --boot-disk-size=30GB \
    --boot-disk-type=pd-ssd \
    --tags=http-server,https-server \
    --metadata=startup-script='#!/bin/bash
        echo "VM initialized at $(date)" > /var/log/startup.log
    '

# Alternative: Use Red Hat Enterprise Linux 8 (requires RHEL subscription)
# gcloud compute instances create $VM_NAME \
#     --zone=$ZONE \
#     --machine-type=e2-medium \
#     --image-family=rhel-8 \
#     --image-project=rhel-cloud \
#     --boot-disk-size=30GB \
#     --boot-disk-type=pd-ssd \
#     --tags=http-server,https-server

# Create firewall rules
gcloud compute firewall-rules create allow-http \
    --allow=tcp:80 \
    --target-tags=http-server \
    --description="Allow HTTP traffic"

gcloud compute firewall-rules create allow-https \
    --allow=tcp:443 \
    --target-tags=https-server \
    --description="Allow HTTPS traffic"

# Get VM external IP
VM_IP=$(gcloud compute instances describe $VM_NAME \
    --zone=$ZONE \
    --format='get(networkInterfaces[0].accessConfigs[0].natIP)')

echo "VM created at IP: $VM_IP"
```

### Step 2: Connect to VM

```bash
# SSH into the VM
gcloud compute ssh $VM_NAME --zone=$ZONE

# Alternative: Use SSH key
gcloud compute ssh $VM_NAME --zone=$ZONE --ssh-key-file=~/.ssh/id_rsa
```

---

## Install System Dependencies

### Step 3: Update System and Install Base Packages

```bash
# Update system packages
sudo dnf update -y

# Install development tools
sudo dnf groupinstall "Development Tools" -y

# Install required packages
sudo dnf install -y \
    git \
    wget \
    curl \
    unzip \
    gcc \
    gcc-c++ \
    make \
    openssl-devel \
    bzip2-devel \
    libffi-devel \
    zlib-devel \
    ca-certificates

# Install EPEL repository (Extra Packages for Enterprise Linux)
sudo dnf install -y epel-release
```

### Step 4: Install Python 3.11

```bash
# Install Python 3.11
sudo dnf install -y python3.11 python3.11-pip python3.11-devel

# Verify installation
python3.11 --version

# Create symbolic links
sudo alternatives --set python3 /usr/bin/python3.11
sudo ln -sf /usr/bin/python3.11 /usr/bin/python
sudo ln -sf /usr/bin/pip3.11 /usr/bin/pip

# Upgrade pip
python -m pip install --upgrade pip setuptools wheel
```

### Step 5: Install Node.js 18 (for building frontend)

```bash
# Install Node.js 18.x from NodeSource
curl -fsSL https://rpm.nodesource.com/setup_18.x | sudo bash -
sudo dnf install -y nodejs

# Verify installation
node --version
npm --version
```

---

## Install D2 CLI

### Step 6: Download and Install D2

```bash
# Detect architecture
ARCH=$(uname -m)
if [ "$ARCH" = "x86_64" ]; then
    D2_ARCH="amd64"
elif [ "$ARCH" = "aarch64" ]; then
    D2_ARCH="arm64"
else
    echo "Unsupported architecture: $ARCH"
    exit 1
fi

# Set D2 version
D2_VERSION="v0.6.3"

# Download D2
wget -O /tmp/d2.tar.gz \
    "https://github.com/terrastruct/d2/releases/download/${D2_VERSION}/d2-${D2_VERSION}-linux-${D2_ARCH}.tar.gz"

# Extract and install
tar -xzf /tmp/d2.tar.gz -C /tmp
sudo mv /tmp/d2-${D2_VERSION}/bin/d2 /usr/local/bin/d2
sudo chmod +x /usr/local/bin/d2

# Cleanup
rm -rf /tmp/d2*

# Verify installation
d2 --version
```

**Expected output:**
```
v0.6.3
```

### Step 7: Test D2 CLI

```bash
# Create a test D2 diagram
cat > /tmp/test.d2 <<'EOF'
direction: right

users: Users {
  shape: person
}

app: Application {
  shape: cloud
}

db: Database {
  shape: cylinder
}

users -> app: HTTP Request
app -> db: Query
EOF

# Render the diagram
d2 /tmp/test.d2 /tmp/test.svg

# Check if SVG was created
ls -lh /tmp/test.svg

# Expected: SVG file created successfully
```

---

## Deploy Application

### Step 8: Clone Repository and Set Up Application

```bash
# Create application directory
sudo mkdir -p /opt/whysper
sudo chown $USER:$USER /opt/whysper
cd /opt/whysper

# Clone your repository (replace with your repo URL)
git clone https://github.com/YOUR_USERNAME/Whysper.git .

# Or upload files via SCP
# gcloud compute scp --recurse ./Whysper/* $VM_NAME:/opt/whysper --zone=$ZONE
```

### Step 9: Build Frontend

```bash
# Navigate to frontend directory
cd /opt/whysper/frontend

# Install dependencies
npm ci --only=production

# Build frontend
npm run build

# Copy built files to backend static directory
sudo mkdir -p /opt/whysper/backend/static
sudo cp -r dist/* /opt/whysper/backend/static/

# Verify files copied
ls -la /opt/whysper/backend/static/
```

### Step 10: Set Up Python Virtual Environment

```bash
# Navigate to project root
cd /opt/whysper

# Create virtual environment
python -m venv venv

# Activate virtual environment
source venv/bin/activate

# Install Python dependencies
pip install -r requirements.txt

# Verify installation
pip list
```

### Step 11: Configure Environment Variables

```bash
# Create .env file in backend directory
cd /opt/whysper/backend

cat > .env <<EOF
# API Configuration
API_KEY=your-openrouter-api-key-here
ACCESS_KEY=your-secure-access-key

# Provider Configuration
PROVIDER=openrouter
DEFAULT_MODEL=google/gemini-2.5-flash-preview-09-2025

# Server Configuration
API_PORT=8080
API_HOST=0.0.0.0

# Path Configuration
STATIC_DIR=/opt/whysper/backend/static
PROMPTS_DIR=/opt/whysper
D2_EXECUTABLE_PATH=/usr/local/bin/d2

# Application Settings
SCORE_TARGET=80
DEBUG_LOGGING=true
LOG_LEVEL=INFO
EOF

# Set proper permissions
chmod 600 .env
```

### Step 12: Test Application

```bash
# Activate virtual environment
cd /opt/whysper
source venv/bin/activate

# Run application manually
cd backend
python main.py

# Open another terminal and test
curl http://localhost:8080/api/v1/

# Expected response: {"message": "Welcome to Whysper API"}

# Stop the application (Ctrl+C)
```

---

## Configure Systemd Service

### Step 13: Create Systemd Service File

```bash
# Create service file
sudo tee /etc/systemd/system/whysper.service > /dev/null <<'EOF'
[Unit]
Description=Whysper Web2 Application
After=network.target

[Service]
Type=simple
User=whysper
Group=whysper
WorkingDirectory=/opt/whysper/backend
Environment="PATH=/opt/whysper/venv/bin:/usr/local/bin:/usr/bin"
ExecStart=/opt/whysper/venv/bin/python main.py
Restart=always
RestartSec=10
StandardOutput=journal
StandardError=journal
SyslogIdentifier=whysper

# Security settings
NoNewPrivileges=true
PrivateTmp=true
ProtectSystem=strict
ProtectHome=true
ReadWritePaths=/opt/whysper

[Install]
WantedBy=multi-user.target
EOF
```

### Step 14: Create Application User

```bash
# Create whysper user (no login shell for security)
sudo useradd -r -s /bin/false whysper

# Set ownership
sudo chown -R whysper:whysper /opt/whysper

# Set permissions
sudo chmod -R 755 /opt/whysper
sudo chmod 600 /opt/whysper/backend/.env
```

### Step 15: Start and Enable Service

```bash
# Reload systemd
sudo systemctl daemon-reload

# Start service
sudo systemctl start whysper

# Check status
sudo systemctl status whysper

# Enable service to start on boot
sudo systemctl enable whysper

# View logs
sudo journalctl -u whysper -f
```

---

## Set Up NGINX Reverse Proxy

### Step 16: Install NGINX

```bash
# Install NGINX
sudo dnf install -y nginx

# Start and enable NGINX
sudo systemctl start nginx
sudo systemctl enable nginx

# Check status
sudo systemctl status nginx
```

### Step 17: Configure NGINX

```bash
# Create NGINX configuration
sudo tee /etc/nginx/conf.d/whysper.conf > /dev/null <<'EOF'
# Upstream backend server
upstream whysper_backend {
    server 127.0.0.1:8080 fail_timeout=0;
}

# HTTP server (redirect to HTTPS)
server {
    listen 80;
    server_name _;

    # Redirect all HTTP to HTTPS
    return 301 https://$host$request_uri;
}

# HTTPS server
server {
    listen 443 ssl http2;
    server_name _;

    # SSL certificates (will be configured later)
    ssl_certificate /etc/nginx/ssl/cert.pem;
    ssl_certificate_key /etc/nginx/ssl/key.pem;

    # SSL configuration
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers HIGH:!aNULL:!MD5;
    ssl_prefer_server_ciphers on;

    # Client max body size
    client_max_body_size 100M;

    # Access and error logs
    access_log /var/log/nginx/whysper_access.log;
    error_log /var/log/nginx/whysper_error.log;

    # Proxy settings
    location / {
        proxy_pass http://whysper_backend;
        proxy_http_version 1.1;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";

        # Timeouts for long-running requests
        proxy_connect_timeout 300s;
        proxy_send_timeout 300s;
        proxy_read_timeout 300s;
    }

    # Static files (optional, if serving separately)
    location /static {
        alias /opt/whysper/backend/static;
        expires 30d;
        add_header Cache-Control "public, immutable";
    }
}
EOF

# For now, create self-signed SSL certificate
sudo mkdir -p /etc/nginx/ssl
sudo openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
    -keyout /etc/nginx/ssl/key.pem \
    -out /etc/nginx/ssl/cert.pem \
    -subj "/C=US/ST=State/L=City/O=Organization/CN=localhost"

# Test NGINX configuration
sudo nginx -t

# Reload NGINX
sudo systemctl reload nginx
```

### Step 18: Configure SELinux (if enabled)

```bash
# Check if SELinux is enabled
sestatus

# If SELinux is enabled, allow NGINX to connect to backend
sudo setsebool -P httpd_can_network_connect 1

# Allow NGINX to serve static files
sudo chcon -R -t httpd_sys_content_t /opt/whysper/backend/static
```

---

## SSL/HTTPS Configuration

### Step 19: Install Let's Encrypt SSL Certificate

```bash
# Install Certbot
sudo dnf install -y certbot python3-certbot-nginx

# Stop NGINX temporarily
sudo systemctl stop nginx

# Obtain certificate (replace with your domain)
sudo certbot certonly --standalone \
    -d your-domain.com \
    -d www.your-domain.com \
    --agree-tos \
    --email your-email@example.com

# Update NGINX configuration to use Let's Encrypt certificates
sudo tee /etc/nginx/conf.d/whysper.conf > /dev/null <<'EOF'
upstream whysper_backend {
    server 127.0.0.1:8080 fail_timeout=0;
}

server {
    listen 80;
    server_name your-domain.com www.your-domain.com;
    return 301 https://$host$request_uri;
}

server {
    listen 443 ssl http2;
    server_name your-domain.com www.your-domain.com;

    # Let's Encrypt SSL certificates
    ssl_certificate /etc/letsencrypt/live/your-domain.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/your-domain.com/privkey.pem;

    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers HIGH:!aNULL:!MD5;
    ssl_prefer_server_ciphers on;

    client_max_body_size 100M;

    access_log /var/log/nginx/whysper_access.log;
    error_log /var/log/nginx/whysper_error.log;

    location / {
        proxy_pass http://whysper_backend;
        proxy_http_version 1.1;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";

        proxy_connect_timeout 300s;
        proxy_send_timeout 300s;
        proxy_read_timeout 300s;
    }
}
EOF

# Start NGINX
sudo systemctl start nginx

# Set up automatic certificate renewal
sudo systemctl enable certbot-renew.timer
sudo systemctl start certbot-renew.timer

# Test renewal
sudo certbot renew --dry-run
```

---

## Monitoring and Logs

### Step 20: Set Up Log Rotation

```bash
# Create logrotate configuration
sudo tee /etc/logrotate.d/whysper > /dev/null <<'EOF'
/opt/whysper/backend/logs/*.log {
    daily
    rotate 14
    compress
    delaycompress
    notifempty
    create 0640 whysper whysper
    sharedscripts
    postrotate
        systemctl reload whysper > /dev/null 2>&1 || true
    endscript
}
EOF
```

### Step 21: View Application Logs

```bash
# View systemd logs
sudo journalctl -u whysper -f

# View NGINX access logs
sudo tail -f /var/log/nginx/whysper_access.log

# View NGINX error logs
sudo tail -f /var/log/nginx/whysper_error.log

# View application logs (if configured)
sudo tail -f /opt/whysper/backend/logs/app.log
```

### Step 22: Set Up Cloud Monitoring

```bash
# Install Cloud Ops Agent
curl -sSO https://dl.google.com/cloudagents/add-google-cloud-ops-agent-repo.sh
sudo bash add-google-cloud-ops-agent-repo.sh --also-install

# Configure logging
sudo tee /etc/google-cloud-ops-agent/config.yaml > /dev/null <<'EOF'
logging:
  receivers:
    whysper_logs:
      type: files
      include_paths:
        - /opt/whysper/backend/logs/*.log
    nginx_access:
      type: files
      include_paths:
        - /var/log/nginx/whysper_access.log
    nginx_error:
      type: files
      include_paths:
        - /var/log/nginx/whysper_error.log
  service:
    pipelines:
      default_pipeline:
        receivers: [whysper_logs, nginx_access, nginx_error]

metrics:
  receivers:
    hostmetrics:
      type: hostmetrics
      collection_interval: 60s
  service:
    pipelines:
      default_pipeline:
        receivers: [hostmetrics]
EOF

# Restart Cloud Ops Agent
sudo systemctl restart google-cloud-ops-agent
```

---

## Maintenance and Updates

### Step 23: Update Application

```bash
# SSH into VM
gcloud compute ssh $VM_NAME --zone=$ZONE

# Navigate to application directory
cd /opt/whysper

# Pull latest code
git pull origin main

# Rebuild frontend
cd frontend
npm install
npm run build
sudo cp -r dist/* /opt/whysper/backend/static/

# Update Python dependencies
cd /opt/whysper
source venv/bin/activate
pip install -r requirements.txt --upgrade

# Restart application
sudo systemctl restart whysper

# Check status
sudo systemctl status whysper
```

### Step 24: Backup Configuration

```bash
# Create backup script
sudo tee /usr/local/bin/backup-whysper.sh > /dev/null <<'EOF'
#!/bin/bash
BACKUP_DIR="/backup/whysper"
DATE=$(date +%Y%m%d_%H%M%S)

mkdir -p $BACKUP_DIR

# Backup application code
tar -czf $BACKUP_DIR/whysper_code_$DATE.tar.gz /opt/whysper

# Backup environment file
cp /opt/whysper/backend/.env $BACKUP_DIR/env_$DATE

# Backup NGINX config
cp /etc/nginx/conf.d/whysper.conf $BACKUP_DIR/nginx_$DATE.conf

# Keep only last 7 backups
find $BACKUP_DIR -type f -mtime +7 -delete

echo "Backup completed: $DATE"
EOF

sudo chmod +x /usr/local/bin/backup-whysper.sh

# Set up cron job for daily backups
echo "0 2 * * * root /usr/local/bin/backup-whysper.sh" | sudo tee -a /etc/crontab
```

---

## Troubleshooting

### Application Won't Start

```bash
# Check service status
sudo systemctl status whysper

# View detailed logs
sudo journalctl -u whysper -n 100 --no-pager

# Check if port is in use
sudo netstat -tlnp | grep 8080

# Test Python directly
cd /opt/whysper/backend
source /opt/whysper/venv/bin/activate
python main.py
```

### D2 Diagrams Not Rendering

```bash
# Verify D2 is installed
which d2
d2 --version

# Test D2 manually
echo "a -> b" > /tmp/test.d2
d2 /tmp/test.d2 /tmp/test.svg
ls -la /tmp/test.svg

# Check D2 path in environment
grep D2_EXECUTABLE /opt/whysper/backend/.env
```

### NGINX Errors

```bash
# Test NGINX configuration
sudo nginx -t

# View NGINX error log
sudo tail -f /var/log/nginx/error.log

# Restart NGINX
sudo systemctl restart nginx
```

---

## Summary

Your Whysper Web2 application is now deployed on a Google Compute Engine VM with:

- ✅ RHEL 8-compatible OS (Rocky Linux/RHEL)
- ✅ Python 3.11 runtime
- ✅ D2 CLI installed and configured
- ✅ Frontend built and served as static files
- ✅ Systemd service for automatic startup
- ✅ NGINX reverse proxy with SSL/HTTPS
- ✅ Cloud Monitoring integration
- ✅ Automated backups

**Access your application:**
```
https://YOUR_VM_IP or https://your-domain.com
```

**Key commands:**
```bash
# Start/Stop/Restart application
sudo systemctl start whysper
sudo systemctl stop whysper
sudo systemctl restart whysper

# View logs
sudo journalctl -u whysper -f

# Update application
cd /opt/whysper && git pull && sudo systemctl restart whysper
```
