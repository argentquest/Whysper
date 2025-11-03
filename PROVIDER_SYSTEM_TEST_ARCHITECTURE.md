# Provider System Test Architecture

**Date**: November 3, 2025
**Purpose**: Clarify how test suites should use the provider system
**Status**: Ready for implementation

---

## Quick Summary

**Your Statement**: "When we run the 7 suite of tests it should only rely on these providers. The old MVP is in use now for the current front end only"

**This means**:
1. ✅ Test suites should use `/api/v1/diagrams/v2/*` (provider system)
2. ✅ Frontend should use `/api/v1/diagrams/*` (MVP system)
3. ✅ Both can coexist during transition
4. ✅ Seven providers in `backend/diagrams/` handle all diagram types

---

## Architecture Diagram

```
FRONTEND (Current)                          TEST SUITES (Future)
        │                                           │
        ├─→ MVP System                              ├─→ Provider System
        │   /api/v1/diagrams/*                      │   /api/v1/diagrams/v2/*
        │   (rendering_api.py)                      │   (diagram_provider.py)
        │   └─ renderer_v2.py                       │   └─ ProviderRegistry
        │                                            │       ├─ mermaidv1
        │                                            │       ├─ d2v1
        │                                            │       ├─ krokid2
        │                                            │       ├─ krokimermaid
        │                                            │       ├─ krokic4
        │                                            │       ├─ krokiplantuml
        │                                            │       └─ krokistructurizr
        │                                            │
        │                                    RESULTS: Test reports
        │                                    (97%+ success expected)
        │
   RESULTS: UI rendering
   (92-100% quality)
```

---

## Seven Providers for Seven Tests

### Test Suite → Provider Mapping

```
backend/tests/

├─ llmd2test
│  └─ Generates D2 code with LLM
│     └─ Renders with: d2v1 provider
│        └─ Expected: 100% success

├─ llmmermaidtest
│  └─ Generates Mermaid code with LLM
│     └─ Renders with: mermaidv1 provider
│        └─ Expected: 92%+ success

├─ llmkrokid2test
│  └─ Generates D2 code with LLM
│     └─ Renders with: krokid2 provider
│        └─ Expected: 100% success

├─ llmkrokimermaidtest
│  └─ Generates Mermaid code with LLM
│     └─ Renders with: krokimermaid provider
│        └─ Expected: 96%+ success

├─ llmkrokic4test
│  └─ Generates C4 code with LLM
│     └─ Renders with: krokic4 provider
│        └─ Expected: TBD (needs investigation)

├─ llmkrokiplantumtest
│  └─ Generates PlantUML code with LLM
│     └─ Renders with: krokiplantuml provider
│        └─ Expected: TBD (new provider)

└─ llmkrokistructurizrtest
   └─ Generates Structurizr code with LLM
      └─ Renders with: krokistructurizr provider
         └─ Expected: TBD (new provider)
```

---

## Provider System Endpoints

### Test Suites Will Use

**Endpoint 1: Render**
```
POST /api/v1/diagrams/v2/render

Request:
{
  "code": "diagram code here",
  "diagram_type": "d2" | "mermaid" | "c4" | "plantuml" | "structurizr",
  "provider_id": "d2v1" | "mermaidv1" | "krokid2" | "krokimermaid" |
                 "krokic4" | "krokiplantuml" | "krokistructurizr",
  "output_format": "svg" | "png",
  "auto_fix": true,
  "use_llm": false
}

Response:
{
  "success": true,
  "content": "SVG or PNG data",
  "output_format": "svg",
  "validation": {
    "is_valid": true,
    "error": null
  },
  "metadata": {...},
  "provider_id": "d2v1"
}
```

**Endpoint 2: Validate**
```
POST /api/v1/diagrams/v2/validate

Request:
{
  "code": "diagram code here",
  "diagram_type": "d2",
  "provider_id": "d2v1",
  "auto_fix": true,
  "use_llm": false
}

Response:
{
  "is_valid": true,
  "error": null,
  "code_length": 150,
  "auto_fixed": false,
  "llm_corrected": false,
  "fixed_code": null
}
```

