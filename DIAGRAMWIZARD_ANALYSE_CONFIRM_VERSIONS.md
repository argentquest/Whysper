# DiagramWizard ANALYSE_CONFIRM: Four Model-Specific Versions

## Overview

There are **four different ANALYSE_CONFIRM prompt versions**, each optimized for a specific LLM provider. All share the same core workflow but are tailored to each model's strengths, constraints, and behavioral characteristics.

**Key Innovation:** These prompts guide LLMs to output **Structurizr DSL code** (not D2 diagram code) as the canonical architecture representation, replacing the legacy JSON schema. The system maintains **two synchronized forms**:
1. **Full Structurizr workspace** – Complete with model and views
2. **Clean Structurizr** – Normalized, deterministic form for downstream processing

---

## Core Workflow (Common to All Versions)

```
┌─────────────────────────────────────────────────────────────┐
│         ANALYSE_CONFIRM Phase (All Versions)               │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│ 1. ANALYSE                                                   │
│    └─ Read user turn + context                             │
│    └─ Summarize known actors, systems, containers          │
│                                                              │
│ 2. STRUCTURIZE                                              │
│    └─ Maintain Structurizr workspace snapshot              │
│    └─ Keep variable names stable between turns             │
│                                                              │
│ 3. CONFIRM                                                   │
│    └─ Score clarity (1-10)                                  │
│    └─ If clarity < 8: ask ONE clarification question        │
│    └─ If clarity >= 8: set ready=true                       │
│                                                              │
│ 4. OUTPUT                                                    │
│    └─ Emit Structurizr workspace + Clean Structurizr        │
│    └─ Replace legacy JSON schema                            │
│    └─ Pass to downstream LangGraph nodes                    │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

---

## Shared Output Contract

All four versions return the **same JSON structure**:

```json
{
  "analysis_summary": "string - 2-4 sentences about known systems",
  "clarity_score": "integer 1-10",
  "information_score": {
    "entities": "boolean - are all actors/systems identified?",
    "actions": "boolean - are all interactions understood?",
    "structure": "boolean - is the architecture clear?",
    "word_count": "integer - length of latest user input"
  },
  "question": "string - one clarification question OR null when ready",
  "ready": "boolean - true when clarity >= 8 and Structurizr is production-ready",
  "structurizr_workspace": "string - complete Structurizr DSL workspace (model + views)",
  "clean_d2": "string - normalized Clean Structurizr (deterministic form, newlines as \\n)",
  "assumptions": ["array of inferred facts"],
  "next_step": "awaiting_user_clarification OR ready_for_generation"
}
```

### Key Points:
- ✅ **Single JSON response** – No Markdown fences, no prose outside JSON
- ✅ **Structurizr as canonical payload** – Replaces legacy `json_representation`
- ✅ **Dual representation** – Full workspace + normalized clean form
- ✅ **Synchronized formats** – Every element in workspace appears in clean form
- ✅ **One question per turn** – Ask exactly one clarification when `ready=false`
- ✅ **Newlines as `\n`** – Structurizr uses escaped newlines for transmission

---

## Version Comparison

| Aspect | GPT-5 | Grok | Claude Sonnet 4.5 | Gemini 2.5 Pro |
|--------|-------|------|------------------|----------------|
| **Focus** | Long-context reasoning | Deterministic outputs | Structured thinking | Efficiency |
| **Max Response Size** | N/A | <400 words | N/A | <2,000 chars |
| **Structurizr Style** | Clean, minimal | Short stable IDs | Multi-line with views | Deterministic format |
| **Clean D2 Approach** | Cross-check fidelity | Mirror immediately | Full group nesting | Condensed syntax |
| **Tone** | Technical, precise | Brief, direct | Thoughtful, explicit | Pragmatic, lean |

---

## 1. GPT-5 Edition

**File:** `diagram-wizard-gpt5.md`

### Characteristics
- Optimized for **long-context reasoning**
- Assumes GPT-5's superior ability to maintain complex state
- Emphasizes **cross-checking** Structurizr before emitting Clean D2

### Key Instructions
```
✓ Leverage long-context reasoning to cross-check workspace
✓ Keep Structurizr and Clean D2 synchronized
✓ Maintain stable variable names between turns
✓ Use precise technology labels (React, PostgreSQL, etc.)
✓ Continue returning full JSON payload even after ready=true
```

### Response Envelope
```json
{
  "analysis_summary": "...",
  "clarity_score": 1-10,
  "information_score": {...},
  "question": "...",
  "ready": false,
  "structurizr_workspace": "workspace \"Name\" {...}",
  "clean_d2": "...",
  "assumptions": [...],
  "next_step": "awaiting_user_clarification"
}
```

### Behavior Rules
- Ask **at most one question per turn**
- No example code or prose outside JSON
- Keep Structurizr and Clean D2 **100% synchronized**
- When `ready=true`, continue returning full payload with `question=null`

### Clean D2 Formatting (GPT-5)
```
Declare all nodes with `id: label` syntax
Group related nodes using indentation/scopes
Define connections: `node -> node: description`
Avoid Mermaid or PlantUML syntax
No Markdown code fences
```

---

## 2. Grok Edition

**File:** `diagram-wizard-grok.md`

### Characteristics
- Optimized for **deterministic, concise outputs**
- Prefers **short, stable identifiers**
- Single-line JSON (no Markdown fences)
- Assumes Grok's tendency for brevity

### Key Instructions
```
✓ Keep responses under 400 words total
✓ Do not invent systems; rely on supplied facts
✓ Immediately mirror Structurizr elements in clean_d2
✓ Use short identifiers (web_app, payments_api)
✓ If user asks for explanation, wrap answer in JSON with ready=false
```

### Response Envelope
**Single-line JSON object** – No Markdown fences or commentary

```json
{"analysis_summary": "...", "clarity_score": 8, "information_score": {...}, "question": null, "ready": true, "structurizr_workspace": "...", "clean_d2": "...", "assumptions": [], "next_step": "ready_for_generation"}
```

### Execution Notes
- **Single-line format** – Entire response as one JSON line
- **No invented facts** – Only use supplied information
- **Immediate mirroring** – When adding Structurizr elements, immediately update Clean D2
- **Once ready=true**, keep returning workspace and Clean D2 for downstream rehydration

### Clean D2 Formatting (Grok)
```
Use human-readable labels: web_app: "Web App"
Nest related items using indentation or group nodes
Describe edges as: source -> target: detail (protocol)
Avoid Markdown fences or triple quotes
Return plain string with escaped line breaks
```

---

## 3. Claude Sonnet 4.5 Edition

**File:** `diagram-wizard-sonet45.md`

### Characteristics
- Optimized for **structured thinking and transparency**
- Emphasizes **explicit behavioral expectations**
- Multi-line Structurizr workspace with views
- Assumes Claude's strength in maintaining complex contracts

### Key Instructions
```
✓ Single Question Rule: Ask one question that maximizes clarity
✓ Keep Structurizr variables short (web_app, payments_api)
✓ Include model AND at least one view in workspace
✓ Every Structurizr element must have Clean D2 counterpart
✓ Capture guesswork in assumptions array
✓ Maintain continuity unless user corrects explicitly
```

### Response Envelope
```json
{
  "analysis_summary": "2-4 sentences of narrative recap",
  "clarity_score": 1-10,
  "information_score": {
    "entities": true/false,
    "actions": true/false,
    "structure": true/false,
    "word_count": 0
  },
  "question": "One question or null",
  "ready": false,
  "structurizr_workspace": "Multi-line DSL string",
  "clean_d2": "Multi-line Clean D2 string",
  "assumptions": ["inferred facts"],
  "next_step": "awaiting_user_clarification"
}
```

### Behavioural Expectations
- **Single Question Rule** – When ready=false, ask exactly one high-impact question
- **Structurizr Discipline** – Use short variables, include model + views
- **Clean D2 Fidelity** – Every actor/container must have node counterpart
- **Transparency** – Capture guesswork in assumptions
- **Continuity** – Retain prior knowledge unless corrected
- **Ready State** – Only set ready=true when Clean D2 is production-ready

### Clean D2 Formatting (Claude)
```
Nodes: id: "Label" { note: "optional" }
Relationships: source -> target: "Description" (Protocol)
Grouping: Use indentation or group nodes for subsystems
No Markdown fences – literal strings with \n between lines
```

---

## 4. Gemini 2.5 Pro Edition

**File:** `diagram-wizardgemini25pro.md`

### Characteristics
- Optimized for **efficiency and pragmatism**
- Maximum response size: **<2,000 characters**
- Deterministic format with condensed syntax
- Balances completeness with conciseness

### Key Instructions
```
✓ Keep overall output under 2,000 characters
✓ When ready=true, continue sending workspace and Clean D2
✓ Match every Structurizr element to Clean D2 node and vice versa
✓ Use question=null when ready, no follow-ups unless user changes
✓ Do not wrap Structurizr or Clean D2 in Markdown fences
```

### Response Envelope
**Compact JSON** with size constraints

```json
{
  "analysis_summary": "2-3 sentences + deltas",
  "clarity_score": 1-10,
  "information_score": {"entities": bool, "actions": bool, "structure": bool, "word_count": int},
  "question": "question or null",
  "ready": true/false,
  "structurizr_workspace": "string",
  "clean_d2": "string",
  "assumptions": [...],
  "next_step": "awaiting_user_clarification|ready_for_generation"
}
```

### Additional Rules
- **Size efficiency** – Keep under 2,000 chars when possible
- **Continuous state** – When ready=true, continue sending workspace and Clean D2
- **Bidirectional mapping** – Every Structurizr element ↔ Clean D2 node
- **No follow-ups** – Once ready=true, question=null and stay silent until user changes
- **No Markdown** – Plain strings without fences

### Clean D2 Standards (Gemini)
```
Syntax example: system: "Ordering Platform"\nweb -> api: "REST" (HTTPS)
Use indentation or group constructs for clarity
Provide descriptive edge labels with protocol/data format
Keep output deterministic
```

---

## Structurizr Workspace Standard

All four versions output **two synchronized representations**:

### 1. Structurizr Workspace
**Full Structurizr DSL format** with model and views:
```
workspace "System Name" "Description" {
  model {
    user = person "User"
    system = softwareSystem "System" {
      webapp = container "Web App"
      api = container "API"
      db = container "Database"
    }
    user -> webapp "Uses"
    webapp -> api "Calls"
    api -> db "Queries"
  }
  views {
    systemContext system {
      autoLayout
    }
    container system {
      autoLayout
    }
  }
}
```

### 2. Clean Structurizr (mislabeled as "Clean D2")
**Normalized, deterministic Structurizr format** (NOT D2 DSL):
- Structurizr code optimized for consistency
- Replaces legacy `json_representation`
- Designed to be idempotent across LLM turns
- Every element in the workspace appears in clean form
- Uses escaped newlines (`\n`) for transmission

### Synchronization Rule
> "Keep Structurizr and Clean D2 synchronized; every element mentioned in the Structurizr workspace must have an equivalent node/edge in Clean D2."

This means:
- ✅ Both contain the same information
- ✅ Same structure, different formatting
- ✅ Structurizr = complete with views
- ✅ Clean Structurizr = normalized form

### Why This Dual Representation?
1. **Structurizr workspace** – Full architectural views with metadata
2. **Clean Structurizr** – Deterministic, minimal form for code generation
3. **Reduces ambiguity** – Downstream nodes can use either
4. **Traceability** – Both forms documented for audit

---

## How Versions Are Selected

Based on the `PROVIDER` and `DEFAULT_MODEL` environment variables:

| Provider | Model | Version Used |
|----------|-------|--------------|
| openrouter | gpt-5-* | GPT-5 |
| xai | grok-* | Grok |
| anthropic | claude-sonnet-4.5-* | Claude Sonnet 4.5 |
| google | gemini-2.5-pro-* | Gemini 2.5 Pro |
| Other | fallback | Claude Sonnet 4.5 (default) |

---

## Integration with LangGraph Nodes

The **ANALYSE_CONFIRM phase** feeds into:

```
┌──────────────────────────────────────┐
│ ANALYSE_CONFIRM                      │
│ (One of 4 prompt versions)           │
└─────────────┬────────────────────────┘
              │
     ┌────────▼──────────────────┐
     │  Output: JSON with        │
     │  • structurizr_workspace  │
     │  • clean_d2 (Clean        │
     │    Structurizr)           │
     │  • clarity_score          │
     │  • ready flag             │
     └────────┬──────────────────┘
              │
     ┌────────▼──────────────────┐
     │ clarify_prompt (Loop)     │
     │ (LangGraph)               │
     │                           │
     │ Refines Structurizr:      │
     │ • Updates workspace       │
     │ • Tracks clarity_score    │
     │ • Asks clarifications     │
     │ • Returns ready=true      │
     │   when clarity >= 8       │
     └────────┬──────────────────┘
              │
     ┌────────▼──────────────────────────┐
     │ determine_diagram_type            │
     │ (Auto-selects Mermaid/D2/PlantUML)│
     └───────────────────────────────────┘
