# SSE Status Reference - Complete Guide

## All Valid SSE Status Values

The DiagramWizard system uses the following status values throughout the LangGraph workflow and SSE stream:

---

## Status Categories

### 1. **Initialization & Analysis Phase**

| Status | Source | Meaning | Frontend Action |
|--------|--------|---------|-----------------|
| `started` | analyze_request node | Session initialized, analysis beginning | Show phase 1 "Analyzing" |
| `analyzing` | analyze_request node | Actively analyzing user input | Show phase 1 "Analyzing" |
| `analysis_complete` | analyze_request node | Initial analysis finished | Show phase 1 complete, show response |

### 2. **Clarification Phase**

| Status | Source | Meaning | Frontend Action |
|--------|--------|---------|-----------------|
| `clarifying` | clarify_prompt node | LLM asking for clarification | Show clarification Q&A interface |
| `clarification_ready` | clarify_prompt node | Clarification provided, processing | Show feedback |
| `can_proceed` | clarify_prompt node | Enough information gathered | Show proceed button |

### 3. **Waiting/Processing Status** (NEW)

| Status | Source | Meaning | Frontend Action |
|--------|--------|---------|-----------------|
| `waiting` | SSE endpoint timeout | LLM is processing (no message yet) | Log progress, show spinner |

**Note:** This is sent by the backend SSE endpoint when `asyncio.wait_for()` timeout occurs (every 60 seconds). It indicates the system is working, just no response yet.

### 4. **JSON Generation Phase**

| Status | Source | Meaning | Frontend Action |
|--------|--------|---------|-----------------|
| `generating_json` | generate_json_representation node | Creating architecture JSON | Show "Preparing structured data" |
| `json_generated` | generate_json_representation node | JSON representation complete | Show next phase |

### 5. **Diagram Type Determination**

| Status | Source | Meaning | Frontend Action |
|--------|--------|---------|-----------------|
| `type_selection` | determine_diagram_type node | Type being determined | Show diagram type options |
| `diagram_type_determined` | determine_diagram_type node | Type selected/determined | Update diagram type, move to generation |

### 6. **Code Generation Phase**

| Status | Source | Meaning | Frontend Action |
|--------|--------|---------|-----------------|
| `generating` | generate_code node | Creating diagram code | Show phase 2 "Generating" |
| `code_generated` | generate_code node | Code successfully created | Show code in editor, preview |
| `generating_json` | (see JSON section above) | Same as json_generated | - |

### 7. **Code Validation Phase**

| Status | Source | Meaning | Frontend Action |
|--------|--------|---------|-----------------|
| `validating` | validate_code node | Checking syntax | Show validation message |
| `refining` | refine_code node | Fixing validation errors | Show "Refining code..." |
| `fallback_fix` | validate_code node | Using fallback syntax fixer | Show "Attempting fix..." |
| `code_refined` | refine_code node | Refinements complete | Show refined code |

### 8. **Rendering Phase**

| Status | Source | Meaning | Frontend Action |
|--------|--------|---------|-----------------|
| `rendering` | render_diagram node | Converting code to SVG | Show "Rendering..." spinner |
| `rendered` | render_diagram node | SVG generated | Display SVG in preview |

### 9. **Terminal States**

| Status | Source | Meaning | Frontend Action |
|--------|--------|---------|-----------------|
| `completed` | render_diagram node | Entire workflow finished | Show success, enable export |
| `error` | Any node | Error occurred | Show error message, allow retry |

---

## Status Flow Diagram

```
START
  ↓
[started] → [analyzing] → [analysis_complete]
  ↓
[clarifying] ↔ (user response)
  ↓
[clarification_ready] ↔ (optional more details)
  ↓
[can_proceed]
  ↓
[generating_json] → [json_generated]
  ↓
[type_selection] → [diagram_type_determined]
  ↓
[generating] → [code_generated]
  ↓
[validating] → [refining/fallback_fix] → [code_refined]
  ↓
[rendering] → [rendered]
  ↓
[completed]
  ↓
END

(error can occur from any node at any time)
```

---

## Waiting Status (New in SSE Fix)

### What is "waiting"?

```
status: "waiting"
message: "AI is processing your request... (no response yet)"
```

### When is it sent?

- **Trigger:** Backend SSE timeout (every 60 seconds when no real messages)
- **Meaning:** LLM is actively processing, just no response yet
- **Frequency:** Every 60 seconds until LLM responds

### How is it handled?

**Backend (diagram.py):**
```python
except asyncio.TimeoutError:
    waiting_status = {
        "type": "status",
        "status": "waiting",
        "message": "AI is processing your request... (no response yet)",
        "session_id": session_id,
    }
    yield f"data: {json.dumps(waiting_status)}\n\n"
```

**Frontend (useSSE.ts):**
```typescript
if (data.status === 'waiting') {
    console.log('[useSSE] Server is waiting for LLM response:', data.message);
}
```

**Frontend (DiagramWizard.tsx):**
```typescript
case 'waiting':
    console.log('⏳ AI is processing... waiting for response');
    break;
```

### Why "waiting" instead of keep-alive?

1. **Keep-alive messages are ignored** (filtered out at line 143-145 in useSSE)
2. **"Waiting" is a real status** that gets processed
3. **Provides meaningful feedback** to frontend and user
4. **Resets keep-alive timer** so connection stays healthy
5. **Easy to debug** - visible in console logs

---

## Status in Different Contexts

