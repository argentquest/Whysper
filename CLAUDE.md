# Whysper Web2 Project Status

This document records the current project status and architectural decisions.

## 🌐 Quick Start - Port Configuration

**Default Ports:**
- **Backend API Server:** Port **8003** (configurable in `backend/.env`)
- **Frontend Dev Server:** Port **5173** (or next available: 5174, 5175, etc.)

**Important:** The frontend must know which port the backend is using:
- If using **port 8003** (default): No frontend configuration needed
- If using a **different port**: Create `frontend/.env` and set `VITE_BACKEND_PORT=your_port`

**Example:** Using backend on port 8003 (default)
```bash
# backend/.env
API_PORT="8003"

# frontend/.env (optional, can be omitted for default port)
VITE_BACKEND_PORT=8003
```

**Architecture Overview:**
```
┌─────────────────────────────────────────────────────────────┐
│  Your Browser                                                │
│  http://localhost:5173  ←─ Frontend (React + Vite)         │
│         │                                                    │
│         │ API Calls                                          │
│         ↓                                                    │
│  http://localhost:8003/api/v1  ←─ Backend (FastAPI)        │
│                                                              │
│  Both ports MUST match between backend/.env and frontend/.env│
└─────────────────────────────────────────────────────────────┘
```

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
- **Two-port architecture:** Backend (default: 8003) and frontend (5173) run on separate ports
- **Dual environment configuration:** Separate .env files for backend and frontend
- **Automated startup:** StartApp.bat for easy development environment setup

---

## 📁 Project Structure

```
backend/
├── .env                # ⚠️ REQUIRED: Backend environment configuration (copy from .envTemplate)
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
├── .env                # ⚠️ OPTIONAL: Frontend environment configuration (copy from .env.example)
├── .env.example        # Template for frontend/.env
├── src/
│   ├── components/     # React components
│   ├── services/       # API service layer
│   └── types/         # TypeScript definitions

.envTemplate           # Template for creating backend/.env
StartApp.bat           # Windows batch script to start both servers
```

**Important Environment Files:**
- **`backend/.env`** - Required backend configuration (API keys, server port, etc.)
- **`frontend/.env`** - Optional frontend configuration (only needed if using non-default backend port)

---

## 🚀 Current Status: Production Ready

- **No legacy code remaining**
- **Clean API architecture**
- **Modern development tooling**
- **Comprehensive testing setup**
- **Two-port architecture:** Pure API server + separate frontend

## 🔧 Development Workflow

### **Initial Setup**

#### **1. Configure Backend Environment**
```bash
# Copy environment template to backend directory
copy .envTemplate backend\.env    # Windows
# cp .envTemplate backend/.env    # Linux/macOS
```

Edit `backend/.env` and configure these **essential settings**:

**Required:**
- **`API_KEY`** - Your OpenRouter API key (required for AI functionality)
  ```bash
  API_KEY="sk-or-v1-your-key-here"
  ```

**Important:**
- **`CODE_PATH`** - Directory containing code you want to analyze (default: current directory)
  ```bash
  CODE_PATH="C:\Code2025\Whysper"  # Windows example
  CODE_PATH="/home/user/projects/myapp"  # Linux example
  ```
  **This tells Whysper where your codebase is located.** Point it to any project you want to analyze.

- **`API_PORT`** - Backend server port (default: 8003)
  ```bash
  API_PORT="8003"
  ```

**Optional but Useful:**
- **`LOG_LEVEL`** - Logging verbosity (DEBUG, INFO, WARNING, ERROR, CRITICAL)
  ```bash
  LOG_LEVEL="INFO"  # Default - shows important messages
  LOG_LEVEL="DEBUG"  # Verbose - shows everything (useful for troubleshooting)
  ```

- **`LOG_DIR`** - Where log files are stored (default: "logs")
  ```bash
  LOG_DIR="logs"
  ```

**Other settings:** Model selection, temperature, max tokens, etc. (see `.envTemplate` for all options)

#### **2. Configure Frontend Environment (Optional)**
Only needed if using a non-default backend port:

```bash
# Copy frontend environment template
copy frontend\.env.example frontend\.env    # Windows
# cp frontend/.env.example frontend/.env    # Linux/macOS
```

Edit `frontend/.env`:
- **`VITE_BACKEND_PORT`** - Must match `backend/.env` API_PORT (e.g., 8003)

**Note:** If using the default port (8003), you don't need to create `frontend/.env`

#### **3. Install Dependencies**
```bash
cd backend
pip install -r requirements.txt
cd ../frontend
npm install
```

---

### **Starting the Application**

#### **Option 1: Automated Startup (Recommended for Windows)**
```bash
# Run from project root - starts both servers automatically
StartApp.bat
```

**What StartApp.bat does:**
1. Checks for `backend/.env` file existence
2. Installs frontend dependencies
3. Builds frontend production assets
4. Reads backend port from `backend/.env` dynamically
5. Starts backend server in new window
6. Starts frontend dev server in new window
7. Works from any directory (uses script location)

#### **Option 2: Manual Startup**
```bash
# Terminal 1: Backend API Server
cd backend
python main.py

# Terminal 2: Frontend Development Server
cd frontend
npm run dev
```

---

### **Access Points**

