# Clarity Score Flow Diagram: Visual Guide to Clarification Phase

---

## 🎯 High-Level Flow: Clarity Score Drives Everything

```
┌─────────────────────────────────────────────────────────────────┐
│                   CLARIFICATION PHASE                           │
│                   (Multi-Turn Loop)                             │
└─────────────────────────────────────────────────────────────────┘

TURN 1: Initial Clarification
┌──────────────────────────────────────┐
│ User: "I need a user login diagram"  │
└──────────────────────────┬───────────┘
                           │
                           ▼
            ┌──────────────────────────┐
            │  LLM Analyzes & Scores   │
            │  Input: User message     │
            │  + Schema (9.3KB)        │
            └───────────┬──────────────┘
                        │
                        ▼
            ┌──────────────────────────┐
            │  Clarity Score: 5/10     │
            │  ready: false            │
            │  Question: "What are     │
            │  the main steps?"        │
            └───────────┬──────────────┘
                        │
                        ▼
            ┌──────────────────────────┐
            │  llm_ready = FALSE       │
            │  → CONTINUE LOOP         │
            │  → Send question to user │
            └──────────────────────────┘
                        │
              ┌─────────┴──────────┐
              │                    │
        Frontend              User responds
        Receives              with more info
        Question                    │
                                    │
                                    ▼
TURN 2: User Provides More Details
┌──────────────────────────────────────┐
│ User: "Steps are: email, validate,   │
│  OTP, verify, redirect to dashboard" │
└──────────────────────────┬───────────┘
                           │
                           ▼
            ┌──────────────────────────┐
            │  LLM Analyzes & Scores   │
            │  Input: All prior + new  │
            │  + Schema (9.3KB)        │
            └───────────┬──────────────┘
                        │
                        ▼
            ┌──────────────────────────┐
            │  Clarity Score: 6/10     │
            │  ready: false            │
            │  Question: "How does     │
            │  email validation work?" │
            └───────────┬──────────────┘
                        │
                        ▼
            ┌──────────────────────────┐
            │  llm_ready = FALSE       │
            │  → CONTINUE LOOP         │
            │  clarity_scores = [5,6]  │
            └──────────────────────────┘
                        │
              ┌─────────┴──────────┐
              │                    │
        Frontend              User responds
        Receives              with more info
        Question                    │
                                    │
                                    ▼
TURN 3: More Detail
┌──────────────────────────────────────┐
│ User: "Regex on client, service API  │
│  check on backend, error logging"    │
└──────────────────────────┬───────────┘
                           │
                           ▼
            ┌──────────────────────────┐
            │  LLM Analyzes & Scores   │
            │  clarity_score: 7/10     │
            │  ready: false            │
            │  json_representation     │
            │  updated with components │
            └───────────┬──────────────┘
                        │
                        ▼
            ┌──────────────────────────┐
            │  llm_ready = FALSE       │
            │  → CONTINUE LOOP         │
            │  clarity_scores = [5,6,7]│
            └──────────────────────────┘
                        │
                        ▼
TURN 4: Final Details
┌──────────────────────────────────────┐
│ User: "Send OTP via email service,   │
│  store attempt in database"          │
└──────────────────────────┬───────────┘
                           │
                           ▼
            ┌──────────────────────────┐
            │  LLM Analyzes & Scores   │
            │  Clarity Score: 8/10 ✅  │
            │  ready: TRUE ✅          │
            │  → ALL REQUIREMENTS MET  │
            └───────────┬──────────────┘
                        │
                        ▼
        ┌──────────────────────────────┐
        │  llm_ready = TRUE ✅         │
        │  → EXIT CLARIFICATION LOOP   │
        │  → clarity_scores=[5,6,7,8]  │
        │  → final_design_summary set  │
        │  → json_representation FINAL │
        └──────────────────────────────┘
                        │
                        ▼
        ┌──────────────────────────────┐
        │ route_after_clarification()  │
        │ Sees llm_ready=True          │
        │ Routes to:                   │
        │ "determine_diagram_type"     │
        └──────────────────────────────┘
                        │
                        ▼
        ┌──────────────────────────────┐
        │ NEXT PHASE: Code Generation  │
        │ Diagram Type → Generate Code │
        │ → Validate → Render          │
        └──────────────────────────────┘
```

---

## 📊 State Machine: Detailed Transitions

