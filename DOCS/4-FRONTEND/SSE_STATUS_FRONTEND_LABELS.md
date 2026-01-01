# SSE Status → Frontend Label Mapping

## Complete Reference for All 20+ Statuses

This document maps every SSE status to its frontend UI label/display.

---

## Status to Label Mapping

### 1. **Initialization Phase**

| Status | Frontend Label | Message | UI Element | Phase |
|--------|---|---|---|---|
| `started` | "Starting Analysis" | "AI received your request and is starting the analysis..." | Info message + spinner | Phase 1 |
| `analyzing` | "Analyzing System" | "AI is analyzing your system description..." | Info message + spinner | Phase 1 |
| `analysis_complete` | "Analysis Complete" | "Analysis complete - review the assistant response." | Success message | Phase 1 |

**Code Location:** `DiagramWizard.tsx:237-253`

```typescript
case 'started':
  setCurrentPhase(1);
  message.info('AI received your request and is starting the analysis...');
  break;
case 'analyzing':
  setCurrentPhase(1);
  message.info('AI is analyzing your system description...');
  break;
case 'analysis_complete':
  setCurrentPhase(1);
  message.success('Analysis complete - review the assistant response.');
  break;
```

---

### 2. **Clarification Phase**

| Status | Frontend Label | Message | UI Element | Phase |
|--------|---|---|---|---|
| `clarifying` | "Needs Clarification" | "AI needs more information - please provide additional details" | Info message + Q&A interface | Phase 1 |
| `clarification_ready` | "Ready for Input" | "Clarification received, processing..." | Info message | Phase 1 |
| `can_proceed` | "Ready to Proceed" | "AI has sufficient information - ready to proceed!" | Success message + Proceed button | Phase 1 |

**Code Location:** `DiagramWizard.tsx:254-278`

```typescript
case 'clarifying':
  setCurrentPhase(1);
  message.info('AI needs more information - please provide additional details');
  break;
case 'clarification_ready':
case 'can_proceed':
  setCurrentPhase(1);
  message.success('AI has sufficient information - ready to proceed!');
  break;
case 'clarification_received':
  message.info('Clarification received, AI is processing...');
  break;
```

---

### 3. **Waiting Status (NEW)**

| Status | Frontend Label | Message | UI Element | Phase |
|--------|---|---|---|---|
| `waiting` | "Processing..." | (No message shown, only console log) | Console log only: "⏳ AI is processing..." | 1-3 |

**Code Location:** `DiagramWizard.tsx:233-236`

```typescript
case 'waiting':
  // Waiting for LLM response (no session message needed, it's verbose)
  console.log('⏳ AI is processing... waiting for response');
  break;
```

**Note:** `waiting` status does NOT show a message to the user because it occurs frequently during processing. Instead, it's logged to console for debugging. The UI remains in its current phase without interruption.

---

### 4. **JSON Generation Phase**

| Status | Frontend Label | Message | UI Element | Phase |
|--------|---|---|---|---|
| `generating_json` | "Preparing Data" | "AI is preparing the structured representation..." | Loading message + spinner | Phase 1.5 |
| `json_generated` | "Data Ready" | "JSON representation ready - moving to code." | Success message | Phase 1.5 |

**Code Location:** `DiagramWizard.tsx:299-308`

```typescript
case 'generating_json':
  setCurrentPhase(2);
  setIsInAnalysisPhase(false);
  message.loading('AI is preparing the structured representation...');
  break;
case 'json_generated':
  setCurrentPhase(2);
  setIsInAnalysisPhase(false);
  message.success('JSON representation ready - moving to code.');
  break;
```

---

### 5. **Diagram Type Selection**

| Status | Frontend Label | Message | UI Element | Phase |
|--------|---|---|---|---|
| `type_selection` | "Select Diagram Type" | "AI analysis complete - please select diagram type" | Info message + Type selection buttons (Mermaid/D2/PlantUML) | Phase 1 |
| `diagram_type_determined` | "Type Selected" | "Using [DiagramType] for the initial diagram - generating code..." | Success message | Phase 2 |

**Code Location:** `DiagramWizard.tsx:271-288`

```typescript
case 'type_selection':
  setCurrentPhase(1);
  setIsInAnalysisPhase(true);
  message.info('AI analysis complete - please select diagram type');
  break;
case 'diagram_type_determined': {
  const inferredType = update.diagram_type || update.diagramType || diagramType;
  setDiagramType(inferredType);
  setCurrentPhase(2);
  setIsInAnalysisPhase(false);
  message.success(`Using ${inferredType} for the initial diagram - generating code...`);
  break;
}
```

