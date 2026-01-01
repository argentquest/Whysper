# Security Layer Cheat Sheet

## The 3 Layers (Visual)

```
Layer 3: Path Traversal Prevention
┌─────────────────────────────────────────┐
│ Blocks: ../, absolute paths, etc/passwd │
│ Effect: Can't escape base directory     │
│ Risk:   CRITICAL if disabled            │
└─────────────────────────────────────────┘
                    ↑
Layer 2: Folder Blacklist
┌─────────────────────────────────────────┐
│ Blocks: node_modules, __pycache__, .git │
│ Effect: Fewer files to scan, faster     │
│ Risk:   Medium (can remove some)        │
└─────────────────────────────────────────┘
                    ↑
Layer 1: File Extension Whitelist
┌─────────────────────────────────────────┐
│ Allows: .py, .js, .json, .yaml, etc     │
│ Effect: Only readable code files        │
│ Risk:   Low (can add extensions)        │
└─────────────────────────────────────────┘
```

---

## One-Line Fixes

### Add File Type (30 seconds)
```bash
# Edit line 95 of backend/common/lazy_file_scanner.py
# Change this:
self.supported_extensions = [".py", ".js", ".ts", ...]
# To this:
self.supported_extensions = [".py", ".js", ".ts", ".svg", ".lock", ".toml", ...]
```

### Increase Size Limit (30 seconds)
```bash
# Edit line 57 of backend/common/lazy_file_scanner.py
# Change this:
max_file_size: int = 1024 * 1024  # 1MB
# To this:
max_file_size: int = 10 * 1024 * 1024  # 10MB
```

### Remove Ignored Folder (1 minute)
```bash
# Edit line 127 of backend/common/lazy_file_scanner.py
# Change this (remove "node_modules,"):
"venv,.venv,env,__pycache__,node_modules,dist,build,.git,..."
# To this:
"venv,.venv,env,__pycache__,dist,build,.git,..."
```

### Via Environment Variable (2 minutes)
```bash
# Add to .env file:
IGNORE_FOLDERS=venv,.venv,env,__pycache__,dist,build,.git,.tox,.nox
```

---

## File Permission Matrix

| File Type | Allowed? | How to Allow |
|-----------|----------|-------------|
| `.py` | ✅ Yes | Already in whitelist |
| `.js` | ✅ Yes | Already in whitelist |
| `.json` | ✅ Yes | Already in whitelist |
| `.yaml` | ✅ Yes | Already in whitelist |
| `.svg` | ❌ No | Add to line 95 |
| `.lock` | ❌ No | Add to line 95 |
| `.png` | ❌ No | Don't add (binary) |
| `.exe` | ❌ No | Don't add (binary) |
| `.env` | ✅ Yes | Already in line 114 |
| `.git/*` | ❌ No | In ignore list, line 127 |
| `node_modules/*` | ❌ No | In ignore list, line 127 |

---

## Folder Permission Matrix

| Folder | Currently Ignored? | Safe to Allow? | Why |
|--------|-------------------|----------------|-----|
| `node_modules` | ✅ Yes | ⚠️ Maybe | Huge, kills performance |
| `__pycache__` | ✅ Yes | ❌ No | Useless bytecode |
| `.git` | ✅ Yes | ❌ No | Expose version history |
| `results` | ✅ Yes | ✅ Yes | Usually generated output |
| `logs` | ✅ Yes | ✅ Yes | Usually generated output |
| `dist` | ✅ Yes | ⚠️ Maybe | Build output, can be large |
| `build` | ✅ Yes | ⚠️ Maybe | Build output, can be large |

---

## Size Limits Reference

| Limit | Current | Common Expansion |
|-------|---------|------------------|
| Single file | 1 MB | 10-50 MB |
| Batch total | 10 MB | 50-100 MB |
| Cached files | 100 | 500-1000 |

**Edit locations**: Lines 57, 393 in `lazy_file_scanner.py`

---

## Risk Scale (1-5, 5 = Most Risk)

```
Add extensions:           ⭐     (very safe)
Increase sizes:           ⭐⭐    (safe)
Remove non-critical dirs: ⭐⭐⭐  (medium risk)
Remove critical dirs:     ⭐⭐⭐⭐ (high risk)
Disable path checks:      ⭐⭐⭐⭐⭐ (NEVER DO THIS)
```

---

## The 3 Most Useful Edits

### Edit 1: File Extensions (Line 95)
```python
# BEFORE:
self.supported_extensions = [
    ".py", ".js", ".ts", ".tsx", ".java", ".cpp", ".c", ".h", ".cs",
    ".rb", ".php", ".go", ".rs", ".kt", ".scala", ".html", ".css",
    ".sql", ".yaml", ".yml", ".json", ".xml", ".md", ".txt", ".sh",
    ".bat", ".ps1",
]

# AFTER (add these):
self.supported_extensions = [
    ".py", ".js", ".ts", ".tsx", ".java", ".cpp", ".c", ".h", ".cs",
    ".rb", ".php", ".go", ".rs", ".kt", ".scala", ".html", ".css",
    ".sql", ".yaml", ".yml", ".json", ".xml", ".md", ".txt", ".sh",
    ".bat", ".ps1", ".svg", ".lock", ".toml", ".ini",  # ← ADDED
]
```

### Edit 2: Max File Size (Line 57)
```python
# BEFORE:
def __init__(self, cache_size: int = 100, max_file_size: int = 1024 * 1024) -> None:

# AFTER:
def __init__(self, cache_size: int = 500, max_file_size: int = 10 * 1024 * 1024) -> None:
#                                 ↑ also increase cache            ↑ 10MB instead of 1MB
```

