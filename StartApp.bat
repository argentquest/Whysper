@echo off
setlocal enabledelayedexpansion

REM Get the directory where this batch file is located
set "SCRIPT_DIR=%~dp0"
cd /d "%SCRIPT_DIR%"

echo ============================================================
echo Whysper Web2 - Starting Development Environment
echo ============================================================
echo Working Directory: %CD%
echo.

REM Check if .env file exists
if not exist "backend\.env" (
    echo ERROR: backend\.env file not found!
    echo Please copy .envTemplate to backend\.env and configure your API key.
    echo.
    echo Run: copy .envTemplate backend\.env
    echo Then edit backend\.env and add your OpenRouter API key.
    pause
    exit /b 1
)

echo [1/3] Building Frontend...
echo ============================================================
cd /d "%SCRIPT_DIR%frontend"
call npm install
call npm run build
if errorlevel 1 (
    echo.
    echo ERROR: Frontend build failed!
    pause
    exit /b 1
)
echo.
echo Frontend build complete!
echo.

REM Read API_PORT from backend/.env (default to 8001 if not found)
set "API_PORT=8001"
for /f "tokens=2 delims==" %%a in ('findstr /i "^API_PORT=" "%SCRIPT_DIR%backend\.env" 2^>nul') do (
    set "API_PORT=%%a"
    set "API_PORT=!API_PORT:"=!"
)

echo [2/3] Starting Backend Server...
echo ============================================================
cd /d "%SCRIPT_DIR%backend"
start "Whysper Backend" cmd /k "py main.py"
echo.
echo Backend server starting on http://localhost:%API_PORT%
echo.

echo [3/3] Starting Frontend Dev Server...
echo ============================================================
cd /d "%SCRIPT_DIR%frontend"
start "Whysper Frontend" cmd /k "npm run dev"
echo.
echo Frontend dev server starting on http://localhost:5173+
echo.

cd /d "%SCRIPT_DIR%"

echo ============================================================
echo Whysper Web2 is starting!
echo ============================================================
echo.
echo Backend API:     http://localhost:%API_PORT%/api/v1
echo API Docs:        http://localhost:%API_PORT%/docs
echo Frontend:        http://localhost:5173 (or next available port)
echo.
echo Press Ctrl+C in the server windows to stop the servers.
echo.
echo You can close this window. The servers will continue running.
echo ============================================================

endlocal
