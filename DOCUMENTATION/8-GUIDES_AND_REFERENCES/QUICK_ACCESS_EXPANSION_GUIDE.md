# Quick Access Expansion Guide

## TL;DR - The Security Layers

Your backend has **3 security layers** preventing code access:

1. **File Extension Whitelist** - Only `.py`, `.js`, `.ts`, `.json`, `.yaml`, `.md` etc.
2. **Folder Blacklist** - Ignores `node_modules`, `__pycache__`, `.git`, etc.
3. **Path Traversal Prevention** - Prevents `../` style attacks

---

## ⚡ 30-Second Fix: Extend Allowed File Types

Edit `backend/common/lazy_file_scanner.py`, lines 84-112:

```python
self.supported_extensions = [
    ".py", ".js", ".ts", ".tsx", ".java", ".cpp", ".c", ".h", ".cs",
    ".rb", ".php", ".go", ".rs", ".kt", ".scala", ".html", ".css",
    ".sql", ".yaml", ".yml", ".json", ".xml", ".md", ".txt", ".sh",
    ".bat", ".ps1",
    # ADD YOUR FILE TYPES HERE:
    ".svg",      # Diagrams
    ".lock",     # Dependency locks
    ".toml",     # Config
    ".gradle",   # Build files
]
```

Then restart the backend. Done!

---

## 🚀 2-Minute Fix: Increase Size Limits

Edit `backend/common/lazy_file_scanner.py`, line 56-57:

```python
def __init__(
    self,
    cache_size: int = 500,              # ← Changed from 100
    max_file_size: int = 10 * 1024 * 1024  # ← Changed from 1MB to 10MB
) -> None:
```

And line 393:
```python
def get_codebase_content_lazy(
    self, file_paths: List[str], max_total_size: int = 100 * 1024 * 1024  # ← Changed from 10MB to 100MB
) -> str:
```

Restart backend.

---

## 🔓 5-Minute Fix: Remove a Folder from Ignore List

Edit `backend/common/lazy_file_scanner.py`, line 127:

```python
# BEFORE:
ignore_folders_env = os.getenv(
    "IGNORE_FOLDERS",
    "venv,.venv,env,__pycache__,node_modules,dist,build,.git,"
    + ".mypy_cache,.claude,.github,.vscode,.idea,.roo,results,logs,"
    + ".tox,.nox,.pytest_cache,htmlcov,cover",
)

# AFTER (remove "node_modules,"):
ignore_folders_env = os.getenv(
    "IGNORE_FOLDERS",
    "venv,.venv,env,__pycache__,dist,build,.git,"
    + ".mypy_cache,.claude,.github,.vscode,.idea,.roo,results,logs,"
    + ".tox,.nox,.pytest_cache,htmlcov,cover",
)
```

Restart backend.

---

## 📋 The Security Layers Explained

### Layer 1: File Extension Whitelist
**File**: `backend/common/lazy_file_scanner.py`

**Current allowed extensions**:
```python
[".py", ".js", ".ts", ".tsx", ".java", ".cpp", ".c", ".h", ".cs",
 ".rb", ".php", ".go", ".rs", ".kt", ".scala", ".html", ".css",
 ".sql", ".yaml", ".yml", ".json", ".xml", ".md", ".txt", ".sh",
 ".bat", ".ps1"]
```

**Special files** (always included):
```python
[".env", ".gitignore", "requirements.txt", "package.json",
 "Dockerfile", "docker-compose.yml", "Makefile", "README.md"]
```

**Why this exists**: Prevents accidental access to binary files, images, or unreadable content.

---

### Layer 2: Folder Blacklist
**File**: `backend/common/lazy_file_scanner.py`

**Default ignored folders**:
```python
venv, .venv, env, __pycache__, node_modules, dist, build, .git,
.mypy_cache, .claude, .github, .vscode, .idea, .roo, results, logs,
.tox, .nox, .pytest_cache, htmlcov, cover
```

**Additional sources**:
- Reads `.gitignore` file automatically
- Hardcoded excludes: `["jink"]`

**Why this exists**: Reduces clutter, improves performance, avoids build artifacts.

---

### Layer 3: Path Traversal Prevention
**File**: `backend/security_utils.py`, method `safe_path_resolve()`

**What it does**:
```python
# Prevents attacks like:
read_file("../../../etc/passwd")      # ❌ Blocked
read_file("/etc/passwd")              # ❌ Blocked
read_file("../../node_modules/foo")   # ❌ Blocked
read_file("backend/app/main.py")      # ✅ Allowed
```

**Why this exists**: Fundamental security protection (CWE-22).

---

