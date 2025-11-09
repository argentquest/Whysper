# Whysper Diagram Architecture Summary

**Date**: November 3, 2025
**Status**: Clarified and documented

---

## Quick Reference

### Three Layers of Diagram System

```
LAYER 1: RENDERING (Low-level CLI tools)
├── mmdc (Mermaid CLI)
├── d2 (D2 CLI)
├── kroki-cli or API (Kroki service)
└── PlantUML, Structurizr

LAYER 2: PROVIDERS (Pluggable providers, each uses Layer 1)
├── mermaidv1 → uses mmdc
├── d2v1 → uses d2
├── krokid2 → uses kroki
├── krokimermaid → uses kroki
├── krokic4 → uses kroki
├── krokiplantuml → uses kroki
└── krokistructurizr → uses kroki

LAYER 3: SERVICES (Use providers)
├── MVP Diagram Generator (MVP frontend)
│  └── /api/v1/diagrams/*
│      └── Uses: renderer_v2.py (direct Layer 1)
│
└── Provider System (New modular system)
   └── /api/v1/diagrams/v2/*
       └── Uses: ProviderRegistry → Providers (Layer 2)

LAYER 4: CLIENTS
├── Frontend (uses MVP)
├── Test Suites (should use Provider System)
└── Other integrations
```

---

## Current Reality (Nov 3, 2025)

### MVP System (MVP Diagram Generator)
- **Location**: `backend/mvp_diagram_generator/`
- **API Endpoint**: `/api/v1/diagrams/*`
- **Used By**: Frontend (current)
- **Status**: ✅ Working, 92-100% success
- **Does**: LLM generation + validation + rendering (monolithic)

**Files**:
- `rendering_api.py` - FastAPI router
- `renderer_v2.py` - Mermaid CLI-only rendering (recently updated)
- `diagram_validators.py` - Basic validation
- `d2_syntax_fixer.py` - D2 fixing
- `mermaid_syntax_fixer.py` - Mermaid fixing
- Other helpers

### Provider System (New modular system)
- **Location**: `backend/diagrams/`
- **API Endpoint**: `/api/v1/diagrams/v2/*`
- **Used By**: Tests (should use)
- **Status**: ✅ Production-ready
- **Does**: Plugin-based providers, each handles one diagram type

**Providers** (in separate folders):
1. **mermaidv1** - Mermaid rendering (native, full features)
2. **d2v1** - D2 rendering (native, full features)
3. **krokid2** - D2 via Kroki API
4. **krokimermaid** - Mermaid via Kroki API
5. **krokic4** - C4 via Kroki API
6. **krokiplantuml** - PlantUML via Kroki API
7. **krokistructurizr** - Structurizr via Kroki API

**Infrastructure**:
- `base_diagram.py` - Abstract base class (Template Method pattern)
- `provider_registry.py` - Auto-discovery and selection
- `provider_config.py` - Configuration system
- `llm_correction_service.py` - AI-powered fixing

---

## Test Suites (Current)

### 7 Test Suites → Should map to 7 Providers

| Test Suite | Currently Uses | Should Use |
|-----------|---------|---------|
| `llmd2test` | MVP + renderer_v2 | **d2v1 provider** |
| `llmmermaidtest` | MVP + renderer_v2 | **mermaidv1 provider** |
| `llmkrokid2test` | MVP + Kroki | **krokid2 provider** |
| `llmkrokimermaidtest` | MVP + Kroki | **krokimermaid provider** |
| `llmkrokic4test` | MVP + Kroki | **krokic4 provider** |
| `llmkrokiplantumtest` | MVP + Kroki | **krokiplantuml provider** |
| `llmkrokistructurizrtest` | MVP + Kroki | **krokistructurizr provider** |

### Results (from Nov 3 test run)
- llmd2test: **100%** ✅
- llmmermaidtest: **92%** ✅
- llmkrokid2test: **100%** ✅
- llmkrokimermaidtest: **96%** ✅
- llmkrokic4test: **0%** ❌ (needs investigation)
- llmkrokiplantumtest: Not tested
- llmkrokistructurizrtest: Not tested

---

## Your Requirements

**Statement**: "When we run the 7 suite of tests it should only rely on these providers. The old MVP is in use now for the current front end only"

**Translation**:
1. Tests → Provider System (`/api/v1/diagrams/v2/*`)
2. Frontend → MVP System (`/api/v1/diagrams/*`)
3. Both can coexist (no immediate changes needed)

**Action Required**:
- Refactor test scripts to use provider endpoints
- Each test suite maps to one provider
- Document findings for each provider

---

## Key Architecture Points

### Separation of Concerns

```
FRONTEND (MVP):
- Needs fast iteration
- Uses simple MVP system
- Direct API endpoints
- Monolithic but simple

TEST SUITES (Provider System):
- Needs to validate each provider independently
- Uses modular provider system
- Plugin architecture
- Each provider tested separately
```

### Provider System Advantages

✅ **Modularity**: Each provider is self-contained
✅ **Extensibility**: Add new providers by adding folders
✅ **Testability**: Each provider tested independently
✅ **Configuration**: Hierarchy (root → provider → runtime)
✅ **Auto-discovery**: Providers auto-detected from folders
✅ **Validation Pipeline**: Three-tier correction (pattern → LLM → manual)

### MVP System Advantages

✅ **Simplicity**: Single code path
✅ **Fast**: No overhead, direct execution
✅ **Proven**: Working with frontend
✅ **Direct**: Combines all steps (generation + validation + rendering)

---

## Implementation Plan

### Phase 1: Understand (Done ✅)
- [x] Reviewed MVP system architecture
- [x] Reviewed provider system architecture
- [x] Identified all 7 providers
- [x] Mapped test suites to providers
- [x] Created documentation

