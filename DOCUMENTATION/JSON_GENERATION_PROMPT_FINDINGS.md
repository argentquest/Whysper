# JSON_GENERATION_PROMPT Findings & Deprecation

## Executive Summary

✅ **Audit Complete**

The `JSON_GENERATION_PROMPT.md` file is **LEGACY CODE** and is **NOT USED** in the current LangGraph workflow.

---

## What We Found

### File Location
`backend/app/utils/diagram_wizard/prompts/JSON_GENERATION_PROMPT.md`

### Current State
- ⚠️ Deprecated
- ❌ Not called in the graph
- ❌ Uses custom JSON schema (not Structurizr)
- ❌ Generates redundant `json_representation`

### Where It's Referenced
1. **prompt_loader.py** (line 51): Loads the prompt file into cache
2. **nodes.py** (line 241): Defines `generate_json_representation()` function
3. **nodes.py** (line 261): Gets the prompt template via `get_prompt("json_generation")`
4. **langgraph_builder.py**: NOT ADDED to the graph ❌

### The Graph Actually Uses (7 nodes)
1. analyze_request
2. clarify_prompt ← **THIS generates Structurizr now**
3. determine_diagram_type
4. generate_code
5. validate_code
6. refine_code
7. render_diagram

### Key Finding

**The `clarify_prompt` node ALREADY outputs:**
- `structurizr_workspace` (full Structurizr DSL)
- `clean_d2` (normalized Structurizr)
- `json_representation` (legacy field)

So `generate_json_representation()` is **completely redundant** and never called.

---

## Current Output from clarify_prompt

```python
return {
    "llm_ready": False,
    "clarification_history": updated_history,
    "json_representation": json_representation,  # ← Legacy
    "structurizr_workspace": structurizr_workspace,  # ← NEW (from ANALYSE_CONFIRM)
    "clean_d2": clean_d2,  # ← NEW (from ANALYSE_CONFIRM)
    "clarity_scores": updated_clarity_scores,
    "clarity_score": clarity_score,
    "question_count": question_count + 1,
    "awaiting_user_confirmation": False,
    "current_state": SessionState.CLARIFYING
}
```

---

## Actions Taken

### 1. ✅ Added Deprecation Notice
Added clear warning to the prompt file:
```
⚠️ **DEPRECATED PROMPT** ⚠️

This prompt is **NOT USED** in the current LangGraph workflow (as of 2025-11-16).
```

### 2. ✅ Documented in JSON_GENERATION_PROMPT_REVIEW.md
Created comprehensive audit report explaining:
- Why it's not used
- What replaced it (Structurizr DSL)
- What to do if it's needed in the future

### 3. ✅ Verified Clarify Prompt Already Has It
Confirmed that `clarify_prompt` node outputs:
- Full Structurizr workspace
- Clean Structurizr representation
- All needed architectural data

---

## What This Means for DiagramWizard

### Before (Legacy)
```
analyze_request
  ↓
clarify_prompt (outputs json_representation)
  ↓
generate_json_representation (NEVER CALLED) ❌
  ↓
determine_diagram_type
  ↓
generate_code
```

### Now (Current)
```
analyze_request
  ↓
clarify_prompt (outputs structurizr_workspace + clean_d2) ✅
  ↓
determine_diagram_type (uses clean_d2)
  ↓
generate_code (uses clean_d2)
```

---

## Recommendation: NO ACTION NEEDED

The system is already correct:
1. ✅ clarify_prompt outputs Structurizr DSL
2. ✅ JSON_GENERATION_PROMPT is marked as deprecated
3. ✅ No graph changes needed
4. ✅ System already uses Structurizr

**If in the future someone wants to re-add this node:**
- Update the prompt to output Structurizr format
- Create 4 model-specific versions (gpt5, grok, claude, gemini)
- Match the ANALYSE_CONFIRM output schema

---

## Files Modified

1. ✅ `backend/app/utils/diagram_wizard/prompts/JSON_GENERATION_PROMPT.md`
   - Added deprecation notice at the top

2. ✅ `JSON_GENERATION_PROMPT_REVIEW.md` (created)
   - Comprehensive audit and analysis
   - Historical context
   - Recommendations

3. ✅ `JSON_GENERATION_PROMPT_FINDINGS.md` (this file)
   - Quick summary of findings
   - Action items
   - Status

---

## Status: ✅ AUDIT COMPLETE

The prompt file is correctly identified as deprecated and no longer needs to follow any specific structure since it's not used.

The actual structured representation now comes from:
- **ANALYSE_CONFIRM phase** (initial analysis)
- **CLARIFY_UNIVERSAL phase** (iterative refinement)

Both output the Structurizr DSL format as designed.

---

**Audit Date:** 2025-11-16
**Status:** COMPLETE
**Recommendation:** Leave as-is (deprecated)
**Next Action:** If re-adding in future, update to Structurizr format with 4 models
