#!/bin/bash

echo "================================"
echo "WhisperCode Web2 Setup Script"
echo "================================"
echo

cd "$(dirname "$0")/.."

echo "📦 Setting up Python virtual environment..."
python3 -m venv venv
if [ $? -ne 0 ]; then
    echo "❌ Failed to create virtual environment. Make sure Python 3 is installed."
    exit 1
fi

echo "🔧 Activating virtual environment..."
source venv/bin/activate

echo "📚 Installing Python dependencies..."
cd backend
pip install -r requirements.txt
if [ $? -ne 0 ]; then
    echo "❌ Failed to install Python dependencies."
    exit 1
fi

echo
echo "✅ Setup completed successfully!"
echo
echo "🚀 To start the application:"
echo "   1. cd MyApp"
echo "   2. source venv/bin/activate"
echo "   3. cd backend"
echo "   4. python main.py"
echo
echo "📱 The app will be available at: http://localhost:8001"
echo