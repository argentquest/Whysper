# DiagramWizard LangGraph Sequence Diagram

## Overview
This document provides a detailed sequence diagram of the DiagramWizard workflow, showing all LangGraph nodes, their entry/exit conditions, and transitions.

---

## Master Sequence Diagram

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                     DIAGRAMWIZARD LANGGRAPH WORKFLOW                        │
└─────────────────────────────────────────────────────────────────────────────┘

┌──────────┐
│  START   │  User submits diagram request via chat/wizard UI
└────┬─────┘
     │
     ▼
┌────────────────────────────────────────────────────────────────┐
│ [1] ANALYZE_REQUEST                                            │
├────────────────────────────────────────────────────────────────┤
│ Entry:   Graph entry point (always triggered)                 │
│ Trigger: User design prompt submitted                          │
│ Actions:                                                       │
│  • LLM analyzes user's design intent                          │
│  • Extracts clarity score (1-10)                              │
│  • Builds initial JSON representation of design               │
│  • Creates conversation history with user message             │
│ Exit:    Always proceeds to CLARIFY_PROMPT                    │
│ Outputs: clarity_score, json_representation,                  │
│          clarification_history, current_state=CLARIFYING      │
└────────────────────────────────────────────────────────────────┘
     │
     ▼
┌────────────────────────────────────────────────────────────────┐
│ [2] CLARIFY_PROMPT (LOOP)                                     │
├────────────────────────────────────────────────────────────────┤
│ Entry:   After ANALYZE_REQUEST completes                      │
│ Trigger: System routes from analyze_request                   │
│ Actions:                                                       │
│  • LLM generates clarification questions                      │
│  • Sends question to user via SSE                             │
│  • Waits for user response                                    │
│  • Updates conversation history with Q&A                      │
│  • Re-scores clarity (1-10) based on new info                 │
│  • Updates json_representation with new details               │
│  • Increments question_count                                  │
│ Loop Check:                                                   │
│  ├─ IF clarity_score >= 8 AND sufficient_detail → llm_ready  │
│  ├─ IF question_count >= 10 → timeout, force ready           │
│  ├─ IF (current_time - start_time) > 300s → timeout          │
│  └─ IF user_confirmed_ready == True → skip checks, force ready
│                                                                │
│ Conditional Exit:                                             │
│  ├─ IF llm_ready = True  ──► Proceed to [3] DETERMINE_TYPE  │
│  ├─ IF llm_ready = False ──► END (wait for next user message)│
│  └─ IF timeout reached   ──► Force llm_ready=True            │
│                              Proceed to [3] DETERMINE_TYPE    │
│ Outputs: clarification_history (appended), final_design_summary,
│          json_representation (updated), llm_ready flag,       │
│          question_count, clarification_timeout                │
└────────────────────────────────────────────────────────────────┘
     │
     │ ┌──────────────────────────────────┐
     │ │ CONDITIONAL EDGE DECISION        │
     │ │ route_to_diagram_type_determination() │
     │ └──────────────────────────────────┘
     │
     ├─────── IF llm_ready = FALSE ──────────┐
     │                                         │
     │                                    ┌────▼─────┐
     │                                    │   END    │
     │                                    │(PAUSE)   │
     │                                    │Wait for  │
     │                                    │next user │
     │                                    │response  │
     │                                    └──────────┘
     │
     └─────── IF llm_ready = TRUE ──────────┐
                                             │
                                        ┌────▼──────────────────────────────────┐
                                        │ [3] DETERMINE_DIAGRAM_TYPE           │
                                        ├────────────────────────────────────────┤
                                        │ Entry:   After CLARIFY_PROMPT         │
                                        │ Trigger: llm_ready = True             │
                                        │ Actions:                              │
                                        │  • Analyzes final_design_summary      │
                                        │  • Keyword-based scoring for types    │
                                        │  • Rates Mermaid, D2, PlantUML,       │
                                        │    Structurizr (percentages)          │
                                        │  • Sends scores to frontend via SSE   │
                                        │  • Waits for user selection           │
                                        │ Conditional Exit:                     │
                                        │  ├─ IF user_selected_diagram_type     │
                                        │  │  = False ──► END (await selection) │
                                        │  └─ IF user_selected_diagram_type     │
                                        │     = True ──► Proceed to [4]         │
                                        │ Outputs: diagram_type (user-selected),│
                                        │          keyword_scores (dict),       │
                                        │          current_state=GENERATING     │
                                        └────┬──────────────────────────────────┘
                                             │
                                        ┌────┴────────────────┐
                                        │                     │
                       ┌────────────────▼───────────┐    ┌───▼────────────────────┐
                       │ USER SELECTED TYPE         │    │ AWAITING SELECTION     │
                       │ user_selected_diagram_type │    │ user_selected_diagram  │
                       │ = TRUE                     │    │ _type = FALSE          │
                       └────────────┬───────────────┘    └───┬────────────────────┘
                                    │                        │
                                    │                   ┌────▼──────┐
                                    │                   │   END     │
                                    │                   │ (PAUSE)   │
                                    │                   │ Wait for  │
                                    │                   │ user to   │
                                    │                   │ click type│
                                    │                   └───────────┘
                                    │
                                    ▼
                                        ┌────────────────────────────────────────┐
                                        │ [4] GENERATE_CODE                      │
                                        ├────────────────────────────────────────┤
                                        │ Entry:   After DETERMINE_DIAGRAM_TYPE  │
                                        │ Trigger: System routes automatically   │
                                        │ Actions:                               │
                                        │  • Calls LLM with diagram-specific     │
                                        │    prompt template                     │
                                        │  • Passes json_representation and      │
                                        │    diagram_type to LLM                 │
                                        │  • LLM converts to diagram syntax      │
                                        │  • Strips markdown formatting          │
                                        │  • Validates basic structure           │
                                        │ Exit:    Always proceeds to [5]        │
                                        │ Outputs: diagram_code (string),        │
                                        │          current_state=VALIDATING      │
                                        └────┬──────────────────────────────────┘
                                             │
                                             ▼
                                        ┌────────────────────────────────────────┐
                                        │ [5] VALIDATE_CODE                      │
                                        ├────────────────────────────────────────┤
                                        │ Entry:   After GENERATE_CODE           │
                                        │ Trigger: System routes automatically   │
                                        │ Actions:                               │
                                        │  • Calls provider system for          │
                                        │    validation (no render)              │
                                        │  • Checks syntax correctness           │
                                        │  • Identifies error types if invalid   │
                                        │  • Generates recovery suggestions      │
                                        │ Conditional Exit:                      │
                                        │  ├─ IF is_valid = True  ──► [6]       │
                                        │  └─ IF is_valid = False ──► [5b]      │
                                        │ Outputs: is_valid (bool),              │
                                        │          validation_error (str or null)│
                                        │          recovery_suggestions          │
                                        └────┬──────────────────────────────────┘
                                             │
                                    ┌────────┴────────────┐
                                    │                     │
                       ┌────────────▼─────────────┐    ┌──▼─────────────────────┐
                       │ VALIDATION PASSED        │    │ VALIDATION FAILED      │
                       │ is_valid = TRUE          │    │ is_valid = FALSE       │
                       └────────────┬─────────────┘    └──┬─────────────────────┘
                                    │                     │
                                    │                ┌────▼──────────────────────────────┐
                                    │                │ [5b] REFINE_CODE (LOOP)         │
                                    │                ├────────────────────────────────────┤
                                    │                │ Entry:   After VALIDATE_CODE fails│
                                    │                │ Trigger: is_valid = False         │
                                    │                │ Actions:                         │
                                    │                │  • Increments refinement_attempt  │
                                    │                │  • Checks if attempts < 3        │
                                    │                │  • Calls LLM with error context  │
                                    │                │  • Passes validation_error to LLM│
                                    │                │  • LLM fixes diagram code        │
                                    │                │  • Updates diagram_code          │
                                    │                │ Conditional Exit:                │
                                    │                │  ├─ IF attempts < 3 ──► [5]     │
                                    │                │  │  (re-validate)                │
                                    │                │  └─ IF attempts >= 3 ──► ERROR  │
                                    │                │                                  │
                                    │                │ Outputs: diagram_code (refined),│
                                    │                │          refinement_attempt++,   │
                                    │                │          error_state if max     │
                                    │                └────┬───────────────────────────┘
                                    │                     │
                                    │              ┌──────┘
                                    │              │
                                    │         ┌────▼─────────────┐
                                    │         │ Re-validate      │
                                    │         │ (back to [5])    │
                                    │         └──────────────────┘
                                    │
                                    ▼
                           ┌────────────────────────────────────────┐
                           │ [6] RENDER_DIAGRAM (ASYNC)             │
                           ├────────────────────────────────────────┤
                           │ Entry:   After VALIDATE_CODE (valid)   │
                           │ Trigger: is_valid = True               │
                           │ Actions:                               │
                           │  • Sends progress update: "rendering"  │
                           │  • Calls provider.render_with_         │
                           │    validation() (async)                │
                           │  • Provider sends progress updates:    │
                           │    - Step 1/4: Validating code         │
                           │    - Step 2/4: Pattern auto-fix (opt)  │
                           │    - Step 3/4: LLM correction (opt,    │
                           │      shows retry count: "attempt 3/8") │
                           │    - Step 4/4: Rendering to SVG        │
                           │  • Receives SVG output from provider   │
                           │  • Sends progress: "rendered"          │
                           │  • Updates session.svg_output          │
                           │  • Sets final svg_output in state      │
                           │ Exit:    Always proceeds to END        │
                           │ Outputs: svg_output (SVG string),      │
                           │          current_state=READY,          │
                           │          success flag                  │
                           │ Note:    Non-blocking async operation, │
                           │          supports long LLM corrections │
                           │          (30-90s) without freezing     │
                           └────┬───────────────────────────────────┘
                                │
                                ▼
                           ┌──────────────────────────────────────┐
                           │          END (SUCCESS)                │
                           ├──────────────────────────────────────┤
                           │ Graph completes with final state      │
                           │ Returns:                              │
                           │  • svg_output (SVG diagram)           │
                           │  • diagram_code (source code)         │
                           │  • diagram_type (selected type)       │
                           │  • final_design_summary (description) │
                           │  • clarity_score (final quality)      │
                           │  • All clarification history          │
                           └──────────────────────────────────────┘

