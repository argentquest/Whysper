param(
    [string]$CertPath,
    [string]$KeyPath
)

$ErrorActionPreference = "Stop"

$repoRoot = (Resolve-Path (Join-Path $PSScriptRoot "..")).Path
$backendDir = Join-Path $repoRoot "backend"
$defaultCertDir = Join-Path $backendDir "certs"

if (-not $CertPath) {
    $CertPath = Join-Path $defaultCertDir "selfsigned.crt"
}
if (-not $KeyPath) {
    $KeyPath = Join-Path $defaultCertDir "selfsigned.key"
}

if (-not (Test-Path $backendDir)) {
    throw "Backend directory not found at $backendDir"
}

New-Item -ItemType Directory -Force -Path (Split-Path $CertPath) | Out-Null
New-Item -ItemType Directory -Force -Path (Split-Path $KeyPath) | Out-Null

Write-Host "Generating self-signed certificate..."
Write-Host "  Cert: $CertPath"
Write-Host "  Key : $KeyPath"

$env:PYTHONPATH = $backendDir
$env:SSL_CERTFILE = $CertPath
$env:SSL_KEYFILE = $KeyPath

$python = Get-Command py -ErrorAction SilentlyContinue
if (-not $python) {
    $python = Get-Command python -ErrorAction SilentlyContinue
}
if (-not $python) {
    throw "Python is required (py or python not found on PATH)."
}

$code = @"
import os
from pathlib import Path

try:
    from app.utils.ssl_utils import _generate_self_signed_certificate
except ImportError as exc:
    raise RuntimeError("Install backend dependencies first: pip install -r requirements.txt") from exc

cert = Path(os.environ["SSL_CERTFILE"]).resolve()
key = Path(os.environ["SSL_KEYFILE"]).resolve()
_generate_self_signed_certificate(cert, key, ["localhost", "127.0.0.1"])
print(f"Generated cert: {cert}")
print(f"Generated key : {key}")
"@

$args = @()
if ($python.Name -eq "py") {
    $args = @("-3", "-c", $code)
} else {
    $args = @("-c", $code)
}

& $python.Path @args

Write-Host ""
Write-Host "Done. To enable HTTPS, add to backend/.env (or set env vars):"
Write-Host "  SSL_ENABLED=true"
Write-Host "  SSL_SELF_SIGNED=true"
Write-Host "  SSL_CERTFILE=$CertPath"
Write-Host "  SSL_KEYFILE=$KeyPath"