---

### 6. **Code Generation Phase**

| Status | Frontend Label | Message | UI Element | Phase |
|--------|---|---|---|---|
| `generating` | "Generating Code" | "AI is generating diagram code..." | Loading message + spinner | Phase 2 |
| `code_generated` | "Code Ready" | "Initial diagram code is ready - review or render it." | Success message | Phase 2 |

**Code Location:** `DiagramWizard.tsx:290-299`

```typescript
case 'generating':
  setCurrentPhase(2);
  setIsInAnalysisPhase(false);
  message.loading('AI is generating diagram code...');
  break;
case 'code_generated':
  setCurrentPhase(2);
  setIsInAnalysisPhase(false);
  message.success('Initial diagram code is ready - review or render it.');
  break;
```

---

### 7. **Code Validation Phase**

| Status | Frontend Label | Message | UI Element | Phase |
|--------|---|---|---|---|
| `validating` | "Validating Code" | (No specific message - passes through) | (No specific UI) | Phase 2 |
| `refining` | "Refining Code" | "AI is refining the diagram code for better accuracy..." | Warning message + spinner | Phase 2 |
| `fallback_fix` | "Fixing Errors" | "AI is refining the diagram code for better accuracy..." | Warning message | Phase 2 |
| `code_refined` | "Code Fixed" | "Refinements applied - code ready for preview." | Success message | Phase 2 |

**Code Location:** `DiagramWizard.tsx:300-309`

```typescript
case 'refining':
case 'fallback_fix':
  setCurrentPhase(2);
  setIsInAnalysisPhase(false);
  message.warning('AI is refining the diagram code for better accuracy...');
  break;
case 'code_refined':
  setCurrentPhase(2);
  setIsInAnalysisPhase(false);
  message.success('Refinements applied - code ready for preview.');
  break;
```

---

### 8. **Rendering Phase**

| Status | Frontend Label | Message | UI Element | Phase |
|--------|---|---|---|---|
| `rendering` | "Rendering SVG" | (No specific message for rendering) | SVG preview begins updating | Phase 3 |
| `rendered` | "Preview Ready" | (No specific message) | SVG displayed in preview panel | Phase 3 |

**Code Location:** `DiagramWizard.tsx` (currently no explicit message)

These statuses update the UI components but don't show explicit messages. The SVG preview panel updates automatically when `svgOutput` is available.

---

### 9. **Terminal States**

| Status | Frontend Label | Message | UI Element | Phase |
|--------|---|---|---|---|
| `completed` | "Complete! ✅" | "dYZ% Diagram generated successfully!" | Success message + enable export/download buttons | Phase 3 Complete |
| `error` | "Error ❌" | "Error: [error message]" | Error alert + retry options | Error |

**Code Location:** `DiagramWizard.tsx:309-333`

```typescript
case 'completed':
  setCurrentPhase(3);
  setIsInAnalysisPhase(false);
  message.success('dYZ% Diagram generated successfully!');

  if (persistedState.preferences.autoSave && sessionId && status) {
    const savedSession: SavedSession = {
      sessionId,
      timestamp: Date.now(),
      initialPrompt: userInput,
      diagramType: diagramType,
      diagramCode: status.diagramCode || '',
      svgOutput: status.svgOutput || '',
      conversationHistory: status.history || [],
      score: score,
      scoreInfo: status.score_info,
    };
    saveSessionToHistory(savedSession);
    message.success('Session saved to history');
  }

  if (onDiagramGenerated && status) {
    onDiagramGenerated(status.diagramCode, status.svgOutput);
  }
  break;
case 'error':
  setIsInAnalysisPhase(false);
  message.error(`Error: ${update.message || 'Unknown error occurred'}`);
  break;
```

---

## Summary Table: All 20+ Statuses

