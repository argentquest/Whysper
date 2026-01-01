# Testing Guide - Diagram Provider Integration

Complete guide to testing the frontend diagram provider integration.

## 📚 Documentation Files

### Core Documentation
1. **[DIAGRAM_PROVIDER_INTEGRATION.md](DIAGRAM_PROVIDER_INTEGRATION.md)** - Complete architecture and implementation details
2. **[TESTING_PLAN.md](TESTING_PLAN.md)** - Comprehensive 10-phase testing plan
3. **[QUICK_TEST_GUIDE.md](QUICK_TEST_GUIDE.md)** - 30-minute quick testing guide
4. **[test-diagrams.js](test-diagrams.js)** - Automated test script for console

---

## 🚀 Quick Start (Choose One)

### Option 1: Quick Test (30 minutes)
Perfect for initial verification.
```
1. Read: QUICK_TEST_GUIDE.md
2. Follow: Step-by-step instructions
3. Verify: 6 key tests pass
```

### Option 2: Full Test (2-3 hours)
Comprehensive testing with all edge cases.
```
1. Read: TESTING_PLAN.md
2. Follow: 10 phases of testing
3. Verify: All test cases pass
```

### Option 3: Automated Test Script (5 minutes)
Quick automated validation.
```
1. Start frontend and backend
2. Open browser console
3. Paste test-diagrams.js and run
4. Review test results
```

---

## 📋 What to Test

### Core Functionality
- ✅ Mermaid diagram rendering
- ✅ D2 diagram rendering
- ✅ Provider service integration
- ✅ Validation with auto-fix
- ✅ Export (SVG, PNG, copy)
- ✅ Zoom and pan controls
- ✅ Error handling
- ✅ Provider metadata display

### Performance
- ✅ Render times < 2 seconds
- ✅ Responsive UI, no freezing
- ✅ Proper caching behavior
- ✅ No memory leaks

### Compatibility
- ✅ Chrome, Firefox, Safari, Edge
- ✅ Desktop and mobile
- ✅ Different screen sizes

---

## 🎯 Testing Workflow

### Setup
```bash
# Terminal 1: Backend
cd backend
python -m uvicorn app.main:app --reload --port 8003

# Terminal 2: Frontend
cd frontend
npm run dev

# Browser
Open: http://localhost:5173
F12: Open DevTools
```

### Test Execution

**Step 1: Quick Automated Test**
```javascript
// In browser console, copy-paste test-diagrams.js and run
```

**Step 2: Manual Testing**
- Follow QUICK_TEST_GUIDE.md (30 minutes)
- Verify all checks pass

**Step 3: Console Validation**
- Check for correct emoji prefixes:
  - 🎨 = Mermaid operations
  - 🎯 = D2 operations
  - 📊 = Provider service operations
- Verify no red errors

**Step 4: Network Inspection**
- DevTools → Network tab
- Look for `/diagram-provider/` endpoints
- Verify all requests return 200 OK

---

## ✅ Test Checklist

### Pre-Testing
- [ ] Backend running on port 8003
- [ ] Frontend running on port 5173
- [ ] Browser DevTools open
- [ ] Network throttling set to "Normal"

### Mermaid Tests
- [ ] Simple flowchart renders
- [ ] Sequence diagram renders
- [ ] Complex diagram renders
- [ ] Provider info displayed
- [ ] Export to SVG works
- [ ] Export to PNG works
- [ ] Zoom/pan works
- [ ] Copy code works
- [ ] Error handling works

### D2 Tests
- [ ] Simple diagram renders
- [ ] Complex diagram renders
- [ ] Styling applied correctly
- [ ] Provider info displayed
- [ ] Export to SVG works
- [ ] Copy SVG works
- [ ] Debug panel works
- [ ] Error handling works

### Provider Service
- [ ] getProviderInfo() works
- [ ] listProviders() works
- [ ] checkHealth() works
- [ ] validate() works
- [ ] render() works
- [ ] Caching works

### Console Output
- [ ] Mermaid logs show 🎨 prefix
- [ ] D2 logs show 🎯 prefix
- [ ] Provider logs show 📊 prefix
- [ ] No red error messages
- [ ] All expected logs appear

### Network
- [ ] All API calls successful (200)
- [ ] Response times acceptable
- [ ] Response formats correct

### Overall
- [ ] No browser crashes
- [ ] UI responsive
- [ ] All features working
- [ ] Ready for production

---

## 🔍 Troubleshooting

### Diagram Not Rendering
1. Check console for errors (F12)
2. Look for emoji prefix: 🎨 (Mermaid) or 🎯 (D2)
3. Check Network tab for API responses
4. Verify backend is running

### Provider Not Found
1. Run: `diagramProviderService.listProviders()` in console
2. Should show mermaidv1 and d2v1
3. If not, check backend logs

### API Errors
1. Check Network tab for status codes
2. 404 = endpoint not found (backend issue)
3. 500 = server error (check backend logs)
4. 503 = provider unavailable (install CLI tools)

### Render Times Slow
1. Check `metadata.render_time` in response
2. Normal: Mermaid 50-200ms, D2 100-500ms
3. If slower, check backend performance
4. May be using LLM correction (slower)

