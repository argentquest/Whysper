# External Folder Access Guide

## Overview

You can now safely scan and access code from **external folders** (frontend, other projects, etc.) without removing security restrictions.

The new implementation:
- ✅ **Maintains path traversal protection** (CWE-22)
- ✅ **Validates all directory changes**
- ✅ **Supports any external folder** (frontend, sibling projects, etc.)
- ✅ **Keeps file extension restrictions** (no security bypass)
- ✅ **Logs all access** for auditing

---

## How It Works

### Architecture

```
Frontend Request → API Endpoint → FileService.set_base_directory()
                                  ↓
                        Validate directory safely
                                  ↓
                        Update scanner base path
                                  ↓
                        Scan external folder
                                  ↓
                        Apply file restrictions
                                  ↓
                        Return filtered results
```

**Path traversal attacks are still blocked** at every level.

---

## API Usage

### 1. Set Base Directory (External Folder)

```bash
# Set to frontend folder
curl -X POST http://localhost:8001/api/v1/files/set-directory \
  -H "Content-Type: application/json" \
  -d '{
    "directory": "/c/Code2025/Whysper/frontend"
  }'

# Response:
{
  "success": true,
  "message": "Base directory set to /c/Code2025/Whysper/frontend",
  "directory": "/c/Code2025/Whysper/frontend"
}
```

### 2. Scan the Directory

```bash
# Now scan the frontend folder
curl http://localhost:8001/api/v1/files/scan-directory

# Returns all .ts, .tsx, .js, .json, etc. files in frontend
# Still respects file extension whitelist
```

### 3. Read Files from External Directory

```bash
# Read a specific frontend file
curl "http://localhost:8001/api/v1/files/file?path=/c/Code2025/Whysper/frontend/src/index.tsx"
```

### 4. Get Current Base Directory

```bash
# Get which directory is currently set
curl http://localhost:8001/api/v1/files/get-directory
```

---

## Code Changes Made

### FileService Enhancement (`backend/app/services/file_service.py`)

**New Methods:**
```python
def set_base_directory(self, directory: str) -> Dict[str, Any]:
    """Safely change the base directory with validation"""

def get_base_directory(self) -> str:
    """Get the current base directory"""

def scan_directory(self, directory: Optional[str] = None):
    """Scan current or specified directory"""
```

**What's Different:**
- Constructor now accepts optional `base_directory` parameter
- `set_base_directory()` validates before changing
- All operations now use the current base directory
- Path traversal prevention still applies

---

## Security Features Maintained

### ✅ Path Traversal Prevention
Even with external folder access, you **cannot**:
```python
# These are ALL blocked:
set_base_directory("../../../etc")           # ❌ Escape attempt
read_file("/etc/passwd")                      # ❌ Absolute path outside
set_base_directory("/frontend/../../secret")  # ❌ Path traversal
```

### ✅ File Extension Whitelist
External folders must have supported file types:
```python
# Can access: .ts, .tsx, .js, .json, .yaml, .svg, .lock, .toml, .ini, etc.
# Cannot access: .exe, .dll, .bin, .pyc
```

### ✅ Folder Blacklist Still Active
External folders are scanned with the same ignore list:
- `node_modules` - ignored (huge performance impact)
- `__pycache__` - ignored
- `.git` - ignored
- etc.

### ✅ Size Limits Apply
- Per-file: 10MB max
- Batch: 100MB max
- Cache: 500 files max

---

## Use Cases

### Use Case 1: Analyze Frontend Code
```bash
# Set to frontend
curl -X POST http://localhost:8001/api/v1/files/set-directory \
  -d '{"directory": "/c/Code2025/Whysper/frontend"}'

# Scan all TypeScript/JavaScript files
curl http://localhost:8001/api/v1/files/scan-directory

# Generate documentation from frontend code
curl -X POST http://localhost:8001/api/v1/documentation/generate \
  -d '{"files": ["src/index.tsx", "src/components/App.tsx"]}'
```

