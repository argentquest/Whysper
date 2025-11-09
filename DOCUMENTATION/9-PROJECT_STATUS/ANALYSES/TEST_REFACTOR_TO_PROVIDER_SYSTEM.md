# Test Refactoring: MVP to Provider System

**Date**: November 3, 2025
**Goal**: Update test suites to use the provider system instead of MVP diagram generator
**Status**: Ready to implement

---

## Current Test Setup (MVP-based)

### Test Files
```
backend/tests/
├── llmd2test/validate_all_25_d2.py
├── llmmermaidtest/validate_all_25_mermaid.py
├── llmkrokid2test/validate_all_25_krokid2.py
├── llmkrokimermaidtest/validate_all_25_krokimermaid.py
├── llmkrokic4test/validate_all_25_krokic4.py
├── llmkrokiplantumtest/validate_all_25_krokiplantuml.py
└── llmkrokistructurizrtest/validate_all_25_krokistructurizr.py
```

### Current Flow (MVP)
```
Test Script
    ↓
POST /api/v1/diagrams/generate (MVP endpoint)
    ↓
rendering_api.py (MVP)
    ├─ LLM generates diagram code
    ├─ Validates with renderer_v2.py
    └─ Renders SVG
    ↓
Test Script saves results
```

### Current Test Structure
```python
# Current approach (MVP-based)
response = requests.post(
    "http://localhost:8003/api/v1/diagrams/generate",
    json={
        "prompt": prompt,
        "diagram_type": diagram_type,
        "output_format": "svg"
    }
)
```

---

## New Test Setup (Provider System)

### Available Providers

