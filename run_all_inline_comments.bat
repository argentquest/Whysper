@echo off
REM Master script to add inline comments to ALL 321 files in the codebase
REM Processes 249 Python files + 72 TypeScript/TSX files

echo ================================================================================
echo COMPREHENSIVE INLINE COMMENTS AUTOMATION
echo ================================================================================
echo.
echo This script will process:
echo   - 249 Python files in backend/
echo   - 72 TypeScript/TSX files in frontend/src/
echo.
echo Total: 321 files
echo.
echo ================================================================================
echo.

REM Check for ANTHROPIC_API_KEY
if "%ANTHROPIC_API_KEY%"=="" (
    echo ERROR: ANTHROPIC_API_KEY environment variable is not set
    echo Please set it using: set ANTHROPIC_API_KEY=your-api-key-here
    exit /b 1
)

echo [1/2] Processing Backend Python Files...
echo ================================================================================
.venv\Scripts\python.exe process_all_backend.py
if errorlevel 1 (
    echo.
    echo WARNING: Backend processing had some errors. Check backend_comments_processing.log
    echo Continuing with frontend processing...
    echo.
) else (
    echo.
    echo Backend processing completed successfully!
    echo.
)

echo.
echo [2/2] Processing Frontend TypeScript/TSX Files...
echo ================================================================================
node process_all_frontend.js
if errorlevel 1 (
    echo.
    echo WARNING: Frontend processing had some errors. Check frontend_comments_processing.log
    echo.
) else (
    echo.
    echo Frontend processing completed successfully!
    echo.
)

echo.
echo ================================================================================
echo ALL PROCESSING COMPLETE
echo ================================================================================
echo.
echo Check the following files for details:
echo   - backend_comments_manifest.json (Backend progress)
echo   - frontend_comments_manifest.json (Frontend progress)
echo   - backend_comments_processing.log (Backend log)
echo   - frontend_comments_processing.log (Frontend log)
echo.
echo ================================================================================
