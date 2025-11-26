# Clarification UI Enhancements

## Summary of Changes

Enhanced the DiagramWizard clarification phase UI to display:
1. **LLM Assessment Score** - Shows the clarity/assessment score after each turn
2. **JSON Representation** - Displays the current JSON structure being built
3. **Improved Response Flow** - Cleaner user interaction with confirm ready button

---

## Files Modified

### 1. **SystemDescriptionScreen.tsx**
**Location:** `frontend/src/components/DiagramWizard/screens/SystemDescriptionScreen.tsx`

**Changes:**
- Added imports for Card, Collapse, and CodeOutlined
- Added score and JSON display card at the top of the clarification panel
- Card shows:
  - **LLM Assessment Score** (color-coded: green ≥8, blue ≥6, orange <6)
  - **JSON Representation** in a collapsible section with formatted output
- Display appears only when in analysis phase (`isInAnalysisPhase && sessionId`)
- Displays only when score > 0 or jsonRepresentation exists

**UI Structure:**
```
Score and JSON Card
├── LLM Assessment Score (tag with color)
└── Collapse Section
    └── JSON Representation (pre-formatted, scrollable)

↓

ChatPanel (Below the score/JSON card)
├── Conversation messages
└── Input + Send/Confirm Ready buttons
```

---

### 2. **Panel1_Chat.tsx**
**Location:** `frontend/src/components/DiagramWizard/panels/Panel1_Chat.tsx`

**Changes:**
- Updated ConversationMessage interface to include optional `score` and `jsonData` fields
- Updated Panel1ChatProps interface to accept new props:
  - `onSubmitClarification` (replaces `onSubmit`)
  - `isClarifying` boolean flag
  - `canConfirmReady` boolean flag
  - `onConfirmReady` callback function
- Added imports for Tag, Collapse, Tooltip, Badge, EyeOutlined, CodeOutlined
- Enhanced message rendering to show:
  - **Score tag** under each assistant message (when available)
  - **JSON collapse section** under each assistant message (when available)
- Updated input section to show:
  - **Send button** when actively clarifying
  - **Confirm Ready button** when clarifications are complete and ready to proceed
- Button styling: "Confirm Ready" is large, full-width, primary type

**Message Display:**
```
Assistant Message
├── Message content
├── Score tag (if score > 0)
│   └── Color-coded: Green/Blue/Orange
├── JSON Collapse (if jsonData exists)
│   └── Formatted JSON in pre-formatted code block
└── "View full details" link
```

**Input Section Logic:**
```
if canConfirmReady && onConfirmReady:
  Show "Confirm Ready to Generate Diagram" button
else if isClarifying:
  Show Input + "Send" button
else:
  Show nothing
```

---

## Visual Flow During Clarification Phase

```
┌─────────────────────────────────────┐
│   Score and JSON Summary Card       │
├─────────────────────────────────────┤
│ 📊 LLM Assessment Score: 7/10      │
│ ┌─────────────────────────────────┐ │
│ │ JSON Representation (collapsed) │ │
│ └─────────────────────────────────┘ │
└─────────────────────────────────────┘
            ↓
┌─────────────────────────────────────┐
│   Chat Panel                        │
├─────────────────────────────────────┤
│                                     │
│  AI: What type of system is this?  │
│  📊 Score: 6/10                    │
│  [JSON Collapse]                    │
│                                     │
│  User: It's a microservices arch    │
│                                     │
│  AI: How many services?             │
│  📊 Score: 8/10                    │
│  [JSON Collapse]                    │
│                                     │
├─────────────────────────────────────┤
│  [Input field] [Send Button]        │
│         OR                          │
│  [✓ Confirm Ready] (when ready)    │
└─────────────────────────────────────┘
```

---

## Color Coding for Scores

| Score Range | Color | Meaning |
|------------|-------|---------|
| 8-10 | Green | Excellent clarity/understanding |
| 6-7 | Blue | Good clarity |
| <6 | Orange | Needs clarification |

---

## User Interaction Flow

1. **Initial Description**: User enters system description
2. **AI Analysis Begins**: LLM processes and asks clarifying questions
3. **Clarification Loop**:
   - AI asks question
   - Score displays (updated after each response)
   - JSON representation shows current understanding
   - User enters response
   - Repeat until ready
4. **Ready to Generate**:
   - When clarifications are sufficient, "Confirm Ready" button appears
   - User clicks to proceed to generation phase

---

## Props Passed to SystemDescriptionScreen

| Prop | Type | Used For |
|------|------|----------|
| `score` | number | Display LLM score in card |
| `status.jsonRepresentation` | object | Display JSON in collapse |
| `isInAnalysisPhase` | boolean | Show/hide score/JSON card |
| `sessionId` | string \| null | Determine if in clarification |
| `isClarifying` | boolean | Show input field vs confirm button |
| `canConfirmReady` | boolean | Enable confirm ready button |
| `onConfirmReady` | function | Handle confirm ready action |
| `chatHistory` | array | Display conversation messages |
| `onSubmitClarification` | function | Handle response submission |

---

## Example Props Structure

```typescript
// During clarification phase
{
  score: 7,
  status: {
    jsonRepresentation: {
      system_type: "microservices",
      component_count: 5,
      architecture: "distributed"
    }
  },
  isInAnalysisPhase: true,
  sessionId: "abc123...",
  isClarifying: true,
  canConfirmReady: false,
  chatHistory: [
    ["assistant", "What type of system is this?"],
    ["user", "It's a microservices architecture"]
  ],
  onSubmitClarification: async (response) => { ... },
  onConfirmReady: async () => { ... }
}

// When clarifications complete
{
  isClarifying: false,
  canConfirmReady: true,
  // ... rest same as above
}
```

---

## Benefits

✅ **Better UX**: Users see score after each turn, encouraging clarity
✅ **Transparency**: JSON shows exactly what the AI understands
✅ **Clear Workflow**: Confirm button appears when ready (no guessing)
✅ **Organized Layout**: Score/JSON at top, chat below, input at bottom
✅ **Responsive**: Collapse sections keep UI clean when not needed
✅ **Accessible**: Color-coded scores aid quick visual assessment

---

## Component Hierarchy

```
SystemDescriptionScreen (orchestrator)
├── Header (model, session, status)
├── Progress Steps
├── Score/JSON Card (NEW)
│   ├── Score Tag
│   └── JSON Collapse
└── ChatPanel (enhanced)
    ├── Messages List
    │   └── Message Item (with score/JSON)
    ├── Scroll Area
    └── Input Section (Send or Confirm Ready)
```

---

## Testing Scenarios

### Scenario 1: Score Updates
1. User enters description
2. AI asks first clarification
3. Score appears (e.g., 6/10)
4. User responds
5. Score updates (e.g., 8/10)
6. Repeat until complete

### Scenario 2: JSON Display
1. Score/JSON card appears
2. User can expand JSON collapse
3. JSON updates as conversation progresses
4. User sees AI's understanding grow

### Scenario 3: Confirm Ready
1. After sufficient clarifications
2. "Confirm Ready" button replaces "Send"
3. User clicks "Confirm Ready"
4. Transitions to GenerationScreen

---

## Future Enhancements

- Add copy button for JSON
- Add JSON validation indicator
- Add score history chart
- Add suggestions based on low score
- Persist JSON/score snapshots per turn

