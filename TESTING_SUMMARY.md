# Testing Summary for Diagram Wizard Changes

## 📚 Documentation Created

I've created comprehensive testing documentation for you:

### 1. **Manual Testing Guide**
[DIAGRAM_WIZARD_TESTING_GUIDE.md](DIAGRAM_WIZARD_TESTING_GUIDE.md)

**Contains:**
- ✅ 6 detailed manual test scenarios
- ✅ Step-by-step instructions with verification checkpoints
- ✅ Expected results for each test
- ✅ Common issues and solutions
- ✅ Test checklist for releases

**Key Tests:**
- Test 1: Basic diagram generation flow
- Test 2: Validation endpoint fix (405 → 200)
- Test 3: Hybrid state architecture
- Test 4: LangGraph prompt template fix
- Test 5: Tab state binding
- Test 6: Error handling

### 2. **Automated Test Suites**

Created 2 new test files:

#### A. [DiagramWizard.stateManagement.test.tsx](frontend/src/components/DiagramWizard/DiagramWizard.stateManagement.test.tsx)
**Tests:**
- Local state initialization
- Code editor state binding
- State persistence across tabs
- REST API as source of truth
- SSE progress updates
- Optimistic updates

#### B. [DiagramWizard.integration.test.tsx](frontend/src/components/DiagramWizard/DiagramWizard.integration.test.tsx)
**Tests:**
- Validation endpoint fix
- Hybrid state architecture
- Code change handler
- REST as source of truth
- Error handling
- Tab state persistence

### 3. **Test Runner Script**
[run-diagram-wizard-tests.ps1](frontend/run-diagram-wizard-tests.ps1)

Quick way to run all tests with color-coded output.

---

## 🚀 Quick Start: Running Tests

### Manual Testing (Recommended First)

1. **Start Backend**
   ```bash
   cd backend
   .venv\Scripts\python.exe -m uvicorn app.main:app --reload --port 8000
   ```

2. **Start Frontend**
   ```bash
   cd frontend
   npm run dev
   ```

3. **Follow Test Guide**
   - Open [DIAGRAM_WIZARD_TESTING_GUIDE.md](DIAGRAM_WIZARD_TESTING_GUIDE.md)
   - Follow "Test 1: Basic Diagram Generation Flow"
   - Check off each ✅ verification step

### Automated Testing

```bash
cd frontend

# Run all tests
npm test

# Run with UI (recommended)
npm run test:ui

# Run with coverage
npm run test:coverage

# Run specific test file
npm test DiagramWizard.integration.test.tsx

# Use PowerShell script
.\run-diagram-wizard-tests.ps1
```

---

## 🎯 What to Verify

### Critical Fixes to Test:

#### ✅ Fix 1: Validation Endpoint (405 Error)
**Before:** POST to `/api/v1/diagram/validate` → 405 Method Not Allowed
**After:** POST to `/api/v1/diagrams/v2/validate` → 200 OK

**How to Test:**
1. Generate a diagram
2. Edit code in "Diagram Code" tab
3. Open DevTools → Network tab
4. Click Save
5. Verify: POST to `/diagrams/v2/validate` returns 200

#### ✅ Fix 2: Prompt Template Bug (Backend)
**Before:** LLM received `{analyze_prompt}` literal text → returned markdown
**After:** LLM receives actual prompt content → returns JSON

**How to Test:**
1. Start backend with `set LOG_LEVEL=DEBUG`
2. Watch console logs during diagram generation
3. Verify: No literal `{placeholder}` text in logs
4. Verify: No JSON parsing errors

#### ✅ Fix 3: Hybrid State Architecture
**Before:** Code edits lost when switching tabs
**After:** Local state persists, REST is source of truth

**How to Test:**
1. Generate a diagram
2. Edit code in "Diagram Code" tab
3. Switch to "Preview" tab
4. Switch back to "Diagram Code" tab
5. Verify: Your edits are still there

#### ✅ Fix 4: Tab State Binding
**Before:** `onCodeChange` handler missing → edits not saved
**After:** Handler connected → edits trigger re-render

**How to Test:**
1. Edit diagram code
2. Click Save
3. Verify: Console shows "Re-rendering diagram with edited code"
4. Verify: Preview updates with new SVG
5. Verify: Success message appears

---

## 📊 Test Coverage Goals

| Component | Current | Target |
|-----------|---------|--------|
| DiagramWizard | ~60% | 80%+ |
| GenerationScreen | ~55% | 75%+ |
| CodeEditorPanel | ~40% | 70%+ |
| useDiagramSession | ~70% | 85%+ |

**Run to check:**
```bash
npm run test:coverage
```

---

## 🐛 Expected Behavior After Fixes

### Validation Endpoint
- ✅ Status: 200 OK (not 405)
- ✅ Response: `{ is_valid: true/false, errors: [...] }`
- ✅ Network tab shows `/diagrams/v2/validate`

### Prompt Templates
- ✅ LLM receives actual prompt text
- ✅ LLM returns valid JSON
- ✅ No "Expecting property name" errors
- ✅ Clarification loop works smoothly

### State Management
- ✅ Code edits persist across tabs
- ✅ SVG updates after code changes
- ✅ Local state overrides SSE when editing
- ✅ REST API called for all mutations

### Tab Binding
- ✅ All 6 tabs work correctly
- ✅ Conversation, Preview: read-only ✓
- ✅ Diagram Code: editable ✓
- ✅ Workspace, Clean Workspace, JSON: read-only ✓

---

## 📝 Test Results Template

After running tests, record results:

```
Date: ___________
Tester: ___________

AUTOMATED TESTS:
[ ] All unit tests pass
[ ] All integration tests pass
[ ] Coverage > 70%

MANUAL TESTS:
[ ] Test 1: Basic Flow - PASS/FAIL
[ ] Test 2: Validation - PASS/FAIL
[ ] Test 3: State Persistence - PASS/FAIL
[ ] Test 4: Prompt Templates - PASS/FAIL
[ ] Test 5: Tab Binding - PASS/FAIL
[ ] Test 6: Error Handling - PASS/FAIL

ISSUES FOUND:
___________________________________
___________________________________
```

---

## 🎉 Success Criteria

Your changes are working correctly if:

1. ✅ All automated tests pass
2. ✅ Manual Test 1-6 complete successfully
3. ✅ No 405 errors in Network tab
4. ✅ Code edits persist across tab switches
5. ✅ SVG updates when code is edited
6. ✅ No JSON parsing errors in backend logs
7. ✅ All 6 tabs display correct content
8. ✅ No console errors in browser

---

## 🔧 Troubleshooting

### Tests Failing?

1. **Check dependencies:**
   ```bash
   cd frontend
   npm install
   ```

2. **Clear cache:**
   ```bash
   npm run build
   ```

3. **Check backend running:**
   - Backend should be on port 8000
   - Frontend on port 5173

### Manual Tests Failing?

See [DIAGRAM_WIZARD_TESTING_GUIDE.md](DIAGRAM_WIZARD_TESTING_GUIDE.md) → "Common Issues and Solutions"

---

## 📞 Next Steps

1. Run automated tests: `npm test`
2. Follow manual testing guide
3. Check test coverage: `npm run test:coverage`
4. Fix any failing tests
5. Document results
6. Push to remote when all pass

**Good luck! 🚀**
