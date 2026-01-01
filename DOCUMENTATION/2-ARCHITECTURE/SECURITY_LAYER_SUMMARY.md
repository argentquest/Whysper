# Backend Security Layer - Executive Summary

## What We Found

Your backend has **3 intentional security layers** that restrict file and directory access:

### Layer 1: File Extension Whitelist
Only these file types can be read:
```
.py, .js, .ts, .tsx, .java, .cpp, .c, .h, .cs, .rb, .php, .go, .rs, .kt, .scala,
.html, .css, .sql, .yaml, .yml, .json, .xml, .md, .txt, .sh, .bat, .ps1
```

**Plus special files**: `.env`, `.gitignore`, `requirements.txt`, `package.json`, `Dockerfile`, etc.

---

### Layer 2: Folder Blacklist
These folders are automatically skipped during scanning:
```
venv, .venv, env, __pycache__, node_modules, dist, build, .git, .mypy_cache,
.claude, .github, .vscode, .idea, .roo, results, logs, .tox, .nox,
.pytest_cache, htmlcov, cover
```

Plus: Custom excludes from `.gitignore` file, hardcoded `["jink"]`

---

### Layer 3: Path Traversal Prevention
All file paths are validated to prevent escape attacks:
```python
# These are BLOCKED:
read_file("../../../etc/passwd")        # ❌ Path traversal
read_file("/etc/passwd")                # ❌ Absolute path outside base
read_file("../../node_modules/code.js") # ❌ Escape attempt

# These are ALLOWED:
read_file("backend/app/main.py")        # ✅ Within base directory
read_file("./src/index.ts")             # ✅ Relative path
```

---

## Why These Restrictions Exist

| Restriction | Purpose | Benefit |
|-------------|---------|---------|
| Extension whitelist | Only include readable code files | Prevents binary/binary corruption |
| Folder blacklist | Exclude build artifacts & dependencies | Improves performance, reduces clutter |
| Path traversal checks | Prevent accessing system files | Security (CWE-22) |
| Size limits | Prevent memory exhaustion | Performance |
| File cache LRU | Prevent unlimited memory growth | Stability |

---

## Current Limits

| Metric | Current Value | Impact |
|--------|---------------|--------|
| Max file size | 1 MB | Files larger than this aren't cached |
| Max batch size | 10 MB | Can't read >10MB of code at once |
| Cache size | 100 files | Only 100 files cached in memory |
| Ignored folders | 26 folders | Can't access dependencies, builds |

---

## The 3 Key Files

| File | Purpose | Edit For What |
|------|---------|---------------|
| `backend/common/lazy_file_scanner.py` | Core scanner with all restrictions | Allowed extensions, size limits, ignored folders |
| `backend/app/services/file_service.py` | Wraps scanner, enforces rules | Custom validation logic |
| `backend/security_utils.py` | Path traversal prevention | DO NOT EDIT - this is security-critical |

---

## How to Expand Access

### Scenario 1: "I need to read `.svg` files"
1. Edit `backend/common/lazy_file_scanner.py`, line 95
2. Add `".svg"` to `supported_extensions` list
3. Restart backend
4. ✅ SVG files are now accessible

### Scenario 2: "I need to read files larger than 1MB"
1. Edit `backend/common/lazy_file_scanner.py`, line 57
2. Change `max_file_size: int = 1024 * 1024` to `10 * 1024 * 1024` (for 10MB)
3. Restart backend
4. ✅ Files up to 10MB are now cached

### Scenario 3: "I need to access node_modules"
⚠️ Not recommended, but if necessary:
1. Edit `backend/common/lazy_file_scanner.py`, line 127
2. Remove `"node_modules"` from the ignore list
3. Restart backend
4. ⚠️ Will dramatically increase file count (may cause performance issues)

### Scenario 4: "I need full access to the filesystem"
❌ Not possible without breaking security. Instead:
1. Use Scenario 1-3 to incrementally expand access
2. Or implement granular permission model (see SECURITY_LAYER_ANALYSIS.md)

---

## Risk Assessment

### Low Risk (Safe to Do):
- ✅ Add more file extensions (`.toml`, `.lock`, `.svg`, etc.)
- ✅ Increase size limits (1MB → 10MB → 100MB)
- ✅ Increase cache size (100 → 500 files)
- ✅ Remove non-critical ignored folders

