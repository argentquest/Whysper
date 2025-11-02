# Testing After Endpoint Fix

## Quick Test (5 minutes)

### Step 1: Hard Refresh Browser
```
Windows/Linux: Ctrl + Shift + R
Mac: Cmd + Shift + R
```
This clears the cache and loads fresh JavaScript files.

### Step 2: Open Browser Console
```
Press: F12
Go to: Console tab
```

### Step 3: Run Quick Check
Paste this in console and run:

```javascript
// Check 1: Verify health (should be 200 OK)
console.log('Checking provider health...');
const health = await diagramProviderService.checkHealth();
console.log('✅ Health:', health);

// Check 2: Get Mermaid provider (should succeed)
console.log('\nGetting Mermaid provider info...');
const mermaid = await diagramProviderService.getProviderInfo('mermaid');
console.log('✅ Mermaid:', mermaid.provider_name);

// Check 3: Get D2 provider (should succeed)
console.log('\nGetting D2 provider info...');
const d2 = await diagramProviderService.getProviderInfo('d2');
console.log('✅ D2:', d2.provider_name);

console.log('\n✨ All provider checks passed!');
```

**Expected Output**:
```
Checking provider health...
✅ Health: { status: 'healthy', available_providers: 2, ... }

Getting Mermaid provider info...
✅ Mermaid: Mermaid v1

Getting D2 provider info...
✅ D2: D2 v1

✨ All provider checks passed!
```

### Step 4: Check Network Requests

Open DevTools Network tab and filter by "diagrams/v2":

**Expected requests**:
```
GET  /api/v1/diagrams/v2/providers           200 OK
GET  /api/v1/diagrams/v2/providers/mermaidv1 200 OK (if clicked)
GET  /api/v1/diagrams/v2/providers/d2v1      200 OK (if clicked)
GET  /api/v1/diagrams/v2/health              200 OK
```

**All should have**:
- Status: 200 OK (green)
- Response time: < 100ms (for cached requests)

### Step 5: Test Diagram Rendering

In the chat application:

**Test Mermaid**:
```
Message: "Create a flowchart: A -> B -> C"
```

Expected:
- ✅ Diagram appears
- ✅ Card shows "Mermaid v1" provider name
- ✅ Blue tag shows render time (e.g., "145ms")
- ✅ Console shows: `🎨 [MERMAID DIAGRAM] SVG rendered successfully via provider`
- ✅ Network shows: POST `/api/v1/diagrams/v2/validate` + POST `/api/v1/diagrams/v2/render`

**Test D2**:
```
Message: "Draw architecture: frontend -> backend -> database"
```

Expected:
- ✅ Diagram appears
- ✅ Card shows "D2 v1" provider name
- ✅ Blue tag shows render time (e.g., "234ms")
- ✅ Console shows: `🎯 [D2 DIAGRAM] SVG rendered successfully via provider`
- ✅ Network shows: POST `/api/v1/diagrams/v2/validate` + POST `/api/v1/diagrams/v2/render`

## Troubleshooting

### Still Getting 404 Errors?

1. **Clear browser cache completely**:
   - DevTools → Storage → Clear site data
   - Or: Ctrl+Shift+Delete → Clear browsing data

2. **Verify backend is running**:
   ```bash
   # Check if backend is listening
   curl http://localhost:8003/api/v1/diagrams/v2/health

   # Should return JSON with status: 'healthy'
   ```

3. **Check backend logs** for any errors:
   ```
   [2025-11-02 ...] No errors should appear
   All requests should show 200 OK
   ```

4. **Restart services**:
   ```bash
   # Terminal 1: Stop and restart backend
   Ctrl+C
   python -m uvicorn app.main:app --reload --port 8003

   # Terminal 2: Stop and restart frontend
   Ctrl+C
   npm run dev

   # Browser: Hard refresh
   Ctrl+Shift+R
   ```

### Getting Different Errors?

**Check what the error is**:
- Red error in console? Copy the message
- 404 in Network tab? Verify endpoint path
- 500 error? Check backend logs for exception
- Timeout? Backend might be slow, try again

## Automated Test

Run the full automated test suite:

```javascript
// Paste entire test-diagrams.js in console and run
// Should see: "✨ ALL TESTS PASSED!"
```

## Success Criteria

You'll know the fix worked when:

✅ Console shows provider info loads without errors
✅ Network tab shows all `/diagrams/v2/*` requests return 200 OK
✅ Mermaid diagrams render with provider name
✅ D2 diagrams render with provider name
✅ No 404 or 500 errors anywhere
✅ All automated tests pass
✅ Both MermaidDiagram and D2DiagramBackend work

## Full Testing

After confirming the quick test passes:

1. Follow: **QUICK_TEST_GUIDE.md** (30 minutes)
2. Follow: **TESTING_PLAN.md** (2-3 hours)

## Endpoint Summary

| Operation | Endpoint | Status |
|-----------|----------|--------|
| Render diagram | `POST /api/v1/diagrams/v2/render` | ✅ Fixed |
| Validate code | `POST /api/v1/diagrams/v2/validate` | ✅ Fixed |
| List providers | `GET /api/v1/diagrams/v2/providers` | ✅ Fixed |
| Get provider info | `GET /api/v1/diagrams/v2/providers/{id}` | ✅ Fixed |
| Health check | `GET /api/v1/diagrams/v2/health` | ✅ Fixed |

All 5 endpoints now properly mapped between frontend and backend! 🎉

## Next Steps

1. **Hard refresh browser**
2. **Run quick checks above**
3. **Test diagram rendering**
4. **Verify Network tab shows 200 OK**
5. **Run full test suite**
6. **Report success!**

Ready to test? Start with the Quick Test above! 🚀
