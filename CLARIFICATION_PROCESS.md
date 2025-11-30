# Diagram Wizard Clarification Process

## Overview
The Diagram Wizard uses an iterative LLM-based clarification loop to gather sufficient architectural details before generating diagrams. This process ensures high-quality, accurate diagrams by asking targeted questions.

## Process Flow

### 1. Initial Analysis (`analyze_request` node)
```
User Input: "A web application with API backend"
   ↓
LLM Analysis:
   - Evaluates initial description
   - Assigns clarity_score (1-100)
   - Generates first question
   - Creates initial json_representation
   ↓
Output: First clarification question sent to user
```

### 2. Clarification Loop (`clarify_prompt` node)
After each user response, the system automatically:

```
User Response: "PostgreSQL and Redis for storage"
   ↓
Automatic LLM Call:
   - Analyzes user's response
   - Updates json_representation with new details
   - Calculates clarity_score (1-100)
   - Determines if more info is needed
   ↓
Decision Point:
   If clarity_score < SCORE_TARGET (default: 80):
      → Ask another question
      → status: "clarifying"

   If clarity_score >= SCORE_TARGET:
      → Mark as ready
      → status: "clarification_ready"
      → awaiting_user_confirmation: true
      → Show "Confirm Ready" button
```

### 3. User Confirmation
```
When clarity_score >= SCORE_TARGET:
   ↓
Frontend displays: "Confirm Ready to Generate Diagram" button
   ↓
User clicks button:
   ↓
API call: confirmReady()
   ↓
Backend:
   - Sets user_confirmed_ready: true
   - Proceeds to diagram type selection
   ↓
Status: "awaiting_diagram_type_selection"
```

## Key Components

### Backend Logic ([clarification_nodes.py](backend/app/utils/diagram_wizard/nodes/clarification_nodes.py))

#### Automatic LLM Evaluation After Each Response
```python
# After user responds, clarify_prompt() automatically:
1. Calls LLM with combined ANALYZE + CLARIFY prompts
2. LLM returns JSON:
   {
     "question": "Next clarification question",
     "analysis_summary": "What we learned",
     "clarity_score": 60,  // 1-100 scale
     "ready": false,       // true if score >= target
     "json_representation": { /* updated architecture */ }
   }

3. Checks if clarity_score >= SCORE_TARGET (from .env)
4. If score >= target:
   - Sends status "clarification_ready" via SSE
   - Sets awaiting_user_confirmation: true
   - Waits for user to click "Confirm Ready"
```

#### Score Enforcement (Line 227-234)
```python
# Enforce score target: If score meets target, mark as ready
if clarity_score >= score_target and not ready:
    ready = True
    design_summary = f"READY: System architecture understood with clarity score of {clarity_score}/{score_target}."
```

#### User Confirmation Requirement (Line 254-298)
```python
if ready or (design_summary and design_summary.startswith("READY:")):
    # Default to requiring explicit user confirmation
    auto_proceed_on_ready = state.get("auto_proceed_on_ready", False)
    await_user_confirmation = not auto_proceed_on_ready

    await update_callback({
        "status": "clarification_ready",
        "awaiting_user_confirmation": await_user_confirmation,
        # ... other data
    })

    # Don't auto-proceed - wait for user
    if not auto_proceed_on_ready:
        return {
            "llm_ready": False,
            "awaiting_user_confirmation": True,
            "user_confirmed_ready": False,
            "current_state": SessionState.CLARIFYING
        }
```

### Frontend Logic ([DiagramWizard.tsx](frontend/src/components/DiagramWizard/DiagramWizard.tsx))

#### SSE Status Updates (Line 199-244)
```typescript
switch (statusValue) {
  case 'clarifying':
    // AI is asking clarification questions
    setCurrentPhase(2);
    message.info('AI is asking clarifying questions...');
    break;

  case 'clarification_ready':
    // Score >= target, ready for user confirmation
    message.success('Clarification received. Processing...');
    break;

  case 'can_proceed':
    // AI determined it has sufficient information
    message.success('Ready to proceed with diagram generation!');
    break;
}
```

#### Button Display Logic ([SystemDescriptionScreen.tsx](frontend/src/components/DiagramWizard/screens/SystemDescriptionScreen.tsx:153))
```typescript
const canConfirmReady =
  status?.status === 'can_proceed' ||
  status?.status === 'clarification_ready';

// Currently shown in Panel1_Chat:
{canConfirmReady && onConfirmReady ? (
  <Button onClick={onConfirmReady}>
    ✓ Confirm Ready to Generate Diagram
  </Button>
) : null}
```

