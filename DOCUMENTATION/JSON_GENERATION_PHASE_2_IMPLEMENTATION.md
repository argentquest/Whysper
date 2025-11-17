# JSON Generation Node: Phase 2 Implementation Plan

**Status:** Phase 1 Complete → Ready for Phase 2 Implementation

**Objective:** Activate the `generate_json_representation` node in the LangGraph workflow and update the prompt to use **Structurizr DSL format**.

**Priority:** CRITICAL for Phase 2

---

## Current State

### Function Exists
- **Location:** `backend/app/utils/diagram_wizard/nodes.py` (lines 241-301)
- **Status:** Defined but NOT in graph
- **Function Name:** `generate_json_representation()`
- **Current Output:** Custom JSON schema (using ArchitectureSchema validation)

### Prompt File Exists
- **Location:** `backend/app/utils/diagram_wizard/prompts/JSON_GENERATION_PROMPT.md`
- **Status:** Exists but deprecated (marked in Phase 1)
- **Current Issue:** Uses custom JSON schema, not Structurizr DSL

### Graph Status
- **Current Nodes:** 7 (analyze_request, clarify_prompt, determine_diagram_type, generate_code, validate_code, refine_code, render_diagram)
- **Missing Node:** generate_json_representation (NOT in graph)
- **Location:** `backend/app/utils/diagram_wizard/langgraph_builder.py` (lines 47-89)

---

## Phase 2 Task: Integrate JSON Generation Node

### Task 1: Update JSON_GENERATION_PROMPT.md

**Current Problem:**
- Prompt outputs custom JSON schema (metadata, components, connections, users)
- Not aligned with Structurizr DSL format
- Not consistent with ANALYSE_CONFIRM and CLARIFY_UNIVERSAL prompts

**Solution:**
Update the prompt to output **Structurizr DSL** with the same unified schema as other prompts.

**New Output Format:**
```json
{
  "analysis_summary": "string - what was updated",
  "clarity_score": 1-10,
  "structurizr_workspace": "Full Structurizr DSL string",
  "clean_d2": "Normalized Structurizr DSL string",
  "json_representation": {
    "metadata": {...},
    "components": {...},
    "connections": [...],
    "users": [...]
  },
  "assumptions": ["array of inferred facts"],
  "next_step": "string"
}
```

**Key Changes:**
1. Add `structurizr_workspace` field (Structurizr DSL)
2. Add `clean_d2` field (normalized Structurizr)
3. Keep `json_representation` field for legacy schema (backward compatibility)
4. Follow same unified schema as ANALYSE_CONFIRM and CLARIFY_UNIVERSAL
5. Create 4 model-specific versions (like other prompts)

**Files to Update:**
- `backend/app/utils/diagram_wizard/prompts/JSON_GENERATION_PROMPT.md`
- Create: `backend/app/utils/diagram_wizard/prompts/JSON_GENERATION_gpt5.md`
- Create: `backend/app/utils/diagram_wizard/prompts/JSON_GENERATION_grok.md`
- Create: `backend/app/utils/diagram_wizard/prompts/JSON_GENERATION_sonet45.md`
- Create: `backend/app/utils/diagram_wizard/prompts/JSON_GENERATION_gemini25pro.md`

---

### Task 2: Update GraphState

**Current Fields:**
```python
json_representation: Dict  # Existing
structurizr_workspace: str  # NEW (added Phase 1)
clean_d2: str              # NEW (added Phase 1)
```

**No Changes Needed:** GraphState already has all required fields from Phase 1.

---

### Task 3: Update Prompt Loader

**Current:**
```python
def get_prompt(prompt_name: str) -> str:
```

**Update:** Ensure model-specific loading works for JSON_GENERATION prompts
```python
def get_prompt(prompt_name: str, model_id: str = None) -> str:
    if model_id:
        model_specific = f"{prompt_name}_{model_id}"
        # Try to load model-specific version first
        # Fall back to generic if not found
```

**No new code needed if already implemented in Phase 2.**

---