| # | Status | Label | Message | Phase | Terminal? |
|---|--------|-------|---------|-------|-----------|
| 1 | started | Starting Analysis | "AI received your request..." | 1 | No |
| 2 | analyzing | Analyzing System | "AI is analyzing your system..." | 1 | No |
| 3 | analysis_complete | Analysis Complete | "Analysis complete..." | 1 | No |
| 4 | clarifying | Needs Clarification | "AI needs more information..." | 1 | No |
| 5 | clarification_ready | Ready for Input | "Clarification received..." | 1 | No |
| 6 | can_proceed | Ready to Proceed | "AI has sufficient information..." | 1 | No |
| 7 | waiting | Processing... | (console log only) | 1-3 | No |
| 8 | generating_json | Preparing Data | "AI is preparing structured representation..." | 1.5 | No |
| 9 | json_generated | Data Ready | "JSON representation ready..." | 1.5 | No |
| 10 | type_selection | Select Diagram Type | "AI analysis complete - select type" | 1 | No |
| 11 | diagram_type_determined | Type Selected | "Using [Type] for diagram..." | 2 | No |
| 12 | generating | Generating Code | "AI is generating diagram code..." | 2 | No |
| 13 | code_generated | Code Ready | "Initial diagram code is ready..." | 2 | No |
| 14 | validating | Validating Code | (no message) | 2 | No |
| 15 | refining | Refining Code | "AI is refining the diagram code..." | 2 | No |
| 16 | fallback_fix | Fixing Errors | "AI is refining the diagram code..." | 2 | No |
| 17 | code_refined | Code Fixed | "Refinements applied..." | 2 | No |
| 18 | rendering | Rendering SVG | (no message) | 3 | No |
| 19 | rendered | Preview Ready | (no message) | 3 | No |
| 20 | completed | Complete! ✅ | "Diagram generated successfully!" | 3 | **YES** |
| 21 | error | Error ❌ | "Error: [message]" | - | **YES** |

---

## Message Types

### Info Messages (Blue)
```typescript
message.info('...')
```
**Used for:** started, analyzing, clarifying, type_selection, clarification_received
**Appearance:** Blue info icon + dismissible notification
**Duration:** Auto-dismiss after 3 seconds

### Loading Messages (with spinner)
```typescript
message.loading('...')
```
**Used for:** generating, generating_json
**Appearance:** Spinner + message, doesn't auto-dismiss
**Duration:** Stays until next update

### Success Messages (Green)
```typescript
message.success('...')
```
**Used for:** analysis_complete, can_proceed, code_generated, json_generated, code_refined, diagram_type_determined, completed
**Appearance:** Green check icon + notification
**Duration:** Auto-dismiss after 3 seconds

### Warning Messages (Orange)
```typescript
message.warning('...')
```
**Used for:** refining, fallback_fix
**Appearance:** Orange warning icon + notification
**Duration:** Auto-dismiss after 3 seconds

### Error Messages (Red)
```typescript
message.error('...')
```
**Used for:** error
**Appearance:** Red X icon + alert box
**Duration:** Stays visible, user must dismiss

---

## Phase Indicators

### What the user sees for each phase:

**Phase 1: Analysis & Clarification**
- Steps indicator shows "Phase 1" highlighted
- Left panel shows conversation history
- Right panel shows clarification Q&A interface
- Status messages update as analysis progresses

**Phase 2: Code Generation**
- Steps indicator shows "Phase 2" highlighted
- Left panel shows conversation history
- Right panel shows code editor with syntax highlighting
- Preview tab shows live SVG rendering
- Tabs: Preview | Code | JSON

**Phase 3: Rendering**
- Steps indicator shows "Phase 3" highlighted
- SVG preview updates
- Export/Download buttons enabled
- Session can be saved

**Error State:**
- Alert box shows error message
- User can see error in left panel
- "End Session" button available
- Can start new session

---

## Special Cases

### `waiting` Status (NEW)
**Not shown to user directly.** Only appears in console log:
```
⏳ AI is processing... waiting for response
```

This is by design because:
- Occurs frequently (every 60 seconds during LLM processing)
- Would spam the UI with messages
- Doesn't require user action
- Console log is for debugging/monitoring

### `clarification_received`
**Unique message** (not tied to phase change):
```
message.info('Clarification received, AI is processing...')
```
Shows that user's response was accepted and system is now processing.

### `validating`
**No explicit message** - system continues silently validating code before rendering.

### `rendering` & `rendered`
**No explicit messages** - SVG preview updates automatically when ready. User sees the diagram appear in the preview panel.

---

## Frontend Status Switch Block

**Complete code location:** `DiagramWizard.tsx:232-345`

