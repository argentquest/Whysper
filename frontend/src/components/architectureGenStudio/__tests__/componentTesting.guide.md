# Component Testing Guide - Architecture Gen Studio

## Overview
This guide provides comprehensive testing procedures for all Architecture Gen Studio components.

---

## Phase 7b: Backend API Integration Testing

### API Endpoints to Test

#### 1. Agent Management Endpoints
**Endpoint:** `GET /api/v1/agents`
- **Expected Response:**
  ```json
  [
    {
      "id": "agent-1",
      "name": "C4 Diagram Agent",
      "description": "Generates C4 architecture diagrams"
    }
  ]
  ```
- **Test Cases:**
  - ✓ Successful agent fetch
  - ✓ Empty agent list handling
  - ✓ Network error handling
  - ✓ Timeout handling (5s timeout)

**Endpoint:** `GET /api/v1/agents/{agentId}/options`
- **Expected Response:**
  ```json
  [
    {
      "id": "option-1",
      "agentId": "agent-1",
      "name": "System Context Diagram",
      "description": "High-level overview",
      "template": "Create a C4 system context...",
      "validationRules": ["Must include system boundary"],
      "outputFormat": "SVG",
      "enabled": true
    }
  ]
  ```
- **Test Cases:**
  - ✓ Fetch options for valid agent
  - ✓ Handle invalid agent ID (404)
  - ✓ Handle disabled options filtering
  - ✓ Network error handling

---

#### 2. Diagram Generation Endpoints

**Endpoint:** `POST /api/v1/diagrams/v2/generate`
- **Request Body:**
  ```json
  {
    "agentId": "agent-1",
    "prompt": "Create a system context diagram for...",
    "diagramType": "mermaid"
  }
  ```
- **Expected Response:**
  ```json
  {
    "requestId": "req-1234567890",
    "diagram": {
      "svg": "<svg>...</svg>",
      "provider": "mermaid",
      "code": "graph TD...",
      "metadata": {
        "provider": "mermaid",
        "generationParameters": {...}
      },
      "status": "success",
      "timestamp": "2024-01-01T12:00:00Z"
    }
  }
  ```
- **Test Cases:**
  - ✓ Valid diagram generation
  - ✓ Missing required fields (400)
  - ✓ Invalid agent ID (404)
  - ✓ Prompt too long (413)
  - ✓ Server error handling (500)
  - ✓ Response time (should be < 30s)

**Endpoint:** `POST /api/v1/diagrams/v2/validate`
- **Request Body:**
  ```json
  {
    "code": "graph TD\n  A --> B",
    "diagramType": "mermaid"
  }
  ```
- **Expected Response:**
  ```json
  {
    "isValid": true,
    "errors": [],
    "warnings": []
  }
  ```
- **Test Cases:**
  - ✓ Valid code validation
  - ✓ Invalid syntax detection
  - ✓ Multiple error reporting
  - ✓ Timeout handling (30s)
  - ✓ Different diagram types (mermaid, d2, structurizr, plantuml)

**Endpoint:** `POST /api/v1/diagrams/v2/render`
- **Request Body:**
  ```json
  {
    "code": "graph TD\n  A --> B",
    "diagramType": "mermaid"
  }
  ```
- **Expected Response:**
  ```json
  {
    "svg": "<svg>...</svg>",
    "provider": "mermaid",
    "code": "graph TD\n  A --> B",
    "metadata": {...},
    "status": "success",
    "timestamp": "2024-01-01T12:00:00Z"
  }
  ```
- **Test Cases:**
  - ✓ Successful render
  - ✓ Large code handling (100KB+)
  - ✓ SVG validation
  - ✓ Different diagram types
  - ✓ Error rendering

**Endpoint:** `POST /api/v1/diagrams/v2/cancel`
- **Request Body:**
  ```json
  {
    "requestId": "req-1234567890"
  }
  ```