```

---

## Node Details Table

| Node | Phase | Entry Trigger | Exit Condition | Route Decision | Output |
|------|-------|---------------|----------------|---|---|
| **analyze_request** | INIT | Graph.ainvoke() called | Always | → clarify_prompt | clarity_score, json_representation |
| **clarify_prompt** | CLARIFYING | After analyze_request | User response OR clarity ≥ 8 OR timeout | Conditional: llm_ready flag | final_design_summary, llm_ready |
| **determine_diagram_type** | GENERATING | llm_ready = True | User selection | Conditional: user_selected_diagram_type | diagram_type, keyword_scores |
| **generate_code** | GENERATING | After determine_type | Always | → validate_code | diagram_code |
| **validate_code** | VALIDATING | After generate_code | Always (but splits) | Conditional: is_valid flag | is_valid, validation_error |
| **refine_code** | VALIDATING | is_valid = False | attempts < 3 | → validate_code | diagram_code (refined) |
| **render_diagram** | RENDERING (ASYNC) | is_valid = True | Always | → END | svg_output, READY state |

---

## State Transitions Map

```
INITIAL STATE
    ↓
[analyze_request] → ANALYZING
    ↓
[clarify_prompt] → CLARIFYING (may loop)
    ├─ llm_ready = False
    │  └─ END (external event needed to resume)
    │
    └─ llm_ready = True
       ↓
    [determine_diagram_type] → GENERATING
       ↓
    [generate_code] → GENERATING
       ↓
    [validate_code] → VALIDATING
       ├─ is_valid = False
       │  └─ [refine_code] (attempts < 3)
       │     └─ [validate_code] (re-check)
       │
       └─ is_valid = True
          ↓
       [render_diagram] → RENDERING
          ↓
       END (READY)
