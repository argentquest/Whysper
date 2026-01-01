# Clarification Phase Logic: How Clarity Scores Drive System Progression

**Document Purpose:** Explain how the clarity score (1-10) determines when the clarification loop exits and proceeds to code generation
**Reference:** nodes.py - clarify_prompt function (lines 278-449)
**Key Concept:** Multi-turn iterative refinement with AI-determined readiness

---

## 📋 Overview: The Clarification Loop

The clarification phase is designed to iteratively ask questions and refine the user's diagram requirements until the system has sufficient clarity to proceed with code generation.

**Core Logic:**
```
┌──────────────────────────────────────────────────┐
│         USER PROVIDES INITIAL PROMPT             │
└────────────┬─────────────────────────────────────┘
             │
             ▼
    ┌─────────────────────┐
    │ ANALYZE_REQUEST     │ (Score 1-10)
    └────────┬────────────┘
             │
             ▼
    ┌──────────────────────────────────────────────┐
    │     CLARIFICATION LOOP (Multi-turn)          │
    │  ┌─────────────────────────────────────┐    │
    │  │ TURN 1:                             │    │
    │  │ • Ask clarifying question           │    │
    │  │ • AI scores clarity (1-10)          │    │
    │  │ • Update JSON schema                │    │
    │  │ • clarity_score < 8? → Loop         │    │
    │  └─────────────────────────────────────┘    │
    │  ┌─────────────────────────────────────┐    │
    │  │ TURN 2, 3, N...                    │    │
    │  │ • Ask follow-up questions           │    │
    │  │ • Accumulate clarity_scores list    │    │
    │  │ • Keep refining JSON                │    │
    │  │ • clarity_score >= 8? → Exit Loop  │    │
    │  └─────────────────────────────────────┘    │
    └────────────┬─────────────────────────────────┘
                 │ llm_ready = True
                 ▼
    ┌────────────────────────────────────────┐
    │ DETERMINE_DIAGRAM_TYPE                 │
    └────────────────────────────────────────┘
```

---

## 🔄 THE CLARIFICATION LOOP: Step-by-Step

### **Step 1: Initialize Loop Variables** (Lines 303-305)
```python
clarification_history = state.get("clarification_history", [])
clarity_scores = state.get("clarity_scores", [])
question_count = state.get("question_count", 0)
```

**What happens:**
- `clarification_history`: Growing list of user questions and AI responses
- `clarity_scores`: List tracking clarity improvement over turns [5, 6, 7, 8]
- `question_count`: How many clarification turns have happened

---

### **Step 2: Prepare Persistent Schema Context** (Lines 307-338)
```python
# Combine TWO prompts:
prompt_template = f"""{analyze_prompt}

---

## Clarification Loop Phase

{clarify_prompt_template}

### Current Clarification Turn
Continue refining the JSON representation based on the user's responses."""
```

**Why this matters:**
- **ANALYZE_PROMPT** (~9.3KB): Contains schema constraints, enum values, required fields
- **CLARIFY_PROMPTS** (~2KB): Specific instructions for asking clarifying questions
- **Combined Size:** ~11-13KB per turn

**Design Intent:**
- LLM remembers the schema throughout all turns (persistent context)
- Prevents LLM from "forgetting" what fields are required or what enums are valid
- Trade-off: Higher token cost per turn, but better consistency

---

### **Step 3: Build User Context** (Lines 340-352)
```python
# Get only USER messages (last 5)
user_messages = [
    msg for msg in clarification_history[-10:]
    if msg.get('role') == 'user'
]
user_content = "\n".join([
    f"User: {msg['content']}"
    for msg in user_messages[-5:]
])
```

**Logic:**
- Look back 10 messages in history
- Filter to only MESSAGES FROM USER (exclude AI questions)
- Take last 5 user messages for context
- Join them with "User: " prefix

**Why:**
- Prevents feedback loops (AI reading its own previous questions)
- Provides recent context without overwhelming the LLM
- Last 5 user messages = ~0.5-2KB of actual user input

---

### **Step 4: Call LLM for Clarification** (Lines 358-362)
```python
logger.info(f"🤖 Making LLM call for clarification - attempt {question_count + 1}")
ai_response_str = await _call_llm(
    prompt_template,      # 11-13KB schema + clarification instruction
    user_content,         # 0.5-2KB user messages
    session_id
)
```

