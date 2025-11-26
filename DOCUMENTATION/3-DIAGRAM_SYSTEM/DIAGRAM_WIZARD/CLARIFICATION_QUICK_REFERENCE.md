# Clarification Phase - Quick Reference Guide

**Purpose:** One-page reference for understanding how clarity scores drive the clarification loop

---

## 🎯 The Core Concept

**Clarity Score = Progress Metric**
- LLM rates understanding of user requirements (1-10)
- At each turn, decides if ready to proceed
- Accumulates in list to show progression
- Triggers loop exit when ≥ 8

---

## 📊 The Loop in One Picture

```
Turn 1: User explains → LLM scores 5 → Ask Q1 → score=[5] → LOOP
Turn 2: User adds detail → LLM scores 6 → Ask Q2 → score=[5,6] → LOOP
Turn 3: User clarifies → LLM scores 7 → Ask Q3 → score=[5,6,7] → LOOP
Turn 4: User completes → LLM scores 8 ✅ → READY → score=[5,6,7,8] → EXIT
                                                     ↓
                              Determine Diagram Type → Generate Code
```

---

## 🔑 Key Variables

| Variable | Type | Purpose | Example |
|----------|------|---------|---------|
| `clarity_score` | int (1-10) | This turn's score | 6 |
| `clarity_scores` | List[int] | All scores so far | [5,6,7,8] |
| `ready` | bool | LLM says ready? | true/false |
| `llm_ready` | bool | Exit clarification? | true (exit), false (continue) |
| `question_count` | int | How many turns? | 4 |
| `final_design_summary` | str | What we'll generate from | "Complete login system..." |
| `json_representation` | Dict | Architecture schema | {components: [...], ...} |

---

## ✅ Exit Condition (The Critical Logic)

```python
# In clarify_prompt function (lines 385-409)

if ready or design_summary.startswith("READY:"):
    # LLM explicitly says ready
    return {
        "llm_ready": True,  ← THIS IS THE EXIT SIGNAL
        "clarity_scores": [5, 6, 7, 8],
        "final_design_summary": summary,
        "json_representation": json_rep
    }
else:
    # LLM wants more clarification
    return {
        "llm_ready": False,  ← CONTINUE LOOP SIGNAL
        "clarity_scores": [5, 6],  ← Grow the list
        "question_count": 2  ← Increment
    }
```

---

## 🚦 Routing Decision

```python
# In langgraph_builder.py (lines 80-84)

def route_after_clarification(state):
    if state.get("llm_ready", False):
        return "generate_code"  # Exit to code generation
    else:
        return END  # Pause, wait for user response
```

---

## 📱 Frontend Experience

### **Clarification Question (Loop Continues)**
```json
{
    "status": "clarifying",
    "question": "What are the main components?",
    "clarity_score": 6,
    "clarity_scores": [5, 6],
    "message_type": "clarification"
}
```
→ **User Response:** Types answer → Posted via API

### **Ready Signal (Loop Exits)**
```json
{
    "status": "ready_for_code_generation",
    "message": "✅ AI has sufficient information (clarity: 8/10)",
    "clarity_score": 8,
    "clarity_scores": [5, 6, 7, 8],
    "message_type": "success"
}
```
→ **Next Phase:** Diagram type determination → Code generation

---

## 💾 State Accumulation

```
Initial: {}

After Turn 1:
  clarification_history: [user_msg, ai_question]
  clarity_scores: [5]
  question_count: 1
  llm_ready: FALSE

After Turn 2:
  clarification_history: [user_msg, ai_q, user_msg, ai_q]
  clarity_scores: [5, 6]
  question_count: 2
  llm_ready: FALSE

After Turn 3:
  clarification_history: [... +2 more ...]
  clarity_scores: [5, 6, 7]
  question_count: 3
  llm_ready: FALSE

After Turn 4:
  clarification_history: [... +2 more ...]
  clarity_scores: [5, 6, 7, 8]
  question_count: 4
  llm_ready: TRUE ← EXIT
```

---

## 🎯 Clarity Score Meaning

```
Score 1-2:  "Need to understand basics"
            → Ask foundational questions

Score 3-4:  "Initial understanding only"
            → Ask about key components

Score 5-6:  "Partially clear"
            → Ask about relationships and flows

Score 7:    "Mostly clear"
            → Ask about edge cases and error handling

Score 8-10: "READY!" ✅
            → Proceed to code generation
```

---

## 🔄 LLM Decision Making

**Each Turn, LLM Asks Itself:**

