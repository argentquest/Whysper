# Quick Reference: Diagram System Architecture

**For**: Understanding how tests should use the provider system

---

## The Two Systems

### MVP System (Frontend uses this)
```
📱 FRONTEND
   ↓
🔧 MVP: /api/v1/diagrams/*
   ├─ POST /diagrams/generate
   │  └─ LLM generates diagram code from prompt
   ├─ POST /diagrams/render
   │  └─ Renders diagram to SVG/PNG
   └─ Internal: renderer_v2.py (Mermaid CLI only)
```

### Provider System (Tests should use this)
```
🧪 TEST SUITES
   ↓
🔌 Provider System: /api/v1/diagrams/v2/*
   ├─ POST /diagrams/v2/render
   │  ├─ provider_id: "d2v1" | "mermaidv1" | "kroki*"
   │  └─ Handles: validate + auto-fix + render
   ├─ POST /diagrams/v2/validate
   │  └─ Validation only
   └─ GET /diagrams/v2/providers
      └─ List available providers
```

---

## Seven Providers for Seven Tests

```
backend/diagrams/

┌─ mermaidv1 ────────────────┐
│ Diagram Type: mermaid      │
│ Rendering: Mermaid CLI     │
│ Test Suite: llmmermaidtest │
│ Expected: 92%+             │
└────────────────────────────┘

┌─ d2v1 ─────────────────────┐
│ Diagram Type: d2           │
│ Rendering: D2 CLI          │
│ Test Suite: llmd2test      │
│ Expected: 100%             │
└────────────────────────────┘

┌─ krokid2 ──────────────────┐
│ Diagram Type: d2           │
│ Rendering: Kroki API       │
│ Test Suite: llmkrokid2test │
│ Expected: 100%             │
└────────────────────────────┘

┌─ krokimermaid ─────────────┐
│ Diagram Type: mermaid      │
│ Rendering: Kroki API       │
│ Test Suite: llmkrokimermaidtest │
│ Expected: 96%+             │
└────────────────────────────┘

┌─ krokic4 ──────────────────┐
│ Diagram Type: c4           │
│ Rendering: Kroki API       │
│ Test Suite: llmkrokic4test │
│ Expected: TBD              │
└────────────────────────────┘

┌─ krokiplantuml ────────────┐
│ Diagram Type: plantuml     │
│ Rendering: Kroki API       │
│ Test Suite: llmkrokiplantumtest │
│ Expected: TBD              │
└────────────────────────────┘

┌─ krokistructurizr ─────────┐
│ Diagram Type: structurizr  │
│ Rendering: Kroki API       │
│ Test Suite: llmkrokistructurizrtest │
│ Expected: TBD              │
└────────────────────────────┘
```

---

## Test Data Flow

### Step 1: Get Diagram Code
```
LLM generates code from description
(using MVP endpoint or pre-generated)

Output: diagram_code = "flowchart TD..."
```

### Step 2: Render with Provider
```
POST /api/v1/diagrams/v2/render
{
  "code": diagram_code,
  "diagram_type": "d2",
  "provider_id": "d2v1",
  "output_format": "svg"
}

Response: SVG content
```

### Step 3: Save Results
```
✅ Success: save to test_results_25/svg/test_001.svg
❌ Failure: save to test_results_25/errors/test_001_error.txt
```

---

## Code Template

```python
# backend/tests/llmd2test/validate_all_25_d2.py

import requests

def render_diagram(code, test_id):
    """Render with provider system"""

    response = requests.post(
        "http://localhost:8003/api/v1/diagrams/v2/render",
        json={
            "code": code,
            "diagram_type": "d2",
            "provider_id": "d2v1",        # ← SPECIFIC PROVIDER
            "output_format": "svg"
        },
        timeout=120
    )

    if response.status_code != 200:
        return None, response.text

    data = response.json()

    if data.get('success'):
        return data.get('content'), None
    else:
        return None, data.get('error')
```

---

## Each Provider Maps to One Test Suite

| Provider | Diagram Type | Test File | Current Status |
|----------|-----------|-----------|-----------------|
| d2v1 | D2 | `llmd2test/validate_all_25_d2.py` | 100% ✅ |
| mermaidv1 | Mermaid | `llmmermaidtest/validate_all_25_mermaid.py` | 92% ✅ |
| krokid2 | D2 | `llmkrokid2test/validate_all_25_krokid2.py` | 100% ✅ |
| krokimermaid | Mermaid | `llmkrokimermaidtest/validate_all_25_krokimermaid.py` | 96% ✅ |
| krokic4 | C4 | `llmkrokic4test/validate_all_25_krokic4.py` | 0% ❌ |
| krokiplantuml | PlantUML | `llmkrokiplantumtest/validate_all_25_krokiplantuml.py` | ? |
| krokistructurizr | Structurizr | `llmkrokistructurizrtest/validate_all_25_krokistructurizr.py` | ? |

---

## Endpoint Comparison

### MVP Endpoint (Frontend)
```
POST /api/v1/diagrams/generate

{
  "prompt": "Create a diagram...",
  "diagram_type": "d2",
  "output_format": "svg"
}

Returns: SVG (combines generation + rendering)
```

### Provider Endpoint (Tests)
```
POST /api/v1/diagrams/v2/render

{
  "code": "d2 diagram code...",
  "diagram_type": "d2",
  "provider_id": "d2v1",
  "output_format": "svg"
}

Returns: SVG (rendering only, code must be pre-generated)
```

---

## Why Two Systems?

**MVP** (for Frontend):
- Simple: one endpoint for everything
- Fast: direct execution
- Proven: working in production
- Focus: speed of development

**Provider System** (for Tests):
- Modular: each provider independent
- Extensible: easy to add new providers
- Testable: validate each provider separately
- Focus: long-term maintainability

---

## Your Task (Summary)

✅ **What's done**:
- MVP system is working (renderer_v2.py uses Mermaid CLI only)
- Provider system is ready (7 providers implemented)
- Architecture is clarified

⏳ **What's needed**:
- Refactor 7 test suites to use provider system
- Change endpoint from `/api/v1/diagrams/*` to `/api/v1/diagrams/v2/*`
- Specify provider_id for each test
- Validate results

📊 **Expected outcome**:
- All tests use provider system only
- Each provider independently tested
- Clear success/failure metrics
- Better architecture

---

## Files to Read

1. **ARCHITECTURE_SUMMARY.md** ← START HERE
   - Overview of everything
   - Your requirements clarified
   - Next steps

2. **PROVIDER_SYSTEM_TEST_ARCHITECTURE.md**
   - Detailed architecture diagrams
   - Endpoint documentation
   - Test design patterns

3. **TEST_REFACTOR_TO_PROVIDER_SYSTEM.md**
   - Code examples
   - Step-by-step implementation
   - Migration timeline

4. **MVP_VS_PROVIDER_SYSTEM_ANALYSIS.md** (optional)
   - Detailed comparison
   - Risk assessment
   - Migration path

---

## Key Points

1. MVP stays for frontend (no changes)
2. Tests should use provider system (needs refactoring)
3. Both endpoints work simultaneously (no conflict)
4. Each test suite maps to exactly one provider
5. Provider system validates independent providers
6. Architecture is cleaner after refactoring

---

**Status**: Ready to refactor tests
**Effort**: ~10 hours
**Confidence**: High (providers already production-ready)
**Start**: Review ARCHITECTURE_SUMMARY.md first