### During Initial Analysis
```
started → analyzing → analysis_complete
```
User enters system description, LLM analyzes it.

### During Clarification Loop
```
analysis_complete → clarifying → clarification_ready
```
LLM asks questions, user answers. May repeat multiple times.

### During Generation
```
can_proceed → generating_json → json_generated → type_selection →
diagram_type_determined → generating → code_generated → validating →
refining (if needed) → code_refined → rendering → rendered → completed
```
System generates diagram from validated architecture.

### If LLM Takes Long Time
```
... → [waiting] → [waiting] → [waiting] → [actual_status] → ...
```
Every 60 seconds of processing, a `waiting` status is sent.

---

## Error Handling

### Error Status
```json
{
  "status": "error",
  "message": "Error description",
  "type": "error"
}
```

**When received:**
- Frontend shows error message
- SSE stream closes (auto-close on error)
- User can start new session

### Keep-Alive Messages (Legacy)
```json
{
  "type": "keep-alive"
}
```

**Handling:**
- Backend sends these during timeouts (old style)
- Frontend ignores them (filtered at line 143)
- Being replaced by "waiting" status

---

## Implementation Details

### SSE Message Format

All SSE messages follow this format:

```json
{
  "status": "one_of_valid_statuses",
  "message": "Human readable message",
  "session_id": "session-uuid-here",
  "type": "status",
  "data": {
    // Additional fields depend on status
    "history": [...],
    "clarifications": [...],
    "diagram_code": "...",
    "svg_output": "...",
    "score": 8,
    "score_info": {...}
  }
}
```

### Status Transitions

Valid transitions follow the LangGraph workflow:
- Each node outputs a new status
- Status flows from one node to next
- Branches: validation → refining OR rendering
- Terminal: completed or error

### Frontend Status Handling

The DiagramWizard component has a switch statement that handles all statuses:

```typescript
switch(statusValue) {
  case 'waiting': // ← NEW
  case 'started':
  case 'analyzing':
  case 'analysis_complete':
  case 'clarifying':
  case 'clarification_ready':
  case 'can_proceed':
  case 'type_selection':
  case 'diagram_type_determined':
  case 'generating':
  case 'code_generated':
  case 'refining':
  case 'fallback_fix':
  case 'code_refined':
  case 'generating_json':
  case 'json_generated':
  case 'completed':
  case 'error':
    // Handle each status
}
```

---

## Testing Status Values

### Check Current Status (Browser Console)
```javascript
// Watch for status updates
// Messages appear in console with timestamps
[DiagramSession] SSE update received: {status: "analyzing"}
[useSSE] Server is waiting for LLM response: AI is processing...
```

### Check Status History
```javascript
// In browser dev tools, check Network tab
// POST /api/v1/diagram/start → returns initial session
// SSE /api/v1/diagram/stream/{sessionId} → streaming updates
```

### Expected Status Sequence
```
started → analyzing → analysis_complete →
[clarifying ↔ clarification_ready]* →
can_proceed → generating_json → json_generated →
type_selection → diagram_type_determined →
generating → code_generated →
[validating → refining]* →
code_refined → rendering → rendered → completed
```

*Clarification loop repeats until clarity >= 8
*Validation/refining loop repeats until code is valid

---

## Summary Table

| Status | Node | Phase | Frontend Phase | Terminal? |
|--------|------|-------|---|---|
| started | analyze_request | 1 | Analysis | No |
| analyzing | analyze_request | 1 | Analysis | No |
| analysis_complete | analyze_request | 1 | Analysis | No |
| clarifying | clarify_prompt | 1 | Clarification | No |
| clarification_ready | clarify_prompt | 1 | Clarification | No |
| can_proceed | clarify_prompt | 1 | Ready | No |
| waiting | SSE timeout | - | Waiting | No |
| generating_json | generate_json | 1.5 | Processing | No |
| json_generated | generate_json | 1.5 | Processing | No |
| type_selection | determine_type | 1.5 | Type Select | No |
| diagram_type_determined | determine_type | 1.5 | Type Selected | No |
| generating | generate_code | 2 | Generation | No |
| code_generated | generate_code | 2 | Generation | No |
| validating | validate_code | 2 | Validation | No |
| refining | refine_code | 2 | Refining | No |
| fallback_fix | refine_code | 2 | Fallback Fix | No |
| code_refined | refine_code | 2 | Refined | No |
| rendering | render_diagram | 3 | Rendering | No |
| rendered | render_diagram | 3 | Rendered | No |
| completed | final | - | Complete | **YES** ✓ |
| error | any | - | Error | **YES** ✓ |

---

## Key Points

✅ **Total Statuses:** 20+
✅ **Terminal Statuses:** completed, error
✅ **New Status:** waiting (for LLM processing timeouts)
✅ **Keep-Alive:** Legacy, being replaced by "waiting"
✅ **Phase 1:** Analysis (analyze, clarify, json_generation)
✅ **Phase 2:** Generation (diagram type, code generation, validation)
✅ **Phase 3:** Rendering (render_diagram)

---

## References

- **Backend:** `backend/app/utils/diagram_wizard/nodes.py` (all status definitions)
- **Frontend:** `frontend/src/components/DiagramWizard/DiagramWizard.tsx` (switch statement)
- **SSE:** `backend/app/api/v1/endpoints/diagram.py` (stream endpoint)
- **Hook:** `frontend/src/hooks/useSSE.ts` (SSE handling)