1. **Are components identified?** (0-2 points)
   - Services? Databases? APIs? External systems?

2. **Are relationships clear?** (0-2 points)
   - How does component A talk to B?
   - What's the data flow?

3. **Is error handling covered?** (0-2 points)
   - What happens on failure?
   - Retry logic? Fallbacks?

4. **Is scope defined?** (0-2 points)
   - In scope vs out of scope?
   - Boundaries clear?

5. **Are requirements specific?** (0-2 points)
   - Enough detail to generate code?
   - Ambiguities resolved?

**Total = clarity_score (1-10)**

---

## 📝 Persistence: 9.3KB Context Per Turn

**Every Turn Includes:**
```
ANALYZE_PROMPT (~9.3KB)
└─ Schema constraints
└─ Enum values
└─ Required fields
└─ Component ID rules

+

CLARIFY_PROMPTS (~2KB)
└─ Instructions for asking questions
└─ What to evaluate
└─ When to mark ready

+

User context (~0.5KB)
└─ Last 5 user messages

= ~11-13KB per turn
```

**Why:** LLM doesn't "forget" schema constraints across turns

---

## 🔍 Example: 4-Turn Clarification

```
TURN 1:
User: "I need a login flow"
Score: 5 (vague)
LLM: "What are the main steps?"

TURN 2:
User: "Email, password, 2FA, dashboard redirect"
Score: 6 (components emerging)
LLM: "How is 2FA implemented?"

TURN 3:
User: "SMS OTP from Twilio, verify in backend"
Score: 7 (mostly clear)
LLM: "What happens on failed verification?"

TURN 4:
User: "Show error, log attempt, lock after 3 fails"
Score: 8 (READY!) ✅
LLM: "I have enough. Generating code..."

Result:
  clarity_scores: [5, 6, 7, 8]
  llm_ready: True → Code generation begins
```

---

## ⚡ Common Issues & Fixes

### **Issue: Loop Never Exits**
**Cause:** clarity_score stays < 8
**Fix:** Add max question limit
```python
if question_count >= 10:
    return {"llm_ready": True, ...}
```

### **Issue: Score Doesn't Increase**
**Cause:** User responses don't add clarity
**Fix:** LLM should ask more specific questions

### **Issue: Too Many Turns**
**Cause:** Schema too complex
**Fix:** Simplify requirements gathering or set lower threshold (7 instead of 8)

---

## 📊 Typical Metrics

```
Average Turns: 3-4
Average Final Score: 8-9
Fastest: 2 turns (if initial clarity high)
Slowest: 7+ turns (complex systems)

Token Cost per Turn: ~11,000 tokens
Multi-turn cost: 4 turns = ~44,000 tokens
```

---

## 🎓 Implementation Reference

**File:** `backend/app/utils/diagram_wizard/nodes.py`
**Function:** `clarify_prompt` (lines 278-449)
**Key Decision:** Line 385 - `if ready or design_summary.startswith("READY:"):`

**Routing:** `backend/app/utils/diagram_wizard/langgraph_builder.py`
**Function:** `route_after_clarification` (lines 21-31)

---

## 🚀 How to Modify

### **Change Exit Threshold (from 8 to 7)**
```python
# In CLARIFY_PROMPTS.md, change:
# FROM: "Mark ready=true when clarity_score >= 8"
# TO:   "Mark ready=true when clarity_score >= 7"
```

### **Add Maximum Questions Limit**
```python
# At start of clarify_prompt function:
if question_count >= 10:
    return {"llm_ready": True, "error_message": "Max questions reached"}
```

### **Disable Persistent Schema (Save Tokens)**
```python
# Remove ANALYZE_PROMPT from clarify_prompt:
# FROM: prompt_template = f"{analyze_prompt}\n...\n{clarify_prompt}"
# TO:   prompt_template = clarify_prompt_template
```

---

## ✨ Key Takeaways

1. **Clarity Score = Progress** - Shows understanding at each turn
2. **Accumulation** - clarity_scores list grows: [5,6,7,8]
3. **LLM Decides** - AI determines when ready (score ≥ 8)
4. **Binary Signal** - llm_ready boolean controls loop exit/continuation
5. **Persistent Context** - 9.3KB schema sent every turn for consistency
6. **Typical Flow** - 4 turns, increasing clarity, then exit with full state

---

**Next Steps:**
- Read `CLARIFICATION_LOGIC_EXPLAINED.md` for detailed explanation
- See `CLARITY_FLOW_DIAGRAM.md` for visual flows
- Check `nodes.py:278-449` for actual implementation

