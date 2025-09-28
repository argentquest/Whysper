# Frontend Deployment Script (PowerShell)
#
# This PowerShell script copies built frontend files to the backend static directory.
# It's an alternative to the Node.js deploy script for Windows environments.
#
# Usage:
#   .\deploy.ps1              - Deploy built files to backend
#   npm run build; .\deploy.ps1 - Build then deploy

Write-Host "🚀 Starting frontend deployment..." -ForegroundColor Green
Write-Host ""

# Define paths
$DistDir = Join-Path $PSScriptRoot "dist"
$BackendStaticDir = Join-Path $PSScriptRoot ".." "backend" "static"

Write-Host "📁 Source: $DistDir" -ForegroundColor Cyan
Write-Host "📁 Destination: $BackendStaticDir" -ForegroundColor Cyan
Write-Host ""

# Check if dist directory exists
if (-not (Test-Path $DistDir)) {
    Write-Host "❌ Dist directory not found: $DistDir" -ForegroundColor Red
    Write-Host "💡 Please run 'npm run build' first." -ForegroundColor Yellow
    Write-Host "💡 Or use 'npm run build:deploy' to build and deploy in one step." -ForegroundColor Yellow
    exit 1
}

try {
    # Create backend static directory if it doesn't exist
    if (-not (Test-Path $BackendStaticDir)) {
        New-Item -ItemType Directory -Path $BackendStaticDir -Force | Out-Null
        Write-Host "📁 Created backend static directory" -ForegroundColor Yellow
    }
    
    # Copy all files and folders from dist to backend/static
    Write-Host "📋 Copying files..." -ForegroundColor Yellow
    Copy-Item -Path "$DistDir\*" -Destination $BackendStaticDir -Recurse -Force
    
    # List copied files for confirmation
    $CopiedFiles = Get-ChildItem -Path $BackendStaticDir -Recurse -File
    foreach ($File in $CopiedFiles) {
        $RelativePath = $File.FullName.Replace($BackendStaticDir + "\", "")
        Write-Host "✓ Copied: $RelativePath" -ForegroundColor Green
    }
    
    Write-Host ""
    Write-Host "✅ Frontend deployment completed successfully!" -ForegroundColor Green
    Write-Host "🎯 The frontend is now available at the backend server URL" -ForegroundColor Cyan
    Write-Host "💡 Start the backend server with: cd ..\backend && python main.py" -ForegroundColor Yellow
    
} catch {
    Write-Host "❌ Deployment failed: $($_.Exception.Message)" -ForegroundColor Red
    exit 1
}