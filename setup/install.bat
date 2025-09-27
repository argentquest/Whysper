@echo off
echo ================================
echo WhisperCode Web2 Setup Script
echo ================================
echo.

cd /d "%~dp0.."

echo 📦 Setting up Python virtual environment...
python -m venv venv
if errorlevel 1 (
    echo ❌ Failed to create virtual environment. Make sure Python is installed.
    pause
    exit /b 1
)

echo 🔧 Activating virtual environment...
call venv\Scripts\activate.bat

echo 📚 Installing Python dependencies...
cd backend
pip install -r requirements.txt
if errorlevel 1 (
    echo ❌ Failed to install Python dependencies.
    pause
    exit /b 1
)

echo.
echo ✅ Setup completed successfully!
echo.
echo 🚀 To start the application:
echo    1. cd MyApp
echo    2. venv\Scripts\activate
echo    3. cd backend
echo    4. python simple_main.py
echo.
echo 🔧 For full AI features, use: python main.py (requires additional setup)
echo.
echo 📱 The app will be available at: http://localhost:8001
echo.
pause