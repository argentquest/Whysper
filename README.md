# Whysper Web2 - Full Stack AI Chat Application

A modern, full-stack web application that provides AI-powered chat functionality with code analysis, file management, and multi-provider AI integration.

## 🚀 Quick Start

### Windows
```bash
cd setup
install.bat
```

### Linux/macOS
```bash
cd setup
./install.sh
```

### Manual Setup
```bash
# 1. Create virtual environment
python -m venv venv

# 2. Activate virtual environment
# Windows:
venv\Scripts\activate
# Linux/macOS:
source venv/bin/activate

# 3. Install dependencies
cd backend
pip install -r requirements.txt

# 4. Run the application
python main.py
```

## 📱 Access the Application

Once started, the application will be available at:
- **Frontend**: http://localhost:8001
- **API**: http://localhost:8001/api/v1
- **Documentation**: http://localhost:8001/docs

## 🏗️ Architecture

```
MyApp/
├── backend/                 # FastAPI backend server
│   ├── app/                 # Application code
│   │   ├── api/v1/         # API version 1 endpoints
│   │   ├── core/           # Core configuration
│   │   └── main.py         # FastAPI app with frontend serving
│   ├── static/             # Built frontend files
│   ├── main.py             # Simple entry point
│   └── requirements.txt    # Python dependencies
├── setup/                  # Installation scripts
│   ├── install.bat         # Windows installer
│   └── install.sh          # Linux/macOS installer
└── README.md               # This file
```

## ✨ Features

### Frontend (React + TypeScript)
- 🎨 Modern UI with Ant Design components
- 🌓 Light/Dark theme support
- 📱 Responsive design
- 🗂️ Multi-tab conversation management
- 📁 File context selection
- 🎯 Quick command templates
- 🔧 Settings management

### Backend (FastAPI + Python)
- 🤖 Multi-provider AI integration (OpenRouter, OpenAI, Anthropic)
- 📊 Code extraction and analysis
- 🎨 Mermaid diagram rendering
- 📂 File system integration
- 🔄 Real-time chat processing
- 📝 Conversation persistence
- 🔐 API key management

### Integration
- 🚀 Single-command deployment
- 📦 Built-in frontend serving via FastAPI
- 🔌 RESTful API with automatic documentation
- 🛡️ CORS configuration for development
- 📋 Comprehensive logging and monitoring

## 🔧 Configuration

The application uses environment variables for configuration. Key settings:

- `API_KEY`: Your AI provider API key
- `DEFAULT_MODEL`: Default AI model to use
- `MAX_TOKENS`: Maximum tokens per response
- `TEMPERATURE`: AI creativity setting (0.0-1.0)

## 🚀 Development

The application is designed for easy development and deployment:

1. **Single Port**: Both frontend and backend run on port 8001
2. **Hot Reload**: Backend supports auto-reload during development
3. **Static Serving**: Frontend is built and served as static files
4. **API Documentation**: Automatic OpenAPI docs at `/docs`

### VS Code Integration

The project includes comprehensive VS Code configuration for one-click development:

**Launch Configurations:**
- 🚀 **Integrated: Backend + Frontend Server** - Automatically builds and deploys frontend, then starts integrated server
- 🔧 **Development: Backend + Frontend Separate** - Runs backend and frontend on separate ports for development
- **Frontend: Build and Deploy** - Builds and deploys frontend to backend
- **Deploy: PowerShell Build & Deploy** - Runs deployment script via PowerShell

**Available Tasks (Ctrl+Shift+P → "Tasks: Run Task"):**
- **Deploy Frontend** - Build and deploy frontend to backend
- **Frontend: Build** - Build frontend only
- **Backend: Run Tests** - Run backend test suite
- **Kill Processes on Ports 8000-8010** - Clean up development ports

**Quick Deployment:**
1. Press `F5` and select "🚀 Integrated: Backend + Frontend Server"
2. VS Code will automatically build the frontend and start the integrated server
3. Visit http://localhost:8001 to access the application

See `DEPLOYMENT.md` for detailed deployment instructions.

## 📚 API Endpoints

- `GET /` - Frontend application
- `GET /api/v1/` - API health check
- `POST /api/v1/chat/` - Send chat messages
- `GET /api/v1/files/` - Browse files
- `GET /api/v1/settings/` - Get application settings
- `GET /docs` - Interactive API documentation

## 🛠️ Troubleshooting

### Common Issues

1. **Port 8001 in use**: Change the port in `backend/app/core/config.py`
2. **API key errors**: Set your AI provider API key in the environment or settings
3. **Frontend not loading**: Ensure the `static/` directory contains the built frontend files

### Getting Help

- Check the logs for detailed error messages
- Visit `/docs` for API documentation
- Ensure all dependencies are installed correctly

## 📄 License

This project is provided as-is for educational and development purposes.