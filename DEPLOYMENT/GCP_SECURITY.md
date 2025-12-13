# Google Cloud Platform Security Guide
## Security Best Practices for Whysper Web2 Deployment

---

## Table of Contents
1. [Security Architecture](#security-architecture)
2. [Secret Management](#secret-management)
3. [Network Security](#network-security)
4. [Container Security](#container-security)
5. [IAM and Access Control](#iam-and-access-control)
6. [Compliance and Auditing](#compliance-and-auditing)
7. [Incident Response](#incident-response)

---

## Security Architecture

### Defense in Depth Strategy

```
┌─────────────────────────────────────────────────┐
│ Layer 1: Network Security                      │
│  • Cloud Armor (DDoS protection)                │
│  • Cloud Load Balancer (SSL/TLS termination)   │
│  • Ingress controls                             │
└─────────────────────────────────────────────────┘
                    ▼
┌─────────────────────────────────────────────────┐
│ Layer 2: Application Security                  │
│  • Cloud Run service isolation                  │
│  • Request authentication                       │
│  • Input validation                             │
└─────────────────────────────────────────────────┘
                    ▼
┌─────────────────────────────────────────────────┐
│ Layer 3: Identity & Access Management          │
│  • Service accounts with least privilege       │
│  • Workload Identity                            │
│  • IAM policies                                 │
└─────────────────────────────────────────────────┘
                    ▼
┌─────────────────────────────────────────────────┐
│ Layer 4: Data Security                         │
│  • Secret Manager (encrypted secrets)          │
│  • Encryption at rest                           │
│  • Encryption in transit (TLS 1.3)             │
└─────────────────────────────────────────────────┘
                    ▼
┌─────────────────────────────────────────────────┐
│ Layer 5: Container Security                    │
│  • Non-root user execution                      │
│  • Minimal base image (RHEL UBI 8)              │
│  • Vulnerability scanning                       │
└─────────────────────────────────────────────────┘
```

---

## Secret Management

### 1. Store All Secrets in Secret Manager

```bash
# ✅ CORRECT: Store API keys in Secret Manager
echo -n "sk-or-v1-xxxxx" | \
gcloud secrets create WHYSPER_API_KEY \
    --data-file=- \
    --replication-policy="automatic"

# ❌ WRONG: Don't use environment variables directly
# gcloud run deploy --set-env-vars="API_KEY=sk-or-v1-xxxxx"  # DON'T DO THIS
```

### 2. Implement Secret Rotation

```bash
# Create new version of secret
echo -n "new-api-key" | \
gcloud secrets versions add WHYSPER_API_KEY \
    --data-file=-

# Cloud Run automatically picks up new version within minutes
# No redeployment needed!

# Disable old version (after testing)
gcloud secrets versions disable 1 --secret=WHYSPER_API_KEY
```

### 3. Use Secret Version Pinning (Production)

```bash
# Pin to specific version for stability
gcloud run services update whysper-app \
    --region=us-central1 \
    --set-secrets="API_KEY=WHYSPER_API_KEY:2"  # Pin to version 2

# Use "latest" for auto-updates (dev/staging)
gcloud run services update whysper-app \
    --region=us-central1 \
    --set-secrets="API_KEY=WHYSPER_API_KEY:latest"
```

### 4. Audit Secret Access

```bash
# View who accessed secrets
gcloud logging read "protoPayload.serviceName=secretmanager.googleapis.com" \
    --limit=50 \
    --format=json

# Set up alerts for secret access
gcloud alpha monitoring policies create \
    --notification-channels=CHANNEL_ID \
    --display-name="Secret Access Alert" \
    --condition-display-name="Unusual secret access"
```

---

## Network Security

### 1. Configure Cloud Run Ingress Controls

```bash
# ✅ Public access (default)
gcloud run services update whysper-app \
    --region=us-central1 \
    --ingress=all

# ✅ Internal only (for internal services)
gcloud run services update whysper-app \
    --region=us-central1 \
    --ingress=internal

# ✅ Internal + Load Balancer (recommended for production)
gcloud run services update whysper-app \
    --region=us-central1 \
    --ingress=internal-and-cloud-load-balancing
```

### 2. Enable Cloud Armor (DDoS Protection)

```bash
# Create security policy
gcloud compute security-policies create whysper-security-policy \
    --description="Whysper DDoS protection"

# Add rate limiting rule
gcloud compute security-policies rules create 1000 \
    --security-policy=whysper-security-policy \
    --expression="true" \
    --action=rate-based-ban \
    --rate-limit-threshold-count=100 \
    --rate-limit-threshold-interval-sec=60 \
    --ban-duration-sec=600

# Add IP allowlist (optional)
gcloud compute security-policies rules create 2000 \
    --security-policy=whysper-security-policy \
    --expression="origin.ip == '1.2.3.4/32'" \
    --action=allow

# Attach to backend service (for Load Balancer setup)
gcloud compute backend-services update whysper-backend \
    --security-policy=whysper-security-policy \
    --global
```

### 3. Enforce HTTPS Only

```bash
# Cloud Run enforces HTTPS by default
# For custom domains, redirect HTTP to HTTPS at load balancer

# Create URL map with HTTP to HTTPS redirect
gcloud compute url-maps import whysper-lb \
    --source=<(cat <<EOF
name: whysper-lb
defaultService: https://www.googleapis.com/compute/v1/projects/$PROJECT_ID/global/backendServices/whysper-backend
hostRules:
- hosts:
  - whysper.example.com
  pathMatcher: path-matcher-1
pathMatchers:
- name: path-matcher-1
  defaultService: https://www.googleapis.com/compute/v1/projects/$PROJECT_ID/global/backendServices/whysper-backend
defaultUrlRedirect:
  httpsRedirect: true
  redirectResponseCode: MOVED_PERMANENTLY_DEFAULT
EOF
)
```

### 4. Implement VPC Service Controls (Enterprise)

```bash
# Create service perimeter
gcloud access-context-manager perimeters create whysper_perimeter \
    --title="Whysper Security Perimeter" \
    --resources=projects/PROJECT_NUMBER \
    --restricted-services=secretmanager.googleapis.com,storage.googleapis.com \
    --policy=POLICY_ID
```

---

## Container Security

### 1. Run as Non-Root User

Dockerfile already implements this:

```dockerfile
# Create non-root user
RUN useradd -m -u 1001 -s /bin/bash whysper && \
    chown -R whysper:whysper /app

# Switch to non-root user
USER whysper
```

### 2. Scan Images for Vulnerabilities

```bash
# Automatic scanning in Artifact Registry
gcloud services enable containerscanning.googleapis.com

# Enable vulnerability scanning
gcloud artifacts repositories update whysper-repo \
    --location=us-central1 \
    --enable-vulnerability-scanning

# View vulnerabilities
gcloud artifacts docker images list \
    us-central1-docker.pkg.dev/$PROJECT_ID/whysper-repo/whysper-web2 \
    --show-occurrences

# Get detailed vulnerability report
gcloud artifacts docker images describe \
    us-central1-docker.pkg.dev/$PROJECT_ID/whysper-repo/whysper-web2:latest \
    --show-all-metadata
```

### 3. Use Binary Authorization (Enterprise)

```bash
# Enable Binary Authorization
gcloud services enable binaryauthorization.googleapis.com

# Create policy requiring attestations
gcloud container binauthz policy import \
    --source=<(cat <<EOF
globalPolicyEvaluationMode: ENABLE
defaultAdmissionRule:
  requireAttestationsBy:
  - projects/$PROJECT_ID/attestors/whysper-attestor
  evaluationMode: REQUIRE_ATTESTATION
  enforcementMode: ENFORCED_BLOCK_AND_AUDIT_LOG
EOF
)

# Configure Cloud Run to use Binary Authorization
gcloud run services update whysper-app \
    --region=us-central1 \
    --binary-authorization=default
```

### 4. Implement Image Signing

```bash
# Create attestor
gcloud container binauthz attestors create whysper-attestor \
    --attestation-authority-note=whysper-note \
    --attestation-authority-note-project=$PROJECT_ID

# Sign image after successful build
gcloud beta container binauthz attestations sign-and-create \
    --artifact-url=us-central1-docker.pkg.dev/$PROJECT_ID/whysper-repo/whysper-web2@sha256:IMAGE_DIGEST \
    --attestor=whysper-attestor \
    --attestor-project=$PROJECT_ID \
    --keyversion=projects/$PROJECT_ID/locations/global/keyRings/KEYRING/cryptoKeys/KEY/cryptoKeyVersions/1
```

---

## IAM and Access Control

### 1. Create Service Account with Least Privilege

```bash
# Create service account
gcloud iam service-accounts create whysper-cloudrun-sa \
    --display-name="Whysper Cloud Run Service Account"

# Grant ONLY required permissions
gcloud projects add-iam-policy-binding $PROJECT_ID \
    --member="serviceAccount:whysper-cloudrun-sa@${PROJECT_ID}.iam.gserviceaccount.com" \
    --role="roles/secretmanager.secretAccessor"

# ❌ DON'T grant broad roles like "Editor" or "Owner"
# ❌ gcloud projects add-iam-policy-binding $PROJECT_ID \
#      --member="serviceAccount:whysper-cloudrun-sa@${PROJECT_ID}.iam.gserviceaccount.com" \
#      --role="roles/editor"  # TOO BROAD!
```

### 2. Implement Service Account Impersonation

```bash
# Allow developers to impersonate service account (for testing)
gcloud iam service-accounts add-iam-policy-binding \
    whysper-cloudrun-sa@${PROJECT_ID}.iam.gserviceaccount.com \
    --member="user:developer@example.com" \
    --role="roles/iam.serviceAccountTokenCreator"

# Test as service account
gcloud run services describe whysper-app \
    --region=us-central1 \
    --impersonate-service-account=whysper-cloudrun-sa@${PROJECT_ID}.iam.gserviceaccount.com
```

### 3. Enable Workload Identity (for GKE)

```bash
# For GKE deployments (not Cloud Run)
gcloud iam service-accounts add-iam-policy-binding \
    whysper-cloudrun-sa@${PROJECT_ID}.iam.gserviceaccount.com \
    --role=roles/iam.workloadIdentityUser \
    --member="serviceAccount:${PROJECT_ID}.svc.id.goog[NAMESPACE/KSA_NAME]"
```

### 4. Audit IAM Permissions

```bash
# List all IAM bindings
gcloud projects get-iam-policy $PROJECT_ID \
    --flatten="bindings[].members" \
    --format="table(bindings.role,bindings.members)"

# Check service account permissions
gcloud projects get-iam-policy $PROJECT_ID \
    --flatten="bindings[].members" \
    --filter="bindings.members:serviceAccount:whysper-cloudrun-sa@${PROJECT_ID}.iam.gserviceaccount.com"
```

---

## Compliance and Auditing

### 1. Enable Cloud Audit Logs

```bash
# Enable data access logs
gcloud projects get-iam-policy $PROJECT_ID \
    --format=json > policy.json

# Add audit config
cat <<EOF >> policy.json
{
  "auditConfigs": [
    {
      "service": "allServices",
      "auditLogConfigs": [
        { "logType": "ADMIN_READ" },
        { "logType": "DATA_READ" },
        { "logType": "DATA_WRITE" }
      ]
    }
  ]
}
EOF

gcloud projects set-iam-policy $PROJECT_ID policy.json
```

### 2. Set Up Log Exports

```bash
# Export logs to BigQuery for long-term retention
gcloud logging sinks create whysper-audit-sink \
    bigquery.googleapis.com/projects/$PROJECT_ID/datasets/audit_logs \
    --log-filter='resource.type="cloud_run_revision" AND resource.labels.service_name="whysper-app"'

# Export to Cloud Storage for archival
gcloud logging sinks create whysper-archive-sink \
    storage.googleapis.com/whysper-audit-logs \
    --log-filter='resource.type="cloud_run_revision" AND severity>=WARNING'
```

### 3. Create Security Dashboard

```bash
# Create custom monitoring dashboard
gcloud monitoring dashboards create --config-from-file=<(cat <<EOF
{
  "displayName": "Whysper Security Dashboard",
  "mosaicLayout": {
    "columns": 12,
    "tiles": [
      {
        "width": 6,
        "height": 4,
        "widget": {
          "title": "Failed Authentication Attempts",
          "xyChart": {
            "dataSets": [{
              "timeSeriesQuery": {
                "timeSeriesFilter": {
                  "filter": "resource.type=\"cloud_run_revision\" severity=\"ERROR\"",
                  "aggregation": {
                    "perSeriesAligner": "ALIGN_RATE",
                    "crossSeriesReducer": "REDUCE_SUM"
                  }
                }
              }
            }]
          }
        }
      }
    ]
  }
}
EOF
)
```

### 4. Implement Compliance Checks

```bash
# Check for compliance violations
gcloud asset search-all-resources \
    --scope=projects/$PROJECT_ID \
    --asset-types=run.googleapis.com/Service \
    --query="state:ACTIVE"

# Check for publicly accessible services
gcloud run services list \
    --platform=managed \
    --format="table(SERVICE_NAME,REGION,URL,INGRESS)"
```

---

## Incident Response

### 1. Create Incident Response Plan

```yaml
# incident_response.yaml
phases:
  detection:
    - Monitor Cloud Logging for anomalies
    - Set up alerting for suspicious activity
    - Use Security Command Center

  containment:
    - Disable compromised service account
    - Rotate all secrets immediately
    - Isolate affected Cloud Run service

  eradication:
    - Patch vulnerabilities
    - Rebuild container image
    - Deploy clean version

  recovery:
    - Gradually restore service
    - Monitor for reinfection
    - Verify all access logs

  lessons_learned:
    - Document incident
    - Update security policies
    - Train team
```

### 2. Emergency Commands

```bash
# EMERGENCY: Disable service immediately
gcloud run services update whysper-app \
    --region=us-central1 \
    --no-allow-unauthenticated \
    --max-instances=0

# EMERGENCY: Rotate API key
echo -n "new-emergency-key" | \
gcloud secrets versions add WHYSPER_API_KEY --data-file=-

# EMERGENCY: Disable service account
gcloud iam service-accounts disable \
    whysper-cloudrun-sa@${PROJECT_ID}.iam.gserviceaccount.com

# EMERGENCY: Review recent access
gcloud logging read "resource.type=cloud_run_revision \
    AND resource.labels.service_name=whysper-app \
    AND timestamp>=\"$(date -u -d '1 hour ago' '+%Y-%m-%dT%H:%M:%SZ')\"" \
    --limit=1000 \
    --format=json > incident_logs.json
```

### 3. Post-Incident Checklist

- [ ] Rotate all secrets
- [ ] Rebuild and redeploy application
- [ ] Review and update IAM policies
- [ ] Scan container image for vulnerabilities
- [ ] Check for unauthorized changes
- [ ] Update security policies
- [ ] Document incident in runbook
- [ ] Conduct post-mortem meeting

---

## Security Checklist

### Pre-Deployment

- [ ] All secrets stored in Secret Manager
- [ ] Service account uses least privilege
- [ ] Container runs as non-root user
- [ ] Image scanned for vulnerabilities
- [ ] HTTPS enforced
- [ ] Audit logging enabled
- [ ] Monitoring alerts configured

### Post-Deployment

- [ ] Verify secrets are not in logs
- [ ] Test authentication/authorization
- [ ] Review IAM policies
- [ ] Enable Cloud Armor (if using LB)
- [ ] Set up log exports
- [ ] Configure backup/DR plan
- [ ] Document security controls

### Ongoing

- [ ] Monthly secret rotation
- [ ] Quarterly security reviews
- [ ] Weekly vulnerability scans
- [ ] Daily log monitoring
- [ ] Incident response drills (quarterly)

---

## Resources

- [Google Cloud Security Best Practices](https://cloud.google.com/security/best-practices)
- [Cloud Run Security Guide](https://cloud.google.com/run/docs/securing/overview)
- [Secret Manager Documentation](https://cloud.google.com/secret-manager/docs)
- [Binary Authorization](https://cloud.google.com/binary-authorization/docs)
- [RHEL UBI Security](https://access.redhat.com/articles/4238681)