**Endpoint 3: List Providers**
```
GET /api/v1/diagrams/v2/providers

Response:
{
  "providers": [
    {
      "provider_id": "mermaidv1",
      "provider_name": "Mermaid CLI Renderer v1",
      "diagram_type": "mermaid",
      "capabilities": ["VALIDATE", "RENDER_SVG", "RENDER_PNG", "AUTO_FIX", "LLM_CORRECTION"],
      "available": true,
      "version": "1.0"
    },
    {
      "provider_id": "d2v1",
      "provider_name": "D2 CLI Renderer",
      "diagram_type": "d2",
      "capabilities": ["VALIDATE", "RENDER_SVG", "RENDER_PNG", "AUTO_FIX", "LLM_CORRECTION"],
      "available": true,
      "version": "1.0"
    },
    // ... more providers
  ]
}
```

---

## Current Test Flow (MVP-based)

```python
# Current approach - uses MVP endpoint only
response = requests.post(
    "http://localhost:8003/api/v1/diagrams/generate",
    json={
        "prompt": prompt,
        "diagram_type": "d2",
        "output_format": "svg"
    }
)

# MVP combines:
# 1. LLM generation (creates diagram code from prompt)
# 2. Validation (checks syntax)
# 3. Rendering (creates SVG)

# All in one endpoint
```

---

## New Test Flow (Provider-based)

```python
# New approach - separates concerns

# STAGE 1: LLM Generation
# (Can use MVP endpoint or move to provider system)
response = requests.post(
    "http://localhost:8003/api/v1/diagrams/generate",
    json={
        "prompt": prompt,
        "diagram_type": "d2",
        "output_format": "code"  # Get code only
    }
)
diagram_code = response.json()['diagram_code']

# STAGE 2: Rendering with Provider
# (Uses provider system - this is the TEST focus)
response = requests.post(
    "http://localhost:8003/api/v1/diagrams/v2/render",
    json={
        "code": diagram_code,
        "diagram_type": "d2",
        "provider_id": "d2v1",  # SPECIFIC PROVIDER TO TEST
        "output_format": "svg"
    }
)

# Provider handles:
# 1. Validation (checks syntax)
# 2. Auto-fix (pattern-based fixes)
# 3. LLM correction (if needed)
# 4. Rendering (creates SVG)
```

---

## Provider Capabilities

### Native Providers (in backend/diagrams/)

**mermaidv1**
```json
{
  "provider_id": "mermaidv1",
  "diagram_type": "mermaid",
  "capabilities": [
    "VALIDATE",      // Check syntax
    "RENDER_SVG",    // Output SVG
    "RENDER_PNG",    // Output PNG
    "AUTO_FIX",      // Pattern-based fixes
    "LLM_CORRECTION" // AI-powered fixes
  ],
  "uses": "Mermaid CLI (mmdc)"
}
```

**d2v1**
```json
{
  "provider_id": "d2v1",
  "diagram_type": "d2",
  "capabilities": [
    "VALIDATE",
    "RENDER_SVG",
    "RENDER_PNG",
    "AUTO_FIX",
    "LLM_CORRECTION"
  ],
  "uses": "D2 CLI"
}
```

### Kroki Providers (API-based)

**krokid2**
```json
{
  "provider_id": "krokid2",
  "diagram_type": "d2",
  "capabilities": [
    "RENDER_SVG",
    "RENDER_PNG"
  ],
  "uses": "Kroki API (D2 endpoint)"
}
```

**krokimermaid, krokic4, krokiplantuml, krokistructurizr**
Similar structure, different diagram types and Kroki endpoints.

---

## Test Suite Design Pattern

Each test suite should follow this pattern:

