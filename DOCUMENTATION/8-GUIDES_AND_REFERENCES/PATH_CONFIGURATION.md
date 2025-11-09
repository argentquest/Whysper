# Path Configuration Guide

This document explains how to configure file paths for deployment on different servers.

## Environment Variables

Add these variables to your `.env` file to customize paths:

### STATIC_DIR
Path to the static files directory. Used by the FastAPI server to serve static files.

**Default:** `backend/static` (relative to backend/app/main.py)

**Examples:**
```bash
# Absolute path (recommended for production)
STATIC_DIR="C:/www/whysper/static"
STATIC_DIR="/var/www/whysper/static"

# Relative path from backend directory
STATIC_DIR="./static"

# Leave empty to use default
STATIC_DIR=""
```

### PROMPTS_DIR
Path to the base directory containing prompts:
- **System message files** (`systemmessage_*.txt`) - located directly in PROMPTS_DIR
- **Agent prompt files** - located in `PROMPTS_DIR/prompts/coding/agent/*.md`

**Default:**
- For system messages: Current working directory
- For agent prompts: `prompts/coding/agent/` relative to project root

**Important Notes:**
- If you set PROMPTS_DIR to your project root, the code will automatically append `/prompts` for agent prompts
- System message files are always looked up directly in PROMPTS_DIR
- Agent prompts are in `PROMPTS_DIR/prompts/coding/agent/` if PROMPTS_DIR ends with `prompts`, otherwise `PROMPTS_DIR/prompts/coding/agent/`

**Examples:**
```bash
# Project root (system messages at root, agent prompts at root/prompts/coding/agent/)
PROMPTS_DIR="C:/www/whysper"
PROMPTS_DIR="/var/www/whysper"

# Absolute path to prompts directory
PROMPTS_DIR="C:/www/whysper/prompts"
PROMPTS_DIR="/var/www/whysper/prompts"

# Relative path
PROMPTS_DIR="."

# Leave empty to use default
PROMPTS_DIR=""
```

### D2_EXECUTABLE_PATH
Path to the D2 diagram executable.

**Default:** Auto-detects in this order:
1. `d2` in system PATH
2. `bin/d2.exe` in project root (Windows)
3. `bin/d2` in project root (Linux/Mac)
4. `D2/d2-v0.7.1/bin/d2.exe` in project root (Windows legacy)
5. `/usr/local/bin/d2` (macOS/Linux)
6. `/usr/bin/d2` (Linux)

**Note:** The project includes `d2.exe` in the `bin/` folder at the project root.

**Examples:**
```bash
# Windows absolute path
D2_EXECUTABLE_PATH="C:/www/whysper/bin/d2.exe"

# Linux absolute path
D2_EXECUTABLE_PATH="/opt/d2/bin/d2"

# Relative path to project root bin
D2_EXECUTABLE_PATH="bin/d2.exe"

# Use system PATH
D2_EXECUTABLE_PATH="d2"

# Leave empty to use default auto-detection
D2_EXECUTABLE_PATH=""
```

## Deployment Examples

### Example 1: Production server at `/var/www/whysper/`

```bash
# Directory structure
/var/www/whysper/
├── backend/
│   ├── app/
│   ├── static/          # Static files
│   └── ...
├── frontend/
├── prompts/
│   └── coding/
│       └── agent/
│           ├── mermaid-architecture.md
│           ├── d2-architecture.md
│           └── c4-architecture.md
├── systemmessage_default.txt
├── systemmessage_documentation.txt
└── bin/
    └── d2

# .env configuration
STATIC_DIR="/var/www/whysper/backend/static"
PROMPTS_DIR="/var/www/whysper"
D2_EXECUTABLE_PATH="/var/www/whysper/bin/d2"
```

### Example 2: Alternative structure with shared resources

```bash
# Directory structure
/var/www/
├── whysper-app/
│   ├── backend/
│   └── frontend/
├── whysper-resources/
│   ├── static/
│   ├── prompts/
│   │   └── coding/
│   │       └── agent/
│   │           ├── mermaid-architecture.md
│   │           ├── d2-architecture.md
│   │           └── c4-architecture.md
│   ├── systemmessage_default.txt
│   └── systemmessage_documentation.txt
└── tools/
    └── bin/
        └── d2

# .env configuration
STATIC_DIR="/var/www/whysper-resources/static"
PROMPTS_DIR="/var/www/whysper-resources"
D2_EXECUTABLE_PATH="/var/www/tools/bin/d2"
```

### Example 3: Windows deployment

```bash
# Directory structure
C:\inetpub\wwwroot\whysper\
├── backend\
│   ├── app\
│   ├── static\
│   └── ...
├── prompts\
│   └── coding\
│       └── agent\
│           ├── mermaid-architecture.md
│           ├── d2-architecture.md
│           └── c4-architecture.md
├── systemmessage_default.txt
└── bin\
    └── d2.exe

# .env configuration
STATIC_DIR="C:\inetpub\wwwroot\whysper\backend\static"
PROMPTS_DIR="C:\inetpub\wwwroot\whysper"
D2_EXECUTABLE_PATH="C:\inetpub\wwwroot\whysper\bin\d2.exe"
```

## Files Modified

1. `.envTemplate` - Added new environment variables
2. `backend/.env` - Added new environment variables
3. `backend/app/main.py` - Uses STATIC_DIR
4. `backend/common/system_message_manager.py` - Uses PROMPTS_DIR
5. `backend/mvp_diagram_generator/rendering_api.py` - Uses PROMPTS_DIR
6. `backend/mcp_server/fastmcp_server.py` - Uses PROMPTS_DIR
7. `backend/app/services/d2_render_service.py` - Uses D2_EXECUTABLE_PATH
8. `backend/mvp_diagram_generator/d2_cli_validator.py` - Uses D2_EXECUTABLE_PATH
