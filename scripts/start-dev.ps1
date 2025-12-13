$ErrorActionPreference = "Stop"

$repoRoot = (Resolve-Path (Join-Path $PSScriptRoot "..")).Path
$frontendDir = Join-Path $repoRoot "frontend"
$backendDir = Join-Path $repoRoot "backend"
$venvActivate = Join-Path $repoRoot ".venv\Scripts\Activate.ps1"
$backendPort = 8003
$frontendPort = 5173

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

if (-not (Test-Path $frontendDir)) {
    Write-Error "Frontend directory not found at $frontendDir"
    exit 1
}

if (-not (Test-Path $backendDir)) {
    Write-Error "Backend directory not found at $backendDir"
    exit 1
}

if (Test-Path $venvActivate) {
    . $venvActivate
    Write-Host "Activated virtual environment for backend."
}

if (-not (Test-Path (Join-Path $frontendDir "node_modules"))) {
    Write-Host "Installing frontend dependencies..."
    Push-Location $frontendDir
    npm install
    Pop-Location
}

Write-Host "Starting backend on http://localhost:8003 ..."
$null = Stop-Port -Port $backendPort
$backendCmd = "cd `"$backendDir`"; python main.py"
Start-Process powershell -ArgumentList "-NoExit", "-Command", $backendCmd

Write-Host "Starting frontend dev server on http://localhost:5173 ..."
$null = Stop-Port -Port $frontendPort
$frontendCmd = "cd `"$frontendDir`"; npm run dev"
Start-Process powershell -ArgumentList "-NoExit", "-Command", $frontendCmd

Write-Host "Backend and frontend launched in separate windows."
