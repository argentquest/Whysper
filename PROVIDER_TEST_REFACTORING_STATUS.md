# Provider System Test Refactoring - Status Report

**Date**: November 3, 2025
**Status**: Phase 2 In Progress - Architecture Complete, First Test Template Created

---

## Work Completed

### ✅ Phase 1: Understanding & Documentation
- Analyzed MVP system and provider system architecture
- Created 6 comprehensive documentation files
- Clarified requirements and mapping
- Created architecture diagrams and flow charts

### ✅ Common Test Utilities Created
**File**: `backend/tests/provider_test_helper.py`

**Classes Created**:
1. **ProviderTestHelper** - Main helper for provider testing
   - `render_with_provider()` - Render with specific provider
   - `validate_with_provider()` - Validate with specific provider
   - `generate_diagram_with_llm()` - Generate code via MVP LLM endpoint
   - `list_providers()` - Get available providers

2. **DiagramTestRunner** - Test runner for each provider
   - `run_tests()` - Execute all tests with a provider
   - `_save_validation_results()` - Save results as JSON
   - `get_results()` - Get detailed test results

**Key Features**:
- Handles both /api/v1/diagrams (MVP) and /api/v1/diagrams/v2 (Provider) endpoints
- Auto-creates test_results_25/svg/ and errors/ directories
- Saves validation results as JSON
- Provides clear pass/fail reporting

---

## Work In Progress

### ⏳ Test Script Refactoring

**First Template**: `backend/tests/llmd2test/validate_all_25_d2_provider.py`

**Status**: 80% complete - needs workflow refinement

**Issue Discovered**:
- Test data (test25.json) contains descriptions but not pre-generated diagram code
- Need two-stage approach:
  1. Generate diagram code from description using MVP LLM endpoint
  2. Render generated code using provider system

**Solution**:
The ProviderTestHelper already has `generate_diagram_with_llm()` method which:
- Calls `/api/v1/diagrams/generate` (MVP endpoint)
- Gets generated diagram code
- This code is then rendered with `/api/v1/diagrams/v2/render` (Provider endpoint)

---

## Recommended Workflow for Each Test Suite

### Step 1: Generate Diagram Code (via MVP LLM)
```python
helper = ProviderTestHelper()
success, code, error = helper.generate_diagram_with_llm(
    prompt=test_case['description'],
    diagram_type='d2'  # or 'mermaid', etc.
)
```

### Step 2: Render with Provider
```python
success, content, metadata = helper.render_with_provider(
    code=code,
    diagram_type='d2',
    provider_id='d2v1',  # Specific provider to test
    output_format='svg'
)
```

### Step 3: Use DiagramTestRunner to Automate
```python
runner = DiagramTestRunner(
    provider_id="d2v1",
    diagram_type="d2"
)
summary = runner.run_tests(test_cases)
```

---

## Seven Test Suites - Implementation Plan

Each test suite needs this workflow implemented:

| Test Suite | Provider | Diagram Type | File Name |
|-----------|----------|-------------|-----------|
| llmd2test | d2v1 | d2 | validate_all_25_d2_provider.py |
| llmmermaidtest | mermaidv1 | mermaid | validate_all_25_mermaid_provider.py |
| llmkrokid2test | krokid2 | d2 | validate_all_25_krokid2_provider.py |
| llmkrokimermaidtest | krokimermaid | mermaid | validate_all_25_krokimermaid_provider.py |
| llmkrokic4test | krokic4 | c4 | validate_all_25_krokic4_provider.py |
| llmkrokiplantumtest | krokiplantuml | plantuml | validate_all_25_krokiplantuml_provider.py |
| llmkrokistructurizrtest | krokistructurizr | structurizr | validate_all_25_krokistructurizr_provider.py |

---

## Next Steps

### Immediate (Now - 1 hour)
1. Refine the workflow to properly handle LLM generation → Provider rendering
2. Test first script with actual backend
3. Create generic test template for remaining 6 test suites

### Short-term (1-2 hours)
1. Duplicate template for remaining 6 test suites
2. Update each with correct:
   - provider_id
   - diagram_type
   - test_file name
   - test_output_dir

### Testing (1-2 hours)
1. Run all 7 test suites sequentially
2. Collect results
3. Document success/failure by provider

### Final (30 min)
1. Create summary report
2. Document provider health
3. Archive results

---

## Current Architecture (After Refactoring)

```
┌─ Test Suite (e.g., llmd2test) ─────────────────┐
│                                                  │
│  1. Load test descriptions from test25.json      │
│  2. For each test:                               │
│     a) Call MVP /diagrams/generate               │
│        → LLM generates diagram code              │
│     b) Call Provider /diagrams/v2/render         │
│        → Provider renders code                   │
│     c) Save SVG or error                         │
│  3. Report: passed/failed metrics                │
│                                                  │
└──────────────────────────────────────────────────┘

Benefits:
✅ Tests validate ONLY provider rendering quality
✅ LLM generation separate from provider validation
✅ Each provider independently tested
✅ Clear metrics for provider performance
✅ MVP can be deprecated later without affecting tests
```

---

## Files Created So Far

1. **provider_test_helper.py** (208 lines)
   - ProviderTestHelper class - ready to use
   - DiagramTestRunner class - ready to use
   - Fully documented with docstrings

2. **validate_all_25_d2_provider.py** (110 lines)
   - Template test script
   - 80% complete - needs workflow adjustment
   - Can be duplicated for other tests

---

## Key Architecture Insights

### Provider System Endpoints
```
POST /api/v1/diagrams/v2/render
{
  "code": "diagram code",
  "diagram_type": "d2",
  "provider_id": "d2v1",
  "output_format": "svg",
  "auto_fix": true,
  "use_llm": false
}
```

### MVP Endpoint (for LLM Generation)
```
POST /api/v1/diagrams/generate
{
  "prompt": "description",
  "diagram_type": "d2",
  "output_format": "code"
}
```

### Two-Stage Process
```
Description → MVP LLM Generation → Diagram Code → Provider Rendering → SVG/PNG
```

---

## Testing Strategy

### Phase A: Individual Provider Testing (7 runs)
Run each test suite against its corresponding provider:
- llmd2test → d2v1
- llmmermaidtest → mermaidv1
- llmkrokid2test → krokid2
- llmkrokimermaidtest → krokimermaid
- llmkrokic4test → krokic4
- llmkrokiplantumtest → krokiplantuml
- llmkrokistructurizrtest → krokistructurizr

### Expected Results
- Core providers (d2v1, mermaidv1, kroki*): 80-100% success
- Test quality: Validate provider rendering only

### Metrics Collected
- Pass/fail count
- Error types
- Rendering time
- SVG/PNG quality

---

## Summary

✅ **Utilities Created**: Reusable test helper classes ready
✅ **Template Started**: First test script template created
✅ **Architecture Solid**: Two-stage workflow clarified
⏳ **Remaining Work**: 6 more test script templates + testing

**Estimated Time to Complete**: 3-4 hours
**Server Status**: Running and ready for testing
**Confidence Level**: High (all infrastructure in place)

---

**Next Action**: Refine workflow in first test script, test with provider system, then duplicate for remaining 6 test suites.

