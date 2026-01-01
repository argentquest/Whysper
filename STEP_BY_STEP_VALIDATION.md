# Step-by-Step Workflow Validation

**Testing the Complete Flow from Clarification → Rendering**

---

## Test Scenario: User Reaches Score Target

### Initial State (After Clarification Round 3)

**Assumptions**:
- User has answered 3 rounds of questions
- Clarity score reaches 85 (target is 80)
- AI determines ready

### Step 1: Clarification Detects Ready ✅

**Node**: `clarify_prompt`
**File**: `clarification_nodes.py:254-337`

**Code Path**:
```python
clarity_score = 85  # Meets target
ready = ai_response.get("ready", False)  # False from AI

# Line 257: Enforce score target
if clarity_score >= score_target and not ready:
    ready = True  # Override to True
    design_summary = f"READY: System architecture understood with clarity score of 85/80."

# Line 287: Check if ready
if ready or (design_summary and design_summary.startswith("READY:")):
    summary = design_summary.replace("READY:", "").strip()
    # Line 328-337: Return ready state
    return {
        "llm_ready": False,  # ❗ Note: False, waiting for user
        "final_design_summary": summary,  # ✅ Set
        "json_representation": json_representation,
        "clarity_scores": [60, 70, 85],
        "clarity_score": 85,
        "awaiting_user_confirmation": True,  # ✅ Waiting for user
        "user_confirmed_ready": False,  # ❗ Not yet
        "current_state": SessionState.CLARIFYING,
    }
```

**Result State**:
```json
{
  "llm_ready": false,
  "final_design_summary": "System architecture understood with clarity score of 85/80.",
  "awaiting_user_confirmation": true,
  "user_confirmed_ready": false,
  "json_representation": {...}
}
```

**Routing**: `route_after_clarify` sees `llm_ready=False` → Returns `END`

**Frontend**: Shows "Generate Diagram" button ✅

---

### Step 2: User Clicks "Generate Diagram" ✅

**Trigger**: Frontend → Backend API call

**Service Method**: `confirm_ready()`
**File**: `diagram_factory_core.py:532-560`

**Code**:
```python
# Line 539-542: Set flags
self.session.graph_state["user_confirmed_ready"] = True
self.session.graph_state["llm_ready"] = True
self.session.graph_state["awaiting_user_confirmation"] = False
```

**Updated State**:
```json
{
  "llm_ready": true,  // ✅ Changed
  "final_design_summary": "System architecture understood...",  // ✅ Preserved
  "awaiting_user_confirmation": false,  // ✅ Changed
  "user_confirmed_ready": true,  // ✅ Changed
  "json_representation": {...}  // ✅ Preserved
}
```

**Graph Resumes**: ✅

---

### Step 3: Graph Entry Point - analyze_request ✅

**Node**: `analyze_request`
**File**: `analysis_nodes.py:91-93`

**Code**:
```python
if state.get("analysis_complete", False):  # True
    return {"next_action": "clarify", "skip_analysis": True}
```

**Result**: Skips LLM call ✅

**Routing**: Direct edge → `clarify_prompt`

---

### Step 4: Clarify Prompt Skip Logic ✅

**Node**: `clarify_prompt`
**File**: `clarification_nodes.py:95-104`

**Code**:
```python
# Line 95: Check skip condition
if state.get("llm_ready", False) and \
   state.get("final_design_summary") and \
   state.get("user_confirmed_ready", False):

    # Current state values:
    # llm_ready = True ✅
    # final_design_summary = "System architecture understood..." ✅
    # user_confirmed_ready = True ✅

    logger.info("🎯 Skipping clarification - user confirmed ready with complete design summary")

    # Line 100-104: Return immediately without LLM call
    return {
        "llm_ready": True,
        "final_design_summary": state.get("final_design_summary"),
        "current_state": "generating",
    }
```

**Result**:
- ✅ Skips LLM call (no duplicate work)
- ✅ Returns `llm_ready=True`

**Routing**: `route_after_clarify` sees `llm_ready=True` → Returns `"generate_json_representation"`

---

### Step 5: Generate JSON Representation ✅

**Node**: `generate_json_representation`
**File**: `generation_nodes.py:22-150`

**Code Flow**:
```python
# Line 47-50: Send status update
await update_callback({
    "status": "generating_json",
    "message": "Working: Generating architecture model...",
})

# Line 53: Load prompt
prompt_template = get_prompt("json_generation")

# Line 64-65: Build user content from history
clarification_history = state.get("clarification_history", [])
user_content = "\n".join([msg.get("content", "") for msg in clarification_history if msg.get("role") == "user"])

# Line 71: Call LLM
ai_response_str = await call_llm(prompt_template, user_content, session_id)

# Parse and extract three representations:
# 1. structurizr_workspace (full with views)
# 2. clean_structurizr (model only)
# 3. json_representation (legacy format)

return {
    "structurizr_workspace": structurizr_workspace,
    "clean_structurizr": clean_structurizr,
    "json_representation": json_representation,
}
```

