# DiagramWizard: 4 Model-Specific Prompt Versions - COMPLETE

## Status: ✅ ALL PROMPTS CREATED

We now have **8 model-specific prompt files**:
- **4 ANALYSE_CONFIRM versions** (initial analysis phase)
- **4 CLARIFY_UNIVERSAL versions** (clarification loop phase)

---

## Prompt File Structure

### ANALYSE_CONFIRM Phase (Initial Analysis)

These run first, analyzing the user's initial design description:

| File | Model | Optimization | Key Feature |
|------|-------|--------------|-------------|
| `diagram-wizard-gpt5.md` | GPT-5 | Long-context reasoning | Cross-check & validate deeply |
| `diagram-wizard-grok.md` | Grok | Deterministic speed | Fast, lean responses |
| `diagram-wizard-sonet45.md` | Claude Sonnet 4.5 | Structured thinking | Transparent assumptions |
| `diagram-wizardgemini25pro.md` | Gemini 2.5 Pro | Efficiency | Compact output |

**Output Schema (all versions identical):**
```json
{
  "analysis_summary": "string",
  "clarity_score": 1-10,
  "information_score": {entities, actions, structure, word_count},
  "question": "string|null",
  "ready": boolean,
  "structurizr_workspace": "string (full DSL with model+views)",
  "clean_d2": "string (normalized Structurizr)",
  "assumptions": ["array"],
  "next_step": "string"
}
```

### CLARIFY_UNIVERSAL Phase (Iterative Refinement)

These run in a loop, refining understanding until clarity >= 8:

| File | Model | Optimization | Key Feature |
|------|-------|--------------|-------------|
| `clarify-universal-gpt5.md` | GPT-5 | Deep verification | 5-point cross-check before ready |
| `clarify-universal-grok.md` | Grok | Response efficiency | <350 words, deterministic |
| `clarify-universal-sonet45.md` | Claude Sonnet 4.5 | Behavioral clarity | Shows reasoning & transparency |
| `clarify-universal-gemini25pro.md` | Gemini 2.5 Pro | Response efficiency | <2,000 chars, pragmatic |

**Output Schema (all versions identical):**
```json
{
  "analysis_summary": "string",
  "clarity_score": 1-10,
  "information_score": {entities, actions, structure, word_count},
  "question": "string|null",
  "ready": boolean,
  "structurizr_workspace": "string (full DSL with model+views)",
  "clean_d2": "string (normalized Structurizr)",
  "assumptions": ["array"],
  "next_step": "string"
}
```

---

## File Locations

All files in: `prompts/coding/agent/`

```
prompts/coding/agent/
├── diagram-wizard-gpt5.md              [ANALYSE_CONFIRM for GPT-5]
├── diagram-wizard-grok.md              [ANALYSE_CONFIRM for Grok]
├── diagram-wizard-sonet45.md           [ANALYSE_CONFIRM for Claude]
├── diagram-wizardgemini25pro.md        [ANALYSE_CONFIRM for Gemini]
├── clarify-universal-gpt5.md           [CLARIFY_UNIVERSAL for GPT-5]
├── clarify-universal-grok.md           [CLARIFY_UNIVERSAL for Grok]
├── clarify-universal-sonet45.md        [CLARIFY_UNIVERSAL for Claude]
└── clarify-universal-gemini25pro.md    [CLARIFY_UNIVERSAL for Gemini]
```

---

## Model Selection at Runtime

### User Flow

1. **User opens DiagramWizard**
2. **ModelSelector UI appears** with 4 options:
   - ☐ GPT-5 (long-context, deep analysis)
   - ☐ Grok (fast, deterministic)
   - ☐ Claude Sonnet 4.5 (transparent, structured)
   - ☐ Gemini 2.5 Pro (efficient, pragmatic)
3. **User selects one** → `model_id` stored in session
4. **System loads both prompts** for selected model:
   - diagram-wizard-{model}.md
   - clarify-universal-{model}.md
5. **Entire session uses selected model's prompts**
6. **Same model processes all turns** until completion

### Backend Implementation

```python
# Map user's choice to prompt files
MODEL_MAPPING = {
    'gpt5': {
        'analyze_prompt': 'diagram-wizard-gpt5.md',
        'clarify_prompt': 'clarify-universal-gpt5.md',
        'provider': 'openrouter',
        'model': 'openai/gpt-5-*'
    },
    'grok': {
        'analyze_prompt': 'diagram-wizard-grok.md',
        'clarify_prompt': 'clarify-universal-grok.md',
        'provider': 'xai',
        'model': 'grok-*'
    },
    'claude': {
        'analyze_prompt': 'diagram-wizard-sonet45.md',
        'clarify_prompt': 'clarify-universal-sonet45.md',
        'provider': 'anthropic',
        'model': 'claude-sonnet-4.5-*'
    },
    'gemini': {
        'analyze_prompt': 'diagram-wizardgemini25pro.md',
        'clarify_prompt': 'clarify-universal-gemini25pro.md',
        'provider': 'google',
        'model': 'gemini-2.5-pro-*'
    }
}
```

---

## Prompt Loader Update

