# Security Layer Analysis - Backend Code Access Restrictions

## Executive Summary

The backend implements **multiple layers of security restrictions** that limit tool access to the root of the backend directory. These restrictions are intentional and security-focused, preventing path traversal attacks and unauthorized access to sensitive files.

---

## Current Security Restrictions

### 1. **LazyCodebaseScanner** (`backend/common/lazy_file_scanner.py`)
The primary security layer that controls file access.

#### Supported File Extensions (Whitelist Approach)
Only the following file types are accessible:
```
.py, .js, .ts, .tsx, .java, .cpp, .c, .h, .cs, .rb, .php, .go, .rs, .kt, .scala,
.html, .css, .sql, .yaml, .yml, .json, .xml, .md, .txt, .sh, .bat, .ps1
```

**Impact**: Binary files, images, and non-code files are excluded.

#### Special Files (Explicitly Allowed)
```
.env, .gitignore, requirements.txt, package.json, Dockerfile,
docker-compose.yml, Makefile, README.md
```

**Impact**: Configuration files like `.env` are explicitly allowlisted but others are excluded.

#### Ignored Folders (Blacklist Approach)
The scanner automatically ignores:
```
venv, .venv, env, __pycache__, node_modules, dist, build, .git,
.mypy_cache, .claude, .github, .vscode, .idea, .roo, results, logs,
.tox, .nox, .pytest_cache, htmlcov, cover
```

Additionally:
- Reads from `.gitignore` file to exclude version-control-ignored directories
- **Hardcoded excludes**: `["jink"]` (line 156)

**Impact**: Dependency folders, build artifacts, and IDE settings are completely inaccessible.

#### Size Limits
```python
max_file_size: int = 1024 * 1024  # 1MB per file
max_total_size: int = 10 * 1024 * 1024  # 10MB total
```

**Impact**: Large files are automatically skipped during batch operations.

#### LRU Cache
```python
cache_size: int = 100  # Maximum cached files in memory
```

**Impact**: Memory usage is controlled by limiting concurrent file caching.

---

### 2. **SecurityUtils** (`backend/security_utils.py`)
Provides additional security validation with the `safe_path_resolve()` method (lines 184-222).

#### Path Traversal Prevention
The `safe_path_resolve()` function ensures:

1. **Base Path Containment Check**:
   ```python
   if str(full_path).startswith(str(base_path) + os.sep):
       # Path is within base directory - allowed
   ```

2. **Absolute Path Handling**: Converts all paths to absolute, then checks containment
3. **File Existence Verification**: Only returns paths for files that actually exist
4. **None Return on Violation**: Returns `None` if path attempts to escape the base directory

**Protection**: Prevents `../../../etc/passwd` style attacks

---

### 3. **FileService** (`backend/app/services/file_service.py`)
Wraps the LazyCodebaseScanner and delegates validation to it.

#### Key Methods:
- `validate_directory()` (line 25): Checks if directory is valid and accessible
- `scan_directory()` (line 44): Uses LazyCodebaseScanner, applies whitelist
- `build_directory_tree()` (line 54): Returns nested tree structure (filtered)
- `read_file()` (line 87): Delegates to scanner's validation
- `read_files()` (line 90): Batch operation with size limits

**All file access** flows through these methods, enforcing restrictions.

---

## How the Security Layers Work Together

```
┌─────────────────────────────────────────────────────────┐
│ FastAPI Endpoint (e.g., /api/v1/files/file)            │
└──────────────────┬──────────────────────────────────────┘
                   │
┌──────────────────▼──────────────────────────────────────┐
│ FileService                                             │
│ - validate_directory()                                  │
│ - scan_directory()                                      │
│ - read_file()                                           │
└──────────────────┬──────────────────────────────────────┘
                   │
┌──────────────────▼──────────────────────────────────────┐
│ LazyCodebaseScanner                                     │
│ - Whitelist: supported_extensions                       │
│ - Whitelist: special_files                              │
│ - Blacklist: ignore_folders + .gitignore               │
│ - Size limits: 1MB per file, 10MB total                │
│ - LRU caching: max 100 files                            │
└──────────────────┬──────────────────────────────────────┘
                   │
┌──────────────────▼──────────────────────────────────────┐
│ SecurityUtils.safe_path_resolve()                       │
│ - Path traversal prevention (CWE-22)                    │
│ - Base directory containment check                      │
│ - File existence verification                           │
└──────────────────┬──────────────────────────────────────┘
                   │
                   ▼
            File System Access
```

