# Quick Start: External Folder Access

## 30-Second Start

### 1. Restart Backend
```bash
# Kill and restart the backend server
# Python file changes require a restart
```

### 2. Set to Frontend Folder
```bash
curl -X POST http://localhost:8001/api/v1/files/set-directory \
  -H "Content-Type: application/json" \
  -d '{"directory": "/c/Code2025/Whysper/frontend"}'
```

### 3. Scan Frontend
```bash
curl http://localhost:8001/api/v1/files/scan-directory
```

**Done!** You now have access to the frontend code.

---

## Common Commands

### Switch to Backend
```bash
curl -X POST http://localhost:8001/api/v1/files/set-directory \
  -d '{"directory": "/c/Code2025/Whysper/backend"}'
```

### Switch to Another Project
```bash
curl -X POST http://localhost:8001/api/v1/files/set-directory \
  -d '{"directory": "/path/to/another/project"}'
```

### Get Current Folder
```bash
curl http://localhost:8001/api/v1/files/get-directory
```

### Read a Specific File
```bash
curl "http://localhost:8001/api/v1/files/file?path=/c/Code2025/Whysper/frontend/src/index.tsx"
```

---

## What Changed

| What | Before | After |
|------|--------|-------|
| Max file size | 1 MB | **10 MB** |
| Batch size | 10 MB | **100 MB** |
| File types | 21 types | **28 types** (added .svg, .lock, .toml, etc.) |
| External access | ❌ No | ✅ **Yes** |
| Security | ✅ Protected | ✅ **Still Protected** |

---

## API Endpoint

### `POST /api/v1/files/set-directory`

**Request:**
```json
{
  "directory": "/path/to/folder"
}
```

**Success Response:**
```json
{
  "success": true,
  "message": "Base directory set to /path/to/folder",
  "directory": "/path/to/folder"
}
```

**Error Response:**
```json
{
  "success": false,
  "message": "Directory does not exist: /invalid/path",
  "error": "Directory does not exist: /invalid/path"
}
```

---

## Security

### ✅ Still Protected

- Path traversal (`../../../etc/passwd`) → BLOCKED
- Binary files (`.exe`, `.dll`) → BLOCKED
- System files (`/etc`, `/var`) → BLOCKED
- Ignored folders (`node_modules`, `.git`) → BLOCKED
- Large files (>10MB) → BLOCKED
- Large batches (>100MB) → BLOCKED

### ✅ What Changed

- Can now access external folders ✅
- Can now read larger files (10MB) ✅
- Can now process larger batches (100MB) ✅
- Can now read new file types ✅

---

## Examples

### Example 1: Analyze Frontend Code
```bash
# Set to frontend
curl -X POST http://localhost:8001/api/v1/files/set-directory \
  -d '{"directory": "/c/Code2025/Whysper/frontend"}'

# List all files
curl http://localhost:8001/api/v1/files/scan-directory

# Get tree structure
curl http://localhost:8001/api/v1/files/scan-directory
```

### Example 2: Generate Documentation
```bash
# Set to backend
curl -X POST http://localhost:8001/api/v1/files/set-directory \
  -d '{"directory": "/c/Code2025/Whysper/backend"}'

# Generate docs
curl -X POST http://localhost:8001/api/v1/documentation/generate \
  -d '{"files": ["app/main.py", "app/services/file_service.py"]}'
```

### Example 3: Compare Frontend vs Backend
```bash
# Scan frontend
curl -X POST http://localhost:8001/api/v1/files/set-directory \
  -d '{"directory": "/c/Code2025/Whysper/frontend"}'
curl http://localhost:8001/api/v1/files/scan-directory > frontend_files.json

# Scan backend
curl -X POST http://localhost:8001/api/v1/files/set-directory \
  -d '{"directory": "/c/Code2025/Whysper/backend"}'
curl http://localhost:8001/api/v1/files/scan-directory > backend_files.json
```

---

## Testing

### Test That Path Traversal is Still Blocked
```bash
# This should FAIL
curl -X POST http://localhost:8001/api/v1/files/set-directory \
  -d '{"directory": "/c/Code2025/Whysper/../../../etc"}'

# Expected: success: false
```

### Test That Frontend Works
```bash
# This should SUCCEED
curl -X POST http://localhost:8001/api/v1/files/set-directory \
  -d '{"directory": "/c/Code2025/Whysper/frontend"}'

# Expected: success: true
```

---

## Files Changed

1. **backend/app/services/file_service.py**
   - Added `set_base_directory()` method
   - Added `get_base_directory()` method

2. **backend/common/lazy_file_scanner.py**
   - Added 7 file types
   - Increased size limits
   - Removed "results" and "logs" from ignore list

---

## Troubleshooting

### Error: "Directory does not exist"
- Check that the path is correct
- Make sure the directory exists
- Use absolute paths (e.g., `/c/Code2025/...`)

### Error: "Directory is not readable"
- Check file permissions
- Make sure the backend has read access
- Try a different directory

### No files found
- Make sure the folder has supported file types (.ts, .js, .json, etc.)
- Check if files are in ignored folders (`node_modules`, `.git`, etc.)
- Try scanning the root folder first

---

## Next Steps

1. **Restart backend**
2. **Test setting external folder** (see commands above)
3. **Update your frontend** (optional) to use the new endpoint
4. **Read full documentation** if you need more details

---

## More Info

- Full guide: `EXTERNAL_FOLDER_ACCESS.md`
- Security details: `SECURITY_LAYER_SUMMARY.md`
- Implementation details: `CHANGES_SUMMARY.md`

**That's it! You're ready to access external folders safely.**