### Phase 2: Refactor Test Suites (To do)
- [ ] Create common test utilities
- [ ] Update `llmd2test` → d2v1 provider
- [ ] Update `llmmermaidtest` → mermaidv1 provider
- [ ] Update `llmkrokid2test` → krokid2 provider
- [ ] Update `llmkrokimermaidtest` → krokimermaid provider
- [ ] Update `llmkrokic4test` → krokic4 provider (for debugging)
- [ ] Update `llmkrokiplantumtest` → krokiplantuml provider
- [ ] Update `llmkrokistructurizrtest` → krokistructurizr provider

### Phase 3: Validation (To do)
- [ ] Run all 7 test suites with provider system
- [ ] Compare results with MVP baseline
- [ ] Identify any provider issues
- [ ] Document findings

### Phase 4: Documentation (To do)
- [ ] Create provider health report
- [ ] Document each provider's capabilities
- [ ] Create migration guide for other systems
- [ ] Archive MVP-based test results

---

## Code Changes Required

### Minimal Changes to Test Suites

**From** (MVP-based):
```python
response = requests.post(
    "http://localhost:8003/api/v1/diagrams/generate",
    json={"prompt": prompt, "diagram_type": "d2", "output_format": "svg"}
)
```

**To** (Provider-based):
```python
response = requests.post(
    "http://localhost:8003/api/v1/diagrams/v2/render",
    json={
        "code": diagram_code,
        "diagram_type": "d2",
        "provider_id": "d2v1",
        "output_format": "svg"
    }
)
```

**Key Changes**:
1. Different endpoint: `/diagrams` → `/diagrams/v2`
2. Different payload structure
3. Specify provider explicitly
4. Separate concerns: generation and rendering

---

## Documentation Created

1. **RENDERING_ARCHITECTURE_CLARIFICATION.md**
   - Explains renderer_v2.py vs mermaidv1 provider
   - Why both exist
   - When to use each

2. **MVP_VS_PROVIDER_SYSTEM_ANALYSIS.md**
   - Detailed comparison of MVP vs Provider
   - Migration path recommendations
   - Risk assessment

3. **TEST_REFACTOR_TO_PROVIDER_SYSTEM.md**
   - How to refactor each test suite
   - Code examples
   - Step-by-step implementation guide

4. **PROVIDER_SYSTEM_TEST_ARCHITECTURE.md**
   - Architecture diagrams
   - Endpoint documentation
   - Test design patterns
   - Implementation checklist

5. **ARCHITECTURE_SUMMARY.md** (this file)
   - Quick reference
   - Current state overview
   - Your requirements clarified

---

## Next Immediate Actions

### If you want to start refactoring tests now:

1. **Create test utilities** (1 hour)
   ```python
   # backend/tests/common_test_utils.py
   class ProviderTestHelper:
       def render_with_provider(self, code, diagram_type, provider_id):
           # Call /api/v1/diagrams/v2/render
           pass
   ```

2. **Refactor one test** (2 hours)
   - Pick `llmd2test` (simplest)
   - Update to use `d2v1` provider
   - Test and verify results

3. **Refactor remaining tests** (4-6 hours)
   - Follow the same pattern
   - Update 6 more test suites

4. **Validate and report** (2 hours)
   - Run all 7 suites
   - Compare with previous results
   - Create summary

**Total time**: ~10 hours of focused work

---

## FAQ

**Q: Should I remove MVP?**
A: No. MVP is still used by frontend. Keep it running.

**Q: Should tests use MVP or Provider system?**
A: Tests should use **Provider System** to validate providers independently.

**Q: Can they coexist?**
A: Yes. MVP at `/api/v1/diagrams/*`, Provider at `/api/v1/diagrams/v2/*`

**Q: What about the C4 test failures (0%)?**
A: Investigate with provider system. May be C4 prompt issues or Kroki API issues.

**Q: Should I update the frontend?**
A: Not immediately. Frontend stays on MVP for now. It's working fine.

**Q: When to migrate frontend to provider system?**
A: Later, after tests prove provider system stability. (Phase 3-4)

**Q: What about renderer_v2.py?**
A: Keep it. It's the rendering engine for MVP. Was updated to use Mermaid CLI only.

---

## Summary

### Architecture (Final)

```
Whysper Diagram System

┌─────────────────────────────────────┐
│          FRONTEND (Web UI)           │ Uses MVP
│   /api/v1/diagrams/*                 │
│   (rendering_api.py)                 │
└─────────────────────────────────────┘
         │
         └──→ MVP Diagram Generator
             ├── LLM Generation
             ├── renderer_v2.py
             └── Rendering

┌─────────────────────────────────────┐
│        TEST SUITES (7 tests)         │ Uses Provider System
│   /api/v1/diagrams/v2/*              │
│   (diagram_provider.py)               │
└─────────────────────────────────────┘
         │
         └──→ Provider Registry
             ├── mermaidv1
             ├── d2v1
             ├── krokid2
             ├── krokimermaid
             ├── krokic4
             ├── krokiplantuml
             └── krokistructurizr
```

### Status

✅ MVP: Working (92-100% for Mermaid/D2)
✅ Providers: Ready for testing
✅ Architecture: Clarified and documented
⏳ Tests: Need refactoring to use providers

### Your Task

Refactor 7 test suites to use provider system instead of MVP, so each provider is independently validated.

**Estimated effort**: 10 hours
**Expected outcome**: 7/7 test suites using only provider system
**Confidence**: High (providers already production-ready)

---

**Created**: November 3, 2025
**Status**: Ready for implementation
**Next step**: Review documents and start Phase 2 refactoring

