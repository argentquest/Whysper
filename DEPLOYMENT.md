# Whysper Deployment Guide

This document explains how to configure, build, and deploy the Whysper Web2 application.

## Overview

Whysper uses an integrated deployment model where:
- **Backend**: FastAPI server runs on port 8001
- **Frontend**: React app served as static files from the backend
- **Configuration**: `.env` file located in `backend/` directory
- **Single Port**: Both frontend and API accessible on port 8001

## Prerequisites

Before deployment, ensure you have:
- Python 3.8+ installed
- Node.js 16+ and npm installed
- An OpenRouter API key (get from https://openrouter.ai/keys)

## Configuration Setup

### Step 1: Create Environment File

The `.env` file **MUST** be located in the `backend/` directory:

```bash
# From project root
copy .envTemplate backend\.env    # Windows
# OR
cp .envTemplate backend/.env      # Linux/macOS
```

### Step 2: Configure API Key

Edit `backend/.env` and set your OpenRouter API key:

```bash
# REQUIRED: Add your OpenRouter API key
API_KEY="sk-or-v1-YOUR_API_KEY_HERE"

# Optional: Configure other settings
PROVIDER="openrouter"
DEFAULT_MODEL="google/gemini-2.5-flash-preview-09-2025"
MAX_TOKENS="4000"
TEMPERATURE="0.7"
```

**Important:**
- The `.env` file location is **`backend/.env`**, not in the project root
- Without a valid API key, the chat functionality will not work
- Get your API key from: https://openrouter.ai/keys

### Step 3: Provider Selection (Optional)

Whysper supports multiple AI providers. By default, it uses OpenRouter (recommended).

**Available Providers:**
- `openrouter` (default) - Access to multiple AI models through single API
- `custom` - Any OpenAI-compatible API

**To switch to custom provider**, edit `backend/.env`:

```bash
# For Custom Provider
PROVIDER="custom"
API_KEY="your-custom-key"
API_URL="https://your-api.com/v1/chat/completions"
```

See the [Provider Configuration section in README.md](README.md#ai-provider-configuration) for detailed provider setup instructions.

## Frontend Deployment

When you make changes to the frontend, you need to rebuild and deploy it to the backend's static directory.

## Quick Start

### Option 1: Automated Build & Deploy (Recommended)

From the project root directory:

```bash
# Windows PowerShell (Recommended)
.\deploy-frontend-clean.ps1

# Windows Batch
.\deploy-frontend.bat

# From frontend directory
cd frontend
npm run build:deploy
```

### Option 2: Manual Steps

```bash
# 1. Build the frontend
cd frontend
npm run build

# 2. Deploy to backend
npm run deploy
# OR use the PowerShell script
cd ..
.\deploy-frontend-clean.ps1 -DeployOnly
```

## Available Scripts

### Project Root Scripts

| Script | Description |
|--------|-------------|
| `deploy-frontend-clean.ps1` | **Recommended** - Builds and deploys with cleanup |
| `deploy-frontend.bat` | Windows batch alternative |
| `deploy-frontend.ps1` | Original (may have encoding issues) |

**PowerShell Script Options:**
```powershell
# Build and deploy (default)
.\deploy-frontend-clean.ps1

# Only build, don't deploy
.\deploy-frontend-clean.ps1 -BuildOnly

# Only deploy (assumes already built)
.\deploy-frontend-clean.ps1 -DeployOnly
```

### Frontend Directory Scripts

| Script | Description |
|--------|-------------|
| `npm run build` | Build frontend for production |
| `npm run deploy` | Deploy built files to backend |
| `npm run build:deploy` | Build and deploy in one command |
| `deploy.ps1` | PowerShell deployment script |
| `deploy.bat` | Batch deployment script |

## File Structure

```
Whysper/
├── frontend/
│   ├── dist/              # Built frontend files (generated)
│   ├── deploy.js          # Node.js deployment script
│   ├── deploy.ps1         # PowerShell deployment script  
│   ├── deploy.bat         # Batch deployment script
│   └── package.json       # Contains build:deploy script
├── backend/
│   ├── static/            # Deployed frontend files (target)
│   └── app/main.py        # FastAPI server with static mounting
├── deploy-frontend-clean.ps1  # Main deployment script
├── deploy-frontend.bat        # Batch alternative
└── DEPLOYMENT.md             # This file
```

## Deployment Process

1. **Build**: TypeScript compilation and Vite bundling
2. **Clean**: Remove old files from `backend/static/`
3. **Copy**: Copy new files from `frontend/dist/` to `backend/static/`
4. **Verify**: Confirm deployment success

## Troubleshooting

### Common Issues

**"Dist directory not found"**
- Run `npm run build` in the frontend directory first
- Or use `npm run build:deploy` to build and deploy together

**"Frontend directory not found"**
- Make sure you're running the script from the project root directory
- Verify the frontend directory exists

**"Permission denied" errors**
- Close any applications that might be using the files
- Run PowerShell as Administrator if needed

**Old files not cleared**
- The Node.js script (`deploy.js`) doesn't clear old files
- Use the PowerShell script for automatic cleanup

**"OpenRouter API key is invalid or expired" error**
- Verify `.env` file is in `backend/` directory (NOT project root)
- Check `API_KEY` value in `backend/.env` is correctly set
- Ensure API key starts with `sk-or-v1-`
- Verify API key is valid at https://openrouter.ai/keys
- Restart the backend server after changing `.env`

**"API key not configured" error**
- The `.env` file is missing or in wrong location
- Copy `.envTemplate` to `backend/.env`
- Add your OpenRouter API key to the `API_KEY` field

### Verification

After deployment, verify everything works correctly:

1. **Check .env file exists:**
   ```bash
   # Verify the file is in the correct location
   dir backend\.env      # Windows
   # ls -la backend/.env # Linux/macOS
   ```

2. **Start the backend server:**
   ```bash
   cd backend
   python main.py
   ```

3. **Verify the application:**
   - Visit http://localhost:8001 (React frontend should load)
   - Check http://localhost:8001/docs (API documentation)
   - Test chat functionality with a simple message

4. **Check browser dev tools:**
   - No 404 errors for CSS/JS assets
   - Assets loading from `/assets/` path
   - API calls going to `/api/v1/*`

5. **Check backend logs:**
   - Should show "Starting Whysper Web2 Backend"
   - No API key errors
   - Successful OpenRouter connections

## Development Workflow

For active development:

1. **Frontend Development**:
   ```bash
   cd frontend
   npm run dev  # Runs on port 5173
   ```

2. **Backend Development**:
   ```bash
   cd backend
   python main.py  # Runs on port 8001
   ```

3. **Integration Testing**:
   ```bash
   # Build and deploy frontend
   .\deploy-frontend-clean.ps1
   
   # Start integrated server
   cd backend
   python main.py
   
   # Test at http://localhost:8001
   ```

## Configuration

### API Base URL

The frontend API base URL is configured in `frontend/src/services/api.ts`:

```typescript
// For integrated deployment (same port)
const API_BASE_URL = '/api/v1';

// For separate development servers
const API_BASE_URL = 'http://localhost:8001/api/v1';
```

### Static File Serving

The backend serves static files via FastAPI configuration in `backend/app/main.py`:

```python
# Mount assets directory for CSS/JS files
app.mount("/assets", StaticFiles(directory=assets_dir), name="assets")

# Mount root static files
app.mount("/static", StaticFiles(directory=static_dir), name="static")

# Serve frontend at root path
@app.get("/")
def serve_frontend():
    return FileResponse(os.path.join(static_dir, "index.html"))
```

## Next Steps

- Consider setting up a CI/CD pipeline for automatic deployment
- Add file watching for automatic rebuild during development
- Implement asset versioning for better caching