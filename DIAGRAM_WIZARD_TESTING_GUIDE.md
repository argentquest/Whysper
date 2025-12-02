# Diagram Wizard Testing Guide

## 🧪 Manual Testing Steps

### Test 1: Basic Diagram Generation Flow
**Purpose**: Verify the complete diagram generation workflow

**Steps**:
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

3. **Open Browser**
   - Navigate to `http://localhost:5173`
   - Open DevTools (F12) → Console tab

4. **Select AI Model**
   - Click on "Diagram Wizard" tab
   - Choose a model (e.g., "GPT-5")
   - Click "Select"
   - ✅ Verify: Model tag appears in header

5. **Enter System Description**
   - Type: "E-commerce platform with user authentication, product catalog, shopping cart, and payment processing"
   - Click "Start Conversation"
   - ✅ Verify: Console shows `[DiagramWizard] Starting session`

6. **Monitor SSE Connection**
   - ✅ Verify: Console shows SSE connection established
   - ✅ Verify: Progress indicators show current phase
   - ✅ Verify: No errors in console

7. **Answer Clarification Questions**
   - Wait for AI to ask questions (e.g., "What database are you using?")
   - Answer: "PostgreSQL for main data, Redis for caching"
   - Click "Submit"
   - ✅ Verify: Score increases after each answer
   - ✅ Verify: JSON preview updates with new information

8. **Confirm Ready**
   - Wait until clarity score reaches target (usually 80)
   - Click "Yes, I'm Ready"
   - ✅ Verify: Transitions to Diagram Type Selection

9. **Select Diagram Type**
   - Choose recommended diagram type (e.g., "Structurizr C4")
   - ✅ Verify: Console shows diagram generation starting

10. **View Generated Diagram**
    - Wait for diagram code generation
    - ✅ Verify: "Preview" tab shows SVG diagram
    - ✅ Verify: "Diagram Code" tab shows Structurizr code
    - ✅ Verify: "Workspace" tab shows full workspace
    - ✅ Verify: "Full JSON" tab shows JSON representation

---

### Test 2: Validation Endpoint Fix
**Purpose**: Verify the `/diagrams/v2/validate` endpoint works

**Steps**:
1. Open DevTools → Network tab
2. Navigate to "Diagram Code" tab
3. Edit the diagram code (make a syntax error)
4. Click "Save"
5. ✅ Verify: Network tab shows POST to `/api/v1/diagrams/v2/validate`
6. ✅ Verify: Status code is 200 (not 405)
7. ✅ Verify: Response contains `is_valid: false`
8. ✅ Verify: Error panel shows validation errors

---

### Test 3: Hybrid State Architecture
**Purpose**: Verify local state persists and REST API is source of truth

**Steps**:
1. Generate a diagram (follow Test 1 steps 1-10)
2. Navigate to "Diagram Code" tab
3. Edit the code:
   ```
   // Add a new component
   database = container "Database" {
     description "PostgreSQL database"
   }
   ```
4. Click "Save"
5. ✅ Verify: Console shows `[DiagramWizard] Re-rendering diagram with edited code`
6. ✅ Verify: Network tab shows POST to `/api/v1/diagram/render`
7. ✅ Verify: "Preview" tab updates with new SVG
8. Switch to "Conversation" tab
9. Switch back to "Diagram Code" tab
10. ✅ Verify: Your edits are still there (local state persisted)
11. Switch to "Preview" tab
12. ✅ Verify: Diagram shows your changes (SVG updated)

---

### Test 4: LangGraph Prompt Template Fix
**Purpose**: Verify LLM receives proper prompts and returns JSON

**Steps**:
1. Start backend in DEBUG mode:
   ```bash
   cd backend
   set LOG_LEVEL=DEBUG
   .venv\Scripts\python.exe -m uvicorn app.main:app --reload --port 8000
   ```
2. Follow Test 1 steps 1-5
3. Watch backend console logs
4. ✅ Verify: No logs showing `{analyze_prompt}` literal text
5. ✅ Verify: Logs show actual prompt content being sent
6. ✅ Verify: No JSON parsing errors like "Expecting property name"
7. ✅ Verify: LLM responses are valid JSON structures

---

### Test 5: Tab State Binding
**Purpose**: Verify all tabs are properly bound to state

