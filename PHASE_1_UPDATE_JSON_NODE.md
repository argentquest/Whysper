# CRITICAL UPDATE: JSON Generation Node Integration

**Date:** 2025-11-16

**Status:** Phase 1 Complete with Updated Phase 2 Plan

**Change:** User requested JSON_GENERATION_PROMPT be **integrated into the LangGraph workflow** and **updated to use Structurizr format**

---

## What Changed

### Previous Plan (Phase 1)
- ❌ JSON_GENERATION_PROMPT marked as deprecated
- ❌ Function exists but not in graph
- ❌ Recommendation: Leave as-is (deprecated)

### Updated Plan (Phase 1 → Phase 2)
- ✅ Keep JSON_GENERATION_PROMPT
- ✅ Update it to output **Structurizr DSL format**
- ✅ Create 4 model-specific versions
- ✅ **Integrate into LangGraph workflow** (Phase 2 task)
- ✅ Wire between `clarify_prompt` and `determine_diagram_type`

---

## New Workflow (After Phase 2)

```
User selects AI model (GPT-5, Grok, Claude, or Gemini)
    ↓
1. analyze_request
   - Initial analysis
   - Output: Structurizr workspace + clarity score
    ↓
2. clarify_prompt (LOOP until clarity >= 8)
   - Iterative refinement
   - Update Structurizr
   - Ask clarifying questions
    ↓
3. generate_json_representation [NEW IN PHASE 2]
   - Validate Structurizr representations
   - Output: structurizr_workspace + clean_d2 + json_representation
   - Ensure dual representation synchronization
    ↓
4. determine_diagram_type
   - Auto-select: Mermaid/D2/PlantUML
    ↓
5. generate_code
   - Generate diagram code
    ↓
6. validate_code
   - Check syntax
   - If invalid → refine_code (max 3 attempts)
    ↓
7. render_diagram
   - Output SVG
```

---

## Phase 2 Tasks (Updated)

### Critical Tasks Added

**Task: Update JSON_GENERATION_PROMPT**
- [ ] Update base prompt to output Structurizr DSL
- [ ] Add `structurizr_workspace` field
- [ ] Add `clean_d2` field (normalized Structurizr)
- [ ] Keep `json_representation` field (legacy schema)
- [ ] Specify dual representation synchronization rules

**Task: Create 4 Model-Specific JSON Prompts**
- [ ] `JSON_GENERATION_gpt5.md` – GPT-5 version
- [ ] `JSON_GENERATION_grok.md` – Grok version
- [ ] `JSON_GENERATION_sonet45.md` – Claude version
- [ ] `JSON_GENERATION_gemini25pro.md` – Gemini version

**Task: Update generate_json_representation Function**
- [ ] Accept `model_id` from state
- [ ] Load model-specific prompt via get_prompt()
- [ ] Parse response with Structurizr + legacy schema
- [ ] Validate dual representation synchronization
- [ ] Return updated state

**Task: Wire JSON Node into Graph**
- [ ] Import `generate_json_representation` in langgraph_builder.py
- [ ] Add node: `workflow.add_node("generate_json_representation", ...)`
- [ ] Update edge: clarify_prompt → generate_json_representation → determine_diagram_type
- [ ] Test graph compilation and execution

**Task: Add to MODEL_MAPPING**
- [ ] Add `json_generation_prompt` field to each model config:
  ```python
  'gpt5': {
      ...
      'json_generation_prompt': 'JSON_GENERATION_gpt5.md'
  }
  ```

---

## Unified Output from JSON Generation Node

All 4 model-specific prompts return identical schema:

```json
{
  "analysis_summary": "Summary of what was analyzed",
  "clarity_score": 8,
  "structurizr_workspace": "Full Structurizr DSL workspace { model { ... } views { ... } }",
  "clean_d2": "Normalized Structurizr model { ... }",
  "json_representation": {
    "metadata": { "system_name": "...", "description": "..." },
    "components": [ { "name": "...", "type": "service", ... } ],
    "connections": [ { "source": "...", "target": "...", ... } ],
    "users": [ { "name": "...", "type": "person", ... } ]
  },
  "assumptions": ["Assumption 1", "Assumption 2"],
  "next_step": "ready_for_generation"
}
```

**Key Guarantees:**
- ✓ Structurizr DSL format (not D2 diagram syntax)
- ✓ Dual representation synchronized (workspace = clean_d2, different format)
- ✓ Legacy JSON schema included for backward compatibility
- ✓ Identical schema across all 4 models

---

## Implementation Reference

**Detailed Implementation Plan:** See `JSON_GENERATION_PHASE_2_IMPLEMENTATION.md`

**Key Sections:**
- Current state of generate_json_representation function
- Prompt structure and requirements
- Function updates needed
- Graph integration steps
- Error handling
- Testing strategy
- Success criteria

---

## Updated Files

### Updated in Phase 1
- `backend/app/utils/diagram_wizard/prompts/JSON_GENERATION_PROMPT.md`
  - Changed header from "DEPRECATED" to "Phase 2 Implementation"
  - Now marks it as "Will be integrated"