## 🧪 Test Your Changes

After modifying `lazy_file_scanner.py`:

```bash
cd /c/Code2025/Whysper

# Run the scanner tests
python -m pytest backend/tests/infrastructure/test_lazy_file_scanner.py -v

# Or test manually
python << 'EOF'
from backend.common.lazy_file_scanner import LazyCodebaseScanner
scanner = LazyCodebaseScanner()
files = list(scanner.scan_directory_lazy("backend"))
print(f"Found {len(files)} files")
# Check if your new extensions appear in the results
EOF
```

---

## ⚠️ Security Notes

### Safe to Modify:
- ✅ `supported_extensions` - Adding more code file types
- ✅ `cache_size` - Increasing memory cache
- ✅ `max_file_size` / `max_total_size` - Increasing limits
- ✅ `special_files` - Adding config files
- ✅ Removing non-critical folders from `ignore_folders`

### NOT Recommended to Modify:
- ❌ Removing path traversal checks in `SecurityUtils`
- ❌ Removing all folder exclusions
- ❌ Trying to work around restrictions in FileService
- ❌ Disabling security checks in LazyCodebaseScanner

### Sensitive Data Risk:
⚠️ If you add `.env` processing (it's already in `special_files`):
- These files contain API keys and secrets
- Consider using `SecurityUtils.mask_sensitive_string()` when returning

---

## 🔍 Finding the Code

All restrictions are in 3 files:

| File | Purpose | Edit For |
|------|---------|----------|
| `backend/common/lazy_file_scanner.py` | Core scanner | Extensions, limits, folders |
| `backend/app/services/file_service.py` | File access wrapper | Add custom validation |
| `backend/security_utils.py` | Path traversal protection | DO NOT MODIFY |

---

## 📞 Common Questions

**Q: Why can't I access `node_modules`?**
A: It's in the ignore list (line 127). Remove it from the environment variable.

**Q: Why can't I read `.png` files?**
A: Only whitelisted extensions are allowed. Add `.png` to `supported_extensions`.

**Q: Can I read files outside the backend folder?**
A: No - the `safe_path_resolve()` function prevents path traversal attacks.

**Q: What's the hardcoded "jink" exclusion?**
A: Unclear purpose. It's on line 156 of `lazy_file_scanner.py`.

**Q: Can the frontend access all the backend code?**
A: No - it goes through the FileService which applies these restrictions.

---

## 🎯 Common Scenarios

### Scenario 1: "I need to read package-lock.json"
1. Edit `backend/common/lazy_file_scanner.py`, line 127
2. Remove `"node_modules"` from ignore list (since package-lock.json is in root)
3. Restart backend
4. File is now accessible

### Scenario 2: "I need to read all config files (*.toml, *.ini)"
1. Edit `backend/common/lazy_file_scanner.py`, line 95
2. Add `.toml` and `.ini` to `supported_extensions`
3. Restart backend
4. All .toml and .ini files are now scanned

### Scenario 3: "I need access to node_modules code"
⚠️ **Not recommended** - causes performance issues and clutter
But if necessary:
1. Edit line 127, remove `"node_modules"`
2. Be prepared for 10x more files in results
3. Consider using size limits to stay under 100MB

### Scenario 4: "I need to read large files (>1MB)"
1. Edit line 57, change `max_file_size` to desired size
2. Edit line 393, change `max_total_size` to desired size
3. Restart backend
4. Larger files are now cached and accessible

---

## 📊 Performance Impact

| Change | Impact |
|--------|--------|
| Add file extension | ⭐ Minimal |
| Remove ignored folder | ⭐⭐⭐ High (can 10x file count) |
| Increase size limits | ⭐⭐ Medium (more memory) |
| Remove path traversal check | 💥 BREAKS SECURITY - Don't do it |

---

## 🔐 Before & After

### Before Modification
```
Supported: .py, .js, .ts, .json, .yaml, .md, etc.
Ignored: node_modules, __pycache__, .git, etc.
Size Limit: 1MB per file, 10MB total
Max Cache: 100 files in memory
```

### After Common Modifications
```
Supported: .py, .js, .ts, .json, .yaml, .md, .svg, .lock, .toml, etc.
Ignored: __pycache__, .git (removed node_modules)
Size Limit: 10MB per file, 100MB total
Max Cache: 500 files in memory
```

---

## Next Steps

1. Review `SECURITY_LAYER_ANALYSIS.md` for detailed explanation
2. Identify which restrictions to relax
3. Make changes to `lazy_file_scanner.py`
4. Test with `pytest backend/tests/`
5. Restart the backend server
6. Verify access works with your frontend/tools