```
START: analyze_request
│
├─ Output: initial json_representation
│          assessment_score (1-10)
│
└─→ CLARIFICATION_LOOP (llm_ready = false)
    │
    ├─ LLM analyzes user messages
    ├─ Generates: question, clarity_score (1-10), json_representation
    │
    ├─ Decision Point: Is clarity_score >= 8?
    │  │
    │  ├─ NO (clarity < 8):
    │  │  │
    │  │  ├─ Send question to frontend
    │  │  ├─ Append to clarification_history
    │  │  ├─ Add score to clarity_scores list
    │  │  ├─ Increment question_count
    │  │  ├─ Set: llm_ready = FALSE
    │  │  │
    │  │  └─ ROUTE: return END
    │  │     └─→ Graph pauses
    │  │         Wait for user response
    │  │         └─→ User responds via API
    │  │             Loop repeats at clarify_prompt node
    │  │
    │  └─ YES (clarity >= 8):
    │     │
    │     ├─ Set: llm_ready = TRUE ✅
    │     ├─ Extract: final_design_summary
    │     ├─ Store: final json_representation
    │     ├─ Complete: clarity_scores list
    │     │
    │     └─ ROUTE: return "generate_code"
    │        └─→ Routing maps "generate_code" → determine_diagram_type
    │            │
    │            ├─ Analyze final_design_summary
    │            ├─ Score keywords (Mermaid, D2, PlantUML)
    │            ├─ Select best diagram type
    │            │
    │            └─→ generate_code
    │                ├─ Type-specific LLM prompt
    │                ├─ Generate code from json_representation
    │                │
    │                └─→ validate_code
    │                    ├─ Provider validation or fallback
    │                    │
    │                    ├─ If valid:
    │                    │  └─→ render_diagram → SVG → END
    │                    │
    │                    └─ If invalid:
    │                       └─→ refine_code (max 3 attempts)
    │                           └─→ Back to validate
```

---

## 🔢 Clarity Score Progression Chart

```
Clarification Progress Over Time (Typical Scenario)

Score
10  ┤
    ├─  ✅ READY THRESHOLD (8)
 9  ├─  ─┐
    │   │
 8  ├───┘  ← Turn 4: All requirements gathered
    │
 7  ├─ ─┐  ← Turn 3: Error handling, flow details
    │   │
 6  ├───┘  ← Turn 2: Component relationships
    │
 5  ├─ ─┐  ← Turn 1: Initial main steps
    │   │
 4  ├───┘
    │
 3  ├─
    │
 2  ├─
    │
 1  └─────────────────────────────────────
    Turn 1  Turn 2  Turn 3  Turn 4

Key Points:
- Score typically increases each turn (5→6→7→8)
- Sometimes plateaus (6→6) if user response unclear
- Rarely decreases (unless user changes mind)
- Exit happens when hitting threshold (≥8)
```

---

## 🎯 LLM Decision Logic: What Determines the Score?

```
LLM Evaluation Checklist:

Question 1: Are COMPONENTS identified?
├─ "Where's the user validation service?"
├─ "Is there a database?"
└─ Score: +1 to +2

Question 2: Are RELATIONSHIPS clear?
├─ "How does component A connect to B?"
├─ "What's the data flow?"
└─ Score: +1 to +2

Question 3: Is ERROR HANDLING covered?
├─ "What happens if validation fails?"
├─ "How are errors logged?"
└─ Score: +1 to +2

Question 4: Is SCOPE defined?
├─ "What's in scope vs out?"
├─ "Are there third-party services?"
└─ Score: +1 to +2

Question 5: Are REQUIREMENTS specific?
├─ "How many concurrent users?"
├─ "What's the performance requirement?"
└─ Score: +1 to +2

Total Score: Sum of all (1-10)
│
├─ 1-3: "Need to understand basics"
├─ 4-5: "Have main concepts, need details"
├─ 6-7: "Mostly clear, need edge cases"
├─ 8-9: "Clear enough to proceed"
└─ 10: "Perfect clarity"

Decision:
├─ If score < 8: Ask follow-up question about gap
└─ If score >= 8: "I have enough info, ready to generate code"
```

---

## 💬 Example: Clarity Score Justification