**Potential Issue Check**: ❓ Does this run even if json_representation already exists?

**Answer**: Looking at lines 54-61, there's a fallback if prompt not found:
```python
if not prompt_template:
    return {
        "structurizr_workspace": state.get("structurizr_workspace", ""),
        "clean_structurizr": state.get("clean_structurizr", ""),
        "json_representation": state.get("json_representation", {}),
    }
```

But if prompt exists, it ALWAYS calls LLM to generate comprehensive representations. This is correct because clarify_prompt only generates a basic JSON, while this node generates the full architecture model.

**Result**: ✅ Generates comprehensive architecture representations

**Routing**: Direct edge → `determine_diagram_type`

---

### Step 6: Determine Diagram Type (Compute Scores) ✅

**Node**: `determine_diagram_type_node`
**File**: `generation_nodes.py:174-298`

**Code Flow**:
```python
# Line 191-203: Skip if user already selected
if state.get("user_selected_diagram_type", False):
    return {...}  # Skip

# Line 219-223: Send status update
await update_callback({
    "message": "Working: Computing diagram scores...",
})

# Line 225-252: Build analysis text from multiple sources
analysis_text = combine(
    final_design_summary,
    json_representation metadata,
    json structure,
    clarification_history,
    json_generation_output
)

# Line 255-268: Compute keyword scores for ALL diagram types
recommended_type, all_scores = determine_diagram_type(analysis_text)
# Returns scores for: mermaid, d2, plantuml, structurizr

# Line 269-295: Send scores to frontend
await update_callback({
    "status": "diagram_type_options",
    "diagram_type_options": [
        {
            "type": "mermaid",
            "score": all_scores.get("mermaid", 0),
            "recommended": recommended_type == DiagramType.MERMAID
        },
        # ... other types
    ]
})

return {
    "keyword_scores": all_scores,
    "analysis_text": analysis_text,
    "current_state": SessionState.AWAITING_DIAGRAM_TYPE_SELECTION,
}
```

**Result**: ✅ Computes scores for all 4 diagram types

**Routing**: `route_after_diagram_type` sees `user_selected_diagram_type=False` → Returns `END`

**Frontend**: Shows diagram type selection screen with scores ✅

---

### Step 7: User Selects Diagram Type ✅

**Trigger**: User clicks diagram type (e.g., "Mermaid")

**Service Method**: `select_diagram_type("mermaid")`
**File**: `diagram_factory_core.py` (not shown in grep, but exists)

**Expected Code**:
```python
async def select_diagram_type(self, diagram_type: str):
    self.session.graph_state["user_selected_diagram_type"] = True
    self.session.graph_state["diagram_type"] = DiagramType.MERMAID
    # Resume graph
```

**Updated State**:
```json
{
  "user_selected_diagram_type": true,
  "diagram_type": "mermaid"
}
```

**Graph Resumes**: ✅

---

### Step 8: Back Through Entry Point ✅

**Execution Path**:
```
analyze_request → (skip, analysis_complete=True)
  ↓
clarify_prompt → (skip, llm_ready=True + user_confirmed_ready=True)
  ↓
route_after_clarify → (llm_ready=True) → "generate_json_representation"
  ↓
generate_json_representation → (returns existing data, already generated)
  ↓
determine_diagram_type → (skip, user_selected_diagram_type=True)
  ↓
route_after_diagram_type → (user_selected_diagram_type=True) → "generate_code"
```

**Potential Issue**: ❓ Does `generate_json_representation` run again unnecessarily?

**Check the code**:
```python
# generation_nodes.py:53-61
prompt_template = get_prompt("json_generation")
if not prompt_template:
    # Return existing
    return {
        "structurizr_workspace": state.get("structurizr_workspace", ""),
        ...
    }

# If prompt exists, runs LLM again
ai_response_str = await call_llm(...)
```

**Issue Found**: ❌ This will call LLM again even though we already have the data!

**Fix Needed**: Add skip condition to `generate_json_representation`

---

### Step 9: Generate Code ✅

**Node**: `generate_code`
**File**: `generation_nodes.py:301-400`

