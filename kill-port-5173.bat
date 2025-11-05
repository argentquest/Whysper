@echo off
echo Killing processes on port 5173 (Frontend)...

for /f "tokens=5" %%i in ('netstat -ano ^| findstr ":5173 "') do (
    echo Killing PID %%i on port 5173
    taskkill /PID %%i /F >nul 2>&1
    if errorlevel 1 (
        echo Failed to kill %%i
    ) else (
        echo Killed %%i
    )
)

echo Done!
