# Whysper Web2 Project Status

This document records the current project status and architectural decisions.

## ✅ Completed Features

### **API Architecture**
- **Clean API routing:** All endpoints properly under `/api/v1/*` (no legacy `/api` routes)
- **Modular endpoint structure:** Organized by functionality (chat, settings, files, etc.)
- **OpenAPI documentation:** Comprehensive API docs available at `/docs`

### **Agent & Subagent System**
- **Agents (System Prompts):** Dynamic agent prompts loaded from markdown files in `prompts/coding/agent/`
- **Subagents (Command Templates):** Command injection system with 40+ categories and commands
- **Frontend Integration:** Proper UI placement - agents in header, subagents in chat area

### **Settings Management**
- **Comprehensive settings API:** Environment variables, themes, and configuration
- **Dynamic agent/subagent loading:** Real-time loading from backend files
- **Theme management:** Light/dark theme switching with persistence

### **Development Environment**
- **Modern debugging:** Updated VS Code launch.json to use `debugpy`
- **Comprehensive launch configs:** Debug, testing, and quality check configurations
- **Clean architecture:** Removed legacy code compatibility layers
- **Two-port architecture:** Backend (8001) and frontend (5173) run on separate ports

---

## 📁 Project Structure

```
backend/
├── .env                # ⚠️ REQUIRED: Environment configuration (copy from .envTemplate)
├── app/
│   ├── api/v1/          # All API endpoints under /api/v1
│   ├── services/        # Business logic services
│   └── core/           # Configuration and setup
├── common/             # Shared utilities
└── prompts/
    └── coding/
        ├── agent/      # Agent prompt files (*.md)
        └── subagent/   # Subagent commands (master.json)

frontend/
├── src/
│   ├── components/     # React components
│   ├── services/       # API service layer
│   └── types/         # TypeScript definitions

.envTemplate           # Template for creating backend/.env
```

**Important:** The `.env` file MUST be located at `backend/.env`, not in the project root.

---

## 🚀 Current Status: Production Ready

- **No legacy code remaining**
- **Clean API architecture**
- **Modern development tooling**
- **Comprehensive testing setup**
- **Two-port architecture:** Pure API server + separate frontend

## 🔧 Development Workflow

### **Initial Setup**
```bash
# 1. Copy environment template to backend directory
copy .envTemplate backend\.env    # Windows
# cp .envTemplate backend/.env    # Linux/macOS

# 2. Edit backend/.env and add your OpenRouter API key
# API_KEY="sk-or-v1-YOUR_KEY_HERE"

# 3. Install dependencies
cd backend
pip install -r requirements.txt
cd ../frontend
npm install
```

### **Starting the Application**
```bash
# Backend API Server (Port 8001)
cd backend
python main.py

# Frontend Development Server (Port 5173)
cd frontend
npm run dev
```

### **Access Points**
- **Frontend:** http://localhost:5173 (React dev server)
- **Backend API:** http://localhost:8001/api/v1 (Pure API)
- **API Documentation:** http://localhost:8001/docs (OpenAPI/Swagger)
- **Integrated (production):** http://localhost:8001 (backend serves frontend)
