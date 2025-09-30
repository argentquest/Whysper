# Whysper Frontend Deployment Guide

This document explains how to build and deploy the frontend to the integrated backend server.

## Overview

Whysper uses an integrated deployment model where the React frontend is served by the FastAPI backend server on a single port (8001). When you make changes to the frontend, you need to rebuild and deploy it to the backend's static directory.

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

### Verification

After deployment, verify the integration works:

1. Start the backend server:
   ```bash
   cd backend
   python main.py
   ```

2. Visit http://localhost:8001
   - Should serve the React application
   - API endpoints available at http://localhost:8001/api/v1/*

3. Check browser dev tools:
   - No 404 errors for CSS/JS assets
   - Assets loading from `/assets/` path

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