#### Confirm Ready Handler ([DiagramWizard.tsx](frontend/src/components/DiagramWizard/DiagramWizard.tsx:537-556))
```typescript
const handleConfirmReady = async () => {
  if (!sessionId) {
    message.error('No active session');
    return;
  }

  try {
    await confirmReady(); // API call
    // Backend sends 'awaiting_diagram_type_selection' status
    // Which triggers navigation to diagram type screen
  } catch (err) {
    message.error('Failed to confirm ready');
  }
};
```

## Environment Configuration

### .env Variables
```bash
# Clarity score threshold for proceeding to generation (1-100)
SCORE_TARGET=80

# Auto-proceed without user confirmation (not recommended)
AUTO_PROCEED_ON_READY=false
```

## Timeout Protection

### Max Questions Limit (Line 108-132)
```python
# Prevent infinite clarification loops
if question_count >= 20 or (current_time - start_time) > 1800:  # 30 minutes
    logger.info(f"Clarification timeout reached")
    await update_callback({
        "status": "clarification_ready",
        "message": "Maximum clarification attempts reached. Please confirm to proceed.",
        "awaiting_user_confirmation": True,
        "clarification_timeout": True,
    })
```

## Data Flow Diagram

```
┌──────────────────────────────────────────────────────────────┐
│                    USER INPUTS DESCRIPTION                    │
└────────────────────────┬─────────────────────────────────────┘
                         │
                         ▼
┌──────────────────────────────────────────────────────────────┐
│              analyze_request (First Question)                 │
│  - Evaluates initial input                                    │
│  - Assigns clarity_score                                      │
│  - Generates json_representation                              │
└────────────────────────┬─────────────────────────────────────┘
                         │
                         ▼
         ┌───────────────────────────┐
         │   User Responds           │
         └───────┬───────────────────┘
                 │
                 ▼
┌──────────────────────────────────────────────────────────────┐
│         AUTOMATIC LLM CALL (clarify_prompt)                   │
│  ┌─────────────────────────────────────────────────────┐     │
│  │ 1. Call LLM with user's response                    │     │
│  │ 2. LLM evaluates and returns:                       │     │
│  │    - question (next clarification)                  │     │
│  │    - clarity_score (1-100)                          │     │
│  │    - json_representation (updated)                  │     │
│  │    - ready (true if score >= target)                │     │
│  └─────────────────────────────────────────────────────┘     │
└────────────────────────┬─────────────────────────────────────┘
                         │
                         ▼
              ┌──────────────────────┐
              │ Score >= Target (80)? │
              └──────┬───────┬────────┘
                     │       │
            NO ◄─────┘       └─────► YES
             │                       │
             ▼                       ▼
    ┌────────────────┐    ┌──────────────────────┐
    │ Ask Another    │    │ status:              │
    │ Question       │    │ "clarification_ready"│
    └────┬───────────┘    │                      │
         │                │ Show "Confirm Ready" │
         └─────┐          │ Button               │
               │          └──────┬───────────────┘
               │                 │
               └─────┐           │
                     │           ▼
                     │  ┌────────────────────┐
                     │  │ User Clicks        │
                     │  │ "Confirm Ready"    │
                     │  └────────┬───────────┘
                     │           │
                     │           ▼
                     │  ┌────────────────────┐
                     │  │ confirmReady()     │
                     │  │ API call           │
                     │  └────────┬───────────┘
                     │           │
                     └───────────┘           │
                                            ▼
                              ┌──────────────────────────┐
                              │ Proceed to Diagram Type  │
                              │ Selection                │
                              └──────────────────────────┘
```

## Example Session

```
Turn 1:
User: "A web application with API backend"
LLM:  clarity_score: 30/100
      question: "What database technologies are you using?"
      status: "clarifying"

Turn 2:
User: "PostgreSQL for main data, Redis for caching"
LLM:  clarity_score: 60/100
      question: "Are there any external services or APIs?"
      status: "clarifying"

Turn 3:
User: "AWS S3 for file storage, SendGrid for emails"
LLM:  clarity_score: 85/100  ✓ >= 80 target
      status: "clarification_ready"
      awaiting_user_confirmation: true
      → Button appears: "Confirm Ready to Generate Diagram"

Turn 4:
User: [Clicks "Confirm Ready"]
      → user_confirmed_ready: true
      → Proceeds to diagram type selection
```

## Why User Confirmation is Required

1. **Control**: User has final say on when to proceed
2. **Review**: User can review json_representation before generation
3. **Additional Details**: User can add more info even after score threshold met
4. **Safety**: Prevents premature generation with incomplete understanding

## Configuration Options

### Enable Auto-Proceed (Not Recommended)
```typescript
// In session start, set:
await startSession(prompt, diagramType, selectedModel, {
  auto_proceed_on_ready: true  // Skip user confirmation
});
```

This will automatically proceed to diagram type selection when `clarity_score >= SCORE_TARGET` without waiting for user confirmation.
