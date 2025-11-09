# Quick Testing Guide - 30 Minutes

Quick start testing guide to verify the diagram provider integration is working.

## Setup (5 minutes)

1. **Start Backend**
   ```bash
   cd backend
   python -m uvicorn app.main:app --reload --port 8003
   ```
   Expected: Server running on http://localhost:8003

2. **Start Frontend**
   ```bash
   cd frontend
   npm run dev
   ```
   Expected: Running on http://localhost:5173

3. **Open Browser**
   - Navigate to http://localhost:5173
   - Open DevTools: `F12` or `Cmd+Option+I`
   - Open Console tab

---

## Test 1: Mermaid Diagram (5 minutes)

### Step 1: Navigate to Chat
- Open the chat interface
- Type message: "Create a flowchart for login process"
- Press Enter

### Step 2: Verify Rendering
✅ **Check these things**:
- [ ] Diagram appears in chat
- [ ] Card title shows: "Mermaid Diagram" + green tag with provider name
- [ ] Blue tag shows render time (e.g., "145ms")
- [ ] Console shows: `🎨 [MERMAID DIAGRAM] SVG rendered successfully via provider`
- [ ] SVG renders correctly without errors

### Step 3: Test Export
- [ ] Click "Copy" button → code copies to clipboard
- [ ] Click "SVG" button → downloads SVG file
- [ ] Click "PNG" button → downloads PNG image
- [ ] Click expand icon → opens in new tab

### Step 4: Test Zoom
- [ ] Scroll to zoom in/out
- [ ] Click "+" and "-" buttons
- [ ] Click center number to reset

---

## Test 2: D2 Diagram (5 minutes)

### Step 1: Request D2 Diagram
- Type: "Draw a D2 diagram showing frontend, backend, and database"
- Press Enter

### Step 2: Verify Rendering
✅ **Check these things**:
- [ ] Diagram appears
- [ ] Card title shows: "D2 Diagram" + green tag with provider name
- [ ] Blue tag shows render time
- [ ] Console shows: `🎯 [D2 DIAGRAM] SVG rendered successfully via provider`
- [ ] Diagram displays correctly

### Step 3: Test Export
- [ ] Click "Copy SVG" → copies SVG
- [ ] Click "Download" button → downloads SVG
- [ ] Click expand → opens in new tab
- [ ] Click "Show Debug" → shows metadata panel

### Step 4: Debug Panel
- [ ] Verify shows: Success, Code Length, Render Time, Timestamp
- [ ] Verify shows: Validation status, Provider ID

---

## Test 3: Provider Service (5 minutes)

### In Browser Console

**Test 3.1: Get Mermaid Provider Info**
```javascript
const info = await diagramProviderService.getProviderInfo('mermaid');
console.log(info);
```
✅ Expected output:
```
{
  provider_id: 'mermaidv1',
  provider_name: 'Mermaid v1',
  diagram_type: 'mermaid',
  capabilities: ['validate', 'render_svg', 'auto_fix', ...],
  available: true,
  ...
}
```

**Test 3.2: List All Providers**
```javascript
const list = await diagramProviderService.listProviders();
console.table(list.providers);
```
✅ Expected:
- [ ] Shows mermaidv1 with diagram_type: 'mermaid'
- [ ] Shows d2v1 with diagram_type: 'd2'
- [ ] Both have available: true

**Test 3.3: Check System Health**
```javascript
const health = await diagramProviderService.checkHealth();
console.log(health);
```
✅ Expected:
- [ ] status: 'healthy'
- [ ] available_providers: 2 (or more)
- [ ] diagram_types includes 'mermaid' and 'd2'

**Test 3.4: Validate Code**
```javascript
const result = await diagramProviderService.validate({
  code: 'flowchart TD\n  A[Start] --> B[End]',
  diagram_type: 'mermaid',
  auto_fix: true
});
console.log(result);
```
✅ Expected:
- [ ] is_valid: true
- [ ] provider_id: 'mermaidv1'

---

## Test 4: Error Handling (5 minutes)

### Test 4.1: Invalid Mermaid Code
```
In chat, request:
"Create a mermaid diagram with code: graph TD → B"
(intentionally broken syntax)
```

✅ Expected:
- [ ] Shows error message
- [ ] Graceful error display
- [ ] No browser crash

### Test 4.2: Invalid D2 Code
```
In chat, request:
"Draw D2: frontend -> backend ->"
(incomplete arrow)
```

✅ Expected:
- [ ] Shows error message
- [ ] May attempt auto-fix
- [ ] Graceful error handling

### Test 4.3: Very Large Code
```javascript
const largeCode = 'flowchart TD\n' + 'A --> B\n'.repeat(1000);
await diagramProviderService.render({
  code: largeCode,
  diagram_type: 'mermaid'
});
```

✅ Expected:
- [ ] Either renders or shows timeout error
- [ ] No browser freeze

---

## Test 5: Console Output Verification (3 minutes)

### Filter Console by Prefix

