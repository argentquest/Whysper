# Start-App.ps1

# Get the script's directory to construct absolute paths
$scriptPath = $PSScriptRoot

# Define paths
$backendPath = Join-Path -Path $scriptPath -ChildPath "backend"
$frontendPath = Join-Path -Path $scriptPath -ChildPath "frontend"
$venvPath = Join-Path -Path $scriptPath -ChildPath ".venv"

# --- Start Backend ---
Write-Host "Starting Backend Server..."

# Activate virtual environment
$activateScript = Join-Path -Path $venvPath -ChildPath "Scripts\Activate.ps1"
if (Test-Path $activateScript) {
    . $activateScript
    Write-Host "Virtual environment activated."
} else {
    Write-Error "Virtual environment activation script not found at $activateScript"
    exit 1
}

# Start the backend server in a new window
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd $backendPath; uvicorn app.main:app --host 0.0.0.0 --port 8003 --reload"

# --- Start Frontend ---
Write-Host "Starting Frontend Development Server..."

# Start the frontend server in a new window
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd $frontendPath; npm run dev"

Write-Host "Application servers are starting in new windows."
Write-Host "Backend will be on http://localhost:8003"
Write-Host "Frontend will be on http://localhost:5173 (or another port if 5173 is in use)."