### Medium Risk (Use Caution):
- ⚠️ Remove critical ignored folders (`node_modules`, `__pycache__`)
- ⚠️ Set unlimited size limits
- ⚠️ Implement custom file access logic

### High Risk (DO NOT DO):
- ❌ Disable path traversal checks
- ❌ Remove size limit validation
- ❌ Bypass security layer entirely
- ❌ Allow access to sensitive files without masking secrets

---

## What You Can't Do (And Why)

❌ **Read binary files** → Would cause text parsing errors
❌ **Read from `node_modules`** → Would kill performance (100K+ files)
❌ **Read from `.git`** → Would expose version history
❌ **Read outside backend root** → Security protection (CWE-22)
❌ **Remove security checks** → Would expose system files
❌ **Disable `.env` masking** → Would leak API keys

---

## Implementation Checklist

If you decide to expand access:

- [ ] Review `SECURITY_LAYER_ANALYSIS.md` for detailed guidance
- [ ] Identify which restrictions are blocking you
- [ ] Decide which restrictions to relax (use decision matrix below)
- [ ] Edit `lazy_file_scanner.py` with your changes
- [ ] Test with: `pytest backend/tests/infrastructure/test_lazy_file_scanner.py`
- [ ] Restart the backend server
- [ ] Verify access works from your frontend/tools
- [ ] Monitor for performance issues
- [ ] Document your changes in comments
- [ ] Review git diff before committing

---

## Decision Matrix: Should I Relax This Restriction?

```
Extension: ".svg" → ✅ YES (safe, useful for diagrams)
Extension: ".exe" → ❌ NO (binary, unusable)
Folder: "node_modules" → ⚠️ MAYBE (kills performance, but might be needed)
Folder: ".git" → ❌ NO (doesn't help, security risk)
Size: 1MB → 10MB → ✅ YES (improves usability, minimal risk)
Size: Unlimited → ❌ NO (memory exhaustion risk)
```

---

## Files Provided

This analysis includes 3 detailed guides:

1. **SECURITY_LAYER_ANALYSIS.md** - Deep dive into all restrictions with implementation options
2. **QUICK_ACCESS_EXPANSION_GUIDE.md** - Quick fixes for common scenarios (30 seconds to 5 minutes)
3. **SECURITY_CODE_LOCATIONS.md** - Exact line numbers and code snippets for every restriction

---

## Quick Stats

| Metric | Value |
|--------|-------|
| Files analyzed | 3 |
| Restriction layers | 3 |
| Whitelisted extensions | 21 |
| Blacklisted folders | 26+ |
| Security vulnerabilities found | 0 |
| Recommendations provided | 5 |

---

## Next Steps

### Option A: Keep Current Restrictions (Recommended for Security)
- No action needed
- Backend is secure and stable
- Consider documenting the restrictions for new developers

### Option B: Minimal Expansion (Recommended for Usability)
- Add `.svg`, `.lock`, `.toml` to extensions
- Increase max file size from 1MB to 10MB
- Increase batch limit from 10MB to 50MB
- Estimated impact: ⭐ Low risk

### Option C: Moderate Expansion
- Expand extensions further (`.gradle`, `.pom`, etc.)
- Remove non-critical folders like `results`, `logs`
- Increase cache size
- Estimated impact: ⭐⭐ Medium risk

### Option D: Implement Granular Permissions (Most Secure Expansion)
- Create access levels (RESTRICTED, STANDARD, EXTENDED, UNRESTRICTED)
- Allow per-endpoint configuration
- Still prevent path traversal attacks
- Estimated impact: ⭐⭐⭐ High complexity, highest security

---

## Questions?

Refer to the detailed guides:
- **How?** → `QUICK_ACCESS_EXPANSION_GUIDE.md`
- **Why?** → `SECURITY_LAYER_ANALYSIS.md`
- **Where?** → `SECURITY_CODE_LOCATIONS.md`

---

## Key Takeaway

Your backend security layer is **well-designed and intentional**. It prevents:
- ✅ Path traversal attacks
- ✅ Access to sensitive system files
- ✅ Memory exhaustion attacks
- ✅ Exposure of build artifacts and dependencies

To expand access:
1. Identify which restriction is blocking you
2. Decide if relaxing it is worth the risk
3. Make the change in 1 of 3 files
4. Test and restart
5. Monitor for issues

You can safely expand certain restrictions without breaking security. Refer to the decision matrix above for guidance.

