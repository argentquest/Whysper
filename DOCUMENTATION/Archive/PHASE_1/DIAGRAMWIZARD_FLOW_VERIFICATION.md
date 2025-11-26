# DiagramWizard Flow Verification Report

## Your Proposed Flow

You described the DiagramWizard flow as follows:

1. **Analyse Request** – Backend scores the initial prompt, drafts a Structurizr snapshot, and streams an "AI is analyzing…" status. UI stays on the single "Describe Your System" screen showing the spinner/toast.
2. **Clarify Prompt loop** – Backend asks targeted questions, updates the Structurizr data, and pauses after each turn. UI remains in the clarification view with conversation bubbles, clarity indicators, and the response box.
3. **Determine Diagram Type** – Once clarity ≥ 8, the backend recommends a DSL. UI switches to the "Ready to Generate" selector so the user can accept the recommendation or pick Mermaid/D2/PlantUML.
4. **Generate Code** – After the user's selection, the graph generates DSL code. isInAnalysisPhase flips false and the UI transitions to the multi-panel layout (chat + Preview/Code/JSON tabs) while showing "AI is generating diagram code…".
5. **Validate Code** – Provider validation checks the DSL. If it passes, the UI notes "Code validated"; if not, a message appears that the AI will refine the code.
6. **Refine Code** – When validation fails, the backend repairs the DSL and loops back to validation. The multi-panel UI shows the error feedback and refinement status before retrying.
7. **Render Diagram** – With valid code in hand, the backend renders the diagram and streams the final SVG. The Preview tab displays the diagram, and the "Render/Export/Copy Code" controls become active.

---

## Verification Against Actual Implementation

### ✅ CORRECT: Basic Node Sequence

Your understanding of the basic node sequence is **correct**:
- analyze_request → clarify_prompt → determine_diagram_type → generate_code → validate_code → [refine_code (loop) OR render_diagram]

### ⚠️ PARTIALLY INCORRECT: Several Important Details

#### 1. **Analyze Request Node** ❌ NOT AS DESCRIBED

**Your Statement:**
> Backend scores the initial prompt, drafts a **Structurizr snapshot**, and streams an "AI is analyzing…" status.

**Actual Implementation:**
```python
# From nodes.py lines 87-112
clarification_history = state.get("clarification_history", [])
user_content = "\n".join([msg.get('content', '') for msg in clarification_history
                          if msg.get('role') == 'user'])

ai_response = json.loads(ai_response_str)
analysis_summary = ai_response.get("analysis_summary")
assessment_score = ai_response.get("assessment_score")
clarity_score = ai_response.get("clarity_score")
architecture_json = ai_response.get("json_representation")  # Not Structurizr!

state["json_representation"] = json.loads(architecture_json)  # Generic JSON, not Structurizr
```

**What Actually Happens:**
- ✅ Backend scores the initial prompt (assessment_score)
- ✅ Streams "AI is analyzing…" status
- ❌ **Does NOT draft a Structurizr snapshot** – Creates a generic `json_representation` (architecture schema)
- ✅ UI stays on single "Describe Your System" screen
- ✅ Shows spinner/toast

**Correction:** The backend creates a **generic JSON representation**, not Structurizr specifically.

---

#### 2. **Clarify Prompt Loop** ✅ CORRECT

Your description is **mostly correct**:

```python
# From nodes.py lines 305-481
# The clarify_prompt node:
# - Asks targeted questions
# - Updates the JSON data (json_representation)
# - Pauses after each turn (awaiting_user_confirmation=True)
# - UI remains in clarification view
```

**Implementation Details Confirmed:**
- ✅ Backend asks targeted questions via LLM
- ✅ Updates JSON representation with each clarification turn
- ✅ Pauses after each turn (returns with `llm_ready=False`)
- ✅ Tracks clarity_score (1-10)
- ✅ Conversation bubbles in UI (handled by chat history)
- ✅ Has response box for user input
- ✅ Tracks question count and has timeout (max 10 questions OR 5 minutes)

**Clarification Ready State:**
```python
# Line 441-448
if ready or design_summary.startswith("READY:"):
    # ...sends clarification_ready status
    await update_callback({
        "status": "clarification_ready",
        "message": summary,
        "clarity_score": clarity_score,
        "awaiting_user_confirmation": True,  # ← Waits for user confirmation
    })
```

---

