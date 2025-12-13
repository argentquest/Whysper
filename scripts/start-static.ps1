$ErrorActionPreference = "Stop"

$repoRoot = (Resolve-Path (Join-Path $PSScriptRoot "..")).Path
$frontendDir = Join-Path $repoRoot "frontend"
$backendDir = Join-Path $repoRoot "backend"
$staticDir = Join-Path $backendDir "static"
$venvActivate = Join-Path $repoRoot ".venv\Scripts\Activate.ps1"
$backendPort = 8003

function Stop-Port {
    param([int]$Port)
    $pids = Get-NetTCPConnection -LocalPort $Port -ErrorAction SilentlyContinue | Select-Object -ExpandProperty OwningProcess -Unique
    foreach ($pid in $pids) {
        $proc = Get-Process -Id $pid -ErrorAction SilentlyContinue
        if ($proc) {
            Write-Host "Stopping process $($proc.ProcessName) (PID $pid) on port $Port"
            Stop-Process -Id $pid -Force
        }
    }
}

Write-Host "Starting monolith on http://localhost:8003 (serving /static)"

if (-not (Test-Path $frontendDir)) {
    Write-Error "Frontend directory not found at $frontendDir"
    exit 1
}

if (-not (Test-Path $backendDir)) {
    Write-Error "Backend directory not found at $backendDir"
    exit 1
}

if (-not (Test-Path (Join-Path $frontendDir "node_modules"))) {
    Write-Host "Installing frontend dependencies..."
    Push-Location $frontendDir
    npm install
    Pop-Location
}

Write-Host "Building frontend bundle..."
Push-Location $frontendDir
npm run build
Pop-Location

if (Test-Path $staticDir) {
    Remove-Item -Path $staticDir -Recurse -Force
}
New-Item -ItemType Directory -Path $staticDir | Out-Null
Copy-Item -Path (Join-Path $frontendDir "dist\*") -Destination $staticDir -Recurse -Force

if (Test-Path $venvActivate) {
    . $venvActivate
    Write-Host "Activated virtual environment."
}

Write-Host "Ensuring port $backendPort is free..."
Stop-Port -Port $backendPort

Push-Location $backendDir
Write-Host "Launching backend with static assets..."
python main.py
Pop-Location
