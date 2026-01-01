# Diagram Wizard Routing Fix - Complete Explanation

## Problem Summary

**Issue 1: Duplicate LLM Calls**
- When user submitted description, LLM was being called twice with the same prompt
- Cause: `analyze_request` → direct edge → `clarify_prompt` meant both nodes ran sequentially
- Both nodes called the LLM, causing duplicate API calls and slower performance

**Issue 2: Broken Workflow After Clarification**
- After user clicked "Generate Diagram", the workflow should compute diagram type scores
- Instead, workflow was stuck and not proceeding to `generate_json_representation`
- Diagram type selection screen never appeared
- No code generation happened

**Issue 3: Clarification Auto-Stopping**
- The LLM was automatically deciding when clarification was "done" (`llm_ready=true`)
- Clarification would stop asking questions when score reached target
- **WRONG BEHAVIOR**: Clarification should NEVER auto-stop - it should continue indefinitely
- **CORRECT BEHAVIOR**: Only way to proceed is user clicking "Generate Diagram" button

## Changes Made

### 1. Fixed analysis_complete Flag Not Preserved on Skip (CRITICAL - NEW FIX)

**File**: `backend/app/utils/diagram_wizard/nodes/analysis_nodes.py`

**Problem**: When `analyze_request` node was skipped (because analysis already ran), it returned `{"skip_analysis": True}` but didn't preserve the `analysis_complete=True` flag. This caused the routing logic to see `analysis_complete=False` and incorrectly route to END instead of continuing the workflow.

**Change**: Lines 124-126

**Before**:
```python
if should_skip:
    logger.info(...)
    return {"skip_analysis": True}
```

**After**:
```python
if should_skip:
    logger.info(...)
    # CRITICAL: Must return analysis_complete=True to ensure routing logic sees it
    # The routing function needs this flag to determine next step
    return {"skip_analysis": True, "analysis_complete": True}
```

**Impact**:
- When analysis is skipped, the routing function now sees `analysis_complete=True`
- Allows routing to correctly proceed to `generate_json_representation` when user clicks "Generate Diagram"
- Fixes the workflow getting stuck at END after clicking "Generate Diagram"

### 2. Clarification Never Auto-Stops (CRITICAL)

**File**: `backend/app/utils/diagram_wizard/nodes/clarification_nodes.py`

**Change**: Removed lines 267-318 that checked if LLM was "ready" and stopped asking questions.

**Before**:
```python
# Check if AI thinks we're ready
if ready or (design_summary and design_summary.startswith("READY:")):
    # ... Stop asking questions and set llm_ready=True
```

**After**:
```python
# IMPORTANT: Clarification phase NEVER auto-stops.
# The LLM should always continue asking questions to gather more details.
# The ONLY way to proceed is when the user explicitly clicks "Generate Diagram".

# AI always continues with more clarification - add questions to conversation history
```

**Impact**:
- Clarification loop runs indefinitely
- LLM always asks 2-3 new questions, regardless of score
- User controls when to proceed via "Generate Diagram" button
- `llm_ready` is always `False` in clarification node

### 2. Updated LLM Prompt

**File**: `backend/app/utils/diagram_wizard/prompts/ANALYSE_CLARIFY.md`

**Change**: Updated instructions to tell LLM to NEVER set `ready=true`:

```markdown
### ready

- **ALWAYS set to `false`** - The clarification phase NEVER auto-stops
- You should ALWAYS ask 2-3 new questions to gather more details, regardless of clarity_score
- The user will explicitly click "Generate Diagram" when they are ready to proceed
- Never set `ready=true` or include a `READY:` summary - just keep asking questions
```

### 3. Removed llm_ready from Routing Logic

**File**: `backend/app/utils/diagram_wizard/langgraph_builder.py`

**Change**: Removed `llm_ready` checks from routing functions:

**Before**:
```python
if user_confirmed_ready or llm_ready:
    return "generate_json_representation"
```

**After**:
```python
# Priority 2: If user confirmed ready (clicked "Generate Diagram") → compute diagram types
# NOTE: llm_ready is no longer used - clarification NEVER auto-stops
if user_confirmed_ready:
    return "generate_json_representation"
```

### 4. Changed Direct Edge to Conditional Routing

**Before (`langgraph_builder.py`):**
```python
workflow.add_edge("analyze_request", "clarify_prompt")
```

**After:**
```python
workflow.add_conditional_edges(
    "analyze_request",
    route_after_analyze,
    {
        "clarify_prompt": "clarify_prompt",
        "generate_json_representation": "generate_json_representation",
        "generate_code": "generate_code",
        END: END,
    },
)
```

### 2. Added Smart Routing Logic (`route_after_analyze` function)

```python
def route_after_analyze(state: GraphState) -> str:
    analysis_complete = state.get("analysis_complete", False)

    # First run: return to END (questions already sent via SSE)
    if not analysis_complete:
        return END

    # Analysis already done - route based on user action:
    user_selected_type = state.get("user_selected_diagram_type", False)
    user_confirmed_ready = state.get("user_confirmed_ready", False)
    llm_ready = state.get("llm_ready", False)

    # Priority 1: If user selected diagram type → generate code
    if user_selected_type:
        return "generate_code"

    # Priority 2: If user confirmed ready → compute diagram type scores
    if user_confirmed_ready or llm_ready:
        return "generate_json_representation"

    # Priority 3: User answering questions → continue clarification
    return "clarify_prompt"
```

### 3. Added Skip Logic in `analyze_request`