#### 3. **Determine Diagram Type** ❌ NOT AS DESCRIBED (CRITICAL DIFFERENCE)

**Your Statement:**
> Once clarity ≥ 8, the backend recommends a DSL. **UI switches to the "Ready to Generate" selector so the user can accept the recommendation or pick Mermaid/D2/PlantUML.**

**Actual Implementation:**
```python
# From nodes.py lines 511-562
async def determine_diagram_type_node(state: GraphState) -> Dict[str, Any]:
    """Determines the appropriate diagram type based on keyword analysis."""

    diagram_type, keyword_scores = determine_diagram_type(analysis_text)

    # Backend sends update with recommended type
    await update_callback({
        "status": "diagram_type_determined",
        "message": f"✅ Selected {diagram_type.value} diagram based on your design.",
        "diagram_type": diagram_type.value,
        "keyword_scores": keyword_scores,
    })

    return {
        "diagram_type": diagram_type,
        "keyword_scores": keyword_scores,
        "current_state": SessionState.GENERATING
    }
```

**What Actually Happens:**
- ✅ Backend determines a diagram type (keyword-based algorithm, NOT user selection)
- ✅ Recommends to frontend via SSE
- ❌ **NO "Ready to Generate" selector UI** – The backend makes the decision automatically
- ❌ **User CANNOT pick a different diagram type** – The system moves directly to code generation
- The UI just shows the selection status message

**UI Confirmation:**
```typescript
// From DiagramWizard.tsx lines 267-276
case 'diagram_type_determined': {
  const inferredType = update.diagram_type || diagramType;
  setDiagramType(inferredType);
  setCurrentPhase(2);
  setIsInAnalysisPhase(false);  // ← Phase changes automatically
  message.success(`Using ${inferredType} for the initial diagram - generating code...`);
  break;
}
```

**Critical Difference:**
- ❌ **There is NO user selection step** – The diagram type is determined automatically
- ❌ **User cannot override the recommendation** – The system proceeds to code generation immediately
- ❌ **No "Ready to Generate" selector screen** – Status message only

---

#### 4. **Generate Code** ✅ CORRECT (With Minor Note)

Your description is **essentially correct**:

```python
# From nodes.py lines 566-648
async def generate_code(state: GraphState) -> Dict[str, Any]:
    """Generates diagram code from the structured JSON representation."""

    diagram_type_str = get_diagram_type_str(diagram_type)

    # LLM generates code
    ai_response = await _call_llm(prompt_template, json_representation, session_id)

    # Clean up markdown
    diagram_code = ai_response.strip()
    if diagram_code.startswith("```"):
        # Remove markdown code blocks
        diagram_code = '\n'.join(lines[1:-1])

    await update_callback({
        "status": "code_generated",
        "message": f"✅ Generated {diagram_type_str} diagram code...",
    })
