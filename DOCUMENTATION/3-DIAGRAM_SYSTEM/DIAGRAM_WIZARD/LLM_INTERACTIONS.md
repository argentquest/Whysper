# Diagram Wizard LLM Interactions

This document details all LLM interactions within the Diagram Wizard system, mapping out when they occur, how they are structured, and their inputs/outputs.

## 1. Request Analysis (`analyze_request`)

*   **Condition:** Triggered at the very start of the session to understand the user's intent. Skipped if `analysis_complete` is already true in the state.
*   **Location:** `backend/app/utils/diagram_wizard/nodes/analysis_nodes.py`

### System Prompt
*   **Source:** `backend/app/utils/diagram_wizard/prompts/ANALYSE_CLARIFY.md` (Unified file) OR `ANALYSE_PROMPT.md` (Legacy).
*   **Loader Key:** `analyze_request`

### Inputs
*   **User Content:** Derived from `clarification_history` (all user messages joined).
    ```python
    user_content = "\n".join([msg.get("content", "") for msg in clarification_history if msg.get("role") == "user"])
    ```
*   **Model ID:** `state.get("model_id")`

### Outputs
**JSON Schema (Expected from LLM):**
```json
{
  "analysis_summary": "string",
  "assessment_score": int, // 0-100
  "clarity_score": int, // 0-100
  "json_representation": object, // Preliminary architecture JSON
  "question": "string" // Follow-up question if needed
}
```

### LangGraph State Updates
*   `next_action`: Set to `"clarify"`.
*   `assessment_score`: Updated with LLM score.
*   `json_representation`: Initial population.
*   `clarification_history`: Appends Assistant's summary and question.
*   `current_state`: Set to `SessionState.CLARIFYING`.
*   `analysis_complete`: Set to `True`.

### Frontend Interaction (SSE)
*   **Status Update:** `status: "analyzing"`, `message: "AI is analyzing your request..."`
*   **Completion:** `status: "analysis_complete"`, includes scores, summary, and question.

---

## 2. Clarification Loop (`clarify_prompt`)

*   **Condition:** Triggered iteratively after analysis until `llm_ready` is true (score target met) OR timeout (max questions/time).
*   **Location:** `backend/app/utils/diagram_wizard/nodes/clarification_nodes.py`

### System Prompt
*   **Source:** `backend/app/utils/diagram_wizard/prompts/ANALYSE_CLARIFY.md` (Unified file) OR `CLARIFY_PROMPTS.md` (Legacy section "Universal Clarification Prompt").
*   **Structure:** Combines `analyze_request` prompt (for schema context) + `clarify_universal` prompt.
*   **Loader Key:** `clarify_universal`

### Inputs
*   **User Content:** Last 5 user messages from `clarification_history`.
    ```python
    user_content = "\n".join([f"User: {msg['content']}" for msg in user_messages[-5:]])
    ```
*   **Context:** `clarification_history` (entire conversation context).

### Outputs
**JSON Schema (Expected from LLM):**
```json
{
  "question": "string", // The clarifying question to ask
  "clarity_score": int, // Current understanding score (0-100)
  "ready": boolean, // True if enough info to generate
  "json_representation": object, // Refined architecture JSON
  "design_summary": "string" // Final summary if ready (prefixed with "READY:")
}
```

### LangGraph State Updates
*   `clarification_history`: Appends the new question.
*   `clarity_scores`: Appends the new score.
*   `json_representation`: Refines the architecture model.
*   `llm_ready`: Set to `True` if ready, else `False`.
*   `final_design_summary`: Set if ready.

### Frontend Interaction (SSE)
*   **Question:** `status: "clarifying"`, `question: "..."`, `clarity_score: ...`.
*   **Completion:** `status: "clarification_ready"`, `message: "..."` (asking for user confirmation).

---

## 3. Architecture Generation (`generate_json_representation`)

*   **Condition:** Triggered after clarification is complete (`llm_ready=True`) and user confirms.
*   **Location:** `backend/app/utils/diagram_wizard/nodes/generation_nodes.py`

### System Prompt
*   **Source:** `backend/app/utils/diagram_wizard/prompts/JSON_GENERATION_PROMPT.md` (Generic) OR Model-specific versions (e.g., `JSON_GENERATION_gpt5.md`).
*   **Loader Key:** `json_generation` or `json_generation_{model_id}`.

### Inputs
*   **User Content:** Full `clarification_history`.

### Outputs
**JSON Schema (Expected from LLM):**
```json
{
  "structurizr_workspace": "string", // DSL content
  "clean_structurizr": "string", // Normalized DSL
  "json_representation": object // Legacy JSON format
}
```

### LangGraph State Updates
*   `structurizr_workspace`: Populated.
*   `clean_structurizr`: Populated.
*   `json_representation`: Finalized.
*   `json_generation_output`: Raw LLM response string.

### Frontend Interaction (SSE)

*   **Status:** `status: "generating_json"`.
*   **Success:** `status: "json_generated"`, includes `json_generation_output` (raw LLM response), `structurizr_workspace` (full Structurizr DSL workspace for Workspace tab), and `clean_structurizr` (normalized Structurizr model section for Workspace tab).

---

## 4. Diagram Type Selection (`determine_diagram_type_node`)

