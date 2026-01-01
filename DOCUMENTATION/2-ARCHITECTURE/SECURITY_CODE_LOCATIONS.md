# Security Layer - Exact Code Locations

## Quick Reference Map

### 📍 File Extension Whitelist
**File**: `backend/common/lazy_file_scanner.py`
**Lines**: 84-112

```python
# Current state:
self.supported_extensions = [
    ".py", ".js", ".ts", ".tsx", ".java", ".cpp", ".c", ".h", ".cs",
    ".rb", ".php", ".go", ".rs", ".kt", ".scala", ".html", ".css",
    ".sql", ".yaml", ".yml", ".json", ".xml", ".md", ".txt", ".sh",
    ".bat", ".ps1",
]
```

**To Modify**: Add new extensions to this list, e.g., `.svg`, `.toml`

---

### 📍 Special Files Whitelist
**File**: `backend/common/lazy_file_scanner.py`
**Lines**: 113-122

```python
self.special_files = [
    ".env",
    ".gitignore",
    "requirements.txt",
    "package.json",
    "Dockerfile",
    "docker-compose.yml",
    "Makefile",
    "README.md",
]
```

**To Modify**: Add configuration files here

---

### 📍 Ignored Folders Blacklist
**File**: `backend/common/lazy_file_scanner.py`
**Lines**: 124-136

```python
# Load ignore folders from environment
load_dotenv()
ignore_folders_env = os.getenv(
    "IGNORE_FOLDERS",
    "venv,.venv,env,__pycache__,node_modules,dist,build,.git,"
    + ".mypy_cache,.claude,.github,.vscode,.idea,.roo,results,logs,"
    + ".tox,.nox,.pytest_cache,htmlcov,cover",
)
self.ignore_folders = set(
    folder.strip()
    for folder in ignore_folders_env.split(",")
    if folder.strip()
)
```

**To Modify**:
- Edit the default string, OR
- Set `IGNORE_FOLDERS` environment variable in `.env` file

**Example**: To remove `node_modules`, change default string to:
```python
"venv,.venv,env,__pycache__,dist,build,.git,"
+ ".mypy_cache,.claude,.github,.vscode,.idea,.roo,results,logs,"
+ ".tox,.nox,.pytest_cache,htmlcov,cover"
```

---

### 📍 Hardcoded Excludes
**File**: `backend/common/lazy_file_scanner.py`
**Line**: 156

```python
self.hardcoded_excludes = ["jink"]
```

**To Modify**: Add or remove specific folder names that should always be excluded

---

### 📍 Size Limits - Per File
**File**: `backend/common/lazy_file_scanner.py`
**Lines**: 56-57

```python
def __init__(
    self, cache_size: int = 100, max_file_size: int = 1024 * 1024  # 1MB limit
) -> None:
```

**Current**: 1 MB per file
**To Modify**: Change `1024 * 1024` to desired bytes (e.g., `10 * 1024 * 1024` for 10MB)

---

### 📍 Size Limits - Batch Total
**File**: `backend/common/lazy_file_scanner.py`
**Line**: 393

```python
def get_codebase_content_lazy(
    self, file_paths: List[str], max_total_size: int = 10 * 1024 * 1024
) -> str:
```

**Current**: 10 MB total for batch operations
**To Modify**: Change `10 * 1024 * 1024` to desired bytes

---

### 📍 LRU Cache Size
**File**: `backend/common/lazy_file_scanner.py`
**Lines**: 56-57 (in `__init__`)

```python
def __init__(
    self, cache_size: int = 100, max_file_size: int = 1024 * 1024
) -> None:
```

**Current**: 100 files max in memory
**To Modify**: Change `cache_size=100` to desired number

---

### 📍 Path Traversal Prevention (DO NOT MODIFY)
**File**: `backend/security_utils.py`
**Lines**: 184-222

```python
@staticmethod
def safe_path_resolve(base_directory: Union[str, Path], file_path: Union[str, Path]) -> Optional[str]:
    """
    Resolves a user-provided file path against a base directory (e.g., codebase root)
    and ensures the resulting path is contained within the base directory to prevent
    path traversal attacks (CWE-22).
    """
    try:
        base_path = Path(base_directory).resolve()

        # Combine base directory with the file path, then resolve
        if Path(file_path).is_absolute():
            full_path = Path(file_path).resolve()
        else:
            # For relative paths, combine with base directory first
            full_path = (base_path / file_path).resolve()

        # Check if the fully resolved path is a subpath of the base path
        if str(full_path).startswith(str(base_path) + os.sep):
            # Also verify the file actually exists
            if full_path.exists():
                return str(full_path)

        # Allow the base directory itself
        if full_path == base_path and full_path.is_file():
            return str(full_path)

        return None
    except Exception:
        return None
```

**⚠️ WARNING**: DO NOT MODIFY this function. It's critical for security.

---

### 📍 Scanner Validation in FileService
**File**: `backend/app/services/file_service.py`
**Lines**: 25-42

```python
def validate_directory(self, directory: str) -> Dict[str, Any]:
    """
    Validate if a given directory path is safe and accessible.

    Uses the internal scanner's logic to check for security vulnerabilities
    (e.g., path traversal) and accessibility.
    """
    is_valid, error_message = self._scanner.validate_directory(directory)
    return {
        "is_valid": is_valid,
        "error": error_message,
    }
```

**File**: `backend/app/services/file_service.py`
**Lines**: 44-52

