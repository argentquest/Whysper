@echo off
echo Killing processes on ports 8000-8010...

for /L %%p in (8000,1,8010) do (
    echo Checking port %%p...
    for /f "tokens=5" %%i in ('netstat -ano ^| findstr ":%%p "') do (
        echo Killing PID %%i on port %%p
        taskkill /PID %%i /F >nul 2>&1
        if errorlevel 1 (
            echo Failed to kill %%i
        ) else (
            echo Killed %%i
        )
    )
)

echo Done!