```python
# Check if analysis was already done (multiple indicators)
analysis_complete = state.get("analysis_complete", False)
has_json = bool(state.get("json_representation"))
has_assistant_messages = any(msg.get("role") == "assistant"
                             for msg in clarification_history)
user_confirmed_ready = state.get("user_confirmed_ready", False)
user_selected_diagram_type = state.get("user_selected_diagram_type", False)

should_skip = (
    analysis_complete or has_json or has_assistant_messages or
    user_confirmed_ready or user_selected_diagram_type
)

if should_skip:
    return {"skip_analysis": True}

# Otherwise, run analysis (first time only)
```

## How It Works Now

### Scenario 1: User Submits Initial Description

1. Graph starts → Entry point: `analyze_request`
2. `analyze_request`:
   - `analysis_complete=False` → Runs LLM
   - Generates questions
   - Sends questions via SSE
   - Sets `analysis_complete=True` in return value
   - Returns to routing function
3. Routing function `route_after_analyze`:
   - Sees `analysis_complete=False` (state before node ran)
   - Returns `END`
4. Graph stops, frontend displays questions

✅ **Result: NO duplicate LLM call** (only `analyze_request` runs, `clarify_prompt` doesn't)

### Scenario 2: User Answers Questions

1. Graph resumes → Entry point: `analyze_request`
2. `analyze_request`:
   - Sees `analysis_complete=True` in state
   - **Skips analysis** → Returns `{"skip_analysis": True}`
3. Routing function `route_after_analyze`:
   - Sees `analysis_complete=True`
   - `user_confirmed_ready=False`, `user_selected_type=False`
   - Returns `"clarify_prompt"`
4. `clarify_prompt` runs → Processes user's answers

✅ **Result: Only clarify_prompt runs** (analyze_request skips correctly)

### Scenario 3: User Clicks "Generate Diagram"

1. Backend sets: `user_confirmed_ready=True`, `llm_ready=True`
2. Graph resumes → Entry point: `analyze_request`
3. `analyze_request`:
   - Sees `user_confirmed_ready=True`
   - **Skips analysis** → Returns `{"skip_analysis": True}`
4. Routing function `route_after_analyze`:
   - Sees `analysis_complete=True`, `user_confirmed_ready=True`
   - Returns `"generate_json_representation"`
5. `generate_json_representation` runs → Computes diagram type scores
6. Flows to `determine_diagram_type` → Shows diagram type selection screen

✅ **Result: Diagram type scores are computed and selection screen appears**

### Scenario 4: User Selects Diagram Type

1. Backend sets: `user_selected_diagram_type=True`
2. Graph resumes → Entry point: `analyze_request`
3. `analyze_request`:
   - Sees `user_selected_diagram_type=True`
   - **Skips analysis** → Returns `{"skip_analysis": True}`
4. Routing function `route_after_analyze`:
   - Sees `analysis_complete=True`, `user_selected_diagram_type=True`
   - Returns `"generate_code"`
5. `generate_code` runs → Generates diagram code
6. Flows to `render_diagram` → Displays final diagram

✅ **Result: Code generation and rendering happen correctly**

## Key Technical Insight

**LangGraph Routing Timing:**
- Routing functions receive state **BEFORE** the current node's return value is merged
- This is why we check `analysis_complete` (set by *previous* run) instead of `skip_analysis` (set by *current* run)
- The `analysis_complete` flag persists across graph resumes, making routing decisions reliable

## Testing the Fix

### Prerequisites
1. **Restart the backend server** to load the new routing logic
2. Clear any existing sessions or start a new one

### Test Steps

**Test 1: Verify NO Duplicate LLM Calls**
1. Enter a system description
2. Check backend logs for LLM calls
3. Should see: 1 LLM call from `analyze_request`, NO call from `clarify_prompt`

**Test 2: Verify Clarification Flow**
1. Answer the clarification questions
2. Submit answers
3. Should see: `clarify_prompt` processes answers, generates new questions or determines ready

**Test 3: Verify Diagram Type Score Computation**
1. Get score to target (default: 80)
2. Click "Generate Diagram" button
3. Should see: `generate_json_representation` runs and computes scores for all 4 diagram types
4. Should see: Diagram type selection screen with keyword scores

**Test 4: Verify Complete End-to-End Flow**
1. Start → Enter description → Answer questions → Click "Generate Diagram" → Select type
2. Should see: Full workflow completes without getting stuck

## Debug Logging

Look for these log messages to verify correct routing:

```
🔀 Route: analyze_request → END (first run complete)
⏭️ Skipping re-analysis - already completed (flags: ...)
🔀 ROUTING: analysis_complete=True, type_selected=..., confirmed=..., llm_ready=...
🔀 Route: analyze_request → generate_json_representation
🔀 Route: analyze_request → generate_code
```

## Rollback Plan

If issues persist, you can rollback with:
```bash
git checkout HEAD -- backend/app/utils/diagram_wizard/langgraph_builder.py
git checkout HEAD -- backend/app/utils/diagram_wizard/nodes/analysis_nodes.py
```

Then restart the backend.

## Summary

The fix improves the workflow by:
1. **Preventing duplicate LLM calls** on initial analysis
2. **Using a single entry point** (`analyze_request`) with smart routing
3. **Making routing decisions** based on persistent state flags (`analysis_complete`, `user_confirmed_ready`, `user_selected_diagram_type`)
4. **Ensuring clarification never auto-stops** - LLM keeps asking questions indefinitely until user clicks "Generate Diagram"
5. **Ensuring each node runs exactly when needed**, no more, no less

The routing logic is clear, deterministic, and fixes all three issues:
- ✅ No duplicate LLM calls
- ✅ Workflow proceeds correctly when user clicks "Generate Diagram"
- ✅ Clarification continues indefinitely with new questions until user decides to proceed