```
TURN 1:
User: "I need a login diagram"

LLM Analysis:
├─ Components? Very vague (just "login")           → 0/2
├─ Relationships? Not mentioned                    → 0/2
├─ Error handling? Not mentioned                   → 0/2
├─ Scope? Not clear                                → 1/2
├─ Specificity? Low                                → 1/2
├─ TOTAL: 2/10
└─ Decision: "I need much more info. What are the main steps?"

TURN 2:
User: "Email entry, validation, OTP sending, OTP verification, redirect"

LLM Analysis:
├─ Components? Yes: email, validator, OTP service, auth   → 2/2
├─ Relationships? Partial: main flow clear               → 1/2
├─ Error handling? Not mentioned                          → 0/2
├─ Scope? Frontend/backend implied                        → 2/2
├─ Specificity? Good for main flow                        → 1/2
├─ TOTAL: 6/10
└─ Decision: "I see the main flow. How does validation work? What about errors?"

TURN 3:
User: "Regex on frontend, backend service call, logs on failure, retry logic"

LLM Analysis:
├─ Components? Yes: client validator, API, DB, logger    → 2/2
├─ Relationships? Clear: validator→API→DB, error→logger  → 2/2
├─ Error handling? Yes: logging, retry mentioned         → 2/2
├─ Scope? Well-defined frontend/backend boundary         → 2/2
├─ Specificity? Very specific                            → 1/2
├─ TOTAL: 9/10
└─ Decision: "I have enough! Ready to generate the diagram"
```

---

## 🔄 State Variable Changes Per Turn

```
TURN 1:
Before:
  clarification_history: []
  clarity_scores: []
  question_count: 0
  llm_ready: undefined

After:
  clarification_history: [
    {role: "user", content: "I need login diagram"},
    {role: "assistant", content: "What are main steps?"}
  ]
  clarity_scores: [5]
  question_count: 1
  llm_ready: FALSE
  ┌─ Routes to: END (pause)

TURN 2:
Before:
  clarification_history: [previous turn x2]
  clarity_scores: [5]
  question_count: 1
  llm_ready: FALSE

After:
  clarification_history: [
    {role: "user", content: "I need login diagram"},
    {role: "assistant", content: "What are main steps?"},
    {role: "user", content: "Email, validate, OTP, verify, redirect"},
    {role: "assistant", content: "How does validation work?"}
  ]
  clarity_scores: [5, 6]
  question_count: 2
  llm_ready: FALSE
  ┌─ Routes to: END (pause)

TURN 3:
Before:
  clarity_scores: [5, 6]
  question_count: 2
  llm_ready: FALSE

After:
  clarity_scores: [5, 6, 7]
  question_count: 3
  llm_ready: FALSE
  ┌─ Routes to: END (pause)

TURN 4:
Before:
  clarity_scores: [5, 6, 7]
  question_count: 3
  llm_ready: FALSE

After:
  clarity_scores: [5, 6, 7, 8]
  question_count: 4
  llm_ready: TRUE ✅
  final_design_summary: "Complete login architecture"
  ┌─ Routes to: "determine_diagram_type"
```

---

## 🚦 Routing Decision Tree

```
route_after_clarification(state):
│
├─ Is state["llm_ready"] == True?
│  │
│  ├─ YES:
│  │  └─ Return "generate_code"
│  │     (Actually routes to determine_diagram_type)
│  │     └─→ Code generation phase begins
│  │
│  └─ NO:
│     └─ Return END
│        └─→ Graph pauses
│           └─→ Wait for next user input via API
│              └─→ Resume clarify_prompt node
```

---

## 📈 Typical Clarification Progression

```
Most Common Pattern:

Turn 1: clarity=5  (Initial understanding)
Turn 2: clarity=6  (+1 increment)
Turn 3: clarity=7  (+1 increment)
Turn 4: clarity=8  (+1 increment) → EXIT ✅

Average: 4 questions, 4 clarification turns

Outliers:
- Fast learner: 2-3 turns (initial clarity high)
- Complex system: 5-6 turns (many follow-ups)
- Unclear user: 7+ turns (might never reach 8)
```

---

## ⚡ Key Points Summary

| Aspect | Details |
|--------|---------|
| **What Drives Progression** | Clarity Score (1-10) |
| **Exit Condition** | clarity_score ≥ 8 AND ready=true |
| **Loop Control Signal** | `llm_ready` boolean |
| **State Growth** | Accumulates history + scores |
| **Typical Turns** | 3-5 turns to reach clarity=8 |
| **Context Retention** | 9.3KB schema sent every turn |
| **Frontend Updates** | Question + score via SSE |
| **Next Phase Trigger** | llm_ready=True → route_after_clarification |

---

## 🎓 For Implementation

**To understand the flow:**
1. Read clarify_prompt function (nodes.py:278-449)
2. Look at clarity_score evaluation (line 368)
3. Check exit condition (line 385: `if ready or ...`)
4. See routing logic (langgraph_builder.py:80-84)

**To modify behavior:**
- Change clarity threshold: Edit clarify_prompt evaluation (line 385)
- Add max questions: Add check at start of function
- Change scoring: Modify CLARIFY_PROMPTS.md instructions
- Add timeout: Check elapsed time in clarify_prompt

---

*End of Clarity Flow Diagram*