### Task 4: Add Node to Graph

**Current Flow:**
```
analyze_request → clarify_prompt → determine_diagram_type → generate_code → validate_code → render_diagram
```

**New Flow (Option A: After clarify_prompt):**
```
analyze_request → clarify_prompt → generate_json_representation → determine_diagram_type → generate_code → validate_code → render_diagram
```

**New Flow (Option B: In parallel after clarify_prompt):**
```
                  ┌─→ determine_diagram_type → generate_code → validate_code → render_diagram
                  │
clarify_prompt ───┤
                  │
                  └─→ generate_json_representation (async, doesn't block main flow)
```

**Recommendation:** **Option A** (sequential) - simpler and ensures Structurizr is finalized before diagram generation.

**Code Changes in `langgraph_builder.py`:**

1. Import the node:
```python
from .nodes import (
    ...
    generate_json_representation,  # ADD THIS
)
```

2. Add the node:
```python
workflow.add_node("generate_json_representation", generate_json_representation)
```

3. Update edges (replace this line):
```python
# OLD:
workflow.add_edge("clarify_prompt", "determine_diagram_type")

# NEW:
workflow.add_edge("clarify_prompt", "generate_json_representation")
workflow.add_edge("generate_json_representation", "determine_diagram_type")
```

4. Update conditional routing (only if using conditional):
```python
# Update the route_to_diagram_type_determination function if needed
workflow.add_conditional_edges(
    "clarify_prompt",
    route_to_diagram_type_determination,
    {"generate_code": "generate_json_representation", END: END},  # Changed to route to JSON node
)
```

---

### Task 5: Update generate_json_representation Function

**Current Implementation Issue:**
- Uses `ArchitectureSchema.validate()` which expects custom schema
- Needs to output both custom schema AND Structurizr DSL

**Required Changes:**

1. **Accept model_id:**
```python
async def generate_json_representation(state: GraphState) -> Dict[str, Any]:
    model_id = state.get("model_id", "claude")  # Get selected model
```

2. **Load model-specific prompt:**
```python
prompt_template = get_prompt("json_generation", model_id=model_id)
```

3. **Parse response to include both schemas:**
```python
ai_response_str = await _call_llm(prompt_template, user_content, session_id, model_id=model_id)

response = json.loads(ai_response_str)

# Extract both representations
structurizr_workspace = response.get("structurizr_workspace", "")
clean_d2 = response.get("clean_d2", "")
json_representation = response.get("json_representation", {})

# Validate legacy schema if present
if json_representation:
    is_valid, errors = ArchitectureSchema.validate(json_representation)
    if not is_valid:
        logger.warning(f"Legacy JSON schema invalid: {errors}")

return {
    "structurizr_workspace": structurizr_workspace,
    "clean_d2": clean_d2,
    "json_representation": json_representation,
}
```

4. **Handle backward compatibility:**
```python
# If Structurizr representations already exist (from clarify_prompt),
# optionally merge/validate instead of replace
existing_workspace = state.get("structurizr_workspace")
if existing_workspace and structurizr_workspace:
    # Log comparison, decide which to keep
    logger.info("Comparing Structurizr workspaces from clarify_prompt and json_generation")
```

---

## Updated JSON_GENERATION_PROMPT Structure

### Base Template

**File:** `backend/app/utils/diagram_wizard/prompts/JSON_GENERATION_PROMPT.md`

