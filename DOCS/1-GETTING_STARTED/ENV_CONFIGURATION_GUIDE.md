# Environment Configuration Guide

## Setting the Base Directory Path in .env

You can now configure the initial base directory by setting the `BASE_DIRECTORY` environment variable in your `.env` file.

---

## Location in .env File

**File**: `backend/.env`
**Section**: 📁 FILE SYSTEM CONFIGURATION (around line 78)

```bash
# =============================================================================
# 📁 FILE SYSTEM CONFIGURATION
# =============================================================================

# Base directory for file scanning - supports external folders
# Leave empty to use current working directory
BASE_DIRECTORY=""
```

---

## Configuration Options

### Option 1: Scan Backend (Default)
```bash
BASE_DIRECTORY="/c/Code2025/Whysper/backend"
```

### Option 2: Scan Frontend
```bash
BASE_DIRECTORY="/c/Code2025/Whysper/frontend"
```

### Option 3: Scan Entire Project
```bash
BASE_DIRECTORY="/c/Code2025/Whysper"
```

### Option 4: Scan Multiple Projects
```bash
BASE_DIRECTORY="/c/Code2025"
```

### Option 5: Empty (Current Directory)
```bash
BASE_DIRECTORY=""
```

---

## Examples

### Example 1: Start with Frontend
```bash
# In backend/.env

BASE_DIRECTORY="/c/Code2025/Whysper/frontend"

# When backend starts, it will scan the frontend folder
```

### Example 2: Start with Backend
```bash
# In backend/.env

BASE_DIRECTORY="/c/Code2025/Whysper/backend"

# When backend starts, it will scan the backend folder
```

### Example 3: Start with Root (Can Switch via API)
```bash
# In backend/.env

BASE_DIRECTORY="/c/Code2025/Whysper"

# When backend starts, it will scan the entire Whysper project
# You can then switch folders via API without restarting
```

### Example 4: Auto-Detect Current Directory
```bash
# In backend/.env

BASE_DIRECTORY=""

# Backend will use the current working directory
# This is the default behavior
```

---

## How to Edit .env

### Method 1: Text Editor
1. Open `backend/.env` in your text editor
2. Find the line: `BASE_DIRECTORY=""`
3. Change to: `BASE_DIRECTORY="/c/Code2025/Whysper/frontend"`
4. Save the file
5. Restart the backend

### Method 2: Command Line (Windows)
```bash
# Edit the .env file (open in default text editor)
start backend\.env

# Or use a specific editor
notepad backend\.env
```

### Method 3: Command Line (Linux/Mac)
```bash
# Edit using nano
nano backend/.env

# Or vim
vim backend/.env
```

### Method 4: PowerShell
```powershell
# Replace the path
(Get-Content backend\.env) -replace 'BASE_DIRECTORY=""', 'BASE_DIRECTORY="/c/Code2025/Whysper/frontend"' | Set-Content backend\.env
```

---

## Common Paths

### Windows Paths

**Backend:**
```bash
BASE_DIRECTORY="C:\Code2025\Whysper\backend"
BASE_DIRECTORY="c:\Code2025\Whysper\backend"
BASE_DIRECTORY="/c/Code2025/Whysper/backend"           # ← This format works
```

**Frontend:**
```bash
BASE_DIRECTORY="/c/Code2025/Whysper/frontend"
```

**Project Root:**
```bash
BASE_DIRECTORY="/c/Code2025/Whysper"
```

---

## What Happens on Startup

1. **Backend starts**
2. **Reads `BASE_DIRECTORY` from .env**
3. **Validates the directory**
4. **Sets it as the scanning folder**
5. **Ready to scan and serve files**

---

## Dynamic Changes (After Startup)

Even if you set `BASE_DIRECTORY` in `.env`, you can change it at runtime using the API:

```bash
# Start with frontend
BASE_DIRECTORY="/c/Code2025/Whysper/frontend"

# Later, switch to backend via API (no restart needed)
curl -X POST http://localhost:8001/api/v1/files/set-directory \
  -d '{"directory": "/c/Code2025/Whysper/backend"}'
```

---

## Recommended Configurations

### For Frontend Development
```bash
BASE_DIRECTORY="/c/Code2025/Whysper/frontend"
```
This allows easy access to frontend code.