```

---

## Conditional Edge Logic

### Edge 1: clarify_prompt → (determine_diagram_type OR END)
**Function**: `route_to_diagram_type_determination(state: GraphState) -> str`

```python
if state.get("llm_ready", False):
    return "generate_code"  # Mapped to determine_diagram_type node
else:
    return END  # Pause and wait for external event
```

**Conditions that set llm_ready = True:**
- LLM assessment: `clarity_score >= 8 AND sufficient_detail`
- User action: `user_confirmed_ready == True`
- Timeout: `question_count >= 10 OR elapsed_time > 300s`

---

### Edge 2: validate_code → (render_diagram OR refine_code)
**Function**: `route_validation(state: GraphState) -> str`

```python
if state.get("is_valid", False):
    return "render_diagram"
else:
    return "refine_code"
```

**Conditions:**
- `is_valid = True`: Provider validated diagram syntax successfully
- `is_valid = False`: Provider found syntax errors

**Additional Check in refine_code:**
```python
if refinement_attempt >= 3:
    # Force error state
    return ERROR
else:
    # Return to validate_code
    return validate_code
```

---

## State Management Flow

### Initial State (at entry)
```
{
  session_id: "uuid-xxxxx",
  user_id: "user-xxxxx",
  clarification_history: [{"role": "user", "content": "<initial_prompt>"}],
  clarity_scores: [],
  llm_ready: False,
  current_state: "INITIALIZED",
  question_count: 0,
  refinement_attempt: 0,
  awaiting_user_confirmation: False,
  clarification_timeout: False
}
```

### After analyze_request
```
Added/Updated:
  clarity_score: 5,  # Initial assessment
  json_representation: {...},
  current_state: "CLARIFYING"
