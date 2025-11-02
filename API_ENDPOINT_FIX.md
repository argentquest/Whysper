# API Endpoint Fix - DiagramProviderService

## Issue Found

The frontend `diagramProviderService` was calling endpoints at `/api/v1/diagram-provider/*` but the backend API router had registered them at `/api/v1/diagrams/v2/*`.

**Error in Logs**:
```
INFO: 127.0.0.1:57928 - "POST /api/v1/diagram-provider/validate HTTP/1.1" 404 Not Found
INFO: 127.0.0.1:51386 - "GET /api/v1/diagram-provider/providers HTTP/1.1" 404 Not Found
```

## Root Cause

In `backend/app/api/v1/api.py`, the diagram_provider router is registered with:
```python
api_router.include_router(
    diagram_provider.router,
    prefix="/diagrams/v2",  # v2 to avoid conflict with existing
    tags=["diagrams-v2", "providers"],
)
```

But the frontend service was using the old prefix: `/diagram-provider/`

## Solution Applied

Updated all 5 endpoints in `frontend/src/services/diagramProviderService.ts`:

| Endpoint | Old Path | New Path |
|----------|----------|----------|
| Render | `/diagram-provider/render` | `/diagrams/v2/render` |
| Validate | `/diagram-provider/validate` | `/diagrams/v2/validate` |
| Get Providers | `/diagram-provider/providers` | `/diagrams/v2/providers` |
| Get Provider Info | `/diagram-provider/providers/{id}` | `/diagrams/v2/providers/{id}` |
| Health Check | `/diagram-provider/health` | `/diagrams/v2/health` |

## Files Modified

- ✅ `frontend/src/services/diagramProviderService.ts` (5 endpoint URLs updated)

## Verification

Run these commands to verify the fix:

**In Browser Console**:
```javascript
// Should now work (200 OK)
await diagramProviderService.checkHealth()

// Should return provider list
await diagramProviderService.listProviders()

// Should return mermaidv1 info
await diagramProviderService.getProviderInfo('mermaid')
```

**In Network Tab**:
- All requests should go to `/api/v1/diagrams/v2/*`
- All should return 200 OK status
- Response times should be < 500ms

## Next Steps

1. **Test Again**:
   ```bash
   # 1. Backend still running
   # 2. Frontend still running
   # 3. Hard refresh browser (Ctrl+Shift+R or Cmd+Shift+R)
   # 4. Try rendering a diagram
   ```

2. **Monitor Console**:
   ```
   ✅ Expected (should see):
   🎨 [MERMAID DIAGRAM] Provider info loaded: Mermaid v1
   🎯 [D2 DIAGRAM] Provider info loaded: D2 v1

   ✅ Expected API calls:
   GET  /api/v1/diagrams/v2/providers → 200 OK
   POST /api/v1/diagrams/v2/validate → 200 OK
   POST /api/v1/diagrams/v2/render → 200 OK
   ```

3. **Run Tests**:
   - Follow QUICK_TEST_GUIDE.md
   - Run test-diagrams.js in console
   - All tests should pass

## Additional Notes

The backend chose `/diagrams/v2/` prefix to avoid conflicts with existing diagram endpoints:
- `/api/v1/diagrams/` - Diagram events logging (existing)
- `/api/v1/d2/` - Legacy D2 API (existing)
- `/api/v1/mermaid/` - Legacy Mermaid API (existing)
- `/api/v1/diagrams/v2/` - **New unified provider API** ✅

This allows both old and new systems to coexist during migration.

## Testing Checklist

After applying this fix:

- [ ] Hard refresh browser
- [ ] Open DevTools (F12)
- [ ] Watch console for provider info logs
- [ ] Check Network tab for 200 OK responses
- [ ] Test Mermaid diagram rendering
- [ ] Test D2 diagram rendering
- [ ] Run automated test script
- [ ] All tests pass

✅ **Fix Complete - Ready to Test**