### For Full-Stack Development
```bash
BASE_DIRECTORY="/c/Code2025/Whysper"
```
This allows switching between frontend and backend via API.

### For Multi-Project Work
```bash
BASE_DIRECTORY="/c/Code2025"
```
This allows access to all projects in the Code2025 folder.

### For Default Behavior (Recommended)
```bash
BASE_DIRECTORY=""
```
Uses the current working directory. Flexibility to change via API.

---

## Troubleshooting

### Error: "Directory does not exist"
**Problem**: The path in `BASE_DIRECTORY` doesn't exist

**Solution**:
1. Check the path is correct
2. Use forward slashes: `/c/Code2025/Whysper/frontend`
3. Not backslashes: `c:\Code2025\Whysper\frontend` ❌
4. Use absolute paths (start with `/c/` or drive letter)

### Error: "Directory is not readable"
**Problem**: Backend process can't access the directory

**Solution**:
1. Check file permissions
2. Make sure the directory isn't locked
3. Try a different directory to test

### No Files Found
**Problem**: Directory exists but no files are listed

**Possible Causes**:
- Folder has no supported file types (.ts, .js, .py, etc.)
- All files are in ignored folders (node_modules, .git, etc.)
- Files are too large (>10MB individual, >100MB batch)

**Solution**:
- Check the folder contains code files
- Verify folder permissions
- Try scanning a different folder

---

## Example .env Configuration

### Frontend Focus
```bash
# =============================================================================
# 📁 FILE SYSTEM CONFIGURATION
# =============================================================================

# Start with frontend folder
BASE_DIRECTORY="/c/Code2025/Whysper/frontend"

# Folders to ignore
IGNORE_FOLDERS="node_modules,.git,.venv,dist,build"
```

### Backend Focus
```bash
# =============================================================================
# 📁 FILE SYSTEM CONFIGURATION
# =============================================================================

# Start with backend folder
BASE_DIRECTORY="/c/Code2025/Whysper/backend"

# Folders to ignore
IGNORE_FOLDERS="node_modules,.git,.venv,dist,build"
```

### Full Project
```bash
# =============================================================================
# 📁 FILE SYSTEM CONFIGURATION
# =============================================================================

# Start with project root (can switch folders via API)
BASE_DIRECTORY="/c/Code2025/Whysper"

# Folders to ignore
IGNORE_FOLDERS="node_modules,.git,.venv,dist,build"
```

---

## Summary

| Config | Effect | API Override |
|--------|--------|--------------|
| `BASE_DIRECTORY=""` | Use current dir | ✅ Yes |
| `BASE_DIRECTORY="/frontend"` | Start with frontend | ✅ Yes |
| `BASE_DIRECTORY="/backend"` | Start with backend | ✅ Yes |
| `BASE_DIRECTORY="/project"` | Start with project | ✅ Yes |

---

## Next Steps

1. **Edit your .env file**
   ```bash
   # Open backend/.env
   # Find: BASE_DIRECTORY=""
   # Change to your desired path
   # Save
   ```

2. **Restart the backend**
   ```bash
   # Kill and restart the backend server
   ```

3. **Verify it works**
   ```bash
   # Test scanning the folder
   curl http://localhost:8001/api/v1/files/scan-directory
   ```

4. **Use the API to switch folders** (optional)
   ```bash
   # Change folders without restarting
   curl -X POST http://localhost:8001/api/v1/files/set-directory \
     -d '{"directory": "/c/Code2025/Whysper/frontend"}'
   ```

---

## Default Path Format

Use forward slashes `/` instead of backslashes `\`:

✅ **Correct:**
```bash
BASE_DIRECTORY="/c/Code2025/Whysper/frontend"
BASE_DIRECTORY="/home/user/project"
```

❌ **Incorrect:**
```bash
BASE_DIRECTORY="c:\Code2025\Whysper\frontend"    # Windows backslashes
BASE_DIRECTORY="C:/Code2025/Whysper/frontend"    # Wrong drive format
```

---

## Questions?

- **How do I use the API to change folders?** → `EXTERNAL_FOLDER_ACCESS.md`
- **What paths work?** → This document (COMMON PATHS section)
- **Full configuration guide?** → `QUICK_START_EXTERNAL_ACCESS.md`

