# Frontend Testing Summary: Model Selection Feature

## Quick Start

The frontend model selection feature is now complete. Here's how to test it:

---

## What Was Built

**Component Flow:**
```
ModelSelector (choose model)
    ↓
Describe Your System (enter description)
    ↓
Start Conversation (begins with model_id)
    ↓
Backend processes with model-specific prompts
```

**Files Modified:**
1. `frontend/src/components/DiagramWizard/ModelSelector.tsx` (created)
2. `frontend/src/components/DiagramWizard/DiagramWizard.tsx` (updated)
3. `frontend/src/components/DiagramWizard/hooks/useDiagramSession.ts` (updated)
4. `frontend/src/services/diagram/diagramApi.ts` (updated)

---

## Testing Approach

### 1. Automated Tests (Unit + Integration)

**Setup:**
```bash
cd frontend
npm install  # if needed
npm run test  # Vitest runs all tests
```

**Test Files to Create:**
```
frontend/src/components/DiagramWizard/
  ├── ModelSelector.test.tsx          (7+ unit tests)
  ├── DiagramWizard.test.tsx          (10+ unit tests)
  ├── DiagramWizard.integration.test.tsx (3+ integration tests)
  └── hooks/
      └── useDiagramSession.test.ts   (3+ unit tests)

frontend/src/services/diagram/
  └── diagramApi.test.ts              (4+ unit tests)
```

**Key Test Scenarios:**
```typescript
// ModelSelector tests
✓ Renders 4 model cards
✓ Calls onSelect with correct modelId
✓ Disables buttons during loading

// DiagramWizard tests
✓ Shows ModelSelector initially
✓ Shows system form after selection
✓ Saves model to localStorage
✓ Loads model from localStorage
✓ "Change Model" button works
✓ Prevents start without model
✓ Prevents start without description

// Hook tests
✓ Passes modelId to API

// API tests
✓ Includes model_id in request body
✓ Omits model_id when not provided
✓ Handles all 4 model IDs
```

### 2. Manual Testing

**Before Starting Session:**
1. [ ] Open DiagramWizard component
2. [ ] See ModelSelector with 4 cards
3. [ ] Click "Select" on any model
4. [ ] Verify model indicator appears
5. [ ] Verify model saved to localStorage

**During Session Start:**
6. [ ] Enter system description
7. [ ] Click "Start Conversation"
8. [ ] Open DevTools Network tab
9. [ ] Verify POST `/api/v1/diagram/start` includes `model_id`

**Data Persistence:**
10. [ ] Refresh page - model selection restored
11. [ ] Close browser - reopen - model restored
12. [ ] Try different models - selection changes

**Error Cases:**
13. [ ] Try starting without model - see warning
14. [ ] Try starting without description - see warning
15. [ ] Change model and start new session - works

---

## Test Execution Commands

```bash
# Run all tests
npm run test

# Watch mode (auto-rerun on changes)
npm run test -- --watch

# Tests with UI dashboard
npm run test:ui

# Coverage report
npm run test:coverage

# Specific test file
npm run test -- ModelSelector.test.tsx

# Specific test pattern
npm run test -- --grep "model selection"
```

---

## What Each Layer Tests

### Unit Tests (Component/Hook/Service Level)

**ModelSelector Component:**
- Renders correctly with all model options
- Calls onSelect callback with correct modelId
- Respects loading prop to disable buttons
- Shows model descriptions and strengths
- Handles all 4 models

**DiagramWizard Component:**
- Conditional rendering (selector vs. form)
- localStorage read/write
- Model indicator display
- Change model functionality
- Form validation

**useDiagramSession Hook:**
- Accepts modelId parameter
- Passes modelId to API
- Backward compatible (works without modelId)

**DiagramApi Service:**
- Includes model_id in POST request body
- Omits model_id when not provided
- Correct HTTP method and headers
- Error handling

### Integration Tests

**Complete User Flow:**
1. User selects model from ModelSelector
2. System description form appears
3. User enters description and clicks Start
4. Backend receives request with correct model_id
5. Session begins with selected model

**Cross-Component Communication:**
- ModelSelector → DiagramWizard state update
- DiagramWizard → useDiagramSession hook
- useDiagramSession → DiagramApi service
- DiagramApi → Backend API

**Data Persistence:**
- Model selection → localStorage
- Page reload → restore selection
- Component remount → restore selection

---

## Expected Test Coverage

```
ModelSelector.tsx:        > 90%
DiagramWizard.tsx:        > 85% (model selection logic)
useDiagramSession.ts:     > 90%
diagramApi.ts:            > 85%
```

---

## Manual Testing Checklist