```python
# backend/tests/llmXXXtest/validate_all_25_XXX.py

import sys
import json
import requests
from pathlib import Path
from typing import Tuple, Dict, Any

class DiagramTest:
    """Test a specific diagram provider"""

    def __init__(self, provider_id: str, diagram_type: str):
        self.provider_id = provider_id
        self.diagram_type = diagram_type
        self.backend_url = "http://localhost:8003"
        self.test_results = []

    def render_with_provider(self, code: str, test_id: int) -> Tuple[bool, str, Dict[str, Any]]:
        """Render diagram using the provider"""
        try:
            response = requests.post(
                f"{self.backend_url}/api/v1/diagrams/v2/render",
                json={
                    "code": code,
                    "diagram_type": self.diagram_type,
                    "provider_id": self.provider_id,
                    "output_format": "svg",
                    "auto_fix": True,  # Allow pattern-based fixes
                    "use_llm": False   # Don't use LLM for this test (cost)
                },
                timeout=120
            )

            if response.status_code != 200:
                return (False, f"HTTP {response.status_code}", {})

            data = response.json()

            if data.get('success'):
                return (True, data.get('content'), {
                    'validation': data.get('validation'),
                    'metadata': data.get('metadata')
                })
            else:
                return (False, data.get('error', 'Unknown error'), {})

        except Exception as e:
            return (False, str(e), {})

    def run_all_tests(self):
        """Run all 25 tests for this provider"""
        test_file = Path(__file__).parent / "test.json"

        with open(test_file) as f:
            tests = json.load(f)

        for i, test_case in enumerate(tests[:25], 1):
            code = test_case.get('code')
            description = test_case.get('description')

            success, content, metadata = self.render_with_provider(code, i)

            result = {
                'test_id': i,
                'description': description,
                'success': success,
                'error': None if success else content,
                'content_length': len(content) if success else 0,
                'metadata': metadata
            }

            self.test_results.append(result)

            if success:
                # Save SVG
                svg_file = Path(f"test_results_25/svg/test_{i:03d}.svg")
                svg_file.parent.mkdir(parents=True, exist_ok=True)
                with open(svg_file, 'w') as f:
                    f.write(content)
            else:
                # Save error
                error_file = Path(f"test_results_25/errors/test_{i:03d}_error.txt")
                error_file.parent.mkdir(parents=True, exist_ok=True)
                with open(error_file, 'w') as f:
                    f.write(f"Test {i}: {description}\nError: {content}")

        # Print summary
        passed = sum(1 for r in self.test_results if r['success'])
        total = len(self.test_results)
        print(f"\n{self.provider_id}: {passed}/{total} ({100*passed//total}%)")

if __name__ == "__main__":
    # Example: Test D2 provider
    tester = DiagramTest(provider_id="d2v1", diagram_type="d2")
    tester.run_all_tests()
```

---

## Implementation Checklist

### Phase 1: Preparation
- [ ] Review this document
- [ ] Understand provider system architecture
- [ ] List all 7 providers in `backend/diagrams/`
- [ ] Verify provider endpoints work

### Phase 2: Common Utilities
- [ ] Create `backend/tests/common_test_utils.py`
- [ ] Implement `ProviderTestHelper` class
- [ ] Test with one provider

### Phase 3: Refactor Tests (One at a time)
- [ ] Update `llmd2test/validate_all_25_d2.py` → use d2v1
- [ ] Update `llmmermaidtest/validate_all_25_mermaid.py` → use mermaidv1
- [ ] Update `llmkrokid2test/validate_all_25_krokid2.py` → use krokid2
- [ ] Update `llmkrokimermaidtest/validate_all_25_krokimermaid.py` → use krokimermaid
- [ ] Update `llmkrokic4test/validate_all_25_krokic4.py` → use krokic4
- [ ] Update `llmkrokiplantumtest/validate_all_25_krokiplantuml.py` → use krokiplantuml
- [ ] Update `llmkrokistructurizrtest/validate_all_25_krokistructurizr.py` → use krokistructurizr

### Phase 4: Validation
- [ ] Run all 7 test suites
- [ ] Collect results
- [ ] Compare with previous MVP results
- [ ] Document findings
- [ ] Create summary report

### Phase 5: Optimization (if needed)
- [ ] Identify failing providers
- [ ] Debug and fix issues
- [ ] Re-run tests
- [ ] Document solutions

---

## Success Criteria

Each test suite should:

1. ✅ Use provider system endpoint `/api/v1/diagrams/v2/render`
2. ✅ Specify correct `provider_id` for that diagram type
3. ✅ Achieve same or better success rate than MVP
4. ✅ Save results to `test_results_25/svg/` and `test_results_25/errors/`
5. ✅ Generate summary report

**Overall Goal**: 7/7 test suites running, only using provider system

---

## Why This Matters

**Current State**:
- Tests use MVP → MVP code must stay stable
- MVP and providers may diverge
- Hard to validate provider quality

**After Refactoring**:
- Tests use providers → Provider code must stay stable
- Providers are validated by tests
- Clear metrics for each provider
- Easy to add new providers

---

## Next Steps

1. Review `TEST_REFACTOR_TO_PROVIDER_SYSTEM.md` for detailed examples
2. Create `backend/tests/common_test_utils.py` with ProviderTestHelper
3. Refactor one test suite as example (recommend `llmd2test` first)
4. Run and validate results
5. Refactor remaining 6 test suites
6. Generate final report

---

**Status**: ✅ Architecture defined, ready for implementation
**Timeline**: 3-5 days for full refactoring
**Risk**: Low (provider system already production-ready)
**Benefit**: High (validates provider quality, decouples from MVP)