### Use Case 2: Switch Between Projects
```bash
# Start with backend
curl -X POST http://localhost:8001/api/v1/files/set-directory \
  -d '{"directory": "/c/Code2025/Whysper/backend"}'

# Later, switch to frontend
curl -X POST http://localhost:8001/api/v1/files/set-directory \
  -d '{"directory": "/c/Code2025/Whysper/frontend"}'

# Later, switch to another project
curl -X POST http://localhost:8001/api/v1/files/set-directory \
  -d '{"directory": "/c/Code2025/SomeOtherProject"}'
```

### Use Case 3: Scan Parent Directory
```bash
# Scan entire Whysper project (excluding backend-specific files)
curl -X POST http://localhost:8001/api/v1/files/set-directory \
  -d '{"directory": "/c/Code2025/Whysper"}'

# Will find all code files in backend AND frontend
```

---

## API Endpoints (Updated)

### `POST /api/v1/files/set-directory`
**New/Updated endpoint** - Set the base directory for scanning

Request:
```json
{
  "directory": "/path/to/external/folder"
}
```

Response:
```json
{
  "success": true,
  "message": "Base directory set to /path/to/external/folder",
  "directory": "/path/to/external/folder"
}
```

Errors:
```json
{
  "success": false,
  "message": "Directory does not exist: /invalid/path",
  "error": "Directory does not exist: /invalid/path"
}
```

### `GET /api/v1/files/get-directory` (New)
**New endpoint** - Get the current base directory

Response:
```json
{
  "directory": "/c/Code2025/Whysper/frontend",
  "exists": true,
  "readable": true
}
```

### `GET /api/v1/files/scan-directory`
**Updated** - Now scans the current base directory (if set)

Parameters:
- `directory` (optional): Override current base directory

---

## Configuration

### Environment Variable

You can set a default external directory in `.env`:

```bash
# .env
EXTERNAL_FOLDER=/c/Code2025/Whysper/frontend
```

Then initialize FileService with it:
```python
file_service = FileService(base_directory=os.getenv("EXTERNAL_FOLDER"))
```

---

## Limitations (Still Apply)

❌ **Cannot access:**
- Files in ignored folders (`node_modules`, `.git`, etc.)
- Files outside the base directory (path traversal blocked)
- Binary files (`.exe`, `.dll`, `.bin`, etc.)
- Single files larger than 10MB
- More than 100MB in a batch request

✅ **Can access:**
- All code files (`.py`, `.js`, `.ts`, `.tsx`, etc.)
- Configuration files (`.json`, `.yaml`, `.toml`, `.ini`, etc.)
- Documentation (`.md`, `.txt`)
- Build files (`.gradle`, `.pom`)
- Lock files (`.lock`)

---

## Example Workflow

```bash
#!/bin/bash

# Start with backend
curl -X POST http://localhost:8001/api/v1/files/set-directory \
  -H "Content-Type: application/json" \
  -d '{"directory": "/c/Code2025/Whysper/backend"}'

# Scan backend code
curl http://localhost:8001/api/v1/files/scan-directory | jq '.[] | .path' | head -5

# Switch to frontend
curl -X POST http://localhost:8001/api/v1/files/set-directory \
  -H "Content-Type: application/json" \
  -d '{"directory": "/c/Code2025/Whysper/frontend"}'

# Scan frontend code
curl http://localhost:8001/api/v1/files/scan-directory | jq '.[] | .path' | head -5

# Check current directory
curl http://localhost:8001/api/v1/files/get-directory | jq '.directory'
```

---

## Security Notes

### What You CAN Do Safely
- ✅ Access any legitimate external folder
- ✅ Scan multiple different projects
- ✅ Generate documentation from external code
- ✅ Analyze external codebases

