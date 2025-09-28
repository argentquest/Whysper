@echo off
REM Frontend Deployment Script (Batch)
REM
REM Simple batch script to copy built frontend files to backend static directory.
REM
REM Usage:
REM   deploy.bat - Deploy built files to backend

echo 🚀 Starting frontend deployment...
echo.

set "DIST_DIR=%~dp0dist"
set "BACKEND_STATIC_DIR=%~dp0..\backend\static"

echo 📁 Source: %DIST_DIR%
echo 📁 Destination: %BACKEND_STATIC_DIR%
echo.

REM Check if dist directory exists
if not exist "%DIST_DIR%" (
    echo ❌ Dist directory not found: %DIST_DIR%
    echo 💡 Please run 'npm run build' first.
    echo 💡 Or use 'npm run build:deploy' to build and deploy in one step.
    exit /b 1
)

REM Create backend static directory if it doesn't exist
if not exist "%BACKEND_STATIC_DIR%" (
    mkdir "%BACKEND_STATIC_DIR%"
    echo 📁 Created backend static directory
)

echo 📋 Copying files...
REM Copy all files and folders from dist to backend/static
xcopy "%DIST_DIR%\*" "%BACKEND_STATIC_DIR%\" /E /I /Y >nul

if errorlevel 1 (
    echo ❌ Deployment failed during file copy
    exit /b 1
)

echo ✅ Frontend deployment completed successfully!
echo 🎯 The frontend is now available at the backend server URL
echo 💡 Start the backend server with: cd ..\backend && python main.py
echo.