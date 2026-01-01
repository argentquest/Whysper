@echo off
echo Clearing Python cache...

REM Delete all __pycache__ directories
for /d /r backend %%d in (__pycache__) do @if exist "%%d" rd /s /q "%%d"

REM Delete all .pyc files
del /s /q backend\*.pyc 2>nul

echo Cache cleared!
echo.
echo Now manually:
echo 1. Stop the backend server (Ctrl+C)
echo 2. Run: cd backend
echo 3. Run: python -m uvicorn app.main:app --reload
echo.
pause