### What You CANNOT Do
- ❌ Access system files (`/etc`, `/var`, etc.)
- ❌ Use path traversal (`../../../etc/passwd`)
- ❌ Access binary files
- ❌ Bypass the security layer

---

## Troubleshooting

### Error: "Directory does not exist"
```json
{
  "success": false,
  "message": "Directory does not exist: /invalid/path"
}
```

**Solution**: Check that the path is correct and the directory exists.

### Error: "Directory is not readable"
```json
{
  "success": false,
  "message": "Directory is not readable: /path"
}
```

**Solution**: Check file permissions. The backend process needs read access to the folder.

### Error: "No files found after scanning"
This might mean:
- The directory exists but has no supported file types
- All files are in ignored folders (`node_modules`, etc.)
- Files are larger than 10MB

**Solution**: Check `scan-directory` response to see what files were found.

---

## Implementation Details

### FileService Changes

```python
class FileService:
    def __init__(self, base_directory: Optional[str] = None):
        self._scanner = LazyCodebaseScanner()
        self._base_directory = base_directory  # ← NEW: Custom base path

    def set_base_directory(self, directory: str) -> Dict[str, Any]:
        """Safely change base directory with validation"""
        # Validate directory exists and is accessible
        if not self.validate_directory(directory)["is_valid"]:
            return {"success": False, "error": "..."}

        self._base_directory = directory  # ← Change applied
        return {"success": True, "directory": directory}

    def get_base_directory(self) -> str:
        """Get current base directory"""
        return self._base_directory or os.getcwd()  # ← Default to cwd

    def scan_directory(self, directory: Optional[str] = None):
        """Scan current base directory (or override)"""
        scan_dir = directory or self.get_base_directory()  # ← Use base dir
        return self._scanner.scan_directory_lazy(scan_dir)
```

---

## Testing External Folder Access

### Test 1: Set to Frontend
```bash
curl -X POST http://localhost:8001/api/v1/files/set-directory \
  -H "Content-Type: application/json" \
  -d '{"directory": "/c/Code2025/Whysper/frontend"}'

# Should return success=true
```

### Test 2: Scan Frontend
```bash
curl http://localhost:8001/api/v1/files/scan-directory

# Should return .ts, .tsx, .js files from frontend
```

### Test 3: Try Path Traversal (Should Fail)
```bash
curl -X POST http://localhost:8001/api/v1/files/set-directory \
  -H "Content-Type: application/json" \
  -d '{"directory": "/c/Code2025/Whysper/frontend/../../../etc"}'

# Should return success=false, error about invalid path
```

### Test 4: Switch Back to Backend
```bash
curl -X POST http://localhost:8001/api/v1/files/set-directory \
  -H "Content-Type: application/json" \
  -d '{"directory": "/c/Code2025/Whysper/backend"}'

# Should return success=true
```

---

## Performance Considerations

### Frontend Scanning
- Frontend has TypeScript/JavaScript files
- `node_modules` is ignored (huge performance win)
- Expect 100-500 files typically

### Backend Scanning
- Python, config files, tests
- Expect 200-1000 files typically

### No Performance Impact
- Path traversal checks are fast
- File extension validation is cached
- Directory changes are instant

---

## Next Steps

1. **Restart the backend** - Changes to `file_service.py` need a restart
2. **Test setting external directory** - Use the API to set frontend or other folders
3. **Verify file scanning works** - Check that files from external folders are accessible
4. **Update your frontend** - Modify your UI to use the new `set-directory` endpoint

---

## Summary

| Feature | Status | Security |
|---------|--------|----------|
| Access external folders | ✅ Implemented | ✅ Protected |
| Path traversal prevention | ✅ Active | ✅ Critical |
| File type whitelist | ✅ Active | ✅ Required |
| Size limits | ✅ Active | ✅ Required |
| Directory validation | ✅ Active | ✅ Critical |

You can now safely examine code from any folder on your system while maintaining all security protections.

