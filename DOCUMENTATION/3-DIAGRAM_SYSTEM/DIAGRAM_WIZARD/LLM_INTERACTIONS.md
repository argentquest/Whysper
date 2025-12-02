# Diagram Wizard LLM Interactions

This document details all LLM interactions within the Diagram Wizard system, mapping out when they occur, how they are structured, and their inputs/outputs. It also covers the lifecycle of Diagram Providers.

## Part 1: Diagram Wizard LangGraph Workflow

This section covers the core workflow orchestrated by LangGraph in `backend/app/utils/diagram_wizard/`.

### 1. Request Analysis (`analyze_request`)

*   **Condition:** Triggered at the very start of the session to understand the user's intent. Skipped if `analysis_complete` is already true in the state.
*   **Location:** `backend/app/utils/diagram_wizard/nodes/analysis_nodes.py`
*   **Line Range:** ~70-160

#### System Prompt
*   **Source:** `backend/app/utils/diagram_wizard/prompts/ANALYSE_CLARIFY.md` (Unified file) OR `ANALYSE_PROMPT.md` (Legacy).
*   **Loader Key:** `analyze_request`

#### Inputs
*   **User Content:** Derived from `clarification_history` (all user messages joined).
    ```python
    user_content = "\n".join([msg.get("content", "") for msg in clarification_history if msg.get("role") == "user"])
    ```
*   **Model ID:** `state.get("model_id")`

#### Outputs
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

#### LangGraph State Updates
*   `next_action`: Set to `"clarify"`.
*   `assessment_score`: Updated with LLM score.
*   `json_representation`: Initial population.
*   `clarification_history`: Appends Assistant's summary and question.
*   `current_state`: Set to `SessionState.CLARIFYING`.
*   `analysis_complete`: Set to `True`.

#### Frontend Interaction (SSE)
*   **Status Update:** `status: "analyzing"`, `message: "AI is analyzing your request..."`
*   **Completion:** `status: "analysis_complete"`, includes scores, summary, and question.

---

### 2. Clarification Loop (`clarify_prompt`)

*   **Condition:** Triggered iteratively after analysis until `llm_ready` is true (score target met) OR timeout (max questions/time).
*   **Location:** `backend/app/utils/diagram_wizard/nodes/clarification_nodes.py`
*   **Line Range:** ~30-220

#### System Prompt
*   **Source:** `backend/app/utils/diagram_wizard/prompts/ANALYSE_CLARIFY.md` (Unified file) OR `CLARIFY_PROMPTS.md` (Legacy section "Universal Clarification Prompt").
*   **Structure:** Combines `analyze_request` prompt (for schema context) + `clarify_universal` prompt.
*   **Loader Key:** `clarify_universal`

#### Inputs
*   **User Content:** Last 5 user messages from `clarification_history`.
    ```python
    user_content = "\n".join([f"User: {msg['content']}" for msg in user_messages[-5:]])
    ```
*   **Context:** `clarification_history` (entire conversation context).

#### Outputs
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

#### LangGraph State Updates
*   `clarification_history`: Appends the new question.
*   `clarity_scores`: Appends the new score.
*   `json_representation`: Refines the architecture model.
*   `llm_ready`: Set to `True` if ready, else `False`.
*   `final_design_summary`: Set if ready.

#### Frontend Interaction (SSE)
*   **Question:** `status: "clarifying"`, `question: "..."`, `clarity_score: ...`.
*   **Completion:** `status: "clarification_ready"`, `message: "..."` (asking for user confirmation).

---

### 3. Architecture Generation (`generate_json_representation`)

*   **Condition:** Triggered after clarification is complete (`llm_ready=True`) and user confirms.
*   **Location:** `backend/app/utils/diagram_wizard/nodes/generation_nodes.py`
*   **Line Range:** ~20-130

#### System Prompt
*   **Source:** `backend/app/utils/diagram_wizard/prompts/JSON_GENERATION_PROMPT.md` (Generic) OR Model-specific versions (e.g., `JSON_GENERATION_gpt5.md`).
*   **Loader Key:** `json_generation` or `json_generation_{model_id}`.

#### Inputs
*   **User Content:** Full `clarification_history`.

#### Outputs
**JSON Schema (Expected from LLM):**
```json
{
  "structurizr_workspace": "string", // DSL content
  "clean_structurizr": "string", // Normalized DSL
  "json_representation": object // Legacy JSON format
}
```

#### LangGraph State Updates
*   `structurizr_workspace`: Populated.
*   `clean_structurizr`: Populated.
*   `json_representation`: Finalized.
*   `json_generation_output`: Raw LLM response string.

#### Frontend Interaction (SSE)
*   **Status:** `status: "generating_json"`.
*   **Success:** `status: "json_generated"`.

---

### 4. Diagram Code Generation (`generate_code`)

*   **Condition:** Triggered after user selects a diagram type (Mermaid, D2, PlantUML, Structurizr).
*   **Location:** `backend/app/utils/diagram_wizard/nodes/generation_nodes.py`
*   **Line Range:** ~220-310

#### System Prompt
*   **Primary Source:** `backend/app/utils/diagram_wizard/prompts/FIRSTPASS_{TYPE}.md` (e.g., `FIRSTPASS_MERMAID.md`).
*   **Fallback Source:** `backend/app/utils/diagram_wizard/prompts/{TYPE}_GENERATION.md` (e.g., `MERMAID_GENERATION.md`).
*   **Loader Keys:** `firstpass_{type}` or `generate_{type}`.