```markdown
# JSON Generation Prompt

## Mission

You are a system architect. Analyze the conversation history to generate:
1. A complete Structurizr DSL workspace
2. A normalized, minimal Structurizr representation
3. A structured JSON representation of the architecture

## Instructions

1. Review the entire conversation history
2. Extract all architecture facts (systems, components, interactions, users)
3. Output a single JSON object with ALL of these fields:

## Output Format

```json
{
  "analysis_summary": "Brief summary of what was discussed",
  "clarity_score": 8,
  "structurizr_workspace": "workspace \"System Name\" \"Description\" { model { ... } views { ... } }",
  "clean_d2": "model { ... }",
  "json_representation": {
    "metadata": {
      "system_name": "string",
      "description": "string",
      "domain": "string"
    },
    "components": [
      {
        "name": "string",
        "type": "service|database|api|ui|etc",
        "description": "string",
        "technology": "string"
      }
    ],
    "connections": [
      {
        "source": "component_name",
        "target": "component_name",
        "description": "string",
        "protocol": "REST|gRPC|message|sync|async"
      }
    ],
    "users": [
      {
        "name": "string",
        "type": "person|system",
        "description": "string"
      }
    ]
  },
  "assumptions": [
    "Inferred fact 1",
    "Inferred fact 2"
  ],
  "next_step": "ready_for_generation"
}
```

## CRITICAL RULES

### Dual Representation Synchronization
- `structurizr_workspace` and `clean_d2` must represent the SAME architecture
- Both must be valid Structurizr DSL syntax
- Both must contain identical systems, components, and relationships
- Difference: workspace includes views, clean_d2 is minimal form

### Legacy JSON Representation
- The `json_representation` field uses a simplified custom schema
- It must be consistent with `structurizr_workspace`
- Use as fallback if Structurizr parsing fails downstream

### Output Requirements
- Return ONLY valid JSON (no Markdown fences, no explanations)
- All string fields are required
- Arrays can be empty but field must exist
- No trailing commas or syntax errors

## Structurizr DSL Syntax

[Insert Structurizr formatting rules - same as other prompts]

## Model-Specific Guidance

[Will be in model-specific versions]
```

### Model-Specific Versions

Create 4 versions with model-specific optimization guidance:

**`JSON_GENERATION_gpt5.md`:**
- Deep context analysis strategy
- Comprehensive validation approach
- Handle very complex systems

**`JSON_GENERATION_grok.md`:**
- Fast, deterministic approach
- Minimal but complete output
- Lean formatting

**`JSON_GENERATION_sonet45.md`:**
- Structured thinking approach
- Transparent decision-making
- Example walkthrough

**`JSON_GENERATION_gemini25pro.md`:**
- Efficient output format
- Token-optimized structure
- Pragmatic approach

---

## Workflow Integration

### Before Phase 2
```
User input (initial description)
    ↓
analyze_request (outputs Structurizr)
    ↓
clarify_prompt loop (refines Structurizr)
    ↓
determine_diagram_type
    ↓
generate_code
    ↓
validate_code
    ↓
refine_code (if needed)
    ↓
render_diagram
    ↓
SVG output
```

### After Phase 2 (with JSON node)
```
User input (initial description)
    ↓
analyze_request (outputs Structurizr)
    ↓
clarify_prompt loop (refines Structurizr)
    ↓
generate_json_representation (NEW - validates and outputs both Structurizr + legacy JSON)
    ↓
determine_diagram_type
    ↓
generate_code
    ↓
validate_code
    ↓
refine_code (if needed)
    ↓
render_diagram
    ↓
SVG output
```

---

## Testing Strategy

### Unit Tests
- Test `generate_json_representation()` function
- Verify Structurizr output syntax
- Verify JSON schema validation
- Test model_id parameter passing

### Integration Tests
- Test full flow with JSON node active
- Verify Structurizr from clarify_prompt → JSON node consistency
- Test each of 4 models
- Verify state transitions

### Validation Tests
- Validate Structurizr syntax for each model
- Validate legacy JSON schema
- Verify dual representation synchronization
- Test error handling (invalid output)

### E2E Tests
- Complete flow from user input to SVG
- Verify JSON_GENERATION phase produces correct output
- Verify downstream nodes (determine_diagram_type, generate_code) receive correct input

---

## Error Handling

### Invalid Structurizr Output
```python
try:
    workspace = response.get("structurizr_workspace")
    # Parse/validate Structurizr syntax
except SyntaxError as e:
    logger.error(f"Invalid Structurizr syntax: {e}")
    return {
        "error_message": "JSON generation produced invalid Structurizr syntax",
        # Fall back to existing Structurizr from clarify_prompt
        "structurizr_workspace": state.get("structurizr_workspace"),
        "clean_d2": state.get("clean_d2"),
    }
```