**Steps**:
1. Generate a diagram (follow Test 1)
2. Test each tab:

   **Conversation Tab**:
   - ✅ Verify: Shows chat history
   - ✅ Verify: Shows Q&A exchanges
   - ✅ Verify: Read-only (as expected)

   **Preview Tab**:
   - ✅ Verify: Shows SVG diagram
   - ✅ Verify: Diagram is interactive (pan/zoom)
   - ✅ Verify: Updates when code changes

   **Diagram Code Tab**:
   - ✅ Verify: Shows editable code editor
   - ✅ Verify: Syntax highlighting works
   - ✅ Verify: Save button enabled when editing
   - ✅ Verify: Copy button works

   **Workspace Tab**:
   - ✅ Verify: Shows full Structurizr workspace
   - ✅ Verify: Copy button works
   - ✅ Verify: Read-only (as expected)

   **Clean Workspace Tab**:
   - ✅ Verify: Shows cleaned workspace
   - ✅ Verify: Copy button works

   **Full JSON Tab**:
   - ✅ Verify: Shows JSON representation
   - ✅ Verify: Properly formatted
   - ✅ Verify: Copy button works

---

### Test 6: Error Handling
**Purpose**: Verify graceful error handling

**Steps**:
1. **Network Error**:
   - Stop backend
   - Try to start a new diagram
   - ✅ Verify: Error message appears
   - ✅ Verify: No console errors or crashes

2. **Invalid Code**:
   - Edit diagram code with syntax errors
   - Click Save
   - ✅ Verify: Validation errors shown
   - ✅ Verify: SVG not updated

3. **SSE Disconnect**:
   - Start diagram generation
   - Restart backend mid-generation
   - ✅ Verify: Frontend shows disconnection
   - ✅ Verify: Auto-reconnect attempts

---

## 🤖 Automated Testing

### Running Tests

```bash
cd frontend

# Run all tests
npm test

# Run tests with UI
npm run test:ui

# Run with coverage
npm run test:coverage

# Run specific test file
npm test DiagramWizard.test.tsx
```

### Example Test Output
```
✓ DiagramWizard Integration (467ms)
  ✓ Initial Rendering
    ✓ should render ModelSelectionScreen on initial mount
    ✓ should display all 4 model options
  ✓ Model Selection Flow
    ✓ should transition to SystemDescriptionScreen after model selection
    ✓ should save selected model to localStorage
```

---

## 📊 Test Coverage Goals

| Component | Target Coverage |
|-----------|----------------|
| DiagramWizard | 80%+ |
| GenerationScreen | 75%+ |
| CodeEditorPanel | 70%+ |
| useDiagramSession | 85%+ |

---

## 🐛 Common Issues and Solutions

### Issue 1: SSE Connection Fails
**Symptom**: Console shows "SSE connection failed"
**Solution**:
- Check backend is running on port 8000
- Verify CORS settings allow `http://localhost:5173`
- Check firewall settings

### Issue 2: Validation Returns 405
**Symptom**: Network tab shows 405 Method Not Allowed
**Solution**: This was fixed in commit 78e8bd0 - make sure you're on latest code

### Issue 3: Code Edits Don't Persist
**Symptom**: Edits lost when switching tabs
**Solution**: This was fixed in commit 78e8bd0 - hybrid state architecture now implemented

### Issue 4: LLM Returns Markdown Instead of JSON
**Symptom**: Backend logs show JSON parsing errors
**Solution**: This was fixed in commit 78e8bd0 - f-string templates now properly interpolated

---

## 📝 Test Checklist

Before each release, verify:

- [ ] All automated tests pass
- [ ] Manual Test 1: Basic Flow - PASS
- [ ] Manual Test 2: Validation - PASS
- [ ] Manual Test 3: State Persistence - PASS
- [ ] Manual Test 4: Prompt Templates - PASS
- [ ] Manual Test 5: Tab Binding - PASS
- [ ] Manual Test 6: Error Handling - PASS
- [ ] No console errors
- [ ] No network errors (check DevTools)
- [ ] All tabs work correctly
- [ ] Code edits persist
- [ ] SVG updates after edits
- [ ] SSE connection stable

---

## 🎯 Next Steps

After validating manually, consider adding:
1. Integration tests for the hybrid state pattern
2. E2E tests using Playwright or Cypress
3. Performance tests for large diagrams
4. Accessibility tests (WCAG compliance)
