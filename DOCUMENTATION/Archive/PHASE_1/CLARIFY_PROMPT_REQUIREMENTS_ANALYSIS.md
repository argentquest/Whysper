# Clarify Prompt Node: Current vs. Proposed Requirements

## Current Implementation (Backend)

**File:** `backend/app/utils/diagram_wizard/nodes.py` lines 304-507

### Current LLM Response Schema Expected

```json
{
  "question": "string - next clarification question",
  "clarity_score": "integer 1-10",
  "ready": "boolean - is clarity >= 8?",
  "json_representation": "object - updated architecture JSON",
  "design_summary": "string - final description when ready"
}
```

### Current Processing Logic

**Line 407-410:**
```python
ai_response = json.loads(ai_response_str)
question = ai_response.get("question")
clarity_score = ai_response.get("clarity_score", 5)  # Scale: 1-10
ready = ai_response.get("ready", False)
json_representation = ai_response.get("json_representation", {})
design_summary = ai_response.get("design_summary", "")
```

### Current State Updates (Lines 471-481)

When NOT ready:
```python
return {
    "llm_ready": False,
    "clarification_history": updated_history,
    "json_representation": json_representation,  # ← JSON only
    "clarity_scores": updated_clarity_scores,
    "clarity_score": clarity_score,  # 1-10 scale
    "question_count": question_count + 1,
    "awaiting_user_confirmation": False,
    "current_state": SessionState.CLARIFYING
}
```

When ready (Lines 449-457):
```python
return {
    "llm_ready": False,
    "final_design_summary": summary,
    "json_representation": json_representation,  # ← JSON only
    "clarity_scores": updated_clarity_scores,
    "clarity_score": clarity_score,  # 1-10 scale
    "awaiting_user_confirmation": True,
    "current_state": SessionState.CLARIFYING
}
```

### SSE Updates to Frontend (Line 422-428)

```python
await update_callback({
    "status": "clarifying",
    "question": question,
    "clarity_score": clarity_score,  # 1-10
    "json_representation": json_representation,  # JSON
    "message_type": "clarification"
})
```

---

## Your Proposal

> Are we asking the LLM to return in the clarify phase to return the structrizer code and a LLM Score between 1 and 100?

### Two Changes:
1. **Return Structurizr code** (in addition to JSON, or instead of?)
2. **Use 1-100 scale** (instead of 1-10)

---

## Analysis & Recommendation

### Option A: Keep Current (1-10 scale, JSON only)

**Pros:**
- Minimal changes to backend
- Current UI already handles 1-10 scores
- JSON representation is flexible

**Cons:**
- Doesn't align with new ANALYSE_CONFIRM prompts (which expect Structurizr)
- 1-10 is less granular than 1-100
- Missing structured Structurizr format

### Option B: Add Structurizr, Keep 1-10 Scale

**New LLM Response Schema:**
```json
{
  "question": "string",
  "clarity_score": "integer 1-10",
  "ready": "boolean",
  "json_representation": "object - legacy JSON",
  "structurizr_workspace": "string - full Structurizr DSL",
  "clean_d2": "string - normalized Structurizr",
  "design_summary": "string"
}
```

**Backend Changes Needed:**
```python
structurizr_workspace = ai_response.get("structurizr_workspace", "")
clean_d2 = ai_response.get("clean_d2", "")

# Update state to include both
return {
    "llm_ready": False,
    "json_representation": json_representation,  # Legacy
    "structurizr_workspace": structurizr_workspace,  # NEW
    "clean_d2": clean_d2,  # NEW
    "clarity_score": clarity_score,  # Still 1-10
    ...
}
```

**Pros:**
- Aligns with new ANALYSE_CONFIRM prompts
- Backward compatible (JSON still there)
- Frontend can display both if needed

**Cons:**
- LLM generating both JSON and Structurizr (redundant)
- Keeps 1-10 scale (less granular)

### Option C: Use 1-100 Scale, Keep JSON

**New LLM Response Schema:**
```json
{
  "question": "string",
  "clarity_score": "integer 1-100",
  "ready": "boolean",
  "json_representation": "object",
  "design_summary": "string"
}
```

**Backend Changes Needed:**
```python
clarity_score = ai_response.get("clarity_score", 50)  # 1-100 scale

# Update readiness logic (was: >= 8, now: >= 80)
if ready or clarity_score >= 80:  # Changed threshold
    ...
```