**Look for Mermaid logs** (Filter: "MERMAID")
```
🎨 [MERMAID DIAGRAM] Provider info loaded: Mermaid v1
🎨 [MERMAID DIAGRAM] Starting Mermaid diagram render via provider
🎨 [MERMAID DIAGRAM] Validation result: { is_valid: true, ... }
🎨 [MERMAID DIAGRAM] SVG rendered successfully via provider
```

**Look for D2 logs** (Filter: "D2 DIAGRAM")
```
🎯 [D2 DIAGRAM] Provider info loaded: D2 v1
🎯 [D2 DIAGRAM] Starting D2 diagram render via provider service
🎯 [D2 DIAGRAM] Validation result: { is_valid: true, ... }
🎯 [D2 DIAGRAM] SVG rendered successfully via provider
```

**Look for Provider Service logs** (Filter: "PROVIDER")
```
[📊 DIAGRAM PROVIDER SERVICE] Render request
[📊 DIAGRAM PROVIDER SERVICE] Validation request
[📊 DIAGRAM PROVIDER SERVICE] Getting provider info
```

---

## Test 6: Network Inspection (2 minutes)

### Check API Calls

1. Open DevTools → Network tab
2. Render a diagram
3. Filter by: "diagram-provider"

✅ **Expected requests**:
- [ ] GET `/diagram-provider/providers` (fetches provider info)
- [ ] POST `/diagram-provider/validate` (validates code)
- [ ] POST `/diagram-provider/render` (renders diagram)

✅ **Check response status**:
- [ ] All requests: 200 OK
- [ ] Response time: <500ms for validation, <2s for render

✅ **Check response format**:
- Validation response includes: `is_valid`, `provider_id`
- Render response includes: `success`, `content` (SVG), `metadata`

---

## Quick Checklist

Print this checklist and mark off as you test:

```
MERMAID TESTS
[ ] Renders successfully
[ ] Shows provider name and render time
[ ] Export to SVG works
[ ] Export to PNG works
[ ] Copy code works
[ ] Zoom in/out works
[ ] No console errors

D2 TESTS
[ ] Renders successfully
[ ] Shows provider name and render time
[ ] Export to SVG works
[ ] Copy SVG works
[ ] Debug panel works
[ ] No console errors

PROVIDER SERVICE
[ ] getProviderInfo('mermaid') returns correct data
[ ] listProviders() shows both mermaidv1 and d2v1
[ ] checkHealth() returns healthy status
[ ] validate() works correctly
[ ] Caching works (2nd call faster)

ERROR HANDLING
[ ] Invalid mermaid code shows error
[ ] Invalid D2 code shows error
[ ] Large code handles gracefully
[ ] Network error shows message

CONSOLE LOGS
[ ] Mermaid has 🎨 prefix
[ ] D2 has 🎯 prefix
[ ] Provider service has 📊 prefix
[ ] All expected log messages appear

NETWORK REQUESTS
[ ] All API calls successful (200 OK)
[ ] Response times acceptable
[ ] Response formats correct

OVERALL
[ ] No crashes
[ ] UI is responsive
[ ] Diagrams render correctly
[ ] Export functions work
[ ] Everything works as expected
```

---

## If Something Fails

### Mermaid Not Rendering
1. Check console for `❌ [MERMAID DIAGRAM] Rendering error`
2. Look at Network tab → POST `/diagram-provider/render`
3. Check response status and error message
4. **Fix**: Verify backend is running, mermaidv1 provider available

### D2 Not Rendering
1. Check console for `❌ [D2 DIAGRAM] Rendering error`
2. Look at Network tab → POST `/diagram-provider/render`
3. Check if error is validation or rendering
4. **Fix**: Ensure d2 CLI is installed on backend

### Provider Info Not Loading
1. Check Network tab → GET `/diagram-provider/providers`
2. Look for 404 or 500 error
3. **Fix**: Backend may not be running or provider endpoint missing

### Console Errors
```javascript
// Clear console
console.clear()

// Try again
// Watch for any red error messages
```

### Timeout Issues
1. Check if backend is slow
2. Try refreshing page
3. Check backend logs for errors

---

## Success Criteria

✅ **Testing Complete When**:
- All 5 diagram tests pass
- Provider service tests return expected data
- Error handling works gracefully
- Console shows correct emoji prefixes
- Network requests are successful
- No crashes or freezes
- Exports work correctly

---

## Time Estimates

| Task | Time |
|------|------|
| Setup | 5 min |
| Mermaid Test | 5 min |
| D2 Test | 5 min |
| Provider Service | 5 min |
| Error Handling | 5 min |
| Console Verification | 3 min |
| Network Check | 2 min |
| **Total** | **~30 min** |

---

## Next Steps If All Tests Pass

1. ✅ Run full testing plan in [TESTING_PLAN.md](TESTING_PLAN.md)
2. ✅ Test on other browsers (Chrome, Firefox, Safari)
3. ✅ Test on mobile devices
4. ✅ Load testing with large diagrams
5. ✅ Performance profiling
6. ✅ Ready for production!

---

## Support

**Questions or Issues?**
- Check console for error messages
- Review Network tab in DevTools
- Compare with expected output above
- Check backend logs for errors
- Review DIAGRAM_PROVIDER_INTEGRATION.md for more details