**In backend/diagrams/**:

| Provider ID | Diagram Type | Capabilities | Status |
|-----------|-------------|-------------|--------|
| **mermaidv1** | mermaid | Validate, Render SVG/PNG, Auto-fix, LLM correct | ✅ Production |
| **d2v1** | d2 | Validate, Render SVG/PNG, Auto-fix, LLM correct | ✅ Production |
| **krokid2** | d2 | Render via Kroki API | ✅ Production |
| **krokimermaid** | mermaid | Render via Kroki API | ✅ Production |
| **krokic4** | c4 | Render via Kroki API | ✅ Production |
| **krokiplantuml** | plantuml | Render via Kroki API | ✅ Production |
| **krokistructurizr** | structurizr | Render via Kroki API | ✅ Production |

### New Flow (Provider System)
```
Test Script
    ↓
POST /api/v1/diagrams/v2/render (Provider endpoint)
    ↓
diagram_provider.py (NEW)
    ↓
ProviderRegistry
    ↓
Selected Provider (e.g., mermaidv1, krokid2, etc.)
    ├─ Validate code
    ├─ Auto-fix if needed
    ├─ LLM correct if needed
    └─ Render
    ↓
Test Script saves results
```

### Test Mapping

**7 Test Suites → 7 Providers**:

1. **llmd2test** → d2v1 (LLM-generated D2 rendered by d2v1)
2. **llmmermaidtest** → mermaidv1 (LLM-generated Mermaid rendered by mermaidv1)
3. **llmkrokid2test** → krokid2 (LLM-generated D2 rendered by Kroki)
4. **llmkrokimermaidtest** → krokimermaid (LLM-generated Mermaid rendered by Kroki)
5. **llmkrokic4test** → krokic4 (LLM-generated C4 rendered by Kroki)
6. **llmkrokiplantumtest** → krokiplantuml (LLM-generated PlantUML rendered by Kroki)
7. **llmkrokistructurizrtest** → krokistructurizr (LLM-generated Structurizr rendered by Kroki)

---

## Refactoring Approach

### Option 1: Two-Stage Refactor (Recommended)

**Stage 1 - Keep MVP, Add Provider Tests**
- Keep existing MVP test scripts as-is
- Create new test scripts using provider system
- Run both in parallel to compare results
- Verify provider system produces same or better results

**Stage 2 - Switch to Provider System**
- Update test scripts to use provider endpoints
- Confirm all tests pass
- Remove MVP test scripts (or keep as legacy)

**Benefits**:
- ✅ Zero disruption to current tests
- ✅ Can validate provider system quality
- ✅ Can compare MVP vs Provider results
- ✅ Easy rollback if issues found

### Option 2: Direct Refactor (Faster)

**One-Step Migration**
- Update all test scripts to use provider system
- Deploy and run all tests
- Verify success

**Benefits**:
- ✅ Faster implementation
- ✅ Single code path (no duplication)

**Risks**:
- ⚠️ If provider system has issues, tests fail immediately
- ⚠️ No comparison data between systems

---

## Implementation

### Current Test Code Pattern (MVP)

```python
# backend/tests/llmd2test/validate_all_25_d2.py (CURRENT)

def generate_diagram_with_llm(prompt: str, test_id: int, diagram_type: str = "d2"):
    """MVP endpoint - handles LLM generation + validation + rendering"""
    response = requests.post(
        "http://localhost:8003/api/v1/diagrams/generate",
        json={
            "prompt": prompt,
            "diagram_type": diagram_type,
            "output_format": "svg"
        },
        timeout=120
    )
    # Process response...
```

### New Test Code Pattern (Provider System)

**Two-stage approach:**

```python
# backend/tests/llmd2test/validate_all_25_d2.py (REFACTORED)

import requests
import json
from typing import Tuple

def generate_diagram_with_llm(prompt: str, test_id: int, diagram_type: str = "d2") -> Tuple[bool, str, str]:
    """
    Stage 1: Generate diagram code using LLM (MVP endpoint still does this)
    Stage 2: Render with provider system
    """
    try:
        # STAGE 1: Generate diagram code with LLM (using MVP endpoint)
        response = requests.post(
            "http://localhost:8003/api/v1/diagrams/generate",
            json={
                "prompt": prompt,
                "diagram_type": diagram_type,
                "output_format": "code"  # NEW: get code only, not rendered
            },
            timeout=120
        )

        if response.status_code != 200:
            return (False, f"LLM generation failed: {response.status_code}", "HTTP Error")

        data = response.json()
        diagram_code = data.get('diagram_code')  # Extract generated code

        if not diagram_code:
            return (False, "No diagram code generated", "Generation Error")

        # STAGE 2: Render with provider system
        provider_response = requests.post(
            "http://localhost:8003/api/v1/diagrams/v2/render",
            json={
                "code": diagram_code,
                "diagram_type": diagram_type,
                "provider_id": "d2v1",  # Use specific provider
                "output_format": "svg"
            },
            timeout=120
        )

        if provider_response.status_code != 200:
            return (False, f"Rendering failed: {provider_response.status_code}", "Render Error")

        provider_data = provider_response.json()

        if not provider_data.get('success'):
            return (False, provider_data.get('error', 'Unknown error'), provider_data.get('error'))

        svg_content = provider_data.get('content')
        return (True, svg_content, None)

    except Exception as e:
        return (False, str(e), str(e))
```

### Provider-Only Approach (If MVP removed)

```python
# Alternative: If MVP no longer does LLM generation

def generate_diagram_with_llm_and_render(prompt: str, test_id: int, provider_id: str):
    """Use provider system for everything"""
    try:
        # Single endpoint handles LLM + rendering
        response = requests.post(
            "http://localhost:8003/api/v1/diagrams/v2/render",
            json={
                "prompt": prompt,  # Provider system generates code from prompt
                "diagram_type": "d2",
                "provider_id": provider_id,
                "output_format": "svg"
            },
            timeout=120
        )

        if response.status_code != 200:
            return (False, f"Error: {response.status_code}", "HTTP Error")

        data = response.json()

        if not data.get('success'):
            return (False, data.get('error', 'Unknown error'), data.get('error'))

        return (True, data.get('content'), None)

    except Exception as e:
        return (False, str(e), str(e))
```

---

## Test Suite Refactoring

### 1. LLM D2 Tests (llmd2test)

**Current**: Uses MVP + custom D2 rendering
**New**: Uses LLM generation + d2v1 provider

```python
# backend/tests/llmd2test/validate_all_25_d2.py

provider_id = "d2v1"  # Use native D2 provider
diagram_type = "d2"

response = requests.post(
    "http://localhost:8003/api/v1/diagrams/v2/render",
    json={
        "code": diagram_code,
        "diagram_type": diagram_type,
        "provider_id": provider_id,
        "output_format": "svg"
    }
)
```

**Expected Results**: ✅ 100% (from previous tests)

### 2. LLM Mermaid Tests (llmmermaidtest)

**Current**: Uses MVP + Mermaid CLI
**New**: Uses LLM generation + mermaidv1 provider

```python
provider_id = "mermaidv1"  # Use native Mermaid provider
diagram_type = "mermaid"

response = requests.post(
    "http://localhost:8003/api/v1/diagrams/v2/render",
    json={
        "code": diagram_code,
        "diagram_type": diagram_type,
        "provider_id": provider_id,
        "output_format": "svg"
    }
)
```

**Expected Results**: ✅ 92% (from previous tests)

### 3. Kroki D2 Tests (llmkrokid2test)

**Current**: Uses MVP + Kroki API
**New**: Uses LLM generation + krokid2 provider

```python
provider_id = "krokid2"  # Use Kroki D2 provider
diagram_type = "d2"

response = requests.post(
    "http://localhost:8003/api/v1/diagrams/v2/render",
    json={
        "code": diagram_code,
        "diagram_type": diagram_type,
        "provider_id": provider_id,
        "output_format": "svg"
    }
)
```

**Expected Results**: ✅ 100% (from previous tests)

### 4. Kroki Mermaid Tests (llmkrokimermaidtest)

**Current**: Uses MVP + Kroki API
**New**: Uses LLM generation + krokimermaid provider

```python
provider_id = "krokimermaid"  # Use Kroki Mermaid provider
diagram_type = "mermaid"

response = requests.post(
    "http://localhost:8003/api/v1/diagrams/v2/render",
    json={
        "code": diagram_code,
        "diagram_type": diagram_type,
        "provider_id": provider_id,
        "output_format": "svg"
    }
)
```

**Expected Results**: ✅ 96% (from previous tests)

### 5. Kroki C4 Tests (llmkrokic4test)

**Current**: Uses MVP + Kroki API (failing)
**New**: Uses LLM generation + krokic4 provider

```python
provider_id = "krokic4"  # Use Kroki C4 provider
diagram_type = "c4"

response = requests.post(
    "http://localhost:8003/api/v1/diagrams/v2/render",
    json={
        "code": diagram_code,
        "diagram_type": diagram_type,
        "provider_id": provider_id,
        "output_format": "svg"
    }
)
```

**Expected Results**: 🔄 Will validate provider's C4 support

### 6. Kroki PlantUML Tests (llmkrokiplantumtest)

**Current**: Uses MVP + Kroki API (not tested yet)
**New**: Uses LLM generation + krokiplantuml provider

```python
provider_id = "krokiplantuml"  # Use Kroki PlantUML provider
diagram_type = "plantuml"

response = requests.post(
    "http://localhost:8003/api/v1/diagrams/v2/render",
    json={
        "code": diagram_code,
        "diagram_type": diagram_type,
        "provider_id": provider_id,
        "output_format": "svg"
    }
)
```

**Expected Results**: 🔄 Will determine baseline

### 7. Kroki Structurizr Tests (llmkrokistructurizrtest)

**Current**: Uses MVP + Kroki API (not tested yet)
**New**: Uses LLM generation + krokistructurizr provider

```python
provider_id = "krokistructurizr"  # Use Kroki Structurizr provider
diagram_type = "structurizr"

response = requests.post(
    "http://localhost:8003/api/v1/diagrams/v2/render",
    json={
        "code": diagram_code,
        "diagram_type": diagram_type,
        "provider_id": provider_id,
        "output_format": "svg"
    }
)
```

**Expected Results**: 🔄 Will determine baseline

---

## Implementation Steps

### Step 1: Create Common Test Utilities

Create `backend/tests/common_test_utils.py`:

```python
"""
Common utilities for provider system tests
"""

import requests
from typing import Tuple, Dict, Any

class ProviderTestHelper:
    """Helper for testing diagram providers"""

    def __init__(self, backend_url: str = "http://localhost:8003"):
        self.backend_url = backend_url
        self.provider_endpoint = f"{backend_url}/api/v1/diagrams/v2"

    def render_with_provider(
        self,
        code: str,
        diagram_type: str,
        provider_id: str,
        output_format: str = "svg",
        timeout: int = 120
    ) -> Tuple[bool, str, Dict[str, Any]]:
        """
        Render diagram using specific provider

        Returns:
            Tuple[bool, str, Dict]: (success, content_or_error, metadata)
        """
        try:
            response = requests.post(
                f"{self.provider_endpoint}/render",
                json={
                    "code": code,
                    "diagram_type": diagram_type,
                    "provider_id": provider_id,
                    "output_format": output_format
                },
                timeout=timeout
            )

            if response.status_code != 200:
                return (False, f"HTTP {response.status_code}", {})

            data = response.json()

            if data.get('success'):
                metadata = {
                    "validation": data.get('validation', {}),
                    "provider_id": data.get('provider_id'),
                    "output_format": data.get('output_format')
                }
                return (True, data.get('content'), metadata)
            else:
                return (False, data.get('error', 'Unknown error'), {})

        except Exception as e:
            return (False, str(e), {})

    def validate_with_provider(
        self,
        code: str,
        diagram_type: str,
        provider_id: str,
        auto_fix: bool = True
    ) -> Tuple[bool, str, str]:
        """
        Validate diagram using specific provider

        Returns:
            Tuple[bool, str, str]: (is_valid, error_or_message, fixed_code)
        """
        try:
            response = requests.post(
                f"{self.provider_endpoint}/validate",
                json={
                    "code": code,
                    "diagram_type": diagram_type,
                    "provider_id": provider_id,
                    "auto_fix": auto_fix
                }
            )

            if response.status_code != 200:
                return (False, f"HTTP {response.status_code}", "")

            data = response.json()
            fixed_code = data.get('fixed_code', code)

            return (data.get('is_valid'), data.get('error', ''), fixed_code)

        except Exception as e:
            return (False, str(e), "")
```

### Step 2: Update Test Scripts

Refactor each test script to use the provider system:

```python
# Example: backend/tests/llmd2test/validate_all_25_d2.py

import sys
sys.path.insert(0, '../')
from common_test_utils import ProviderTestHelper

def generate_diagram_with_llm(prompt: str, test_id: int):
    """Generate D2 diagram and render with d2v1 provider"""

    helper = ProviderTestHelper()

    # Generate code with LLM (using MVP endpoint)
    # OR get from test.json if pre-generated

    diagram_code = get_test_code(test_id)  # Load from test data

    # Render with provider
    success, content, metadata = helper.render_with_provider(
        code=diagram_code,
        diagram_type="d2",
        provider_id="d2v1",
        output_format="svg"
    )

    return success, content, metadata
```

### Step 3: Run Tests and Compare

```bash
# Run refactored tests
cd backend/tests/llmd2test
python validate_all_25_d2.py

# Results should match or exceed previous MVP results
```

---

## Expected Outcomes

### Success Criteria

| Test Suite | Current | Target | Provider |
|-----------|---------|--------|----------|
| llmd2test | 100% | 100% | d2v1 |
| llmmermaidtest | 92% | 92%+ | mermaidv1 |
| llmkrokid2test | 100% | 100% | krokid2 |
| llmkrokimermaidtest | 96% | 96%+ | krokimermaid |
| llmkrokic4test | 0% | ?% | krokic4 |
| llmkrokiplantumtest | N/A | ?% | krokiplantuml |
| llmkrokistructurizrtest | N/A | ?% | krokistructurizr |

**Overall**: ✅ Should achieve same or better results

---

## Architecture After Refactoring

### Test Flow (New)

```
Test Suite
    │
    ├─ LLM generates diagram code (via MVP /generate endpoint)
    │  OR loads pre-generated code from test.json
    │
    └─ Render with provider system
       │
       ├─ POST /api/v1/diagrams/v2/render
       │   │
       │   └─ ProviderRegistry
       │       │
       │       └─ Selected Provider (d2v1, mermaidv1, kroki*, etc.)
       │           ├─ Validate
       │           ├─ Auto-fix if needed
       │           ├─ Render
       │           └─ Return SVG/PNG
       │
       └─ Save results
```

### Benefits

1. ✅ **Tests use only official providers** (not MVP-specific code)
2. ✅ **Provider system gets real-world testing** through test suite
3. ✅ **Can validate all 7 providers** in single test run
4. ✅ **Clearer architecture** - tests → providers (no MVP intermediary)
5. ✅ **Future-proof** - new providers automatically work with tests
6. ✅ **Easier to maintain** - centralized provider system, distributed tests

---

## Migration Timeline

**Day 1**: Create common test utilities
**Day 2**: Refactor 2-3 test suites as examples
**Day 3**: Refactor remaining test suites
**Day 4**: Run full test suite and validate results
**Day 5**: Document findings and next steps

---

## Risk Mitigation

**If provider system has issues**:
- Can still use MVP for fallback
- Tests have detailed error reporting
- Easy to compare MVP vs Provider results

**If specific provider fails**:
- Isolate to that provider only
- Other tests continue
- Provider can be debugged independently

---

## Conclusion

Refactoring the 7 test suites to use the provider system will:

✅ Validate provider system quality with real test data
✅ Remove dependency on MVP for testing
✅ Ensure providers work correctly
✅ Give clear success/failure metrics for each provider
✅ Provide foundation for future provider additions

**Recommendation**: Implement Option 1 (Two-Stage) for safety and validation.

