@echo off
REM Whysper Frontend Build & Deploy Script
REM
REM This script builds the frontend and deploys it to the backend static directory.
REM Run this from the project root directory.

echo 🧠 Whysper Frontend Build ^& Deploy
echo ==================================================
echo.

REM Define paths
set "PROJECT_ROOT=%~dp0"
set "FRONTEND_DIR=%PROJECT_ROOT%frontend"
set "BACKEND_STATIC_DIR=%PROJECT_ROOT%backend\static"
set "DIST_DIR=%FRONTEND_DIR%\dist"

REM Verify we're in the right directory
if not exist "%FRONTEND_DIR%" (
    echo ❌ Frontend directory not found. Please run this script from the project root.
    exit /b 1
)

echo 🔨 Building frontend...
echo 📁 Frontend directory: %FRONTEND_DIR%
echo.

REM Change to frontend directory and build
cd /d "%FRONTEND_DIR%"
call npm run build
if errorlevel 1 (
    echo ❌ Frontend build failed
    exit /b 1
)

echo.
echo ✅ Frontend build completed successfully!

echo 🚀 Deploying frontend to backend...
echo 📁 Source: %DIST_DIR%
echo 📁 Destination: %BACKEND_STATIC_DIR%
echo.

REM Check if dist directory exists
if not exist "%DIST_DIR%" (
    echo ❌ Dist directory not found: %DIST_DIR%
    echo 💡 Build may have failed. Check the output above.
    exit /b 1
)

REM Create backend static directory if it doesn't exist
if not exist "%BACKEND_STATIC_DIR%" (
    mkdir "%BACKEND_STATIC_DIR%"
    echo 📁 Created backend static directory
)

REM Remove old files first
if exist "%BACKEND_STATIC_DIR%\*" (
    del /q "%BACKEND_STATIC_DIR%\*" >nul 2>&1
    for /d %%d in ("%BACKEND_STATIC_DIR%\*") do rmdir /s /q "%%d" >nul 2>&1
    echo 🗑️  Cleared old static files
)

REM Copy all files and folders from dist to backend/static
xcopy "%DIST_DIR%\*" "%BACKEND_STATIC_DIR%\" /E /I /Y >nul

if errorlevel 1 (
    echo ❌ Deployment failed during file copy
    exit /b 1
)

echo ✅ Frontend deployment completed successfully!
echo.
echo 🎉 Process completed successfully!
echo 🎯 The frontend is now integrated with the backend
echo 💡 Start the server with: cd backend ^&^& python main.py
echo 🌐 Then visit: http://localhost:8001

REM Return to project root
cd /d "%PROJECT_ROOT%"