---

## Current Limitations

### ❌ Cannot Access:
- Binary files (`.exe`, `.dll`, `.so`, `.bin`)
- Image files (`.png`, `.jpg`, `.gif`, `.svg`)
- Archive files (`.zip`, `.tar`, `.gz`)
- Lock files (`package-lock.json` is listed but may be filtered)
- Any file in ignored folders
- Files larger than 1MB individually
- More than 10MB of total content in a batch request
- Files outside the specified base directory (path traversal prevention)

### ✅ Can Access:
- Python source code (`.py`)
- JavaScript/TypeScript (`.js`, `.ts`, `.tsx`)
- Configuration files (`.json`, `.yaml`, `.yml`, `.env`)
- Documentation (`.md`, `.txt`)
- Database/Query files (`.sql`)
- Shell scripts (`.sh`, `.bat`, `.ps1`)

---

## Recommendations to Expand Access

### Option 1: Extend Supported Extensions (Low Security Impact)
**File**: `backend/common/lazy_file_scanner.py`, lines 84-112

Add more file types to the whitelist:
```python
self.supported_extensions = [
    # ... existing ...
    ".svg",      # SVG diagrams
    ".lock",     # Dependency locks
    ".toml",     # Configuration files
    ".ini",      # Config files
    ".gradle",   # Build files
    ".pom",      # Maven
]
```

**Security Consideration**: Only add file types that won't expose sensitive data or binary content.

---

### Option 2: Add Conditional Access Rules (Medium Security Impact)
**Modify**: `backend/app/services/file_service.py`

Create a new method that allows expanding access for specific use cases:

```python
def read_file_with_validation(
    self,
    file_path: str,
    allow_large_files: bool = False,
    allow_binary: bool = False
) -> str:
    """
    Read file with conditional validation rules.

    Args:
        file_path: Path to the file
        allow_large_files: Allow files > 1MB (default: False)
        allow_binary: Allow non-text files (default: False)

    Returns:
        File content or error message
    """
    # Implementation with flexible validation
```

**Security Consideration**: Requires explicit opt-in per read operation and proper authorization checks.

---

### Option 3: Remove Folder Exclusions Selectively (Medium-High Security Impact)
**File**: `backend/common/lazy_file_scanner.py`, line 127-136

Currently hardcoded ignored folders. Consider making this configurable:

```python
# BEFORE: Hardcoded list
ignore_folders_env = os.getenv(
    "IGNORE_FOLDERS",
    "venv,.venv,env,__pycache__,node_modules,dist,build,.git,"
    + ".mypy_cache,.claude,.github,.vscode,.idea,.roo,results,logs,"
    + ".tox,.nox,.pytest_cache,htmlcov,cover",
)

# AFTER: Configurable with safe defaults
default_ignore = "venv,.venv,env,__pycache__,node_modules,dist,build,.git,.tox,.nox"
override_ignore = os.getenv("OVERRIDE_IGNORE_FOLDERS", "")
ignore_folders_env = override_ignore if override_ignore else default_ignore
```

**Security Consideration**: Removing folder exclusions exposes dependency code and build artifacts. Only do this if the tool user is trusted.

---

### Option 4: Increase Size Limits (Low Security Impact)
**File**: `backend/common/lazy_file_scanner.py`, line 56-57

```python
def __init__(
    self,
    cache_size: int = 500,              # Increase from 100
    max_file_size: int = 10 * 1024 * 1024  # 10MB per file (from 1MB)
) -> None:
```

Also modify:
```python
max_total_size: int = 100 * 1024 * 1024  # 100MB total (from 10MB)
```

**Security Consideration**: Only impacts memory usage and processing time. No data exposure risk.

---

### Option 5: Implement Granular Permission Model (High Security, Complex)
**Create**: `backend/app/core/access_control.py`