- **Expected Response:**
  ```json
  {
    "status": "cancelled"
  }
  ```
- **Test Cases:**
  - ✓ Cancel ongoing request
  - ✓ Cancel non-existent request
  - ✓ Multiple cancellation attempts

**Endpoint:** `GET /api/v1/diagrams/v2/stream?requestId={requestId}`
- **SSE Stream Messages:**
  ```
  event: message
  data: {"type":"progress","message":"Generating..."}

  event: diagram
  data: {"svg":"...","provider":"mermaid"}
  ```
- **Test Cases:**
  - ✓ SSE connection establishment
  - ✓ Message streaming
  - ✓ Connection persistence (10+ messages)
  - ✓ Graceful disconnection
  - ✓ Reconnection with backoff

---

## Phase 7c: State Synchronization Testing

### State Management Tests

#### 1. Agent State Flow
```typescript
Test Case: Agent Selection Updates State
1. Initial state: currentAgent = null
2. Fetch agents: agents = [Agent1, Agent2, ...]
3. Select agent: currentAgent = Agent1
4. Fetch options: currentAgentOptions = [Option1, Option2, ...]
5. Verify state consistency
```

#### 2. Prompt State Management
```typescript
Test Case: Prompt Input and Changes
1. Select agent option: currentPrompt = template
2. Edit prompt: promptHasUnsavedChanges = true
3. Change agent: Show unsaved changes dialog
4. Save prompt: localStorage persists
5. Reload page: Prompt restored from localStorage
```

#### 3. Diagram Generation State Flow
```typescript
Test Case: Complete Diagram Generation
1. Submit prompt: isProcessing = true, processingRequestId = "req-xxx"
2. SSE: Receive progress updates
3. Diagram ready: generatedDiagrams[mermaid] = DiagramResponse
4. Complete: isProcessing = false, currentStatus = "success"
5. Verify state immutability
```

#### 4. Column State Management
```typescript
Test Case: Column Width and Collapse
1. Initial: columnWidths = {left: 33%, center: 33%, right: 34%}
2. Drag divider: columnWidths updated
3. Collapse left: collapsedColumns.left = true
4. Verify minimum width (33.33%)
5. localStorage persistence
```

#### 5. Code Editor State
```typescript
Test Case: Code Editing and Validation
1. Change diagram type: codeEditorContent cleared
2. Edit code: codeEditorHasUnsavedChanges = true
3. Validate: isValidating = true
4. Errors received: validationResult populated
5. Render: isRendering = true
```

---

## Phase 7d: Error Recovery & Loading States

### Error Handling Test Cases

#### 1. Network Errors
```typescript
Test Scenarios:
- ✓ Connection timeout (5s for agents, 30s for validation)
- ✓ 404 Not Found (Agent not found)
- ✓ 400 Bad Request (Invalid parameters)
- ✓ 500 Server Error (Backend failure)
- ✓ Network offline (Show offline banner)
```

#### 2. Validation Errors
```typescript
Test Scenarios:
- ✓ Syntax errors in diagram code
- ✓ Missing required elements
- ✓ Invalid references
- ✓ Multiple errors (show all)
- ✓ Error details popup
```

#### 3. User Action Errors
```typescript
Test Scenarios:
- ✓ Empty prompt submission (show toast)
- ✓ Render without validation (show warning)
- ✓ Unsaved changes dialog (confirm/cancel)
- ✓ Agent change with unsaved prompt
- ✓ Code editor unsaved changes indicator
```

#### 4. Loading States
```typescript
Test Scenarios:
- ✓ Agent loading spinner
- ✓ Options loading skeleton
- ✓ Diagram generation progress
- ✓ Validation timeout indication
- ✓ Render in progress button state
```

#### 5. SSE Errors
```typescript
Test Scenarios:
- ✓ Connection failure (show error message)
- ✓ Reconnection with exponential backoff
- ✓ Max reconnection attempts (5)
- ✓ Error message queuing
- ✓ Graceful degradation
```