**LLM Input Structure:**
```
System Prompt:
├── ANALYZE_PROMPT (schema constraints)
├── CLARIFY_PROMPTS (clarification instructions)
└── Instructions for this turn

User Message:
└── Last 5 user responses
```

**Expected LLM Output (JSON):**
```json
{
    "question": "What are the main components in your system?",
    "clarity_score": 6,
    "ready": false,
    "json_representation": {
        "components": [...],
        "connections": [...]
    },
    "design_summary": ""
}
```

---

### **Step 5: Parse and Check Clarity Score** (Lines 364-409)

#### **Option A: LLM Says "Ready" (ready=true OR clarity_score ≥ 8)**

```python
if ready or design_summary.startswith("READY:"):
    # EXIT THE LOOP
    updated_clarity_scores = clarity_scores + [clarity_score]

    return {
        "llm_ready": True,                    # ← Signal to exit clarification
        "final_design_summary": summary,
        "json_representation": json_representation,
        "clarity_scores": updated_clarity_scores,  # [5, 6, 7, 8]
        "current_state": SessionState.GENERATING
    }
```

**What triggers exit:**
- `ready = true` in JSON (LLM explicitly says ready)
- `design_summary.startswith("READY:")` (fallback string parsing)
- Implicit: clarity_score ≥ 8 (LLM's own readiness threshold)

**State updated:**
- `llm_ready = True` ← This is the signal!
- `clarity_scores` list complete
- `current_state = GENERATING` (next phase)

**SSE Callback sent to frontend:**
```json
{
    "status": "ready_for_code_generation",
    "message": "✅ AI has sufficient information (clarity: 8/10). Proceeding to code generation.",
    "clarity_score": 8,
    "clarity_scores": [5, 6, 7, 8],
    "json_representation": {...},
    "message_type": "success"
}
```

---

#### **Option B: LLM Wants More Clarification (ready=false OR clarity_score < 8)**

```python
else:
    # STAY IN LOOP
    updated_history = clarification_history.copy()
    updated_history.append({"role": "assistant", "content": question})

    updated_clarity_scores = clarity_scores + [clarity_score]

    return {
        "llm_ready": False,                   # ← Stay in loop
        "clarification_history": updated_history,
        "clarity_scores": updated_clarity_scores,  # [5, 6]
        "question_count": question_count + 1,
        "current_state": SessionState.CLARIFYING
    }
```

**What triggers loop:**
- `ready = false` in JSON
- clarity_score < 8 (not ready yet)

**State updated:**
- `llm_ready = False` ← Signal to stay in loop
- `clarification_history` grows (user question + AI response)
- `clarity_scores` accumulates [5, 6, 7, ...]
- `question_count` incremented
- `current_state = CLARIFYING` (stay in this phase)

**SSE Callback sent to frontend:**
```json
{
    "status": "clarifying",
    "question": "What are the main components?",
    "clarity_score": 6,
    "json_representation": {...},
    "message_type": "clarification"
}
```

---

## 📊 Example: Multi-Turn Clarification Flow

### **Turn 1: Initial Analysis**
```
User Input: "I need a flowchart for user login"

AI Response:
{
    "clarity_score": 5,
    "ready": false,
    "question": "What are the main steps involved in the login process?",
    "design_summary": ""
}

State Update:
- clarity_scores: [5]
- question_count: 1
- llm_ready: false → LOOP
```

**Frontend sees:** Question asking about login steps

---

### **Turn 2: User Clarifies**
```
User Input: "User enters email, system validates, sends OTP, user verifies"

AI Response:
{
    "clarity_score": 6,
    "ready": false,
    "question": "How does the system validate the email format?",
    "json_representation": {
        "components": [
            {"id": "user", "type": "actor"},
            {"id": "email_validator", "type": "service"}
        ],
        "connections": [
            {"from": "user", "to": "email_validator"}
        ]
    }
}

State Update:
- clarity_scores: [5, 6]
- question_count: 2
- llm_ready: false → LOOP
```

**Frontend sees:** Question about email validation + updated JSON

---

### **Turn 3: More Details**
```
User Input: "Regex validation on client side, email service check on backend"

AI Response:
{
    "clarity_score": 7,
    "ready": false,
    "question": "What happens if validation fails?",
    "json_representation": {
        "components": [
            {"id": "user", ...},
            {"id": "email_validator", ...},
            {"id": "email_service", ...}
        ],
        ...
    }
}

State Update:
- clarity_scores: [5, 6, 7]
- question_count: 3
- llm_ready: false → LOOP
```

**Frontend sees:** Question about error handling

---

### **Turn 4: Final Clarification**
```
User Input: "Show error message to user, log to monitoring system"

AI Response:
{
    "clarity_score": 8,
    "ready": true,
    "design_summary": "READY: User login flow with email validation and error handling",
    "json_representation": {
        "components": [
            {"id": "user", "type": "actor"},
            {"id": "email_validator", "type": "service"},
            {"id": "email_service", "type": "external"},
            {"id": "monitoring", "type": "service"}
        ],
        "connections": [...],
        "metadata": {
            "description": "Complete user login architecture",
            "flow": "Email validation → OTP → Verification"
        }
    }
}

State Update:
- clarity_scores: [5, 6, 7, 8]
- question_count: 4
- llm_ready: true ✅ EXIT LOOP
- final_design_summary: "User login flow with email validation..."
```

**Frontend sees:** "✅ Ready! Proceeding to code generation"
**Next Phase:** Determine diagram type → Generate code

---

## 🎯 The Clarity Score: What It Means

### **Clarity Score Scale (1-10)**

| Score | Meaning | AI Action |
|-------|---------|-----------|
| 1-3 | Very unclear | Ask very specific foundational questions |
| 4-5 | Partially clear | Ask about key components/flows |
| 6-7 | Mostly clear | Ask about edge cases/details |
| 8-10 | Clear enough | Ready to generate code |

### **How LLM Determines Score**

LLM evaluates:
- ✅ Are main components identified?
- ✅ Are relationships between components clear?
- ✅ Are error cases mentioned?
- ✅ Is scope well-defined?
- ✅ Are requirements specific enough?

---

## 🔀 State Machine: Clarification Phase Routing

### **In langgraph_builder.py**

```python
workflow.add_conditional_edges(
    "clarify_prompt",
    route_after_clarification,  # Function that checks llm_ready
    {"generate_code": "determine_diagram_type", END: END}
)
```

### **route_after_clarification Logic**

```python
def route_after_clarification(state: GraphState) -> str:
    if state.get("llm_ready", False):
        return "generate_code"  # Actually routes to determine_diagram_type
    else:
        return END  # Pause and wait
```

### **What Happens at Each Return Value**

**If `llm_ready = True`:**
- Route to `determine_diagram_type` node
- Use `final_design_summary` and `json_representation`
- System proceeds to code generation
- Clarification loop is COMPLETE

**If `llm_ready = False` (returns END):**
- Graph pauses
- Frontend receives the clarification question
- User responds
- API submits response (POST /diagram/clarify)
- Graph resumes at `clarify_prompt` node
- Next clarification turn begins

---

## 💾 State Accumulation Over Turns

### **After Turn 1:**
```python
state = {
    "clarification_history": [
        {"role": "user", "content": "I need a flowchart for user login"},
        {"role": "assistant", "content": "What are the main steps?"}
    ],
    "clarity_scores": [5],
    "question_count": 1,
    "llm_ready": False,
    "json_representation": {}
}
```

### **After Turn 2:**
```python
state = {
    "clarification_history": [
        {"role": "user", "content": "I need a flowchart for user login"},
        {"role": "assistant", "content": "What are the main steps?"},
        {"role": "user", "content": "User enters email, validates..."},
        {"role": "assistant", "content": "How does the system validate email?"}
    ],
    "clarity_scores": [5, 6],
    "question_count": 2,
    "llm_ready": False,
    "json_representation": {
        "components": [{"id": "user", ...}, ...],
        "connections": [...]
    }
}
```

### **After Turn 4 (Exit):**
```python
state = {
    "clarification_history": [...4 turns...],
    "clarity_scores": [5, 6, 7, 8],
    "question_count": 4,
    "llm_ready": True,  ← EXIT SIGNAL
    "final_design_summary": "User login flow with...",
    "json_representation": {
        "components": [...complete...],
        "connections": [...complete...],
        "metadata": {...}
    },
    "current_state": SessionState.GENERATING
}
```

---

## 🚦 Key Decision Points

### **Decision #1: Ready to Exit Loop?**
```
LLM evaluates based on:
├── ready field = true? → EXIT
├── design_summary starts with "READY:"? → EXIT
├── clarity_score >= 8? → EXIT (implicit)
└── All else? → CONTINUE LOOP
```

### **Decision #2: What to Ask Next?**
```
LLM decides based on:
├── Missing components? → "What are the main components?"
├── Unclear relationships? → "How do X and Y interact?"
├── No error handling? → "What happens if X fails?"
├── Insufficient scope? → "What are the boundaries?"
└── All covered? → "I think I understand. Shall I generate code?"
```

### **Decision #3: How to Score Clarity?**
```
LLM assigns score based on:
├── Component identification: 1-2 points
├── Relationship clarity: 1-2 points
├── Flow understanding: 1-2 points
├── Error handling: 1-2 points
├── Scope definition: 1-2 points
└── Total: 1-10 scale
```

---

## 📱 Frontend Integration: SSE Updates

### **Turn N - Clarification Question**
```json
{
    "status": "clarifying",
    "question": "What are the main components in your system?",
    "clarity_score": 6,
    "clarity_scores": [5, 6],
    "json_representation": {...},
    "message_type": "clarification"
}
```

**Frontend Action:** Show question to user, wait for response

---

### **Turn N+1 - Ready Signal**
```json
{
    "status": "ready_for_code_generation",
    "message": "✅ AI has sufficient information (clarity: 8/10). Proceeding to code generation.",
    "clarity_score": 8,
    "clarity_scores": [5, 6, 7, 8],
    "json_representation": {...complete...},
    "message_type": "success"
}
```

**Frontend Action:** Show progress message, transition to code generation phase

---

## 🔍 Edge Cases & Special Handling

### **Edge Case 1: User Provides Complete Info on First Turn**
```python
# If initial analysis already gives clarity_score >= 8
if clarity_score >= 8 and ready:
    # Might skip clarification entirely!
    return {"llm_ready": True, ...}
```

---

### **Edge Case 2: No Clarity After Multiple Turns**
```python
# Current code doesn't enforce max questions
# Could theoretically loop forever
# But refinement_attempt should be adapted here too
```

---

### **Edge Case 3: User Confirms Ready Manually**
```python
if (state.get("llm_ready", False) and
    state.get("final_design_summary") and
    state.get("user_confirmed_ready", False)):  # ← Manual confirmation
    return {"llm_ready": True, ...}
```

**Allows:** User to skip remaining clarification if they choose

---

## ⚡ Performance Characteristics

### **Token Consumption Per Turn**
```
ANALYZE_PROMPT:      ~9,300 tokens (~9.3KB)
CLARIFY_PROMPTS:     ~2,000 tokens (~2KB)
User context (5):    ~400 tokens (~0.5KB)
LLM response:        ~200 tokens (~0.2KB)
─────────────────────────────────────
Total per turn:      ~11,900 tokens (~11KB)

Multiple turns cost:
- 2 turns:  ~24K tokens (still reasonable)
- 4 turns:  ~48K tokens (moderate cost)
- 10 turns: ~120K tokens (expensive)
```

### **Trade-off**
- **Pro:** Persistent schema context ensures consistency
- **Con:** High token cost per turn (9.3KB overhead)
- **Mitigation:** Most diagrams settle at 2-4 turns

---

## 📋 Summary: How Clarity Drives Progression

| Aspect | Details |
|--------|---------|
| **Clarity Score** | 1-10 scale, LLM-determined per turn |
| **Exit Condition** | clarity_score ≥ 8 OR ready=true OR "READY:" prefix |
| **Loop Signal** | `llm_ready` boolean in state |
| **Accumulation** | `clarity_scores` list tracks progression |
| **Context Size** | 11-13KB per turn (schema + prompts) |
| **Loop Exit** | Sets llm_ready=True, triggers route_after_clarification |
| **Next Phase** | Determine diagram type, then generate code |

---

## 🎓 Developer Notes

### **To Add Timeout Limit**
```python
# Add at start of clarify_prompt:
if question_count >= 10:  # Max 10 questions
    return {
        "llm_ready": True,
        "final_design_summary": "Timeout: Using gathered information",
        "error_message": "Clarification timeout reached"
    }
```

### **To Change Clarity Threshold**
```python
# Current: >= 8 (in LLM prompt)
# Change in CLARIFY_PROMPTS.md:
# "Mark ready=true when clarity_score >= 7"
```

### **To Disable Persistent Context**
```python
# Remove ANALYZE_PROMPT combination:
prompt_template = clarify_prompt_template  # Just clarify, no schema
# Pro: Fewer tokens
# Con: LLM might "forget" schema constraints
```

---

*End of Clarification Logic Explanation*

