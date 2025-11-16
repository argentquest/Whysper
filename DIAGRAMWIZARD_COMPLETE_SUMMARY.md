# DiagramWizard: Complete Architecture Summary

## 📊 Project Status: PHASE 1 COMPLETE ✅

All prompt files created and documented. Ready for backend/frontend implementation.

---

## 🎯 System Overview

### What is DiagramWizard?

A **LangGraph-based system** that helps users create architecture diagrams through:
1. **Intelligent analysis** of user descriptions
2. **Interactive clarification** (asking targeted questions)
3. **Automatic diagram generation** (Mermaid, D2, or PlantUML)

### User Journey

```
1. User opens DiagramWizard
   ↓
2. Selects preferred AI model (GPT-5, Grok, Claude, or Gemini)
   ↓
3. Describes their system architecture
   ↓
4. AI analyzes (ANALYSE_CONFIRM phase)
   ↓
5. AI asks clarifying questions (CLARIFY_UNIVERSAL loop)
   ↓
6. When clarity >= 8, system determines diagram type
   ↓
7. AI generates diagram code
   ↓
8. Code validated and refined if needed
   ↓
9. Final SVG diagram rendered
   ↓
10. User can export/copy
```

---

## 🗂️ Architecture: LangGraph Workflow

### Nodes (7 total)

| Node | Phase | Trigger | Purpose | Output |
|------|-------|---------|---------|--------|
| **analyze_request** | Init | Graph entry point | Initial analysis of user description | Clarity score, Structurizr workspace |
| **clarify_prompt** | Loop | After analysis | Ask clarifying questions | Updated Structurizr, clarity score |
| **determine_diagram_type** | Post-clarify | Clarity >= 8 | Keyword-based selection | Mermaid/D2/PlantUML choice |
| **generate_code** | Generation | Type selected | LLM generates diagram code | Source code string |
| **validate_code** | Validation | Code generated | Check syntax correctness | Valid/invalid flag |
| **refine_code** | Refinement | Invalid code | LLM fixes errors | Fixed code (max 3 attempts) |
| **render_diagram** | Rendering | Valid code | Render to SVG | SVG output |

### Edges (Flow)

```
analyze_request
    ↓
clarify_prompt (LOOP)
    ↓
determine_diagram_type (auto-select)
    ↓
generate_code
    ↓
validate_code
    ├─ valid → render_diagram → END
    └─ invalid → refine_code (max 3) → validate_code
```

---

## 📝 Prompt Files: 8 Model-Specific Versions

### ANALYSE_CONFIRM Phase (Initial Analysis)

Analyzes user's initial description and determines clarity level.

**Files:**
- `diagram-wizard-gpt5.md` – GPT-5 (long-context)
- `diagram-wizard-grok.md` – Grok (fast)
- `diagram-wizard-sonet45.md` – Claude Sonnet 4.5 (transparent)
- `diagram-wizardgemini25pro.md` – Gemini 2.5 Pro (efficient)

**Output:** Structurizr workspace + Clean Structurizr + clarity score (1-10)

### CLARIFY_UNIVERSAL Phase (Iterative Refinement)

Refines understanding through targeted questions until clarity >= 8.

**Files:**
- `clarify-universal-gpt5.md` – GPT-5 (deep verification)
- `clarify-universal-grok.md` – Grok (fast iteration)
- `clarify-universal-sonet45.md` – Claude Sonnet 4.5 (structured)
- `clarify-universal-gemini25pro.md` – Gemini 2.5 Pro (efficient)

**Output:** Updated Structurizr workspace + question or ready signal

---

## 🎨 Model Selection: User Chooses at Start

### Why 4 Models?

| Model | Strength | Best For | Users Who |
|-------|----------|----------|-----------|
| **GPT-5** | Long-context reasoning | Complex systems | Want deep analysis |
| **Grok** | Fast & deterministic | Simple systems | Value speed |
| **Claude** | Transparent thinking | Understanding decisions | Want explainability |
| **Gemini** | Efficient output | Performance-critical | Minimize latency |

### Selection Flow

```
┌─────────────────────────┐
│ ModelSelector Screen    │
├─────────────────────────┤
│ ☐ GPT-5                 │
│ ☐ Grok                  │
│ ☐ Claude Sonnet 4.5     │
│ ☐ Gemini 2.5 Pro        │
│                         │
│ [Select] [Cancel]       │
└────────────┬────────────┘
             │
     ┌───────▼────────┐
     │ Session Start  │
     │ model_id stored│
     └───────┬────────┘
             │
     ┌───────▼─────────────────┐
     │ Load 2 Prompts:         │
     │ • diagram-wizard-{id}   │
     │ • clarify-universal-{id}│
     └───────┬─────────────────┘
             │
     ┌───────▼──────────────────┐
     │ Use selected model       │
     │ throughout session       │
     └───────────────────────────┘
```