### Will Update in Phase 2
- `backend/app/utils/diagram_wizard/prompts/JSON_GENERATION_PROMPT.md` (full content)
- `backend/app/utils/diagram_wizard/nodes.py` (generate_json_representation function)
- `backend/app/utils/diagram_wizard/langgraph_builder.py` (add to graph)
- `backend/app/utils/diagram_wizard/main.py` (MODEL_MAPPING)

### Will Create in Phase 2
- `backend/app/utils/diagram_wizard/prompts/JSON_GENERATION_gpt5.md`
- `backend/app/utils/diagram_wizard/prompts/JSON_GENERATION_grok.md`
- `backend/app/utils/diagram_wizard/prompts/JSON_GENERATION_sonet45.md`
- `backend/app/utils/diagram_wizard/prompts/JSON_GENERATION_gemini25pro.md`

---

## Phase 2 Timeline Impact

**Original Phase 2:** 2-3 days

**With JSON Node Integration:** ~1 extra day (total 3-4 days)

**Breakdown:**
- GraphState + MODEL_MAPPING: ~2-3 hours
- Prompt loader updates: ~1 hour
- Node updates (analyze, clarify): ~1-2 hours
- JSON prompts (create 5 files): ~2-3 hours ← NEW
- JSON node function: ~1 hour ← NEW
- Graph integration: ~1 hour ← NEW
- Testing: ~3-4 hours

**Total Phase 2:** ~3-4 days (1 extra day for JSON node)

---

## Success Criteria (Updated)

### Phase 2 Success Includes:
- ✅ User can select model at start
- ✅ Selected model used throughout session
- ✅ All 4 models work correctly
- ✅ **JSON_GENERATION_PROMPT updated to Structurizr format** ← NEW
- ✅ **4 model-specific JSON prompts created** ← NEW
- ✅ **JSON node integrated into graph** ← NEW
- ✅ **Dual representation synchronized** ← NEW
- ✅ Proper error handling
- ✅ Backward compatible
- ✅ Tests passing

---

## Why This Makes Sense

### Benefits of Integrating JSON Node
1. **Validation Layer:** Ensures Structurizr output is valid before diagram generation
2. **Redundancy:** Additional verification of architecture understanding
3. **Legacy Schema:** Maintains backward compatibility with existing code
4. **Metadata Extraction:** Pulls structured data for potential future use
5. **Quality Gate:** One more chance to catch issues before code generation

### Why Structurizr Format
- Same format as ANALYSE_CONFIRM and CLARIFY_UNIVERSAL
- Ensures consistency across all 3 phases
- Enables easy model-specific variations
- Follows unified output schema

---

## Phase 1 to Phase 2 Transition

### What Phase 1 Provided
- ✅ 8 prompt files (ANALYSE + CLARIFY)
- ✅ Comprehensive documentation
- ✅ Architecture design
- ✅ Implementation roadmap

### What Phase 2 Will Add
- ✅ Backend implementation of model selection
- ✅ Frontend ModelSelector component
- ✅ **JSON_GENERATION node activation** ← NEW
- ✅ **5 JSON-specific prompt files** ← NEW
- ✅ Integration testing

### Total Deliverable
- 13 prompt files (4 ANALYSE + 4 CLARIFY + 5 JSON)
- Complete working system with model selection
- Full test coverage

---

## Documentation References

**For Phase 2 Implementation:**
- `JSON_GENERATION_PHASE_2_IMPLEMENTATION.md` – Complete implementation guide
- `IMPLEMENTATION_CHECKLIST.md` Phase 2 – Updated with JSON tasks
- `DIAGRAMWIZARD_COMPLETE_SUMMARY.md` – Architecture overview
- `PROMPT_VERSIONS_COMPLETE.md` – Updated for 13 total prompts

---

## Next Steps

1. ✅ Phase 1 COMPLETE (with updated plan)
2. → **Begin Phase 2 Backend Implementation**
   - Start with GraphState + MODEL_MAPPING
   - Then JSON prompts (5 files)
   - Then node updates
   - Then graph integration
   - Then testing

3. → Continue with Phase 3 Frontend
4. → Phase 4 Testing
5. → Phases 5-7 Deployment

---

## Summary

**User Request:** Keep JSON_GENERATION_PROMPT and integrate it into the workflow

**Response:**
- ✅ Created comprehensive Phase 2 implementation plan
- ✅ Updated IMPLEMENTATION_CHECKLIST with JSON node tasks
- ✅ Designed 5-file JSON prompt structure (1 base + 4 model-specific)
- ✅ Specified node function updates
- ✅ Detailed graph integration steps
- ✅ All 8+ hours of work documented and task-broken-down

**Impact:** +1 day to Phase 2 timeline (2-3 days → 3-4 days)

**Result:** System will have comprehensive validation layer + legacy schema support

---

**Status:** ✅ Phase 1 COMPLETE

**Phase 2 Ready:** ✅ YES (with JSON node integration)

**Timeline:** ~11 days remaining (Phase 2-7)

---