### Edit 3: Batch Size (Line 393)
```python
# BEFORE:
def get_codebase_content_lazy(self, file_paths: List[str], max_total_size: int = 10 * 1024 * 1024) -> str:

# AFTER:
def get_codebase_content_lazy(self, file_paths: List[str], max_total_size: int = 100 * 1024 * 1024) -> str:
#                                                                                 ↑ 100MB instead of 10MB
```

---

## Undo/Rollback

```bash
# See what changed:
git diff backend/common/lazy_file_scanner.py

# Revert all changes:
git checkout backend/common/lazy_file_scanner.py

# Revert to specific commit:
git log --oneline backend/common/lazy_file_scanner.py
git checkout <commit-hash> -- backend/common/lazy_file_scanner.py
```

---

## Test Your Changes

```bash
# Run tests:
cd /c/Code2025/Whysper
python -m pytest backend/tests/infrastructure/test_lazy_file_scanner.py -v

# Quick check (bash):
python << 'EOF'
from backend.common.lazy_file_scanner import LazyCodebaseScanner
scanner = LazyCodebaseScanner()
files = list(scanner.scan_directory_lazy("backend"))
print(f"Found {len(files)} files")
print(f"Extensions: {set(f.extension for f in files)}")
EOF
```

---

## Environment Variables

Add to `.env` file in project root:

```bash
# Override ignored folders
IGNORE_FOLDERS=venv,.venv,env,__pycache__,dist,build,.git,.tox,.nox

# (Other related env vars, if they exist)
CODE_PATH=/path/to/codebase
UPLOAD_PATH=/path/to/uploads
```

---

## Common Scenarios (Copy-Paste)

### "I need to read SVG files"
**File**: `backend/common/lazy_file_scanner.py`, line 95
```python
# Add ".svg" to the list
```

### "I need to read Lock files (package-lock.json, poetry.lock, etc)"
**File**: `backend/common/lazy_file_scanner.py`, line 95
```python
# Add ".lock" to the list
```

### "I need to read Config files (TOML, INI, etc)"
**File**: `backend/common/lazy_file_scanner.py`, line 95
```python
# Add ".toml" and ".ini" to the list
```

### "Files larger than 1MB aren't working"
**File**: `backend/common/lazy_file_scanner.py`, line 57
```python
# Change: max_file_size: int = 1024 * 1024  # 1MB
# To:     max_file_size: int = 10 * 1024 * 1024  # 10MB
```

### "Batch operations fail with large projects"
**File**: `backend/common/lazy_file_scanner.py`, line 393
```python
# Change: max_total_size: int = 10 * 1024 * 1024  # 10MB
# To:     max_total_size: int = 100 * 1024 * 1024  # 100MB
```

### "Too many files in cache"
**File**: `backend/common/lazy_file_scanner.py`, line 57
```python
# Change: cache_size: int = 100
# To:     cache_size: int = 500
```

---

## DO NOT Change These

❌ **Line 184-222** in `security_utils.py` (path traversal prevention)
❌ **Any security validation** in `FileService`
❌ **Directory access checks** in `_is_directory_valid`
❌ **Path resolution** in `safe_path_resolve`

These are critical security functions. If you need to bypass them, you've designed your system wrong.

---

## When to Refer to Full Docs

| Question | Document |
|----------|----------|
| "How do I fix this?" | `QUICK_ACCESS_EXPANSION_GUIDE.md` |
| "Why does this exist?" | `SECURITY_LAYER_ANALYSIS.md` |
| "Where exactly is this?" | `SECURITY_CODE_LOCATIONS.md` |
| "What's the overview?" | `SECURITY_LAYER_SUMMARY.md` |
| "Quick reference" | `CHEAT_SHEET.md` (this file) |

---

## TL;DR for Busy People

**Your backend has 3 security layers blocking file access:**

1. **Extension whitelist** (line 95) - Only code files allowed
2. **Folder blacklist** (line 127) - Dependencies/builds ignored
3. **Path traversal prevention** (security_utils.py) - Can't escape base dir

**To expand access:**
- Add extensions to line 95 (safe)
- Increase sizes on lines 57, 393 (safe)
- Remove folders from line 127 (risky for performance)
- Never touch security_utils.py (DANGER)

**One change = One restart = Done**

---

## File Reference (For Ctrl+G in IDE)

```
lazy_file_scanner.py:95     - Supported extensions
lazy_file_scanner.py:114    - Special files
lazy_file_scanner.py:127    - Ignored folders
lazy_file_scanner.py:156    - Hardcoded excludes
lazy_file_scanner.py:57     - Max file size & cache size
lazy_file_scanner.py:393    - Max batch size
security_utils.py:184-222   - Path traversal prevention (DO NOT EDIT)
file_service.py:25-42       - Validation wrapper
file_service.py:44-52       - Scanner wrapper
```

---

## Last Resort: Full Bypass

⚠️ **NOT RECOMMENDED** - Only if you understand the risks:

```python
# In lazy_file_scanner.py, modify:

def _is_supported_file(self, filename: str) -> bool:
    # BEFORE: Check whitelist
    return any(filename.endswith(ext) for ext in self.supported_extensions)

    # AFTER: Allow everything
    return True  # ⚠️ ENABLES ALL FILES
```

This opens you to:
- Binary file parsing errors
- Massive performance issues
- Memory exhaustion
- No buffer overflow protection

**Don't do this.** Use the granular approach instead.

---

**Last Updated**: 2025-11-05
**Security Level**: Production-Ready
**Audit Status**: ✅ Complete