```

**Implementation Details Confirmed:**
- ✅ After diagram_type_determined, generates DSL code
- ✅ `isInAnalysisPhase` flips to `false` (line 274)
- ✅ UI transitions to multi-panel layout (handled by `currentPhase` = 2)
- ✅ Shows "AI is generating diagram code…" message
- ✅ Strips markdown formatting from LLM response

---

#### 5. **Validate Code** ✅ CORRECT

Your description is **correct**:

```python
# From nodes.py - validate_code function (not shown in excerpt but exists)
# The validate_code node:
# - Calls provider validation
# - Returns is_valid flag
# - If valid: proceeds to render
# - If invalid: routes to refine_code
```

**Implementation Pattern:**
```python
# From langgraph_builder.py lines 82-86
workflow.add_conditional_edges(
    "validate_code",
    route_validation,  # Checks is_valid flag
    {"render_diagram": "render_diagram", "refine_code": "refine_code"},
)
```

---

#### 6. **Refine Code** ✅ CORRECT

Your description is **correct**:

```python
# When validation fails:
# - Backend repairs the DSL using LLM
# - Loops back to validation
# - Multi-panel UI shows error feedback
# - Refinement counter (max 3 attempts)
```

**Safety Feature Confirmed:**
- Max 3 refinement attempts before ERROR state
- Each attempt loops back to validation

---

#### 7. **Render Diagram** ✅ CORRECT

Your description is **correct**:

```python
# After valid code:
# - Backend renders to SVG
# - Streams final SVG output
# - Preview tab displays diagram
# - Export/Copy controls become active
```

---

## Summary of Issues Found

| Item | Your Description | Actual Implementation | Status |
|------|------------------|----------------------|--------|
| **Analyze Request** | Drafts "Structurizr snapshot" | Creates generic `json_representation` | ❌ Inaccurate terminology |
| **Clarify Prompt** | Asks questions, pauses, updates data | Exactly as described | ✅ Correct |
| **Determine Type** | UI shows "Ready to Generate" selector for user choice | Backend auto-selects, no user override | ❌ **MAJOR DIFFERENCE** |
| **Generate Code** | After user selection, transitions to multi-panel | After auto-selection, transitions to multi-panel | ⚠️ Correct outcome, different trigger |
| **Validate Code** | If passes: "Code validated", if fails: "will refine" | Exactly as described | ✅ Correct |
| **Refine Code** | Loop with error feedback | Exactly as described (max 3 attempts) | ✅ Correct |
| **Render Diagram** | SVG rendered, preview shows, controls active | Exactly as described | ✅ Correct |

---

## Key Differences

### 1. **No User Diagram Type Selection UI**
Your proposed flow includes:
```
User selects diagram type → generate_code
```

Actual flow:
```
determine_diagram_type (automatic keyword-based) → generate_code
```

**Implication:** The system is more autonomous than your description suggests. The backend makes all key decisions without user intervention except during clarification.

### 2. **JSON Representation ≠ Structurizr**
Your description mentions "Structurizr snapshot" but the actual system uses:
- Generic `json_representation` (architecture schema JSON)
- Not Structurizr-specific format
- Structurizr is mentioned in code but as context/inspiration, not as the actual output format

### 3. **Phase Transition Timing**
Your description:
```
clarification_ready (user sees selector) → user selects type → transitions to multi-panel
```

Actual implementation:
```
clarification_ready → determine_diagram_type (auto) → transitions to multi-panel
```

---

## Recommendations

If you're documenting or implementing based on this flow, consider:

1. **Remove "Ready to Generate" selector concept** – Replace with "Diagram type automatically determined" message
2. **Clarify JSON representation** – Not Structurizr, but a generic architecture JSON schema
3. **Emphasize automation** – The determine_diagram_type node is automatic, not user-driven
4. **Update UI expectations** – No diagram type selection screen; user interaction happens only during clarification
5. **Correct the flow diagram** – Skip from determine_diagram_type directly to generate_code (no user selection step)

---

## Revised Accurate Flow

```
1. ANALYZE_REQUEST
   ├─ Scores user prompt
   ├─ Creates initial json_representation
   └─ Streams "analyzing" status
   ↓
2. CLARIFY_PROMPT (LOOP)
   ├─ Asks clarifying questions
   ├─ Updates json_representation
   ├─ Pauses for user response
   ├─ Tracks clarity_score
   ├─ Waits for user confirmation when ready
   └─ Returns llm_ready=True when sufficient
   ↓
3. DETERMINE_DIAGRAM_TYPE (AUTOMATIC, NO USER INPUT)
   ├─ Keyword analysis on final_design_summary
   ├─ Selects Mermaid/D2/PlantUML
   ├─ Scores: keyword_scores returned
   └─ Streams "diagram_type_determined" status
   ↓
4. GENERATE_CODE
   ├─ LLM converts json_representation to DSL code
   ├─ Strips markdown formatting
   ├─ isInAnalysisPhase = false
   ├─ UI transitions to multi-panel layout
   └─ Streams "code_generated" status
   ↓
5. VALIDATE_CODE
   ├─ Provider validates DSL syntax
   ├─ Returns is_valid flag
   └─ Routes to refine_code (invalid) OR render_diagram (valid)
   ↓
6. [REFINE_CODE - conditional loop, max 3 attempts]
   ├─ LLM fixes validation errors
   ├─ Loops back to validate_code
   └─ On max attempts → ERROR state
   ↓
7. RENDER_DIAGRAM
   ├─ Provider renders to SVG
   ├─ Streams svg_output
   ├─ UI shows Preview tab with diagram
   └─ Export/Copy controls become active
   ↓
END (SUCCESS)
```

---

**Generated:** 2025-11-16
**Based on codebase analysis of:**
- `backend/app/utils/diagram_wizard/nodes.py`
- `backend/app/utils/diagram_wizard/langgraph_builder.py`
- `frontend/src/components/DiagramWizard/DiagramWizard.tsx`