```

### After each clarify_prompt iteration
```
Updated:
  clarification_history: [..., Q, ..., A],
  clarity_scores: [5, 6, 7],
  json_representation: {...updated...},
  question_count: 1,
  awaiting_user_confirmation: True
```

### After clarify_prompt (ready)
```
Updated:
  llm_ready: True,
  final_design_summary: "...",
  json_representation: {...finalized...},
  current_state: "CLARIFYING" → will switch to GENERATING
```

### After determine_diagram_type
```
Added:
  diagram_type: DiagramType.MERMAID,
  keyword_scores: {"Mermaid": 75.0, "D2": 15.0, "PlantUML": 10.0},
  current_state: "GENERATING"
```

### After generate_code
```
Added:
  diagram_code: "graph TD\n A --> B\n...",
  current_state: "VALIDATING"
```

### After validate_code (valid)
```
Updated:
  is_valid: True,
  validation_error: None,
  current_state: "RENDERING"
```

### After validate_code (invalid)
```
Updated:
  is_valid: False,
  validation_error: "Line 3: Invalid syntax",
  recovery_suggestions: ["Check closing brackets", "..."]
```

### After refine_code
```
Updated:
  diagram_code: "graph TD\n A --> B\n...fixed...",
  refinement_attempt: 1,
  current_state: "VALIDATING"
```

### After render_diagram (final)
```
Added:
  svg_output: "<svg xmlns=...></svg>",
  current_state: "READY"

Final State Ready for Return
```

---

## Error Paths

### Path 1: Clarification Timeout
```
[clarify_prompt] (10 questions OR 5 minutes reached)
  ↓ (force llm_ready=True)
[determine_diagram_type]
  ↓
[generate_code]
  ↓
... (continues to completion)
```

### Path 2: Refinement Failure (max attempts)
```
[validate_code] → is_valid = False
  ↓
[refine_code] (attempt 1)
  ↓
[validate_code] → is_valid = False
  ↓
[refine_code] (attempt 2)
  ↓
[validate_code] → is_valid = False
  ↓
[refine_code] (attempt 3)
  ↓
ERROR STATE (no more refinements allowed)
  ↓
Return error to user
```

### Path 3: User Pauses in Clarification
```
[clarify_prompt] (user reads response)
  ↓ (llm_ready = False)
END (waiting)
  ↓ (external: user submits next message)
[clarify_prompt] (resumes with history)
  ↓
