# Mermaid System - Visual Guide

This document provides visual flowcharts and diagrams to help understand how the Mermaid validation and retry system works.

---

## Table of Contents

1. [High-Level Overview](#high-level-overview)
2. [Detailed Validation Flow](#detailed-validation-flow)
3. [AI Retry Flow](#ai-retry-flow)
4. [Error Handling Flow](#error-handling-flow)
5. [Frontend Tester Flow](#frontend-tester-flow)
6. [System Architecture](#system-architecture)

---

## High-Level Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                     MERMAID DIAGRAM SYSTEM                      │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  ┌──────────────┐      ┌──────────────┐      ┌──────────────┐ │
│  │   Frontend   │      │   Backend    │      │  Mermaid CLI │ │
│  │              │      │              │      │    (mmdc)    │ │
│  ├──────────────┤      ├──────────────┤      ├──────────────┤ │
│  │              │      │              │      │              │ │
│  │ Chat View    │◄────►│ Conversation │◄────►│ Validation   │ │
│  │              │      │  Service     │      │              │ │
│  │              │      │              │      │              │ │
│  ├──────────────┤      ├──────────────┤      ├──────────────┤ │
│  │              │      │              │      │              │ │
│  │ Mermaid      │◄────►│ Mermaid      │◄────►│ Rendering    │ │
│  │ Tester       │      │  Service     │      │              │ │
│  │              │      │              │      │              │ │
│  └──────────────┘      └──────────────┘      └──────────────┘ │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘

                    ▼                  ▼                  ▼

              User Interface    REST API + Logic    CLI Validation
```

---

## Detailed Validation Flow

### Step 1: User Asks Question

```
┌──────────────────────────────────────────────────────────────┐
│  User in Chat                                                │
├──────────────────────────────────────────────────────────────┤
│                                                              │
│  💬 "Create a flowchart showing the user login process"     │
│                                                              │
│  [Send] ────────────────────────────────────────────────────►│
│                                                              │
└──────────────────────────────────────────────────────────────┘
                           │
                           ▼
┌──────────────────────────────────────────────────────────────┐
│  Frontend: InputPanel.tsx                                    │
├──────────────────────────────────────────────────────────────┤
│                                                              │
│  POST /api/v1/chat/question                                 │
│  {                                                           │
│    "question": "Create a flowchart...",                      │
│    "conversation_id": "abc123",                              │
│    ...                                                       │
│  }                                                           │
│                                                              │
└──────────────────────────────────────────────────────────────┘
                           │
                           ▼
┌──────────────────────────────────────────────────────────────┐
│  Backend: chat.py (API endpoint)                             │
├──────────────────────────────────────────────────────────────┤
│                                                              │
│  session.send_question(question, ...)                       │
│                                                              │
└──────────────────────────────────────────────────────────────┘
```

### Step 2: AI Generates Response

```
┌──────────────────────────────────────────────────────────────┐
│  Backend: conversation_service.py                            │
│  send_question()                                             │
├──────────────────────────────────────────────────────────────┤
│                                                              │
│  1. ai_processor.process_question()                          │
│     ↓                                                        │
│  2. Receive AI response                                      │
│     ↓                                                        │
│  3. Extract response text                                    │
│                                                              │
└──────────────────────────────────────────────────────────────┘
                           │
                           ▼
┌──────────────────────────────────────────────────────────────┐
│  AI Response Text                                            │
├──────────────────────────────────────────────────────────────┤
│                                                              │
│  Here's a flowchart for the login process:                  │
│                                                              │
│  ```mermaid                                                  │
│  flowchart TD                                                │
│      A[User Opens App] --> B{Logged In?}                     │
│      B -->|Yes| C[Show Dashboard]                            │
│      B -->|No| D[Show Login Form]                            │
│      D --> E[Enter Credentials]                              │
│      E --> F{Valid?}                                         │
│      F -->|Yes| C                                            │
│      F -->|No| D                                             │
│  ```                                                         │
│                                                              │
└──────────────────────────────────────────────────────────────┘
```

### Step 3: Automatic Validation

```
┌──────────────────────────────────────────────────────────────┐
│  Backend: conversation_service.py                            │
│  send_question() [continued]                                 │
├──────────────────────────────────────────────────────────────┤
│                                                              │
│  # Auto-validate D2 diagrams                                 │
│  response_text = _validate_and_fix_d2_diagrams(...)          │
│                                                              │
│  # Auto-validate Mermaid diagrams ← YOU ARE HERE            │
│  response_text = _validate_and_fix_mermaid_diagrams(...)     │
│                                                              │
│  # Return to user                                            │
│  return response                                             │
│                                                              │
└──────────────────────────────────────────────────────────────┘
                           │
                           ▼
┌──────────────────────────────────────────────────────────────┐
│  _validate_and_fix_mermaid_diagrams()                        │
├──────────────────────────────────────────────────────────────┤
│                                                              │
│  STEP 1: Extract Mermaid blocks                              │
│  ────────────────────────────────────────────────────────    │
│  pattern = r'```mermaid\s*\n?(.*?)```'                       │
│  matches = re.findall(pattern, response, DOTALL)             │
│                                                              │
│  📊 Found 1 Mermaid diagram(s)                               │
│                                                              │
│  ──────────────────────────────────────────────────────────  │
│                                                              │
│  STEP 2: Validate each diagram                               │
│  ────────────────────────────────────────────────────────    │
│  for diagram in matches:                                     │
│      is_valid, error = service.validate_mermaid_code(code)   │
│                                                              │
│      if not is_valid:                                        │
│          validation_errors.append(error)                     │
│                                                              │
└──────────────────────────────────────────────────────────────┘
                           │
                           ▼
┌──────────────────────────────────────────────────────────────┐
│  mermaid_render_service.py                                   │
│  validate_mermaid_code()                                     │
├──────────────────────────────────────────────────────────────┤
│                                                              │
│  [MERMAID VALIDATE] Starting validation...                   │
│                                                              │
│  is_valid, message = validate_mermaid_with_cli(code)         │
│                                                              │
└──────────────────────────────────────────────────────────────┘
                           │
                           ▼
┌──────────────────────────────────────────────────────────────┐
│  mermaid_cli_validator.py                                    │
│  validate_mermaid_with_cli()                                 │
├──────────────────────────────────────────────────────────────┤
│                                                              │
│  1. Save code to temp file: /tmp/mermaid_xxxxx.mmd           │
│  2. Run: mmdc -i /tmp/mermaid_xxxxx.mmd -o /tmp/out.svg      │
│  3. Check exit code and stderr                               │
│  4. Delete temp files                                        │
│  5. Return (is_valid, message)                               │
│                                                              │
└──────────────────────────────────────────────────────────────┘
                           │
                           ▼
┌──────────────────────────────────────────────────────────────┐
│  Mermaid CLI (mmdc)                                          │
├──────────────────────────────────────────────────────────────┤
│                                                              │
│  $ mmdc -i diagram.mmd -o output.svg                         │
│                                                              │
│  ✅ Exit code: 0 → Valid                                     │
│  ❌ Exit code: 1 → Invalid (stderr has error message)       │
│                                                              │
└──────────────────────────────────────────────────────────────┘
```

---

## AI Retry Flow

```
┌─────────────────────────────────────────────────────────────────┐
│  Validation Result: ❌ INVALID                                  │
│  Error: "Parse error on line 3: unexpected token 'end'"         │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│  _validate_and_fix_mermaid_diagrams() [continued]               │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  STEP 3: Build error summary                                    │
│  ───────────────────────────────────────────────────────────    │
│  error_summary = "\n\n".join(validation_errors)                 │
│                                                                 │
│  🔧 Validation errors found - requesting AI auto-fix            │
│     (attempt 1/5)                                               │
│                                                                 │
│  ─────────────────────────────────────────────────────────────  │
│                                                                 │
│  STEP 4: Create correction prompt                               │
│  ───────────────────────────────────────────────────────────    │
│  correction_prompt = f"""                                       │
│  FIX THESE MERMAID SYNTAX ERRORS:                               │
│                                                                 │
│  {error_summary}                                                │
│                                                                 │
│  RULES:                                                         │
│  - Always start with diagram type                              │
│  - Use proper arrow syntax with spaces: A --> B                 │
│  - Quote labels with special characters                         │
│  - Do NOT use reserved keywords as node IDs                     │
│  - Close all subgraphs with 'end'                               │
│                                                                 │
│  Return ONLY the corrected ```mermaid code block.               │
│  Keep it SIMPLE and COMPLETE.                                   │
│  """                                                            │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│  STEP 5: Send to AI                                             │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  corrected_response = ai_processor.process_question(            │
│      question=correction_prompt,                                │
│      conversation_history=history,                              │
│      model=selected_model,                                      │
│      ...                                                        │
│  )                                                              │
│                                                                 │
│  ✅ Received corrected Mermaid code (234 chars)                │
│     - re-validating...                                          │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│  STEP 6: Re-validate corrected code                             │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  Validation attempt 2/5                                         │
│                                                                 │
│  Extract mermaid blocks from corrected_response                 │
│  Validate each diagram again                                    │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
                    ┌──────────────────┐
                    │  Valid now?      │
                    └─────────┬────────┘
                              │
            ┌─────────────────┼─────────────────┐
            │                 │                 │
           YES                NO                │
            │                 │                 │
            ▼                 ▼                 │
    ┌──────────────┐  ┌──────────────┐         │
    │  ✅ SUCCESS  │  │ More retries?│         │
    │              │  └──────┬───────┘         │
    │ Return fixed │         │                 │
    │   response   │     ┌───┴───┐             │
    └──────────────┘     │       │             │
                        YES      NO             │
                         │       │              │
                         │       ▼              │
                         │  ┌──────────────┐    │
                         │  │ ❌ FAILED    │    │
                         │  │              │    │
                         │  │ Show error   │    │
                         │  │ report       │    │
                         │  └──────────────┘    │
                         │                      │
                         └──────────────────────┘
                              Retry again
                              (max 5 times)
```

---

## Error Handling Flow

### Success Path

```
User Question
     ↓
AI Response (with Mermaid)
     ↓
Extract ```mermaid blocks
     ↓
Validate with mmdc
     ↓
✅ Valid!
     ↓
Return to User
     ↓
Display in Chat
     ↓
🎉 User sees diagram
```

### Auto-Fix Path

```
User Question
     ↓
AI Response (with Mermaid)
     ↓
Extract ```mermaid blocks
     ↓
Validate with mmdc
     ↓
❌ Invalid (missing diagram type)
     ↓
Auto-fix (3 attempts)
     ↓
Add "flowchart TD"
     ↓
Re-validate
     ↓
✅ Valid!
     ↓
Return to User
     ↓
Display in Chat
     ↓
🎉 User sees diagram
(never knew there was an issue)
```

### AI Retry Path

```
User Question
     ↓
AI Response (with Mermaid)
     ↓
Extract ```mermaid blocks
     ↓
Validate with mmdc
     ↓
❌ Invalid (reserved keyword 'end')
     ↓
Auto-fix (3 attempts)
     ↓
❌ Still invalid
     ↓
AI Retry #1
     ↓
"FIX THESE ERRORS: ... 'end' is reserved ..."
     ↓
AI generates new code
     ↓
Re-validate
     ↓
✅ Valid!
     ↓
Return to User
     ↓
Display in Chat
     ↓
🎉 User sees diagram
(maybe noticed a slight delay)
```

### Failure Path

```
User Question
     ↓
AI Response (with Mermaid)
     ↓
Extract ```mermaid blocks
     ↓
Validate with mmdc
     ↓
❌ Invalid (complex nested error)
     ↓
Auto-fix (3 attempts)
     ↓
❌ Still invalid
     ↓
AI Retry #1 → ❌ Still invalid
AI Retry #2 → ❌ Still invalid
AI Retry #3 → ❌ Still invalid
AI Retry #4 → ❌ Still invalid
AI Retry #5 → ❌ Still invalid
     ↓
All retries exhausted
     ↓
Build error report
     ↓
Append to response
     ↓
Return to User
     ↓
Display in Chat
     ↓
⚠️ User sees:
   - AI's attempt
   - Error report
   - Common fixes
   - Suggestions
```

---

## Frontend Tester Flow

```
┌─────────────────────────────────────────────────────────────┐
│  User clicks: More Options (⋮) → Mermaid Tester            │
└─────────────────────────────────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────┐
│  MermaidTesterModal opens                                   │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  ┌────────────────────────┬────────────────────────────┐   │
│  │  Left Panel            │  Right Panel               │   │
│  ├────────────────────────┼────────────────────────────┤   │
│  │                        │                            │   │
│  │  Monaco Editor         │  Test Cases                │   │
│  │  ┌──────────────────┐  │  ┌──────────────────────┐  │   │
│  │  │ flowchart TD     │  │  │ ✅ Valid Flowchart  │  │   │
│  │  │   A --> B        │  │  └──────────────────────┘  │   │
│  │  │   B --> C        │  │  ┌──────────────────────┐  │   │
│  │  └──────────────────┘  │  │ ✅ Valid Sequence   │  │   │
│  │                        │  └──────────────────────┘  │   │
│  │  [Validate Only]       │  ┌──────────────────────┐  │   │
│  │  [Validate & Auto-Fix] │  │ ❌ Missing Type     │  │   │
│  │  [Validate & Render]   │  └──────────────────────┘  │   │
│  │                        │                            │   │
│  │  ┌──────────────────┐  │  Rendered Diagram          │   │
│  │  │ ✅ Valid Syntax! │  │  ┌──────────────────────┐  │   │
│  │  └──────────────────┘  │  │                      │  │   │
│  │                        │  │   [SVG Display]      │  │   │
│  └────────────────────────┴──│                      │──┘   │
│                              └──────────────────────┘      │
└─────────────────────────────────────────────────────────────┘
```

### Tester Action Flow

```
User clicks "Validate & Render"
     ↓
┌─────────────────────────────────────┐
│  Frontend: MermaidTesterModal       │
│  renderMermaid()                    │
├─────────────────────────────────────┤
│                                     │
│  POST /api/v1/mermaid/render        │
│  {                                  │
│    "code": "flowchart TD\n...",     │
│    "return_svg": true,              │
│    "output_format": "svg"           │
│  }                                  │
│                                     │
└─────────────────────────────────────┘
     ↓
┌─────────────────────────────────────┐
│  Backend: mermaid_render.py         │
│  render_mermaid()                   │
├─────────────────────────────────────┤
│                                     │
│  1. Validate code                   │
│  2. Auto-fix if needed              │
│  3. Render to SVG                   │
│  4. Return SVG content              │
│                                     │
└─────────────────────────────────────┘
     ↓
┌─────────────────────────────────────┐
│  Response                           │
├─────────────────────────────────────┤
│                                     │
│  {                                  │
│    "success": true,                 │
│    "svg_content": "<svg>...</svg>", │
│    "metadata": {                    │
│      "render_time": 0.42            │
│    }                                │
│  }                                  │
│                                     │
└─────────────────────────────────────┘
     ↓
┌─────────────────────────────────────┐
│  Frontend: Update UI                │
├─────────────────────────────────────┤
│                                     │
│  setRenderResult(data)              │
│  message.success("Rendered!")       │
│  Display SVG in preview panel       │
│                                     │
└─────────────────────────────────────┘
     ↓
🎉 User sees rendered diagram
```

---

## System Architecture

### Component Diagram

```
┌──────────────────────────────────────────────────────────────────┐
│                         FRONTEND                                 │
├──────────────────────────────────────────────────────────────────┤
│                                                                  │
│  ┌────────────────────────────────────────────────────────────┐ │
│  │  Chat View (ChatView.tsx)                                  │ │
│  │  ┌──────────────────────────────────────────────────────┐  │ │
│  │  │  MermaidDiagram.tsx - Renders mermaid blocks in chat │  │ │
│  │  └──────────────────────────────────────────────────────┘  │ │
│  └────────────────────────────────────────────────────────────┘ │
│                                                                  │
│  ┌────────────────────────────────────────────────────────────┐ │
│  │  Mermaid Tester (MermaidTesterModal.tsx)                   │ │
│  │  ┌──────────────────────────────────────────────────────┐  │ │
│  │  │  MonacoEditor - Code editing                         │  │ │
│  │  │  Test Cases - Pre-loaded examples                    │  │ │
│  │  │  Preview Panel - SVG display                         │  │ │
│  │  └──────────────────────────────────────────────────────┘  │ │
│  └────────────────────────────────────────────────────────────┘ │
│                                                                  │
└──────────────────────────────────────────────────────────────────┘
                              │
                              │ HTTP REST API
                              │
                              ▼
┌──────────────────────────────────────────────────────────────────┐
│                         BACKEND                                  │
├──────────────────────────────────────────────────────────────────┤
│                                                                  │
│  ┌────────────────────────────────────────────────────────────┐ │
│  │  API Layer (FastAPI)                                       │ │
│  │  ┌──────────────────────────────────────────────────────┐  │ │
│  │  │  chat.py - POST /api/v1/chat/question                │  │ │
│  │  │  mermaid_render.py - POST /api/v1/mermaid/render     │  │ │
│  │  │                     POST /api/v1/mermaid/validate    │  │ │
│  │  └──────────────────────────────────────────────────────┘  │ │
│  └────────────────────────────────────────────────────────────┘ │
│                                                                  │
│  ┌────────────────────────────────────────────────────────────┐ │
│  │  Service Layer                                             │ │
│  │  ┌──────────────────────────────────────────────────────┐  │ │
│  │  │  conversation_service.py                             │  │ │
│  │  │    - send_question()                                 │  │ │
│  │  │    - _validate_and_fix_mermaid_diagrams()            │  │ │
│  │  │                                                       │  │ │
│  │  │  mermaid_render_service.py                           │  │ │
│  │  │    - validate_mermaid_code()                         │  │ │
│  │  │    - render_mermaid_diagram()                        │  │ │
│  │  └──────────────────────────────────────────────────────┘  │ │
│  └────────────────────────────────────────────────────────────┘ │
│                                                                  │
│  ┌────────────────────────────────────────────────────────────┐ │
│  │  Validation Layer                                          │ │
│  │  ┌──────────────────────────────────────────────────────┐  │ │
│  │  │  mermaid_cli_validator.py                            │  │ │
│  │  │    - validate_mermaid_with_cli()                     │  │ │
│  │  │    - validate_and_fix_mermaid_with_cli()             │  │ │
│  │  │                                                       │  │ │
│  │  │  mermaid_syntax_fixer.py                             │  │ │
│  │  │    - fix_mermaid_syntax()                            │  │ │
│  │  └──────────────────────────────────────────────────────┘  │ │
│  └────────────────────────────────────────────────────────────┘ │
│                                                                  │
└──────────────────────────────────────────────────────────────────┘
                              │
                              │ Subprocess call
                              │
                              ▼
┌──────────────────────────────────────────────────────────────────┐
│                       MERMAID CLI                                │
├──────────────────────────────────────────────────────────────────┤
│                                                                  │
│  mmdc (Mermaid CLI v11.9.0)                                      │
│                                                                  │
│  $ mmdc -i input.mmd -o output.svg                               │
│                                                                  │
│  - Validates Mermaid syntax                                      │
│  - Renders to SVG/PNG                                            │
│  - Returns exit code and error messages                          │
│                                                                  │
└──────────────────────────────────────────────────────────────────┘
```

---

## Data Flow Diagram

```
┌────────────┐
│    USER    │
└─────┬──────┘
      │ 1. Types question
      ▼
┌────────────────────────────┐
│  Frontend: InputPanel      │
└─────┬──────────────────────┘
      │ 2. POST /chat/question
      ▼
┌────────────────────────────┐
│  Backend: chat.py          │
└─────┬──────────────────────┘
      │ 3. session.send_question()
      ▼
┌────────────────────────────────────────┐
│  conversation_service.py               │
│  ┌──────────────────────────────────┐  │
│  │ 4. ai_processor.process_question │  │
│  └────────────┬─────────────────────┘  │
│               │                        │
│               │ 5. AI generates        │
│               │    response with       │
│               │    ```mermaid block    │
│               ▼                        │
│  ┌──────────────────────────────────┐  │
│  │ 6. _validate_and_fix_mermaid...  │  │
│  └────────────┬─────────────────────┘  │
└───────────────┼────────────────────────┘
                │ 7. Extract mermaid blocks
                ▼
┌────────────────────────────────────────┐
│  mermaid_render_service.py             │
│  ┌──────────────────────────────────┐  │
│  │ 8. validate_mermaid_code()       │  │
│  └────────────┬─────────────────────┘  │
└───────────────┼────────────────────────┘
                │ 9. Validate with CLI
                ▼
┌────────────────────────────────────────┐
│  mermaid_cli_validator.py              │
│  ┌──────────────────────────────────┐  │
│  │ 10. validate_mermaid_with_cli()  │  │
│  └────────────┬─────────────────────┘  │
└───────────────┼────────────────────────┘
                │ 11. subprocess.run(mmdc)
                ▼
┌────────────────────────────────────────┐
│  Mermaid CLI (mmdc)                    │
└────────────┬───────────────────────────┘
             │ 12. Return (valid, error)
             ▼
┌────────────────────────────────────────┐
│  Back to conversation_service.py       │
│  ┌──────────────────────────────────┐  │
│  │ 13. if invalid: retry with AI    │  │
│  │ 14. if valid: return response    │  │
│  └────────────┬─────────────────────┘  │
└───────────────┼────────────────────────┘
                │ 15. Return response
                ▼
┌────────────────────────────────────────┐
│  Backend: chat.py                      │
└────────────┬───────────────────────────┘
             │ 16. HTTP 200 + JSON
             ▼
┌────────────────────────────────────────┐
│  Frontend: ChatView                    │
│  ┌──────────────────────────────────┐  │
│  │ 17. Display response in chat     │  │
│  │ 18. Render mermaid blocks        │  │
│  └──────────────────────────────────┘  │
└────────────┬───────────────────────────┘
             │ 19. User sees diagram
             ▼
┌────────────────────────────────────────┐
│    USER                                │
│  🎉 Sees rendered diagram in chat      │
└────────────────────────────────────────┘
```

---

## Logging Flow

```
┌──────────────────────────────────────────────────────────────┐
│  Log Tags by Component                                       │
├──────────────────────────────────────────────────────────────┤
│                                                              │
│  conversation_service.py:                                    │
│    🔍 [MERMAID PROGRESS] Found X diagram(s) - validating...  │
│    🔧 [MERMAID PROGRESS] Requesting AI auto-fix (attempt X)  │
│    ✅ [MERMAID PROGRESS] All diagrams validated!             │
│    ❌ [MERMAID PROGRESS] Validation failed after X retries   │
│    ⚠️  Corrected response may be TRUNCATED!                  │
│                                                              │
│  mermaid_render_service.py:                                  │
│    [MERMAID VALIDATE] Starting validation...                 │
│    [MERMAID VALIDATE] ✅ Validation successful               │
│    [MERMAID VALIDATE] ❌ Validation failed                   │
│    [MERMAID RENDER] Starting render...                       │
│    [MERMAID RENDER] ✅ Rendered successfully                 │
│                                                              │
│  mermaid_cli_validator.py:                                   │
│    [MERMAID AUTO-FIX] Starting auto-fix (max X attempts)     │
│    [MERMAID AUTO-FIX] Attempt X/Y                            │
│    [MERMAID AUTO-FIX] ✅ Success on attempt X!               │
│    [MERMAID AUTO-FIX] Applied fix: ...                       │
│                                                              │
└──────────────────────────────────────────────────────────────┘

Example Log Sequence (Success):
────────────────────────────────────────────────────────────────

[INFO] 🔍 [MERMAID PROGRESS] Found 1 Mermaid diagram(s) - validating...
[INFO] [MERMAID VALIDATE] Starting validation for 123 character code
[DEBUG] [MERMAID VALIDATE] Code preview: flowchart TD\n    A --> B...
[INFO] [MERMAID VALIDATE] ✅ Validation successful
[INFO] ✅ [MERMAID PROGRESS] All Mermaid diagrams validated successfully!
[INFO] After Mermaid validation/fix: 1234 characters

Example Log Sequence (Auto-Fix):
────────────────────────────────────────────────────────────────

[INFO] 🔍 [MERMAID PROGRESS] Found 1 Mermaid diagram(s) - validating...
[INFO] [MERMAID VALIDATE] Starting validation for 89 character code
[WARNING] [MERMAID VALIDATE] ❌ Validation failed
[WARNING] [MERMAID VALIDATE] Error: Unknown diagram type
[INFO] [MERMAID AUTO-FIX] Starting auto-fix (max 3 attempts)
[INFO] [MERMAID AUTO-FIX] Attempt 1/3
[INFO] [MERMAID AUTO-FIX] Applied fix: Added missing diagram type
[INFO] [MERMAID VALIDATE] ✅ Validation successful
[INFO] [MERMAID AUTO-FIX] ✅ Success on attempt 1!
[INFO] ✅ [MERMAID PROGRESS] All Mermaid diagrams validated successfully!

Example Log Sequence (AI Retry):
────────────────────────────────────────────────────────────────

[INFO] 🔍 [MERMAID PROGRESS] Found 1 Mermaid diagram(s) - validating...
[DEBUG] [MERMAID PROGRESS] Validation attempt 1/5
[WARNING] [MERMAID PROGRESS] Diagram #1 validation failed: Parse error...
[INFO] 🔧 [MERMAID PROGRESS] Requesting AI auto-fix (attempt 1/5)...
[INFO] ✅ [MERMAID PROGRESS] Received corrected code (234 chars) - re-validating...
[DEBUG] [MERMAID PROGRESS] Validation attempt 2/5
[INFO] ✅ [MERMAID PROGRESS] All Mermaid diagrams validated successfully!
[INFO] After Mermaid validation/fix: 2345 characters
```

---

## Summary

This visual guide shows:

1. **High-level flow** - How components interact
2. **Validation details** - Step-by-step validation process
3. **AI retry mechanism** - How errors trigger AI regeneration
4. **Error handling** - Different paths (success, auto-fix, retry, failure)
5. **Frontend tester** - User interaction with testing tool
6. **System architecture** - Component relationships
7. **Data flow** - Complete end-to-end data journey
8. **Logging patterns** - What to look for in logs

**The system is designed to handle Mermaid diagrams automatically, with multiple layers of error recovery to ensure users get valid diagrams as often as possible!**

For more details, see:
- [MERMAID_QUICK_START.md](MERMAID_QUICK_START.md) - User guide
- [MERMAID_AI_RETRY_SYSTEM.md](MERMAID_AI_RETRY_SYSTEM.md) - Technical deep dive
- [MERMAID_SYSTEM_COMPLETE.md](MERMAID_SYSTEM_COMPLETE.md) - Complete overview
