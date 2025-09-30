# Whysper Frontend Build & Deploy Script
#
# This script builds the frontend and deploys it to the backend static directory.
# Run this from the project root directory.
#
# Usage:
#   .\deploy-frontend.ps1           - Build and deploy frontend
#   .\deploy-frontend.ps1 -BuildOnly - Only build, don't deploy
#   .\deploy-frontend.ps1 -DeployOnly - Only deploy (assumes already built)

param(
    [switch]$BuildOnly,
    [switch]$DeployOnly
)

$ErrorActionPreference = "Stop"

Write-Host "🧠 Whysper Frontend Build & Deploy" -ForegroundColor Magenta
Write-Host "=" * 50 -ForegroundColor Gray
Write-Host ""

# Define paths
$ProjectRoot = $PSScriptRoot
$FrontendDir = Join-Path $ProjectRoot "frontend"
$BackendStaticDir = Join-Path $ProjectRoot "backend" "static"
$DistDir = Join-Path $FrontendDir "dist"

# Verify we're in the right directory
if (-not (Test-Path $FrontendDir)) {
    Write-Host "❌ Frontend directory not found. Please run this script from the project root." -ForegroundColor Red
    exit 1
}

if (-not $DeployOnly) {
    Write-Host "🔨 Building frontend..." -ForegroundColor Yellow
    Write-Host "📁 Frontend directory: $FrontendDir" -ForegroundColor Cyan
    Write-Host ""
    
    # Change to frontend directory and build
    Push-Location $FrontendDir
    try {
        # Run npm build
        npm run build
        if ($LASTEXITCODE -ne 0) {
            throw "npm build failed"
        }
        Write-Host ""
        Write-Host "✅ Frontend build completed successfully!" -ForegroundColor Green
    } catch {
        Write-Host "❌ Frontend build failed: $($_.Exception.Message)" -ForegroundColor Red
        Pop-Location
        exit 1
    } finally {
        Pop-Location
    }
}

if (-not $BuildOnly) {
    Write-Host "🚀 Deploying frontend to backend..." -ForegroundColor Yellow
    Write-Host "📁 Source: $DistDir" -ForegroundColor Cyan
    Write-Host "📁 Destination: $BackendStaticDir" -ForegroundColor Cyan
    Write-Host ""
    
    # Check if dist directory exists
    if (-not (Test-Path $DistDir)) {
        Write-Host "❌ Dist directory not found: $DistDir" -ForegroundColor Red
        Write-Host "💡 Please run with build enabled or run 'npm run build' in frontend directory." -ForegroundColor Yellow
        exit 1
    }
    
    try {
        # Create backend static directory if it doesn't exist
        if (-not (Test-Path $BackendStaticDir)) {
            New-Item -ItemType Directory -Path $BackendStaticDir -Force | Out-Null
            Write-Host "📁 Created backend static directory" -ForegroundColor Yellow
        }
        
        # Remove old files first
        if (Test-Path $BackendStaticDir) {
            Remove-Item "$BackendStaticDir\*" -Recurse -Force
            Write-Host "🗑️  Cleared old static files" -ForegroundColor Yellow
        }
        
        # Copy all files and folders from dist to backend/static
        Copy-Item -Path "$DistDir\*" -Destination $BackendStaticDir -Recurse -Force
        
        # Count copied files
        $CopiedFiles = Get-ChildItem -Path $BackendStaticDir -Recurse -File
        Write-Host "✅ Deployed $($CopiedFiles.Count) files successfully!" -ForegroundColor Green
        
    } catch {
        Write-Host "❌ Deployment failed: $($_.Exception.Message)" -ForegroundColor Red
        exit 1
    }
}

Write-Host ""
Write-Host "Process completed successfully!" -ForegroundColor Green
Write-Host "The frontend is now integrated with the backend" -ForegroundColor Cyan
Write-Host "Start the server with: cd backend then python main.py" -ForegroundColor Yellow
Write-Host "Then visit: http://localhost:8001" -ForegroundColor Cyan