#### Inputs
*   **Payload:** `json_generation_output` (Raw JSON/Structurizr from previous step) OR structured `json_representation`.
*   **Prompt:** Selected based on `diagram_type`.

#### Outputs
*   **Format:** Raw string containing the diagram code (often wrapped in markdown code blocks).

#### LangGraph State Updates
*   `diagram_code`: The generated code string.
*   `current_state`: Set to `SessionState.VALIDATING`.

#### Frontend Interaction (SSE)
*   **Status:** `status: "generating"`, `message: "AI is generating {type} diagram code..."`.
*   **Success:** `status: "code_generated"`.

---

### 5. Code Refinement (`refine_code`) [DEPRECATED / UNUSED]

> **Note:** This node is currently **disconnected** in the active LangGraph workflow (`langgraph_builder.py`).
> The responsibility for syntax validation and refinement has been moved to the **Diagram Provider System** (see Part 2 below), which handles its own internal LLM correction loop. This section is preserved for reference to the legacy logic still present in the codebase.

*   **Condition:** formerly triggered if validation failed within the Wizard workflow. Now superseded by Provider self-correction.
*   **Location:** `backend/app/utils/diagram_wizard/nodes/validation_nodes.py`
*   **Line Range:** ~90-180

#### System Prompt
*   **Source:** `backend/app/utils/diagram_wizard/prompts/REFINE_PROMPTS.md`.
*   **Loader Key:** `refine_{type}`.

#### Inputs
*   **Context:**
    ```text
    Code: {current_invalid_code}
    Error: {validation_error_message}
    Attempt: {attempt_count}
    ```
*   **Design Summary:** `final_design_summary`.

#### Outputs
*   **Format:** Corrected diagram code string.

#### LangGraph State Updates
*   `diagram_code`: Updated with fixed code.
*   `validation_error`: Cleared.
*   `refinement_attempt`: Incremented.

#### Frontend Interaction (SSE)
*   **Status:** `status: "refining"`, `message: "AI is fixing diagram code..."`.
*   **Success:** `status: "code_refined"`.

---

## Part 2: Diagram Provider Lifecycle

This section covers the lifecycle of Diagram Providers (located in `backend/diagrams/`), which handle the actual validation, rendering, and self-correction of diagram code.

### 1. Provider Discovery & Registration

*   **Condition:** Occurs on application startup or when `get_registry()` is called.
*   **Location:** `backend/diagrams/provider_registry.py`
*   **Logic:**
    1.  Scans `backend/diagrams/` for subfolders.
    2.  Checks for `config.json` in each folder.
    3.  Imports the renderer module (e.g., `mermaid_renderer.py`).
    4.  Instantiates the `BaseDiagramProvider` subclass.
    5.  Registers it in the `ProviderRegistry`.

### 2. Render Pipeline (`render_with_validation`)

*   **Condition:** Called by the `render_diagram` node in the Wizard or any service requesting a diagram.
*   **Location:** `backend/diagrams/base_diagram.py`
*   **Line Range:** ~350-520 (approx)

#### Lifecycle Steps
1.  **Validation:** Calls `provider.validate_code(code)`.
2.  **Pattern-Based Fix:** (If invalid) Calls `provider.auto_fix_pattern_based()` for regex fixes.
3.  **LLM Correction:** (If still invalid) Calls `_attempt_llm_correction()`.
4.  **Rendering:** Calls `provider.render(code)`.

#### Inputs
*   `code`: Diagram source code.
*   `output_format`: "svg", "png", etc.
*   `auto_fix`: Boolean to enable pattern fixing.
*   `llm_correction`: Boolean to enable AI fixing.

#### Outputs
**RenderResult Object:**
```python
RenderResult(
    success=True/False,
    content="<svg>...</svg>",
    validation=ValidationResult(...),
    metadata={...},
    error="Error message if failed"
)
```

---

### 3. LLM-Based Correction (`_attempt_llm_correction`)

*   **Condition:** Triggered inside `render_with_validation` if initial validation fails AND `llm_correction=True`.
*   **Location:** `backend/diagrams/base_diagram.py`
*   **Line Range:** ~530-580
*   **Service:** Delegates to `backend/diagrams/llm_correction_service.py`.

#### System Prompt
*   **Source:** Constructed dynamically in `LLMCorrectionService.correct_diagram_code`.
*   **Structure:**
    ```text
    You are an expert at fixing {diagram_type} diagram syntax.
    Return only the corrected diagram code block with no commentary.
    Follow these rules strictly:
    - {Generic Rules}
    - {Type Specific Rules}
    - {Provider Specific Rules from correction_rules.md}
    ```
*   **Provider Rules Source:** `backend/diagrams/{provider}/correction_rules.md` (e.g., `mermaidv1/correction_rules.md`).

#### Inputs
*   `invalid_code`: The broken diagram code.
*   `error_message`: The specific validation error from the CLI/Tool.
*   `provider_specific_rules`: Loaded from the provider's `correction_rules.md`.

#### Outputs
*   **Format:** Corrected diagram code extracted from the LLM response.

#### Frontend Interaction (SSE)
*   **Status:** `status: "llm_correcting"`.
*   **Message:** `message: "Attempting AI-powered correction for {type}..."`.
*   **Metadata:** Includes `attempt` number and `max_retries`.