```python
def scan_directory(self, directory: str) -> List[Dict[str, Any]]:
    """Return metadata for all supported files under a directory."""
    logger.info(f"Scanning directory: {directory}")
    files: List[Dict[str, Any]] = []
    for batch in self._scanner.scan_directory_lazy(directory):
        for info in batch:
            files.append(self._serialize_file_info(info, directory))
    logger.info(f"Scan complete for {directory}: {len(files)} files")
    return files
```

**To Modify**: Add custom validation logic here before calling the scanner

---

### 📍 Directory Validation Helper
**File**: `backend/common/lazy_file_scanner.py`
**Lines**: 559-573

```python
def validate_directory(self, directory: str) -> Tuple[bool, str]:
    """Validate directory (compatibility method)."""
    if not directory:
        return False, "No directory specified"

    if not os.path.exists(directory):
        return False, f"Directory does not exist: {directory}"

    if not os.path.isdir(directory):
        return False, f"Path is not a directory: {directory}"

    if not os.access(directory, os.R_OK):
        return False, f"Directory is not readable: {directory}"

    return True, ""
```

**To Modify**: Add additional checks here

---

### 📍 Directory Filtering Logic
**File**: `backend/common/lazy_file_scanner.py`
**Lines**: 584-587

```python
def _should_skip_directory(self, directory_path: str) -> bool:
    """Check if directory should be skipped based on ignore folders."""
    path_parts = set(Path(directory_path).parts)
    return bool(path_parts.intersection(self.ignore_folders))
```

**Used By**: Lines 247-250 during directory traversal

---

### 📍 File Extension Validation
**File**: `backend/common/lazy_file_scanner.py`
**Lines**: 589-594

```python
def _is_supported_file(self, filename: str) -> bool:
    """Check if file is supported."""
    return (
        any(filename.endswith(ext) for ext in self.supported_extensions)
        or filename in self.special_files
    )
```

**Used By**: Line 261 during file scanning

---

### 📍 Cached Results Check
**File**: `backend/common/lazy_file_scanner.py`
**Lines**: 216-233

```python
# Check if we have cached results that are still valid
cached_info = self._get_cached_directory_info(directory)
if cached_info:
    logger.info(
        "Using cached directory info",
        directory=directory,
        cached_files=len(cached_info),
    )
    # Yield cached results in batches
    batch_size = 50
    for i in range(0, len(cached_info), batch_size):
        batch = cached_info[i : i + batch_size]
        if progress_callback:
            progress_callback(i + len(batch), len(cached_info))
        logger.debug("Yielding cached batch", batch_size=len(batch))
        yield batch
    logger.info("Completed cached scan yield", directory=directory)
    return
```

**Note**: Cache is valid for 5 minutes (see line 604)

---

## All Restriction Points Summary

| Restriction | File | Lines | Type |
|-------------|------|-------|------|
| File extensions | `lazy_file_scanner.py` | 84-112 | Whitelist |
| Special files | `lazy_file_scanner.py` | 113-122 | Whitelist |
| Ignored folders | `lazy_file_scanner.py` | 124-136 | Blacklist |
| Hardcoded excludes | `lazy_file_scanner.py` | 156 | Blacklist |
| Max file size | `lazy_file_scanner.py` | 56-57 | Limit |
| Max batch size | `lazy_file_scanner.py` | 393 | Limit |
| Cache size | `lazy_file_scanner.py` | 56-57 | Limit |
| Path traversal | `security_utils.py` | 184-222 | Security |
| Cache validity | `lazy_file_scanner.py` | 604 | Time-based |

---

## How Access Flows Through the System

```
Frontend Request
        ↓
API Endpoint (e.g., /api/v1/files/file)
        ↓
FileService.read_file()
        ↓
FileService.validate_directory()
        ↓
LazyCodebaseScanner.validate_directory()  ← Check if dir exists
        ↓
LazyCodebaseScanner.get_file_content_lazy()
        ↓
_should_skip_directory()  ← Check ignore_folders
        ↓
_is_supported_file()  ← Check supported_extensions
        ↓
Check file size  ← Check max_file_size
        ↓
Read from cache or disk
        ↓
Cache file if < max_file_size  ← LRU eviction if cache full
        ↓
Return to frontend
```

---

## Environment Configuration

The system checks for `IGNORE_FOLDERS` environment variable:

**File**: `.env` (if it exists)

```bash
# Example .env
IGNORE_FOLDERS=venv,.venv,env,__pycache__,dist,build,.git,.tox,.nox
```

**Fallback**: Uses hardcoded defaults in `lazy_file_scanner.py` line 127 if `.env` not set

---

## Testing the Restrictions

**Test File**: `backend/tests/infrastructure/test_lazy_file_scanner.py`

Run with:
```bash
python -m pytest backend/tests/infrastructure/test_lazy_file_scanner.py -v
```

---

## Making Safe Modifications

### ✅ Safe Changes:
1. Add `.svg`, `.lock`, `.toml` to `supported_extensions` (lines 84-112)
2. Add config files to `special_files` (lines 113-122)
3. Increase `max_file_size` (line 57)
4. Increase `max_total_size` (line 393)
5. Increase `cache_size` (line 57)
6. Remove non-critical folders from `ignore_folders` (line 127)

### ⚠️ Risky Changes:
1. Removing path traversal checks
2. Removing all folder exclusions
3. Setting unlimited size limits
4. Disabling the security layer entirely

### ❌ Never Change:
1. `safe_path_resolve()` in `security_utils.py`
2. Path traversal validation logic
3. File access control fundamentals

---

## Rollback Instructions

If you make changes and want to revert:

```bash
# View current state
git diff backend/common/lazy_file_scanner.py

# Revert to previous version
git checkout backend/common/lazy_file_scanner.py
```

---

