@echo off
echo Killing processes on port 8003 (Backend)...

for /f "tokens=5" %%i in ('netstat -ano ^| findstr ":8003 "') do (
    echo Killing PID %%i on port 8003
    taskkill /PID %%i /F >nul 2>&1
    if errorlevel 1 (
        echo Failed to kill %%i
    ) else (
        echo Killed %%i
    )
)

echo Done!