(continues as normal)
```

---

## Node Execution Properties

| Property | Value |
|----------|-------|
| **Execution Model** | Async (all nodes are async functions) |
| **State Mutation** | Immutable (returns new state dict, not mutating) |
| **Isolation** | Each node is independently callable |
| **Retries** | No built-in retries; refinement loop is manual |
| **Timeout** | Optional timeout per node (async timeout wrapper) |
| **Logging** | SSE callbacks on every state change |
| **Session Storage** | In-memory with TTL (1 hour default) |

---

## Key Transition Rules

1. **No skipping nodes**: Every valid path executes through fixed nodes in order (except conditional routing)
2. **Clarification is optional entry point**: User can skip if `user_confirmed_ready = True`
3. **Validation is mandatory**: Cannot render without validation (safety critical)
4. **Refinement is bounded**: Max 3 attempts prevents infinite loops
5. **Clarification is bounded**: Max 10 questions OR 5 minutes prevents infinite loops
6. **Type determination is keyword-based**: Not ML-based; deterministic algorithm
7. **Code generation is LLM-based**: Non-deterministic; quality varies
8. **No rollback**: Once a node completes, previous state is not restored

---

## Entry/Exit Summary

### Entry Points (What starts execution?)
1. **Primary**: Graph.ainvoke(initial_state) → enters analyze_request
2. **Resume**: External message to paused clarify_prompt → resumes clarify_prompt loop
3. **Force Ready**: User clicks "Ready" button → sets user_confirmed_ready=True

### Exit Points (What stops execution?)
1. **Successful completion**: render_diagram → END (success)
2. **User pause**: clarify_prompt with llm_ready=False → END (pause)
3. **Max refinements**: refine_code with attempts=3 → ERROR state
4. **Provider error**: Provider validation/render fails → ERROR state
5. **User abort**: External signal (timeout or explicit cancel) → ERROR state

---

## Sequence Flow Examples

### Example 1: Happy Path (Minimal Clarification)
```
User: "Create a flowchart for user login process"
  ↓
[analyze_request] → score=7, needs clarification
  ↓
[clarify_prompt] → "Any authentication methods besides password?"
  ↓
User: "Yes, also OAuth and biometric"
  ↓
[clarify_prompt] → score=9, llm_ready=True
  ↓
[determine_diagram_type] → Mermaid (82%)
  ↓
[generate_code] → Valid diagram syntax
  ↓
[validate_code] → is_valid=True
  ↓
[render_diagram] → SVG generated
  ↓
END ✓
```

### Example 2: Multiple Clarification Rounds
```
User: "Architecture diagram"
  ↓
[analyze_request] → score=3, very unclear
  ↓
[clarify_prompt] → "What scale? Microservices or monolith?"
  ↓
User: "Microservices"
  ↓
[clarify_prompt] → score=5, "How many services?"
  ↓
User: "5 services with API gateway"
  ↓
[clarify_prompt] → score=9, llm_ready=True
  ↓
[determine_diagram_type] → D2 (88%)
  ↓
... (continues to render)
```

### Example 3: Code Refinement Loop
```
[generate_code] → "flowchart LR\nA --> B\nC --->"  (incomplete)
  ↓
[validate_code] → is_valid=False, "Syntax error: incomplete edge"
  ↓
[refine_code] → attempt=1, fixes to "flowchart LR\nA --> B\nC --> D"
  ↓
[validate_code] → is_valid=True
  ↓
[render_diagram] → Success
  ↓
END ✓
```

### Example 4: Max Refinements Exceeded
```
[generate_code] → "invalid syntax..."
  ↓
[validate_code] → Error (attempt 1)
[refine_code] attempt=1
  ↓
[validate_code] → Still invalid (attempt 2)
[refine_code] attempt=2
  ↓
[validate_code] → Still invalid (attempt 3)
[refine_code] attempt=3
  ↓
attempts >= 3 → ERROR STATE
  ↓
Return error to user ✗
```

---

## Performance Notes

- **Clarification Loop**: Typically 1-2 rounds for clear requests, 3-4 for ambiguous requests
- **Code Generation**: Single pass LLM call (~2-5 seconds)
- **Validation + Refinement**: Usually 0 passes (75% success), max 3 passes
- **Rendering**: Provider-dependent (usually <2 seconds)
- **Total Time**: 10-60 seconds depending on clarification rounds and refinement needs

---

## Session Lifecycle

```
Session Created
  ↓
Graph Execution
  ├─ [analyze_request] (0-1s)
  ├─ [clarify_prompt] (10-40s, with user delays)
  ├─ [determine_diagram_type] (0-1s)
  ├─ [generate_code] (2-5s)
  ├─ [validate_code] (1-2s)
  ├─ [refine_code] (0-10s, optional, max 3 iterations)
  └─ [render_diagram] (1-5s)
  ↓
Session Stored in Memory (TTL: 1 hour)
  ↓
Session Expires (1 hour OR explicit cleanup)
  ↓
Session Deleted
```

---

Generated with analysis of:
- `backend/app/utils/diagram_wizard/langgraph_builder.py`
- `backend/app/utils/diagram_wizard/nodes.py`
- `backend/app/utils/diagram_wizard/graph_state.py`