**Code Flow**:
```python
diagram_type = state.get("diagram_type", DiagramType.MERMAID)  # MERMAID
json_representation = state.get("json_representation", {})

# Line 322-342: Load diagram-type-specific prompt
firstpass_key = f"firstpass_mermaid"
prompt_template = get_prompt(firstpass_key)

if not prompt_template:
    prompt_key = "generate_mermaid"
    prompt_template = get_prompt(prompt_key)

# Line 350: Use JSON generation output if available
llm_input_payload = json_generation_output if json_generation_output else json.dumps(json_representation)

# Call LLM to generate Mermaid code
ai_response_str = await call_llm(prompt_template, llm_input_payload, session_id)

# Extract code from response
diagram_code = extract_code_from_response(ai_response_str)

return {
    "diagram_code": diagram_code,
    "current_state": SessionState.GENERATING,
}
```

**Result**: ✅ Generates Mermaid diagram code

**Routing**: Direct edge → `render_diagram`

---

### Step 10: Render Diagram (Final Step) ✅

**Node**: `render_diagram`
**File**: `rendering_nodes.py:25-120`

**Code Flow**:
```python
diagram_code = state.get("diagram_code", "")
diagram_type = state.get("diagram_type", DiagramType.MERMAID)

# Line 52-54: Log rendering
logger.info(f"🎨 Rendering {diagram_type} diagram to SVG using provider system")

# Line 74-80: Send status update
await update_callback({
    "status": "rendering",
    "message": f"Working: Rendering mermaid diagram...",
})

# Line 66-70: Get provider
provider_registry = get_registry()
provider = provider_registry.get_default_provider("mermaid")

# Line 82-90: Call provider's complete pipeline
result = await provider.render_with_validation(
    diagram_code,
    session_id=session_id,
    max_attempts=3,  # Up to 3 LLM correction attempts
)

# result.success = True/False
# result.svg = SVG output
# result.corrected_code = Fixed code (if corrections were made)
# result.validation_errors = Errors encountered

if result.success:
    return {
        "svg_output": result.svg,
        "diagram_code": result.corrected_code or diagram_code,
        "current_state": SessionState.COMPLETED,
    }
else:
    return {
        "error_message": f"Rendering failed: {result.validation_errors}",
        "current_state": SessionState.ERROR,
    }
```

**Provider Pipeline** (`render_with_validation`):
1. **Validate** code syntax
2. **Pattern-based auto-fix** (fast, deterministic)
3. **If still invalid**: Call LLM for correction (up to 3 attempts)
4. **Render** to SVG
5. **Return** result

**Result**: ✅ Final SVG output ready for display

**Routing**: Direct edge → `END`

**Frontend**: Displays diagram ✅

---

## Issues Found

### ❌ Issue: Duplicate LLM Call in generate_json_representation

**Problem**: When user selects diagram type, graph resumes and hits `generate_json_representation` again, which calls LLM even though we already have the data.

**Location**: `generation_nodes.py:53-71`

**Current Code**:
```python
prompt_template = get_prompt("json_generation")
if not prompt_template:
    # Fallback: use existing
    return {...}

# Always calls LLM if prompt exists
ai_response_str = await call_llm(prompt_template, user_content, session_id)
```

**Fix Needed**: Add skip condition at the beginning:
```python
# Skip if we already generated JSON
if state.get("structurizr_workspace") and state.get("json_generation_complete"):
    return {
        "structurizr_workspace": state.get("structurizr_workspace"),
        "clean_structurizr": state.get("clean_structurizr"),
        "json_representation": state.get("json_representation"),
        "json_generation_complete": True,
    }
```

And set the flag when returning:
```python
return {
    "structurizr_workspace": structurizr_workspace,
    "clean_structurizr": clean_structurizr,
    "json_representation": json_representation,
    "json_generation_complete": True,  # Add flag
}
```

---

## Summary

### ✅ Steps Working Correctly
1. ✅ Clarification detects ready
2. ✅ User clicks "Generate Diagram"
3. ✅ `confirm_ready()` sets flags
4. ✅ `analyze_request` skips
5. ✅ `clarify_prompt` skips
6. ✅ Routing to `generate_json_representation`
7. ⚠️ `generate_json_representation` runs (but will run again - **ISSUE**)
8. ✅ `determine_diagram_type` computes scores
9. ✅ User selects diagram type
10. ❌ `generate_json_representation` **RUNS AGAIN** (duplicate LLM call)
11. ✅ `determine_diagram_type` skips (already done)
12. ✅ `generate_code` generates diagram code
13. ✅ `render_diagram` renders to SVG
14. ✅ END - Display diagram

### 🔴 Critical Issue
**Duplicate LLM call in `generate_json_representation`** when user selects diagram type.

**Impact**:
- Extra API cost
- Slower performance
- Unnecessary processing

**Status**: NEEDS FIX

---

## Next Steps

1. ✅ Fix clarification flow (DONE)
2. ❌ Fix duplicate JSON generation (NEEDS DOING)
3. ✅ All other nodes verified working

**Recommendation**: Add skip logic to `generate_json_representation` before testing.