---

## 🔄 State Management

### GraphState (Central)

Tracks session data throughout LangGraph execution:

```python
class GraphState(TypedDict, total=False):
    # Session
    session_id: str
    model_id: str              # USER'S SELECTION
    provider: str              # (openrouter|xai|anthropic|google)
    model: str                 # Full model name

    # Clarification Loop
    clarification_history: List[Dict]
    clarity_score: int         # 1-10 scale
    json_representation: Dict  # Structurizr data
    structurizr_workspace: str # Full workspace DSL
    clean_d2: str             # Normalized Structurizr
    llm_ready: bool           # Clarity >= 8?
    question: str             # Next clarification question

    # Diagram Type & Code
    diagram_type: DiagramType # Mermaid|D2|PlantUML
    diagram_code: str         # Source code

    # Validation
    is_valid: bool            # Syntax valid?
    validation_error: str     # Error message
    refinement_attempt: int   # Counter (max 3)

    # Final Output
    svg_output: str           # Rendered SVG
    current_state: SessionState
```

---

## 📊 Prompt Output Schema

### Unified JSON Contract

All 8 prompts return identical schema:

```json
{
  "analysis_summary": "string - what changed this turn",
  "clarity_score": "1-10 integer",
  "information_score": {
    "entities": "boolean - all systems identified?",
    "actions": "boolean - all interactions understood?",
    "structure": "boolean - architecture clear?",
    "word_count": "integer - user input length"
  },
  "question": "string - one clarifying question OR null when ready",
  "ready": "boolean - clarity >= 8?",
  "structurizr_workspace": "string - full Structurizr DSL",
  "clean_d2": "string - normalized Structurizr (no views)",
  "assumptions": ["array of inferred facts"],
  "next_step": "awaiting_user_clarification OR ready_for_generation"
}
```

### Key Guarantees

- ✅ **Same schema across all models** – No model variations
- ✅ **Structurizr DSL only** – Not D2 diagram syntax
- ✅ **Dual representation** – workspace + clean_d2 always synchronized
- ✅ **One question per turn** – Exactly one, never zero or multiple
- ✅ **Clarity scale** – Always 1-10
- ✅ **Ready = clarity >= 8** – Consistent threshold

---

## 🔧 Implementation Phases

### Phase 1: Prompts ✅ COMPLETE
- ✅ All 8 model-specific prompts created
- ✅ All prompts tested for format/syntax
- ✅ Documentation complete

### Phase 2: Backend (📋 Ready to Implement)
- GraphState updates (add model_id, provider, model)
- Prompt loader (load model-specific prompts)
- Node updates (pass model_id through)
- API endpoint (accept model_id at start)

### Phase 3: Frontend (📋 Ready to Implement)
- ModelSelector component (4 model options)
- DiagramWizard update (show selector first)
- API client updates (pass model_id)

### Phase 4-7: Testing, Documentation, Deployment
- Unit tests, integration tests, E2E tests
- API documentation
- User guide
- Production deployment

---

## 📈 Data Flow

### Session Initialization

```
User selects model (GPT-5)
    ↓
POST /api/diagram-wizard/start-session
    {
      "initial_prompt": "I have a microservices system...",
      "model_id": "gpt5"
    }
    ↓
Backend lookup: MODEL_MAPPING['gpt5']
    ↓
Create session with:
    - session_id
    - model_id = 'gpt5'
    - provider = 'openrouter'
    - model = 'openai/gpt-5-*'
    ↓
Load prompts:
    - diagram-wizard-gpt5.md
    - clarify-universal-gpt5.md
    ↓
Start LangGraph with state
```

### During Clarification Loop

```
Each turn:

1. clarify_prompt node runs
   - Gets model_id from state
   - Loads clarify-universal-{model_id}.md
   - Calls _call_llm with model_id
   - Uses selected model (GPT-5) for API call
   ↓
2. LLM responds with JSON
   - Structurizr workspace updated
   - Clean Structurizr updated
   - Clarity score increased (5 → 6 → 7 → 8)
   ↓
3. If clarity < 8: ask next question
   If clarity >= 8: mark ready=true
   ↓
4. Return to step 1 or proceed to next node
```