---

## Phase 7e: Complete User Workflow Testing

### End-to-End Workflows

#### Workflow 1: New Diagram Generation
```
1. Open application
   → Load agents list
   → Display in dropdown

2. Select agent
   → Load agent options
   → Auto-populate prompt template
   → Display in left column

3. Edit prompt
   → Show character count (X/5000)
   → Enable submit button
   → Show unsaved indicator

4. Submit prompt
   → Show "Generating..." status
   → Connect SSE stream
   → Display progress in footer
   → Receive diagram SVG

5. View diagram
   → Display in center column
   → Enable zoom controls
   → Enable export button

6. Export diagram
   → Choose format (SVG/PDF/Code)
   → Download file
   → Show success toast
```

#### Workflow 2: Code Editing & Rendering
```
1. Switch diagram type
   → Load code for selected type
   → Clear validation errors
   → Show diagram code in right column

2. Edit code
   → Real-time character validation
   → Show unsaved indicator
   → Disable render button

3. Validate code
   → Show validation spinner
   → Display errors/warnings
   → Update validation status

4. Fix errors
   → Edit code
   → Re-validate (only if changed)
   → Verify all errors resolved

5. Render diagram
   → Show render spinner
   → Update SVG in center column
   → Show success toast
   → Add to diagram history
```

#### Workflow 3: Multiple Diagram Types
```
1. Generate diagram (mermaid)
   → Display in center column
   → Show checkmark on mermaid tab

2. Switch to d2
   → Load d2 code in editor
   → Clear mermaid code
   → Update right column

3. Generate d2 diagram
   → Validate d2 code
   → Render separately
   → Show d2 diagram

4. Switch back to mermaid
   → Load saved mermaid diagram
   → Show cached SVG instantly
   → Restore zoom level
```

#### Workflow 4: Error Recovery
```
1. Submit invalid prompt
   → Show error message
   → Keep prompt in editor
   → Allow re-edit and retry

2. Network timeout during generation
   → Show timeout error
   → Enable cancel button
   → Offer retry option

3. Invalid code validation
   → Show error list with line numbers
   → Highlight error locations
   → Allow error dismiss
   → Keep code in editor

4. Render failure
   → Show error message
   → Suggest validation
   → Enable retry
```

---

## Testing Checklist

### Before Deployment
- [ ] All API endpoints respond correctly
- [ ] State updates are atomic and consistent
- [ ] Error messages are clear and actionable
- [ ] Loading states show progress
- [ ] SSE reconnection works reliably
- [ ] localStorage persistence works
- [ ] Column resizing is smooth
- [ ] Collapse/expand buttons work
- [ ] Zoom controls are responsive
- [ ] Export functionality works
- [ ] Theme colors apply correctly
- [ ] All keyboard shortcuts work
- [ ] Navigation breadcrumb displays correctly
- [ ] User menu logout works
- [ ] Notification badge counts correctly

### Performance Targets
- [ ] Agent fetch: < 1s
- [ ] Options fetch: < 1s
- [ ] Diagram generation: < 30s
- [ ] Code validation: < 30s
- [ ] Diagram rendering: < 5s
- [ ] SSE message latency: < 1s
- [ ] Page load: < 3s
- [ ] Initial render: < 2s

---

## Running Tests

### Integration Tests
```bash
npm test -- integration.test.ts
```

### Component Tests
```bash
npm test -- components/
```

### E2E Tests
```bash
npm run test:e2e
```

### Manual Testing Checklist
```
[ ] Create new diagram
[ ] Edit diagram code
[ ] Validate code
[ ] Render diagram
[ ] Export diagram
[ ] Switch diagram types
[ ] Zoom in/out
[ ] Collapse/expand columns
[ ] Change agents
[ ] View SSE messages
[ ] Cancel request
[ ] Test offline mode
[ ] Test error cases
[ ] Test localStorage persistence
```