```python
from enum import Enum
from typing import Set

class FileAccessLevel(Enum):
    RESTRICTED = 1      # Only code files, supported extensions
    STANDARD = 2        # Code + config files
    EXTENDED = 3        # Code + config + build artifacts
    UNRESTRICTED = 4    # Everything (not recommended)

class AccessControlManager:
    def __init__(self, access_level: FileAccessLevel):
        self.access_level = access_level
        self.allowed_extensions = self._get_allowed_extensions()
        self.allowed_folders = self._get_allowed_folders()

    def _get_allowed_extensions(self) -> Set[str]:
        if self.access_level == FileAccessLevel.RESTRICTED:
            return {".py", ".js", ".ts", ".tsx", ".java"}
        elif self.access_level == FileAccessLevel.STANDARD:
            return {
                ".py", ".js", ".ts", ".tsx", ".java", ".cpp",
                ".json", ".yaml", ".yml", ".env", ".md"
            }
        # ... etc
```

**Security Consideration**: Allows fine-grained control per user/request. Most secure option for expansion.

---

## Recommended Implementation Path

### For Immediate Access Expansion:
1. **Option 1 + Option 4**: Extend supported file types and increase size limits
   - Minimal security impact
   - Easy to implement
   - Solves most access issues

### For Controlled Access:
2. **Option 5**: Implement granular permission model
   - Best balance of security and flexibility
   - Allows different tools to have different access levels
   - Future-proof

### For Full Access (Not Recommended):
3. Remove all restrictions in FileService/LazyCodebaseScanner
   - Opens up to path traversal attacks
   - Exposes sensitive configuration files
   - Could leak API keys and credentials

---

## Security Concerns to Address

### ⚠️ Critical Issues
None identified in current implementation. The security layer is well-designed.

### ⚠️ Medium Issues
1. **Hardcoded "jink" Exclusion** (line 156 of lazy_file_scanner.py)
   - Purpose unclear - consider documenting or removing

2. **.env Files Are Accessible** (special_files, line 114)
   - Configuration files with secrets can be read
   - Mitigation: Use SecurityUtils.mask_sensitive_string() when returning

3. **No Request-Level Rate Limiting**
   - Large batch requests could impact server performance
   - Recommendation: Add rate limiting at FastAPI level

### ⚠️ Low Issues
1. **Cache Not Invalidated on File Modification**
   - Files modified externally won't update cache until 5 minutes pass
   - Mitigation: Already implemented (line 604)

---

## Testing the Security Layer

### Test Path Traversal Prevention:
```python
# These should all return None or error
safe_path_resolve("/app/backend", "../../../etc/passwd")
safe_path_resolve("/app/backend", "/../../../etc/passwd")
safe_path_resolve("/app/backend", "/etc/passwd")
```

### Test Whitelist:
```python
# .py file should be accessible
scan_directory_lazy("/app/backend")  # Returns .py files
# But .exe files should NOT be in results
```

### Test Ignore Folders:
```python
# Files in __pycache__ should not appear
files = scan_directory_lazy("/app/backend")
assert not any("__pycache__" in f.path for f in files)
```

---

## Implementation Checklist for Expansion

- [ ] Decide which restrictions to relax based on use case
- [ ] Update `supported_extensions` list in LazyCodebaseScanner
- [ ] Update `special_files` list if needed
- [ ] Consider updating `ignore_folders` environment variable
- [ ] Increase `max_file_size` and `max_total_size` if needed
- [ ] Add security logging for expanded access attempts
- [ ] Update API documentation to reflect new capabilities
- [ ] Add unit tests for new access patterns
- [ ] Review for sensitive data exposure (`.env`, keys, etc.)
- [ ] Perform security audit after changes
- [ ] Document the rationale for any restrictions removed

---

## Files Modified for These Changes

1. `backend/common/lazy_file_scanner.py` - Core scanner logic
2. `backend/app/services/file_service.py` - Service layer wrapper
3. `backend/app/core/config.py` - Configuration management (if adding env vars)
4. `backend/app/api/v1/endpoints/files.py` - API endpoints (documentation update)
5. `.env` or `.env.example` - New configuration options (if needed)

---

## Related Files for Reference

- [SecurityUtils](backend/security_utils.py) - Path traversal prevention
- [FileService](backend/app/services/file_service.py) - File access wrapper
- [LazyCodebaseScanner](backend/common/lazy_file_scanner.py) - Core restrictions
- [MCP Router](backend/app/routers/MCP.py) - Tool integration layer