### Invalid JSON Response
```python
try:
    response = json.loads(ai_response_str)
except json.JSONDecodeError as e:
    logger.error(f"AI response not valid JSON: {e}")
    # Return state unchanged, continue with existing data
    return state
```

### Sync Mismatch (Structurizr vs clean_d2)
```python
workspace_systems = extract_systems(structurizr_workspace)
clean_systems = extract_systems(clean_d2)

if workspace_systems != clean_systems:
    logger.warning(f"Workspace and clean_d2 mismatch: {workspace_systems} vs {clean_systems}")
    # Could return error or use best guess
```

---

## Backward Compatibility

✅ **Existing Sessions Continue to Work:**
- JSON node inserted between clarify_prompt and determine_diagram_type
- No existing node logic changes
- Downstream nodes (determine_diagram_type, generate_code) work unchanged

✅ **State Management:**
- New node updates json_representation field (already in state)
- Also outputs structurizr_workspace and clean_d2 (already in state from Phase 1)
- No new state fields required

✅ **Fallback:**
- If JSON_GENERATION_PROMPT fails, continue with data from clarify_prompt
- Structurizr representations already exist from earlier nodes
- JSON node adds redundancy, not requirement

---

## Success Criteria

- ✅ JSON_GENERATION_PROMPT updated to output Structurizr format
- ✅ 4 model-specific versions created
- ✅ generate_json_representation function accepts model_id
- ✅ Node added to LangGraph workflow
- ✅ Edges properly configured
- ✅ Structurizr validation passing
- ✅ Legacy JSON schema validation passing
- ✅ Dual representation synchronized
- ✅ All tests passing
- ✅ No breaking changes to existing flow
- ✅ Backward compatibility verified

---

## Timeline

**Phase 2 Implementation:**
- Update JSON_GENERATION_PROMPT: ~30 min
- Create 4 model-specific versions: ~1-2 hours
- Update generate_json_representation function: ~1 hour
- Update langgraph_builder.py: ~30 min
- Testing and validation: ~2-3 hours

**Total:** ~1 day included in Phase 2 Backend (2-3 days total)

---

## Files to Modify/Create

### Modify
- `backend/app/utils/diagram_wizard/prompts/JSON_GENERATION_PROMPT.md`
- `backend/app/utils/diagram_wizard/nodes.py` (generate_json_representation function)
- `backend/app/utils/diagram_wizard/langgraph_builder.py` (add node to graph)

### Create
- `backend/app/utils/diagram_wizard/prompts/JSON_GENERATION_gpt5.md`
- `backend/app/utils/diagram_wizard/prompts/JSON_GENERATION_grok.md`
- `backend/app/utils/diagram_wizard/prompts/JSON_GENERATION_sonet45.md`
- `backend/app/utils/diagram_wizard/prompts/JSON_GENERATION_gemini25pro.md`

### Add to MODEL_MAPPING
```python
'gpt5': {
    ...
    'json_generation_prompt': 'JSON_GENERATION_gpt5.md'
},
# etc for other models
```

---

## References

- Existing generate_json_representation: `backend/app/utils/diagram_wizard/nodes.py:241-301`
- LangGraph builder: `backend/app/utils/diagram_wizard/langgraph_builder.py:47-89`
- Current JSON_GENERATION_PROMPT: `backend/app/utils/diagram_wizard/prompts/JSON_GENERATION_PROMPT.md`
- Phase 1 Structurizr specs: `DIAGRAMWIZARD_ANALYSE_CONFIRM_VERSIONS.md`
- Unified output schema: `PROMPT_VERSIONS_COMPLETE.md`

---

**Status:** Ready for Phase 2 Implementation

**Next Steps:**
1. Create/update prompts with Structurizr format
2. Update generate_json_representation function
3. Wire node into graph
4. Test and validate

---