*   **Condition:** Triggered after JSON representation is generated and user confirms ready.
*   **Location:** `backend/app/utils/diagram_wizard/nodes/generation_nodes.py`
*   **Note:** This is NOT an LLM interaction - it uses keyword-based scoring algorithm.

### Process

*   Analyzes the `final_design_summary`, `json_representation`, and `clarification_history` for keywords specific to each diagram type.
*   Calculates match scores for Mermaid, D2, PlantUML, and Structurizr.
*   Returns recommended diagram type and all scores.
*   **Pauses workflow** waiting for user to select their preferred diagram type.

### Frontend Interaction (SSE)

*   **Status:** `status: "awaiting_diagram_type_selection"`, includes `recommended_diagram_type` (highest scoring type), `keyword_scores` (scores for all diagram types in %), `analysis_text` (context used for scoring), and `awaiting_user_selection: true`.
*   **Resume:** After user selects type via `/diagram/select_diagram_type` endpoint, workflow continues to code generation.

---

## 5. Diagram Code Generation (`generate_code`)

*   **Condition:** Triggered after user selects a diagram type (Mermaid, D2, PlantUML, Structurizr).
*   **Location:** `backend/app/utils/diagram_wizard/nodes/generation_nodes.py`

### System Prompt
*   **Primary Source:** `backend/app/utils/diagram_wizard/prompts/FIRSTPASS_{TYPE}.md` (e.g., `FIRSTPASS_MERMAID.md`).
*   **Fallback Source:** `backend/app/utils/diagram_wizard/prompts/{TYPE}_GENERATION.md` (e.g., `MERMAID_GENERATION.md`).
*   **Loader Keys:** `firstpass_{type}` or `generate_{type}`.

### Inputs
*   **Payload:** `json_generation_output` (Raw JSON/Structurizr from previous step) OR structured `json_representation`.
*   **Prompt:** Selected based on `diagram_type`.

### Outputs
*   **Format:** Raw string containing the diagram code (often wrapped in markdown code blocks).

### LangGraph State Updates
*   `diagram_code`: The generated code string.
*   `current_state`: Set to `SessionState.VALIDATING`.

### Frontend Interaction (SSE + REST API)

*   **SSE (Read-Only Progress):**
    *   **Status:** `status: "generating"`, `message: "AI is generating {type} diagram code..."`.
    *   **Success:** `status: "code_generated"`.
*   **REST API (State Mutation):**
    *   After receiving `code_generated` event, frontend polls `GET /diagram/{session_id}` to fetch `diagramCode`.

---

## 5. Code Refinement (`refine_code`)

*   **Condition:** Triggered if validation fails (and attempt count < 3). **Note:** While this node exists in `validation_nodes.py`, the current graph (`langgraph_builder.py`) may bypass it if using the Provider System's internal validation/refinement loop.
*   **Location:** `backend/app/utils/diagram_wizard/nodes/validation_nodes.py`

### System Prompt
*   **Source:** `backend/app/utils/diagram_wizard/prompts/REFINE_PROMPTS.md`.
*   **Loader Key:** `refine_{type}`.

### Inputs
*   **Context:**
    ```text
    Code: {current_invalid_code}
    Error: {validation_error_message}
    Attempt: {attempt_count}
    ```
*   **Design Summary:** `final_design_summary`.

### Outputs
*   **Format:** Corrected diagram code string.

### LangGraph State Updates
*   `diagram_code`: Updated with fixed code.
*   `validation_error`: Cleared.
*   `refinement_attempt`: Incremented.

### Frontend Interaction (SSE)

*   **Status:** `status: "refining"`, `message: "AI is fixing diagram code..."`.
*   **Success:** `status: "code_refined"`.

---

## 6. Diagram Rendering (`render_diagram`)

*   **Condition:** Triggered after diagram code is generated.
*   **Location:** `backend/app/utils/diagram_wizard/nodes/rendering_nodes.py`
*   **Note:** This is NOT an LLM interaction - rendering is handled by the Provider System. However, the provider system MAY use LLM for automatic code correction if validation fails.

### Process

*   Uses the diagram provider system to validate and render the diagram code to SVG.
*   Provider's `render_with_validation()` handles: validation, pattern-based auto-fix, LLM correction (if needed), and final rendering.
*   The LLM model used for correction comes from `settings.default_model` (.env), not the user-selected model.

### LangGraph State Updates

*   `svg_output`: The rendered SVG content.
*   `diagram_code`: May be updated if provider corrected the code.
*   `current_state`: Set to `SessionState.READY` on success, `SessionState.ERROR` on failure.

### Frontend Interaction (SSE + REST API)

*   **SSE (Read-Only Progress):**
    *   **Status:** `status: "rendering"`, `message: "Rendering {type} diagram to SVG..."`.
    *   **Provider Progress:** `validating`, `auto_fixing`, `auto_fixed`, `llm_correcting`, `llm_corrected`, `render_complete`.
    *   **Success:** `status: "rendered"`.
    *   **Error:** `status: "error"`, includes error message.
*   **REST API (State Mutation):**
    *   After receiving `rendered` event, frontend polls `GET /diagram/{session_id}` to fetch `svgOutput` and final `diagramCode` (may be corrected by provider).