```typescript
const statusValue = update.status;
switch (statusValue) {
  case 'waiting':
    console.log('⏳ AI is processing... waiting for response');
    break;
  case 'started':
    setCurrentPhase(1);
    setIsInAnalysisPhase(true);
    message.info('AI received your request and is starting the analysis...');
    break;
  case 'analyzing':
    setCurrentPhase(1);
    setIsInAnalysisPhase(true);
    message.info('AI is analyzing your system description...');
    break;
  case 'analysis_complete':
    setCurrentPhase(1);
    setIsInAnalysisPhase(true);
    message.success('Analysis complete - review the assistant response.');
    break;
  case 'clarifying':
    setCurrentPhase(1);
    setIsInAnalysisPhase(true);
    message.info('AI needs more information - please provide additional details');
    break;
  case 'clarification_ready':
  case 'can_proceed':
    setCurrentPhase(1);
    setIsInAnalysisPhase(true);
    message.success('AI has sufficient information - ready to proceed!');
    break;
  case 'type_selection':
    setCurrentPhase(1);
    setIsInAnalysisPhase(true);
    message.info('AI analysis complete - please select diagram type');
    break;
  case 'clarification_received':
    message.info('Clarification received, AI is processing...');
    break;
  case 'diagram_type_determined': {
    const inferredType = update.diagram_type || update.diagramType || diagramType;
    setDiagramType(inferredType);
    setCurrentPhase(2);
    setIsInAnalysisPhase(false);
    message.success(`Using ${inferredType} for the initial diagram - generating code...`);
    break;
  }
  case 'generating':
    setCurrentPhase(2);
    setIsInAnalysisPhase(false);
    message.loading('AI is generating diagram code...');
    break;
  case 'code_generated':
    setCurrentPhase(2);
    setIsInAnalysisPhase(false);
    message.success('Initial diagram code is ready - review or render it.');
    break;
  case 'refining':
  case 'fallback_fix':
    setCurrentPhase(2);
    setIsInAnalysisPhase(false);
    message.warning('AI is refining the diagram code for better accuracy...');
    break;
  case 'code_refined':
    setCurrentPhase(2);
    setIsInAnalysisPhase(false);
    message.success('Refinements applied - code ready for preview.');
    break;
  case 'generating_json':
    setCurrentPhase(2);
    setIsInAnalysisPhase(false);
    message.loading('AI is preparing the structured representation...');
    break;
  case 'json_generated':
    setCurrentPhase(2);
    setIsInAnalysisPhase(false);
    message.success('JSON representation ready - moving to code.');
    break;
  case 'completed':
    setCurrentPhase(3);
    setIsInAnalysisPhase(false);
    message.success('dYZ% Diagram generated successfully!');
    // ... save session, call callback ...
    break;
  case 'error':
    setIsInAnalysisPhase(false);
    message.error(`Error: ${update.message || 'Unknown error occurred'}`);
    break;
  default:
    break;
}
```

---

## User Experience Flow

### Typical Happy Path - Console Output vs UI Messages

```
Timeline | Console Log | Frontend Message | Phase | UI
---------|-------------|------------------|-------|---
T+0s     | 🚀 Starting | (starting) | 1 | Model selected
T+1s     | started | ℹ️ "AI received your request..." | 1 | Analyze
T+2s     | analyzing | (auto-dismiss) | 1 | Analyze
T+15s    | ⏳ waiting | (console only) | 1 | Analyze
T+30s    | ⏳ waiting | (console only) | 1 | Analyze
T+45s    | analysis_complete | ✅ "Analysis complete..." | 1 | Show response
T+46s    | clarifying | ℹ️ "AI needs more info..." | 1 | Q&A interface
T+60s    | (user answers) | - | 1 | Waiting for processing
T+65s    | ⏳ waiting | (console only) | 1 | Processing
T+70s    | clarification_ready | ℹ️ "Clarification received..." | 1 | Processing
T+75s    | can_proceed | ✅ "Ready to proceed!" | 1 | Proceed button
T+76s    | (user proceeds) | - | 1 | Proceeding
T+80s    | generating_json | ⏳ "Preparing data..." | 1.5 | Preparing
T+90s    | json_generated | ✅ "Data ready..." | 1.5 | Ready
T+95s    | type_selection | ℹ️ "Select diagram type..." | 1 | Type buttons
T+96s    | (user selects) | - | - | Selected
T+100s   | diagram_type_determined | ✅ "Using Mermaid..." | 2 | Generate
T+105s   | generating | ⏳ "Generating code..." | 2 | Spinner
T+120s   | code_generated | ✅ "Code ready..." | 2 | Code editor
T+121s   | (validation) | - | 2 | Silent check
T+130s   | rendering | (no message) | 3 | SVG renders
T+135s   | rendered | (no message) | 3 | Preview ready
T+136s   | completed | ✅ "Generated successfully!" | 3 | Export enabled
```

---

## Key Insights

1. **`waiting` is intentionally hidden** - console-only, no UI spam
2. **Messages progress through 3 phases** - clear visual progression
3. **Terminal states are clear** - success (green) or error (red)
4. **No messages for silent operations** - validation, rendering happen without notifications
5. **Loading messages stay visible** - until replaced by next status
6. **Info messages auto-dismiss** - after 3 seconds, keeping UI clean