**Frontend Changes Needed:**
```typescript
// Convert 1-100 to percentage display
const percentage = (clarityScore / 100) * 100;  // Already %
// Or adapt existing 1-10 logic to 1-100
```

**Pros:**
- More granular scoring
- Better precision in clarity assessment

**Cons:**
- Frontend UI needs updates (might show 87% instead of 8/10)
- Need to update readiness threshold logic
- Less familiar scale for users

### Option D: Structurizr + 1-100 Scale (Most Comprehensive)

**New LLM Response Schema:**
```json
{
  "question": "string",
  "clarity_score": "integer 1-100",
  "ready": "boolean",
  "json_representation": "object - legacy",
  "structurizr_workspace": "string - full Structurizr DSL",
  "clean_d2": "string - normalized Structurizr",
  "design_summary": "string"
}
```

**Backend Changes Needed:**
```python
clarity_score = ai_response.get("clarity_score", 50)  # 1-100
structurizr_workspace = ai_response.get("structurizr_workspace", "")
clean_d2 = ai_response.get("clean_d2", "")

# Update readiness threshold
if ready or clarity_score >= 80:  # 80/100 = ready
    ...

# Update state
return {
    "llm_ready": False,
    "json_representation": json_representation,
    "structurizr_workspace": structurizr_workspace,  # NEW
    "clean_d2": clean_d2,  # NEW
    "clarity_score": clarity_score,  # 1-100
    ...
}
```

**Pros:**
- Full alignment with ANALYSE_CONFIRM prompts
- More granular scoring (1-100)
- Complete transition to Structurizr representation
- Future-proof architecture

**Cons:**
- Most changes required
- Frontend UI needs updates
- LLM generating more data per turn

---

## Current State in Code

Looking at lines 373-376 in the fallback prompt:
```python
prompt_template = """You are an expert system architect. Your role is to interview the user about their system architecture and iteratively refine the JSON representation of components and connections.

INSTRUCTIONS:
1. Ask ONE clarifying question per turn to understand system components and connections
2. After each user response, provide a clarity_score (1-10)
3. Update the json_representation with new information
4. Respond ONLY in JSON format with: question, clarity_score, ready, json_representation
5. Mark ready=true when clarity_score >= 8 and you have sufficient detail
```

This is the **legacy prompt** (not using ANALYSE_CONFIRM versions).

---

## Recommendation Summary

| Aspect | Current | Option B | Option C | Option D ✅ |
|--------|---------|----------|----------|------------|
| **Structurizr support** | ❌ No | ✅ Yes | ❌ No | ✅ Yes |
| **Granular scoring** | ❌ 1-10 | ❌ 1-10 | ✅ 1-100 | ✅ 1-100 |
| **ANALYSE_CONFIRM aligned** | ❌ No | ⚠️ Partial | ❌ No | ✅ Yes |
| **Backend changes needed** | None | Moderate | Moderate | Significant |
| **Frontend changes needed** | None | Minimal | Significant | Significant |
| **Future-proof** | ❌ No | ⚠️ Somewhat | ⚠️ Somewhat | ✅ Yes |

**My Recommendation:** **Option D** - Full transition to Structurizr + 1-100 scale

### Why?
1. Aligns perfectly with new ANALYSE_CONFIRM prompt versions
2. More granular scoring reduces ambiguity
3. Complete transition away from legacy JSON
4. Sets up system for long-term evolution

### Implementation Steps:
1. **Update all 4 ANALYSE_CONFIRM prompts** to expect 1-100 scale
2. **Update clarify_prompt node** to parse Structurizr fields
3. **Update readiness logic**: change `clarity >= 8` to `clarity >= 80`
4. **Update frontend** to display 1-100 scale properly
5. **Migrate state** to use Structurizr instead of (or alongside) JSON

---

## Next Steps

Which option would you like to implement?

- **Option A:** No changes (keep current)
- **Option B:** Add Structurizr, keep 1-10
- **Option C:** Use 1-100, keep JSON
- **Option D:** Structurizr + 1-100 (recommended)

Once decided, I can:
1. Update all 4 prompt files
2. Create backend migration guide
3. Update clarify_prompt node
4. Frontend integration guidelines
