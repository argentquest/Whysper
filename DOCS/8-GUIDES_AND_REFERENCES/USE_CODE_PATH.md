# Important: Use CODE_PATH Variable (Not BASE_DIRECTORY)

## Correction

We discovered that your codebase already has a `CODE_PATH` environment variable that serves this exact purpose. We've updated the implementation to use the existing `CODE_PATH` variable instead of introducing a new `BASE_DIRECTORY` variable.

---

## How to Set the Path in .env

**File**: `backend/.env` (around line 60)

### Find the CODE_PATH line:
```bash
CODE_PATH=""
```

### Set it to your desired folder:
```bash
# Option 1: Scan backend
CODE_PATH="/c/Code2025/Whysper/backend"

# Option 2: Scan frontend
CODE_PATH="/c/Code2025/Whysper/frontend"

# Option 3: Scan entire project
CODE_PATH="/c/Code2025/Whysper"

# Option 4: Scan multiple projects
CODE_PATH="/c/Code2025"

# Option 5: Use current directory (default)
CODE_PATH=""
```

### Then restart the backend!

---

## Why CODE_PATH?

The codebase already uses `CODE_PATH` throughout:
- ✅ In `files.py` endpoints
- ✅ In `conversation_service.py`
- ✅ In `env_manager.py`
- ✅ In multiple other locations

By using the existing `CODE_PATH` variable, we:
- ✅ Maintain consistency with existing code
- ✅ Don't introduce new configuration variables
- ✅ Leverage existing environment management
- ✅ Follow established patterns

---

## What Was Changed

### In .env (backend/.env, line 60)
```bash
# BEFORE: Comments referenced CODE_PATH
CODE_PATH=""

# AFTER: Comments updated to clarify usage for external folders
CODE_PATH=""
# Code path for file scanning - supports external folders
# Examples:
#   CODE_PATH="/c/Code2025/Whysper/backend"           (backend)
#   CODE_PATH="/c/Code2025/Whysper/frontend"          (frontend)
```

### In FileService (backend/app/services/file_service.py)
```python
# NOW: FileService reads CODE_PATH from environment
def __init__(self, base_directory: Optional[str] = None) -> None:
    # Support for custom base directory - uses CODE_PATH from env
    env_vars = env_manager.load_env_file()
    self._base_directory = env_vars.get("CODE_PATH", None)
```

---

## How It Works

1. **On startup**: FileService reads `CODE_PATH` from `.env`
2. **Sets it as base**: The folder is set as the scanning base
3. **Via API**: You can change it dynamically without restarting
4. **Backward compatible**: Existing code that uses `CODE_PATH` continues to work

---

## Quick Start

### Step 1: Edit backend/.env
```bash
# Find line 60 with CODE_PATH
CODE_PATH="/c/Code2025/Whysper/frontend"
```

### Step 2: Restart Backend
Kill and restart your backend server.

### Step 3: Test
```bash
curl http://localhost:8001/api/v1/files/scan-directory
```

---

## API Usage (Unchanged)

The API endpoints work the same as before:

```bash
# Set directory via API
curl -X POST http://localhost:8001/api/v1/files/set-directory \
  -d '{"directory": "/c/Code2025/Whysper/frontend"}'

# Get current directory
curl http://localhost:8001/api/v1/files/get-directory

# Scan current directory
curl http://localhost:8001/api/v1/files/scan-directory
```

---

## Backward Compatibility

✅ **100% Backward Compatible**

Existing code that reads from `CODE_PATH`:
- `files.py` endpoints
- `conversation_service.py`
- Any other location using `env_vars.get("CODE_PATH", ...)`

All continue to work without any changes.

---

## Example .env Configuration

```bash
# =============================================================================
# 📁 FILE SYSTEM CONFIGURATION
# =============================================================================

# Code path for file scanning - supports external folders
# Leave empty to use current working directory
# Examples:
#   CODE_PATH="/c/Code2025/Whysper/backend"           (backend)
#   CODE_PATH="/c/Code2025/Whysper/frontend"          (frontend)
#   CODE_PATH="/c/Code2025/Whysper"                   (project root)
#   CODE_PATH="/c/Code2025"                           (multiple projects)
CODE_PATH="/c/Code2025/Whysper/frontend"

# Folders to ignore during codebase scanning
IGNORE_FOLDERS=""

# Supported file extensions (comma-separated, with dots)
SUPPORTED_EXTENSIONS=""

# Maximum file size to process (in bytes)
MAX_FILE_SIZE="10485760"
```

---

## Summary

| Variable | Status | Usage |
|----------|--------|-------|
| `CODE_PATH` | ✅ USE THIS | Set scanning folder in .env |
| `BASE_DIRECTORY` | ❌ Don't use | Was temporary, not needed |

Use `CODE_PATH` - it's the existing standard in your codebase!

---

## Next Steps

1. Edit `backend/.env`
2. Set `CODE_PATH` to your desired folder
3. Restart the backend
4. Test with the API examples above

That's it! You now have full external folder access using the established `CODE_PATH` variable.