### UI Verification
```
[ ] ModelSelector displays with gradient background
[ ] All 4 model cards visible (GPT-5, Grok, Claude, Gemini)
[ ] Model icons display correctly
[ ] Descriptions readable
[ ] "Select" buttons clickable
[ ] Hover effects work smoothly
```

### Model Selection
```
[ ] Clicking Select hides ModelSelector
[ ] System description form appears
[ ] Model tag displays in header
[ ] "Change Model" button visible and works
[ ] Model name correctly formatted (uppercase)
```

### Data Persistence
```
[ ] Model saved to localStorage: 'diagramWizard.selectedModel'
[ ] Refresh page → model selection restored
[ ] Close browser → reopen → restored
[ ] Each model ID stored correctly:
    - gpt5
    - grok
    - claude
    - gemini
```

### Session Start
```
[ ] Cannot start without model → warning
[ ] Cannot start without description → warning
[ ] With both: API call includes model_id
[ ] Session begins with selected model
[ ] Model indicator shows in header
```

### Error Handling
```
[ ] localStorage quota error → graceful degradation
[ ] API error → handled appropriately
[ ] Component renders even if localStorage unavailable
[ ] Console warnings logged for failures
```

---

## API Request Format

When user starts session with a model, DiagramApi sends:

```json
{
  "initial_prompt": "User's system description",
  "diagram_type": "auto",
  "model_id": "gpt5"  // or grok, claude, gemini
}
```

**Backend Routes To:**
- ANALYSE_CONFIRM_gpt5.md (if model_id = 'gpt5')
- ANALYSE_CONFIRM_grok.md (if model_id = 'grok')
- ANALYSE_CONFIRM_sonet45.md (if model_id = 'claude')
- ANALYSE_CONFIRM_gemini25pro.md (if model_id = 'gemini')

---

## Browser DevTools Verification

### Check localStorage
```javascript
// In browser console:
localStorage.getItem('diagramWizard.selectedModel')
// Should return: 'gpt5', 'grok', 'claude', or 'gemini'
```

### Check Network Request
1. Open DevTools → Network tab
2. Start diagram generation
3. Look for POST `/api/v1/diagram/start`
4. Click on request → Request tab
5. Check JSON body includes `model_id` field

### Check Console Logs
```
[DiagramSession] Starting session { modelId: 'gpt5' }
🚀 Starting new diagram session with model: gpt5
✅ Session started, waiting for AI analysis...
```

---

## Test Coverage Goals

Run coverage report:
```bash
npm run test:coverage
```

Expected output should show:
```
ModelSelector.tsx:        Lines: 85%+, Branches: 85%+
DiagramWizard.tsx:        Lines: 80%+, Branches: 75%+
useDiagramSession.ts:     Lines: 85%+, Branches: 85%+
diagramApi.ts:            Lines: 80%+, Branches: 80%+
```

---

## Common Issues & Solutions

### localStorage Not Persisting in Tests
**Solution:** Mock localStorage in test setup (already done in `src/test/setup.ts`)

### ModelSelector Not Rendering
**Solution:** Check import path in DiagramWizard - should be `./ModelSelector` (relative)

### API Not Receiving model_id
**Solution:** Verify DiagramApi.startDiagramGeneration includes modelId in body when provided

### Tests Timeout
**Solution:** Use `waitFor()` for async operations, increase timeout if needed

---

## Next Steps

1. **Write Test Files:**
   - ModelSelector.test.tsx (7+ tests)
   - DiagramWizard.test.tsx (10+ tests)
   - DiagramWizard.integration.test.tsx (3+ tests)
   - useDiagramSession.test.ts (3+ tests)
   - diagramApi.test.ts (4+ tests)

2. **Run Tests:**
   ```bash
   npm run test -- --watch
   ```

3. **Check Coverage:**
   ```bash
   npm run test:coverage
   ```

4. **Manual Testing:**
   - Follow manual testing checklist
   - Test in multiple browsers
   - Test on different devices

5. **Deploy When Ready:**
   - All tests passing
   - Coverage > 80%
   - Manual testing complete
   - No console errors

---

## Complete Testing Reference

For detailed test code examples and full test file templates, see:
**`frontend/FRONTEND_TESTING_GUIDE.md`**

This guide includes:
- Complete test code for all components
- Integration test scenarios
- E2E test examples
- Manual testing checklist
- Debugging tips
- Performance testing guidance

---

## Summary

The frontend model selection feature is complete and ready for testing:

✅ ModelSelector component created
✅ DiagramWizard updated
✅ useDiagramSession hook updated
✅ DiagramApi updated
✅ localStorage persistence implemented
✅ Error handling in place

**To Verify:**
1. Run automated tests: `npm run test`
2. Follow manual checklist
3. Check DevTools Network tab
4. Verify localStorage values
5. Test all 4 models
6. Test error cases