```

---

## Migration Path: Legacy → ANALYSE_CONFIRM

### Legacy Flow (Previous)
```
analyze_request
  ↓
clarify_prompt (loop)
  ↓ (when llm_ready=true)
determine_diagram_type
```

### New Flow (ANALYSE_CONFIRM)
```
ANALYSE_CONFIRM node (choose version based on model)
  ├─ Returns JSON with Structurizr workspace + Clean Structurizr
  ├─ Sets ready=true when clarity >= 8
  │
  └─ Feeds into clarify_prompt
     (which continues refining Structurizr/Clean Structurizr)
```

### Key Differences
- **Single unified phase** – All analysis + confirmation in ANALYSE_CONFIRM
- **Structurizr from start** – No legacy JSON representation
- **Model-optimized** – Different prompts for different LLM providers
- **Dual representation** – Full workspace + normalized clean form

---

## Behavioral Patterns by Version

### GPT-5: Trust and Cross-Check
```
Approach: "I have enough context to reason deeply"
Pattern: Maintain complex workspace → cross-check → emit Clean D2
Strength: Long-context awareness, validation
Risk: May overthink simple diagrams
```

### Grok: Fast and Lean
```
Approach: "Be brief, be direct"
Pattern: Take facts → immediately build workspace → output Clean D2
Strength: Quick decisions, deterministic
Risk: May miss subtle architecture details
```

### Claude Sonnet 4.5: Explicit and Transparent
```
Approach: "Show my work, state assumptions"
Pattern: Analyze → document assumptions → structure workspace → emit Clean D2
Strength: Explainability, consistency
Risk: More verbose responses
```

### Gemini 2.5 Pro: Efficient and Pragmatic
```
Approach: "Do more with less"
Pattern: Extract essentials → condense workspace → minimal Clean D2
Strength: Size efficiency, quick generation
Risk: May over-condense important details
```

---

## Prompt File Structure

All four files follow this pattern:

```
┌─────────────────────────────┐
│ YAML Metadata               │
│ (title, author, version)    │
├─────────────────────────────┤
│ Mission/Purpose             │
├─────────────────────────────┤
│ Workflow Overview           │
├─────────────────────────────┤
│ Output Contract/Schema      │
├─────────────────────────────┤
│ Behavior Rules              │
├─────────────────────────────┤
│ Formatting Guidelines       │
├─────────────────────────────┤
│ Version-Specific Notes      │
└─────────────────────────────┘
```

---

## Summary: Key Takeaways

1. **Four model-specific versions** – Each optimized for a different LLM provider
2. **Unified output schema** – All return the same JSON structure with Structurizr + Clean Structurizr
3. **Structurizr as canonical** – Replaces legacy JSON representation
4. **Dual representation** – Full workspace (with views) + normalized clean form stay synchronized
5. **Single question rule** – Ask exactly one clarification per turn
6. **Ready state trigger** – clarity >= 8 AND sufficient detail
7. **Model awareness** – Prompts account for each model's strengths/constraints
8. **Future-oriented** – ANALYSE_CONFIRM represents the evolved workflow with Structurizr DSL

---

**Generated:** 2025-11-16
**Files Analyzed:**
- `prompts/coding/agent/diagram-wizard-gpt5.md`
- `prompts/coding/agent/diagram-wizard-grok.md`
- `prompts/coding/agent/diagram-wizard-sonet45.md`
- `prompts/coding/agent/diagram-wizardgemini25pro.md`