**Development (Two-Port Architecture):**
- **Frontend:** http://localhost:5173 (React dev server with hot reload)
- **Backend API:** http://localhost:8003/api/v1 (Pure API server)
- **API Documentation:** http://localhost:8003/docs (OpenAPI/Swagger)

**Production (Single-Port Architecture):**
- **Integrated:** http://localhost:8003 (backend serves built frontend)

**Note:** Port numbers may vary based on your `backend/.env` configuration and availability. Vite will use 5173, 5174, 5175, etc. if ports are in use.

---

### **Logging and Debugging**

Whysper has comprehensive logging to help you understand what's happening and troubleshoot issues.

#### **Log Levels**
Configure logging verbosity in `backend/.env`:

```bash
LOG_LEVEL="INFO"   # Recommended for normal use - shows important events
LOG_LEVEL="DEBUG"  # Verbose mode - shows detailed execution flow
LOG_LEVEL="WARNING"  # Only warnings and errors
LOG_LEVEL="ERROR"  # Only errors
```

#### **Log Files Location**
Logs are stored in the directory specified by `LOG_DIR` (default: `backend/logs/`):

```
backend/logs/
├── structured.log      # Main application log with all events
├── errors.log          # Error-only log for quick troubleshooting
└── performance.log     # Performance metrics and timing data
```

#### **What Gets Logged**
- **API requests and responses** - Track all chat interactions
- **File operations** - See which files are being read/processed
- **AI provider calls** - Monitor API usage and responses
- **Configuration changes** - Track settings updates
- **Performance metrics** - See how long operations take
- **Errors and exceptions** - Detailed stack traces for debugging

#### **Console Output**
When running servers manually, you'll see:
- **Backend:** Colored structured logs with timestamps
- **Frontend:** Vite dev server output and hot-reload notifications

**Example DEBUG output:**
```
[2025-10-06 15:52:03] DEBUG whysper.app.services.conversation_service | Adding user message to conversation history
[2025-10-06 15:52:03] INFO  whysper.app.services.conversation_service | Started processing question for session conv-1
[2025-10-06 15:52:03] DEBUG whysper.common.lazy_file_scanner | Cache miss, reading file
```

**Tip:** Use `LOG_LEVEL="DEBUG"` when developing or troubleshooting, and `LOG_LEVEL="INFO"` for normal usage.

---

### **Agent & Subagent System**

Whysper uses a powerful two-tier prompt system to customize AI behavior for different tasks.

#### **What Are Agents?**
**Agents** are system-level prompts that define the AI's overall role and expertise. They set the foundational behavior and knowledge domain.

**Location:** `prompts/coding/agent/*.md`

**Examples:**
- `code_reviewer.md` - Expert code reviewer focused on best practices
- `documentation_writer.md` - Technical documentation specialist
- `debugging_expert.md` - Bug analysis and troubleshooting expert
- `architecture_designer.md` - System architecture and design expert

**How to use:**
1. Select an agent from the dropdown in the header
2. The AI will adopt that role for all subsequent conversations
3. Agents persist across your session

**Creating custom agents:**
```bash
# Create a new agent file
echo "You are an expert in Python data science..." > prompts/coding/agent/data_scientist.md

# It will automatically appear in the UI dropdown
```

#### **What Are Subagents?**
**Subagents** are task-specific command templates that inject specialized instructions into your prompts. They're like AI shortcuts for common tasks.

**Location:** `prompts/coding/subagent/master.json`

**Categories & Examples:**
- **Analysis** - Code analysis, complexity review, dependency mapping
- **Documentation** - README generation, API docs, code comments
- **Refactoring** - Code optimization, pattern improvements
- **Testing** - Unit tests, integration tests, test coverage
- **Security** - Vulnerability scanning, security audit
- **Mermaid** - 20+ diagram types (flowcharts, class diagrams, sequence diagrams, etc.)
- **And many more!** (89 subagents total)

**How to use:**
1. Click the "Subagent" dropdown in the chat input area
2. Select a category, then choose a specific subagent
3. The subagent command is injected into your message
4. The AI responds according to that specialized template

**Example workflow:**
```
1. Select Agent: "Code Reviewer"
2. Select Subagent: "Mermaid > Class Diagram"
3. Select Files: backend/common/base_ai.py
4. Send message
5. AI generates a class diagram as a code reviewer would
```

#### **File Structure**
```
prompts/
└── coding/
    ├── agent/              # System-level role definitions
    │   ├── code_reviewer.md
    │   ├── documentation_writer.md
    │   ├── debugging_expert.md
    │   └── [20 total agents]
    │
    └── subagent/           # Task-specific templates
        └── master.json     # All 89+ subagent commands organized by category
```

#### **Creating Custom Subagents**
Edit `prompts/coding/subagent/master.json`:

```json
{
  "category": "My Custom Category",
  "commands": [
    {
      "name": "My Custom Task",
      "prompt": "Analyze the code and provide specific insights about..."
    }
  ]
}
```

**The system automatically reloads** - no restart needed!

#### **Best Practices**
- **Agents** = "Who is the AI?" (role/expertise)
- **Subagents** = "What task to perform?" (specific action)
- **Combine both** for powerful, specialized AI assistance
- **Experiment** with different combinations to find what works best
- **Create custom ones** for your specific workflow needs

**Pro Tip:** The Mermaid subagents are particularly powerful for visualizing codebases - try "Mermaid > Component Architecture" on a complex module!
