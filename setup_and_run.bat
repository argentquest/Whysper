@echo off
REM Setup and run the inline comments automation

echo ================================================================================
echo INLINE COMMENTS AUTOMATION - SETUP AND RUN
echo ================================================================================
echo.

REM Check if API key is already set
if not "%ANTHROPIC_API_KEY%"=="" (
    echo API Key is already set!
    goto :run_automation
)

REM Look for .env file
if exist .env (
    echo Found .env file, loading API key...
    for /f "usebackq tokens=1,* delims==" %%a in (.env) do (
        if "%%a"=="ANTHROPIC_API_KEY" set ANTHROPIC_API_KEY=%%b
    )
)

REM Check again
if not "%ANTHROPIC_API_KEY%"=="" (
    echo API Key loaded successfully!
    goto :run_automation
)

REM Prompt user for API key
echo.
echo API Key not found in environment or .env file.
echo.
echo Please enter your Anthropic API key:
echo (You can get one from: https://console.anthropic.com/)
echo.
set /p ANTHROPIC_API_KEY="API Key: "

if "%ANTHROPIC_API_KEY%"=="" (
    echo.
    echo ERROR: API key is required to run this automation.
    echo Please set ANTHROPIC_API_KEY environment variable or create a .env file.
    exit /b 1
)

:run_automation
echo.
echo ================================================================================
echo Starting automation...
echo ================================================================================
echo.

call run_all_inline_comments.bat

echo.
echo ================================================================================
echo Done!
echo ================================================================================