---

## ⚙️ Configuration

### MODEL_MAPPING

```python
{
    'gpt5': {
        'provider': 'openrouter',
        'model': 'openai/gpt-5-*',
        'analyze_prompt': 'diagram-wizard-gpt5.md',
        'clarify_prompt': 'clarify-universal-gpt5.md'
    },
    'grok': {
        'provider': 'xai',
        'model': 'grok-*',
        'analyze_prompt': 'diagram-wizard-grok.md',
        'clarify_prompt': 'clarify-universal-grok.md'
    },
    'claude': {
        'provider': 'anthropic',
        'model': 'claude-sonnet-4.5-*',
        'analyze_prompt': 'diagram-wizard-sonet45.md',
        'clarify_prompt': 'clarify-universal-sonet45.md'
    },
    'gemini': {
        'provider': 'google',
        'model': 'gemini-2.5-pro-*',
        'analyze_prompt': 'diagram-wizardgemini25pro.md',
        'clarify_prompt': 'clarify-universal-gemini25pro.md'
    }
}
```

---

## 📚 Key Documents

| Document | Purpose |
|----------|---------|
| **DIAGRAMWIZARD_SEQUENCE_DIAGRAM.md** | Visual flow of all 7 nodes |
| **DIAGRAMWIZARD_ANALYSE_CONFIRM_VERSIONS.md** | Deep dive into 4 ANALYSE versions |
| **CLARIFY_PROMPT_REQUIREMENTS_ANALYSIS.md** | Options for LLM score scale (1-10 vs 1-100) |
| **MODEL_SELECTION_AT_START.md** | User selection flow & implementation guide |
| **PROMPT_VERSIONS_COMPLETE.md** | Summary of all 8 prompts |
| **IMPLEMENTATION_CHECKLIST.md** | Detailed task list for phases 2-7 |
| **This file** | Complete system summary |

---

## 🎓 Key Concepts

### Structurizr vs. D2

- **Structurizr DSL**: Architecture modeling language (output by ANALYSE_CONFIRM & CLARIFY)
- **D2 Diagram Syntax**: Diagram rendering syntax (used by generate_code phase)
- **Relationship**: Structurizr → Clean Structurizr → D2/Mermaid/PlantUML → SVG

### Clarity Score (1-10)

- **1-3**: Very unclear, need lots of detail
- **4-6**: Some understanding, need clarifications
- **7-8**: Good understanding, minor gaps (READY level)
- **9-10**: Complete, production-ready

### Clean Structurizr

- Normalized, minimal form of Structurizr workspace
- Used for code generation (more concise than full workspace)
- Always synchronized with full workspace
- No views block (minimal form)

### Model Selection Persistence

- Selected model ID stored in session
- All subsequent LLM calls use the selected model
- Same model throughout entire session
- No switching between models mid-session

---

## 🔐 Safety Features

- **Refinement limit**: Max 3 attempts to fix invalid code
- **Clarification timeout**: Max 10 questions or 5 minutes
- **Schema validation**: All prompts return identical JSON
- **Synchronization check**: Workspace ↔ Clean Structurizr always match
- **No model switching**: Selected model used throughout

---

## 📞 Support & Next Steps

### For Backend Implementation
→ See: `IMPLEMENTATION_CHECKLIST.md` Phase 2

### For Frontend Implementation
→ See: `IMPLEMENTATION_CHECKLIST.md` Phase 3

### For Testing Strategy
→ See: `IMPLEMENTATION_CHECKLIST.md` Phase 4

### For API Documentation
→ See: `MODEL_SELECTION_AT_START.md` - API Changes

### For Troubleshooting
1. Check prompt files in `prompts/coding/agent/`
2. Verify model_id in session state
3. Confirm MODEL_MAPPING configuration
4. Check prompt_loader.py for model-specific loading
5. Verify LLM API credentials for selected provider

---

## 📊 Success Metrics

- ✅ All 8 prompts created and documented
- ✅ Unified output schema defined
- ✅ Model selection architecture designed
- ✅ Implementation checklist detailed
- ✅ Zero breaking changes to existing system
- ⏳ Next: Backend/frontend implementation (~10 days)
- ⏳ Finally: Production deployment & monitoring

---

**Project Status:** Phase 1 Complete ✅
**Last Updated:** 2025-11-16
**Ready for:** Backend Implementation
**Estimated Total Duration:** 10-12 days from Phase 2 start