```python
def get_prompt(prompt_key: str, model_id: str = None) -> str:
    """
    Load a prompt, optionally model-specific version.

    Examples:
        get_prompt("analyze_request", "gpt5")
        → Loads: diagram-wizard-gpt5.md

        get_prompt("clarify_universal", "grok")
        → Loads: clarify-universal-grok.md
    """
    if model_id:
        model_specific_key = f"{prompt_key}_{model_id}"
        if model_specific_key in PROMPTS_CACHE:
            return PROMPTS_CACHE[model_specific_key]

    if prompt_key in PROMPTS_CACHE:
        return PROMPTS_CACHE[prompt_key]

    # Load from file...
```

---

## Node Updates Required

### clarify_prompt Node

**Current behavior:**
```python
prompt_template = get_prompt("clarify_universal")  # Gets generic
```

**Updated behavior:**
```python
model_id = state.get("model_id")  # From session
prompt_template = get_prompt("clarify_universal", model_id)  # Gets model-specific
```

### analyze_request Node

**Current behavior:**
```python
prompt_template = get_prompt("analyze_request")  # Gets generic
```

**Updated behavior:**
```python
model_id = state.get("model_id")  # From session
prompt_template = get_prompt("analyze_request", model_id)  # Gets model-specific

# Note: analyze_request doesn't exist as separate files yet
# This would be implemented as:
# - diagram-wizard-{model}.md handles INITIAL analysis
# - So re-use those files for the analyze_request prompt
```

---

## Key Features by Model

### GPT-5 Edition
- ✅ **Cross-check strategy**: 5-point validation before marking ready
- ✅ **Deep reasoning**: Leverages long-context capability
- ✅ **Explicit verification**: "Entities Check", "Relationships Check", etc.
- ✅ Best for: Complex, multi-tier architectures

### Grok Edition
- ✅ **Fast responses**: <400 words, <350 for clarify
- ✅ **Deterministic**: No invention, facts-only approach
- ✅ **Lean output**: Minimal but complete
- ✅ Best for: Quick iterations, simple systems

### Claude Sonnet 4.5 Edition
- ✅ **Structured thinking**: Clear step-by-step reasoning
- ✅ **Transparent assumptions**: Shows what it's inferring
- ✅ **Example-driven**: Conversation flow examples provided
- ✅ Best for: Understanding decision process, auditable results

### Gemini 2.5 Pro Edition
- ✅ **Efficiency**: <2,000 chars output, pragmatic
- ✅ **Table-driven**: Uses markdown tables for clarity
- ✅ **Condensed guidance**: Rules as compact table
- ✅ Best for: Performance-critical scenarios, quick processing

---

## Unified Output Contract

All 8 prompts return the **same JSON schema**:

```json
{
  "analysis_summary": "Narrative update on architecture understanding",
  "clarity_score": 1-10,
  "information_score": {
    "entities": boolean,
    "actions": boolean,
    "structure": boolean,
    "word_count": integer
  },
  "question": "One clarifying question or null",
  "ready": boolean,
  "structurizr_workspace": "Full Structurizr DSL workspace",
  "clean_d2": "Normalized Clean Structurizr code",
  "assumptions": ["Array of inferred facts"],
  "next_step": "awaiting_user_clarification or ready_for_generation"
}
```

**Guarantees:**
- ✅ All models return identical schema
- ✅ All models use **Structurizr DSL syntax only** (not D2 diagram code)
- ✅ All models maintain **dual representation** (workspace + clean_d2)
- ✅ All models ask **exactly one question per turn**
- ✅ All models mark **ready=true only when clarity >= 8**

---

## Next Implementation Steps

1. **Update session initialization**
   - Accept `model_id` from frontend
   - Store in `GraphState`
   - Pass to all nodes

2. **Update prompt_loader.py**
   - Implement model-specific prompt loading
   - Create proper key mapping

3. **Update clarify_prompt node**
   - Pass `model_id` to get_prompt()
   - Same for _call_llm()

4. **Create frontend ModelSelector component**
   - Show 4 model options at start
   - Pass selection to backend

5. **Update API endpoints**
   - `/start-session` accepts `model_id`
   - `/clarify` uses stored `model_id`

6. **Testing**
   - Test each model's prompt with sample conversations
   - Verify Structurizr sync between workspace and clean_d2
   - Validate clarity scoring progression

---

## Backward Compatibility

**Current system (without model selection):**
- Uses environment variables: `PROVIDER`, `DEFAULT_MODEL`
- Falls back to Claude Sonnet if no env vars set

**New system (with model selection):**
- User explicitly chooses model at start
- Selected model's prompts used throughout session
- Falls back to Claude if selection unavailable

**Migration:** No breaking changes. System works with or without explicit model selection.

---

## Summary

| Component | Status | Files |
|-----------|--------|-------|
| **ANALYSE_CONFIRM prompts** | ✅ Complete | 4 files |
| **CLARIFY_UNIVERSAL prompts** | ✅ Complete | 4 files |
| **Model selection logic** | 📋 Documented | MODEL_SELECTION_AT_START.md |
| **Prompt loader updates** | 📋 Documented | This file |
| **Node updates** | 📋 Documented | This file |
| **Frontend ModelSelector** | 📋 Documented | MODEL_SELECTION_AT_START.md |
| **API changes** | 📋 Documented | MODEL_SELECTION_AT_START.md |

---

**Generated:** 2025-11-16
**Total Prompts:** 8 model-specific versions
**Next Action:** Implement backend/frontend integration for model selection
