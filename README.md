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

# 3. Install backend dependencies
cd backend
pip install -r requirements.txt

# 4. Configure environment variables
# Copy the template and add your API key
copy ..\.envTemplate .env    # Windows
# cp ../.envTemplate .env    # Linux/macOS
# Edit .env and add your OpenRouter API key to the API_KEY field

# 5. Install frontend dependencies (for development)
cd ../frontend
npm install

# 6. Run the application
cd ../backend
python main.py
```

## 📱 Access the Application

Once started, the application will be available at:
- **Frontend**: http://localhost:8001 (integrated React app)
- **API**: http://localhost:8001/api/v1
- **API Documentation**: http://localhost:8001/docs (Swagger UI)

**Note:** For development, you can run frontend separately on port 5173:
```bash
cd frontend
npm run dev
```
Then configure frontend to use `http://localhost:8001/api/v1` for the backend API.

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

The application uses a `.env` file located in the **`backend/`** directory for configuration.

### Required Configuration Steps

1. **Copy the environment template:**
   ```bash
   # From project root
   copy .envTemplate backend\.env    # Windows
   # cp .envTemplate backend/.env    # Linux/macOS
   ```

2. **Edit `backend/.env` and configure:**
   - `API_KEY`: Your OpenRouter API key (get from https://openrouter.ai/keys)
   - `DEFAULT_MODEL`: Default AI model to use (e.g., `google/gemini-2.5-flash-preview-09-2025`)
   - `PROVIDER`: AI provider name (default: `openrouter`)
   - `MAX_TOKENS`: Maximum tokens per response (default: `4000`)
   - `TEMPERATURE`: AI creativity setting 0.0-1.0 (default: `0.7`)

3. **Important:** The `.env` file **MUST** be in the `backend/` directory, not the project root

### AI Provider Configuration

Whysper supports multiple AI providers through a modular provider system. Each provider may require different configuration settings in your `.env` file.

#### Available Providers

The application includes the following built-in providers (located in `backend/providers/`):

1. **OpenRouter Provider** (`openrouter`) - **Default & Recommended**
   - Unified API for multiple AI models (OpenAI, Anthropic, Google, etc.)
   - Single API key for all models
   - Automatic model routing and fallback
   - Get API key: https://openrouter.ai/keys

2. **Custom Provider** (`custom`)
   - Configurable for any OpenAI-compatible API
   - Flexible configuration via environment variables

#### Switching Between Providers

To use a different provider, update these fields in `backend/.env`:

```bash
# Set the provider name (openrouter or custom)
PROVIDER="openrouter"

# Provider-specific API key
API_KEY="your-provider-api-key-here"
```

#### Provider-Specific Configuration

**For OpenRouter (Default):**
```bash
PROVIDER="openrouter"
API_KEY="sk-or-v1-YOUR_OPENROUTER_KEY"
DEFAULT_MODEL="google/gemini-2.5-flash-preview-09-2025"
# OpenRouter handles all model routing automatically
```

**For Custom Provider:**
```bash
PROVIDER="custom"
API_KEY="your-custom-api-key"
API_URL="https://your-api.com/v1/chat/completions"
DEFAULT_MODEL="your-model-name"

# Optional custom provider settings
# AUTH_HEADER="Authorization"          # Header name for auth
# AUTH_FORMAT="Bearer {api_key}"       # Auth format string
# REQUEST_TIMEOUT="30"                 # Request timeout in seconds
```

#### Adding a New Provider

To add support for a new AI provider:

1. Create a new provider file in `backend/providers/` (e.g., `my_provider.py`)
2. Extend the `BaseAIProvider` class from `common/base_ai.py`
3. Implement the required methods:
   - `_get_provider_config()` - Provider-specific configuration
   - `_prepare_headers()` - Authentication headers
   - `_prepare_request_data()` - Request payload formatting
   - `_extract_response_content()` - Parse AI response
   - `_extract_token_usage()` - Extract token usage info
   - `_handle_api_error()` - Custom error handling
4. Register your provider in `backend/providers/__init__.py`
5. Add provider-specific configuration to `.envTemplate`

See `backend/providers/openrouter_provider.py` for a complete example implementation.

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