param(
    [switch]$UseHttps # Force HTTPS for VITE_API_URL even if backend SSL is disabled
)

$ErrorActionPreference = "Stop"

function Get-EnvValue {
    param($Path, $Key, $Default)
    if (-not (Test-Path $Path)) { return $Default }
    $line = Get-Content $Path | Where-Object { $_ -match "^$Key\s*=" } | Select-Object -First 1
    if (-not $line) { return $Default }
    return ($line -split "=", 2)[1].Trim("`"", "'")
}

function Set-Or-Replace-Line {
    param($Path, $Key, $Value)
    $lines = @()
    if (Test-Path $Path) { $lines = Get-Content $Path }
    $filtered = $lines | Where-Object { $_ -notmatch "^$Key\s*=" }
    $filtered += "$Key=$Value"
    Set-Content -Path $Path -Value $filtered
}

function Stop-Port {
    param([int]$Port)
    $pids = Get-NetTCPConnection -LocalPort $Port -ErrorAction SilentlyContinue | Select-Object -ExpandProperty OwningProcess -Unique
    foreach ($processId in $pids) {
        if ($processId -eq 0) { continue }
        $proc = Get-Process -Id $processId -ErrorAction SilentlyContinue
        if ($proc) {
            Write-Host "Stopping process $($proc.ProcessName) (PID $processId) on port $Port"
            Stop-Process -Id $processId -Force
        }
    }
}

$repoRoot = (Resolve-Path (Join-Path $PSScriptRoot "..")).Path
$frontendDir = Join-Path $repoRoot "frontend"
$backendDir = Join-Path $repoRoot "backend"
$backendEnv = Join-Path $backendDir ".env"
$frontendEnv = Join-Path $frontendDir ".env"
$staticDir = Join-Path $backendDir "static"

$apiPort = [int](Get-EnvValue $backendEnv "API_PORT" 8003)
$sslEnabled = Get-EnvValue $backendEnv "SSL_ENABLED" "false"
$protocol = if ($UseHttps -or ($sslEnabled.ToLower() -eq "true")) { "https" } else { "http" }

$viteApiUrl = ("{0}://localhost:{1}/api/v1" -f $protocol, $apiPort)
Write-Host "Setting VITE_API_URL to $viteApiUrl"
Set-Or-Replace-Line -Path $frontendEnv -Key "VITE_API_URL" -Value $viteApiUrl
Set-Or-Replace-Line -Path $frontendEnv -Key "VITE_BACKEND_PORT" -Value $apiPort
if ($protocol -eq "https") {
    Set-Or-Replace-Line -Path $frontendEnv -Key "VITE_BACKEND_PROTOCOL" -Value "https"
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

Write-Host "Copying dist -> backend/static ..."
if (Test-Path $staticDir) { Remove-Item -Recurse -Force $staticDir }
New-Item -ItemType Directory -Path $staticDir | Out-Null
Copy-Item -Path (Join-Path $frontendDir "dist\\*") -Destination $staticDir -Recurse -Force

Write-Host "Ensuring port $apiPort is free..."
Stop-Port -Port $apiPort

Write-Host ("Starting backend on {0}://0.0.0.0:{1} ..." -f $protocol, $apiPort)
Push-Location $backendDir
py main.py
Pop-Location