### Cache Issues
1. Run: `diagramProviderService.clearCache()`
2. Try again
3. Cache expires after 5 minutes anyway

---

## 📊 Test Results Template

```
Date: ____________
Tester: __________
Backend Version: __________
Frontend Version: __________

QUICK TEST (30 min):  PASS / FAIL
FULL TEST (3 hours): PASS / FAIL
AUTO TEST SCRIPT:    PASS / FAIL

Issues Found:
- [List any issues]

Performance:
- Mermaid avg render: ___ms
- D2 avg render: ___ms

Browser(s) Tested:
- Chrome: PASS / FAIL
- Firefox: PASS / FAIL
- Safari: PASS / FAIL
- Edge: PASS / FAIL

Overall: PASS / FAIL

Notes:
[Any additional notes]
```

---

## 📈 Key Metrics to Track

### Performance Benchmarks
```
Mermaid Simple:     ~50ms
Mermaid Complex:    ~150ms
D2 Simple:          ~100ms
D2 Complex:         ~400ms
Large Diagram:      < 2000ms
```

### Success Criteria
- ✅ 100% of core tests pass
- ✅ No crashes or freezes
- ✅ All error cases handled
- ✅ Performance acceptable
- ✅ Cross-browser compatible

---

## 🔧 Advanced Testing

### Console Commands

**Test provider service directly**
```javascript
// Get provider info
const info = await diagramProviderService.getProviderInfo('mermaid');
console.log(info);

// Validate code
const result = await diagramProviderService.validate({
  code: 'flowchart TD\n  A --> B',
  diagram_type: 'mermaid'
});
console.log(result);

// Render diagram
const svg = await diagramProviderService.render({
  code: 'flowchart TD\n  A --> B',
  diagram_type: 'mermaid'
});
console.log(svg);

// Check health
const health = await diagramProviderService.checkHealth();
console.log(health);

// Clear cache
diagramProviderService.clearCache();
```

### Performance Profiling
```javascript
// Time a render
console.time('diagram-render');
await diagramProviderService.render({...});
console.timeEnd('diagram-render');

// Memory usage
console.memory.usedJSHeapSize

// Network throttling
DevTools → Network → Slow 3G
```

### Network Inspection
1. Open DevTools → Network tab
2. Filter by "diagram-provider"
3. Check:
   - Request method (GET/POST)
   - Status code (should be 200)
   - Response time
   - Response size
   - Response format

---

## 📝 Test Report Template

**Date**: _______________
**Tester**: _______________
**Build**: _______________

### Summary
- Total Tests: ___
- Passed: ___
- Failed: ___
- Success Rate: ___%

### Issues Found
1. **[Issue Title]**
   - Severity: [Critical/High/Medium/Low]
   - Reproducible: [Yes/No]
   - Steps: [How to reproduce]
   - Expected: [What should happen]
   - Actual: [What happened]

### Performance Results
- Mermaid avg: ___ms
- D2 avg: ___ms
- Largest diagram: ___ms
- API response time: ___ms

### Browser Compatibility
| Browser | Version | Result |
|---------|---------|--------|
| Chrome | 120 | PASS |
| Firefox | 121 | PASS |
| Safari | 17 | PASS |
| Edge | 120 | PASS |

### Recommendation
- [ ] Ready for production
- [ ] Minor fixes needed
- [ ] Major fixes needed
- [ ] Do not deploy

### Sign-off
- Tester: _______________
- Date: _______________
- Approved by: _______________

---

## 🎓 Learning Resources

### Understanding the Architecture
1. Read: [DIAGRAM_PROVIDER_INTEGRATION.md](DIAGRAM_PROVIDER_INTEGRATION.md)
2. Review: Data flow diagrams
3. Check: Type definitions

### API Documentation
1. Backend endpoints: `/api/v1/diagram-provider/`
2. Request/response formats in DIAGRAM_PROVIDER_INTEGRATION.md
3. Error handling examples

### Common Issues
1. Provider not available → Check if CLI installed
2. Slow renders → Check if LLM correction enabled
3. Cache stale → Run `diagramProviderService.clearCache()`

---

## ✨ Success!

You've successfully tested the diagram provider integration when:
- ✅ All quick tests pass
- ✅ No errors in console
- ✅ All API calls successful
- ✅ Diagrams render correctly
- ✅ Export functions work
- ✅ Cross-browser compatible
- ✅ Performance acceptable

**Next Steps**:
1. Deploy to staging
2. Run full testing plan
3. Get user feedback
4. Deploy to production

---

## 📞 Support

**Questions?**
- Check [DIAGRAM_PROVIDER_INTEGRATION.md](DIAGRAM_PROVIDER_INTEGRATION.md) for architecture details
- Review [TESTING_PLAN.md](TESTING_PLAN.md) for comprehensive guide
- Run [test-diagrams.js](test-diagrams.js) for automated tests
- Check backend logs for errors

**Found a bug?**
- Document it using the template above
- Include console errors
- Attach screenshots
- Note reproduction steps
