# DiagramWizard Refactored Architecture

## Overview

The DiagramWizard component has been refactored from a single monolithic component (~800+ lines) into three focused screen components, each responsible for a distinct phase of the diagram generation workflow.

## Component Structure

```
DiagramWizard/
├── DiagramWizardRefactored.tsx    ← Main orchestrator (new)
├── screens/                        ← Three screen components (new)
│   ├── ModelSelectionScreen.tsx    ← Screen 1: Model selection
│   ├── SystemDescriptionScreen.tsx ← Screen 2: Input + Analysis + Clarification
│   ├── GenerationScreen.tsx        ← Screen 3: Code generation + Rendering
│   └── index.ts                    ← Exports
├── ModelSelector.tsx               ← (deprecated, functionality in ModelSelectionScreen)
├── panels/                         ← Sub-panels (unchanged)
│   ├── Panel1_Chat.tsx
│   ├── Panel2_Preview.tsx
│   └── Panel3_CodeEditor.tsx
├── components/                     ← Sub-components (unchanged)
│   ├── ExportModal.tsx
│   └── Footer.tsx
├── hooks/                          ← Custom hooks (unchanged)
├── types/                          ← TypeScript types (unchanged)
└── diagram-wizard.module.css       ← Styles (unchanged)
```

## Three Screens Explained

### Screen 1: ModelSelectionScreen

**File:** `frontend/src/components/DiagramWizard/screens/ModelSelectionScreen.tsx`

**Purpose:** User selects which AI model to use for diagram generation

**Display:**
- Purple gradient background
- 4 model cards with descriptions and strengths
- Each model shows icon, name, description, and best-use cases

**Models Available:**
```typescript
export type ModelId = 'gpt5' | 'grok' | 'claude' | 'gemini';

interface ModelOption {
  id: ModelId;
  name: string;
  displayName: string;
  description: string;
  strengths: string[];
  icon: React.ReactNode;
  color: string;
}
```

**Props:**
```typescript
interface ModelSelectionScreenProps {
  onSelect: (modelId: ModelId) => void;
  loading?: boolean;
}
```

**Flow:**
```
User launches DiagramWizard
          ↓
ModelSelectionScreen appears
          ↓
User clicks model card
          ↓
onSelect handler → navigates to SystemDescriptionScreen
```

---

### Screen 2: SystemDescriptionScreen

**File:** `frontend/src/components/DiagramWizard/screens/SystemDescriptionScreen.tsx`

**Purpose:** User enters system description and goes through clarification loop

**Display:**
- Textarea for system description input
- Model tag + "Change Model" button in header
- Progress steps indicator
- Clarity score display

**Phases Handled:**
1. **Input Phase:** User enters description, clicks "Start Conversation"
2. **Analysis Phase:** AI analyzes the description
3. **Clarification Phase:** AI asks questions, user responds (loop)
4. **Decision:** Once clarity ≥ 8, user confirms ready

**Props:**
```typescript
interface SystemDescriptionScreenProps {
  selectedModel: ModelId;
  currentPhase: number;
  phases: Array<{ title: string; description: string; icon: React.ReactNode }>;
  userInput: string;
  loading: boolean;
  isInAnalysisPhase: boolean;
  sessionId: string | null;
  status: DiagramUpdate | null;
  score: number;
  clarifications: Array<{ question: string; answer?: string }>;
  chatHistory: any[];
  sseConnected: boolean;

  // Event handlers
  onChangeModel: () => void;
  onStartDiagram: (prompt: string) => void;
  onClearInput: () => void;
  onInputChange: (value: string) => void;
  onSubmitClarification: (clarification: string) => void;
  onConfirmReady: () => void;
  error?: { message: string };
}
```

**Conditional Rendering:**
- If NOT in analysis phase → Show textarea input
- If in analysis/clarification phase → Show ChatPanel

---

### Screen 3: GenerationScreen

**File:** `frontend/src/components/DiagramWizard/screens/GenerationScreen.tsx`

**Purpose:** Shows three-panel layout for code generation, validation, refinement, and rendering

**Display:**
- Three-panel layout:
  - **Left (25%):** Chat panel (conversation history)
  - **Center (50%):** Preview panel (SVG rendering)
  - **Right (25%):** Code editor (diagram code)
- Header with model tag and session info
- Footer with export/new diagram buttons

**Panels Used:**
1. **ChatPanel:** Shows conversation history (read-only in this screen)
2. **PreviewPanel:** Displays SVG preview with zoom controls
3. **CodeEditorPanel:** Shows/edits diagram code

**Props:**
```typescript
interface GenerationScreenProps {
  selectedModel: ModelId;
  currentPhase: number;
  phases: Array<{ title: string; description: string; icon: React.ReactNode }>;
  loading: boolean;
  sessionId: string | null;
  status: DiagramUpdate | null;
  score: number;
  diagramCode: string;
  svgOutput: string;
  chatHistory: any[];
  clarifications: Array<{ question: string; answer?: string }>;
  sseConnected: boolean;
  exportModalOpen: boolean;

  // Event handlers
  onChangeModel: () => void;
  onNewDiagram: () => void;
  onExportClick: () => void;
  onExportModalClose: () => void;
  onExportSubmit: (filename: string, format: string) => void;
  onCodeChange?: (code: string) => void;
  error?: { message: string };
}
```

**Statuses Shown:**
- `generating` / `code_generated` - Code generation in progress
- `validating` / `refining` - Validation and refinement
- `fallback_fix` - Using fallback fixes
- `rendering` / `rendered` - SVG rendering
- `completed` - Generation complete ✅
- `error` - Error occurred ❌

---

## DiagramWizardRefactored (Orchestrator)

**File:** `frontend/src/components/DiagramWizard/DiagramWizardRefactored.tsx`

**Purpose:** Main component that orchestrates the three screens and manages global state

**Key Responsibilities:**

1. **Screen Navigation**
   - Tracks current screen: `'model' | 'description' | 'generation'`
   - Navigates between screens based on user actions
   - Handles transitions based on session state

2. **State Management**
   ```typescript
   // Screen navigation
   const [currentScreen, setCurrentScreen] = useState<'model' | 'description' | 'generation'>('model');
   const [selectedModel, setSelectedModel] = useState<ModelId | null>();

   // Session state
   const [sessionId, setSessionId] = useState<string | null>(null);
   const [currentPhase, setCurrentPhase] = useState<number>(0);
   const [score, setScore] = useState<number>(0);

   // User input
   const [userInput, setUserInput] = useState<string>('');
   const [clarificationInput, setClarificationInput] = useState<string>('');
   ```

3. **Event Handler Delegation**
   ```typescript
   handleModelSelect → Change to 'description' screen
   handleChangeModel → Reset to 'model' screen
   handleStartDiagram → Call startSession with selected model
   handleSubmitClarification → Call submitClarification
   handleConfirmReady → Move to 'generation' screen
   handleNewDiagram → Reset everything, return to 'model' screen
   ```

4. **Status Update Handling**
   - Listens to all SSE status updates
   - Updates phase based on status
   - Shows appropriate messages
   - Triggers screen transitions
   - Saves session on completion

5. **Helper Functions**
   ```typescript
   normalizeJsonRepresentation() // Parse JSON safely
   getScoreInfo() // Extract score info from updates
   trackAssistantResponse() // Track AI responses
   saveSessionToHistory() // Persist to localStorage
   ```

## Data Flow

```
┌─────────────────────────────────────────────────────────────────┐
│                    DiagramWizardRefactored                      │
│              (Screen Navigation & State Management)              │
└─────────────────────────────────────────────────────────────────┘
                              │
                ┌─────────────┼─────────────┐
                │             │             │
        ┌───────▼────────┐   │    ┌────────▼─────────┐
        │ ModelSelection │   │    │ SystemDescription│
        │    Screen      │   │    │     Screen       │
        │                │   │    │                  │
        │ • 4 models     │   │    │ • TextArea input │
        │ • Select one   │   │    │ • ChatPanel      │
        │ • Save to LS   │   │    │ • Clarifications │
        └────────────────┘   │    └───────────────────┘
                             │
                             │ (when analysis done)
                             │
                    ┌────────▼──────────┐
                    │ GenerationScreen  │
                    │                   │
                    │ ┌─────┬──────┬───┐│
                    │ │Chat │Preview│Cod││
                    │ │Panel│ Panel │Ed.││
                    │ └─────┴──────┴───┘│
                    │                   │
                    │ • Code generation │
                    │ • Validation      │
                    │ • Refinement      │
                    │ • Rendering       │
                    └───────────────────┘
                             │
                             ↓
                        (Complete)
```

## State Flow Diagram

```
                    ┌─────────────────────────┐
                    │  DiagramWizardRefactored│
                    └────────────┬────────────┘
                                 │
                 ┌───────────────┴────────────────┐
                 │                                │
            ┌────▼──────────┐         ┌──────────▼─────┐
            │  selectedModel │         │  currentScreen │
            │   (ModelId)    │         │ ('model'|...)  │
            └────┬──────────┘         └──────────┬──────┘
                 │                              │
         ┌───────┴──────────┐          ┌────────┴──────────┐
         │                  │          │                   │
    ┌────▼────┐     ┌───────▼───┐     │            ┌──────▼──────┐
    │  gpt5   │     │ grok      │     │            │ description  │
    └─────────┘     └───────────┘     │            └──────────────┘
                                      │
                            ┌─────────▼────────┐
                            │   useDiagramSession
                            │   (hook)
                            └─────────┬────────┘
                                      │
                    ┌─────────────────┼──────────────┬───────────┐
                    │                 │              │           │
             ┌──────▼───┐      ┌──────▼──┐   ┌─────▼───┐  ┌───▼──┐
             │ sessionId │      │ status  │   │ chatHist│  │ score│
             └───────────┘      └─────────┘   └─────────┘  └──────┘
                    │
           ┌────────┴────────┐
           │                 │
      ┌────▼────┐       ┌────▼────┐
      │ started │       │analyzing │
      └─────────┘       └──────────┘
```

## State Persistence

**localStorage Keys:**
- `diagramWizard.selectedModel` - User's selected model (persists across page reloads)
- `diagramWizard.v2` - Full persisted state including history and preferences

**Auto-Save:**
- On diagram completion, session saved to `persistedState.sessionHistory`
- Tracks: timestamp, model, prompt, code, SVG output

## Screen Transition Logic

```typescript
// Transition 1: Model Selection → System Description
if (!selectedModel) {
  return <ModelSelectionScreen onSelect={handleModelSelect} />
}

// Transition 2: System Description → Generation
if (status?.status === 'completed') {
  setCurrentScreen('generation');
}

// Transition 3: All → Back to Model Selection (New Diagram)
if (userClicksNewDiagram) {
  setCurrentScreen('model');
  setSelectedModel(null);
  // Clear all state
}

// Transition 4: All → Back to Model Selection (Change Model)
if (userClicksChangeModel) {
  setCurrentScreen('model');
  // Modal warning shown first
}
```

## Benefits of This Architecture

### ✅ **Separation of Concerns**
- Each screen has single responsibility
- Easier to understand and modify individual screens
- Clean component boundaries

### ✅ **Reusability**
- Screens can be tested independently
- Could be extracted to separate routes/pages if needed
- Model selector can be used elsewhere

### ✅ **Maintainability**
- Smaller components → easier to read (200-300 lines each)
- Orchestrator manages flow clearly
- State updates organized by responsibility

### ✅ **Testability**
- Can test ModelSelectionScreen without starting session
- Can test SystemDescriptionScreen with mock data
- Can test GenerationScreen separately
- Unit tests easier to write

### ✅ **User Experience**
- Clear visual separation between screens
- Focused UI for each phase
- Reduced cognitive load (one thing per screen)

### ✅ **Code Organization**
```
Before: DiagramWizard.tsx (~1000+ lines)
After:
  - DiagramWizardRefactored.tsx (~400 lines, orchestration)
  - ModelSelectionScreen.tsx (~150 lines)
  - SystemDescriptionScreen.tsx (~250 lines)
  - GenerationScreen.tsx (~250 lines)
```

## Migration Guide

### For Current Users

No breaking changes if using the new `DiagramWizardRefactored` component:

```typescript
// Old (still works)
import { DiagramWizard } from './DiagramWizard';
<DiagramWizard />

// New (recommended)
import { DiagramWizardRefactored } from './DiagramWizardRefactored';
<DiagramWizardRefactored />
```

### For Import Changes

If screens need to be imported separately:

```typescript
// Import individual screens
import { ModelSelectionScreen, ModelId } from './screens';
import { SystemDescriptionScreen } from './screens';
import { GenerationScreen } from './screens';

// Or import from index
import { ModelSelectionScreen, SystemDescriptionScreen, GenerationScreen } from './screens';

// Import orchestrator
import { DiagramWizardRefactored as DiagramWizard } from './DiagramWizardRefactored';
```

## Future Enhancements

1. **Extract screens to routes** - Each screen could be a separate page/route
2. **Global state management** - Use Context API or Redux for cross-component state
3. **Screen persistence** - Save current screen to localStorage for session recovery
4. **Analytics** - Track which screens users visit, time spent on each
5. **A/B Testing** - Different orderings or presentations of screens
6. **Keyboard shortcuts** - Navigate between screens with keyboard

## Testing Strategy

### Unit Tests
```typescript
// ModelSelectionScreen.test.tsx
describe('ModelSelectionScreen', () => {
  test('renders 4 model cards', () => {});
  test('calls onSelect when model clicked', () => {});
  test('disables buttons when loading', () => {});
});

// SystemDescriptionScreen.test.tsx
describe('SystemDescriptionScreen', () => {
  test('shows textarea when not in analysis', () => {});
  test('shows ChatPanel when in analysis', () => {});
  test('calls onStartDiagram with input', () => {});
});

// GenerationScreen.test.tsx
describe('GenerationScreen', () => {
  test('displays three-panel layout', () => {});
  test('shows export button when complete', () => {});
  test('updates preview on code change', () => {});
});
```

### Integration Tests
```typescript
// DiagramWizardRefactored.test.tsx
describe('DiagramWizardRefactored Flow', () => {
  test('shows ModelSelectionScreen on mount', () => {});
  test('transitions to SystemDescriptionScreen after model select', () => {});
  test('transitions to GenerationScreen after analysis complete', () => {});
  test('can start new diagram from GenerationScreen', () => {});
  test('preserves model selection after page reload', () => {});
});
```

## Summary

The refactored DiagramWizard architecture provides:

✅ Three focused screen components
✅ Clear orchestrator managing transitions
✅ Better code organization and readability
✅ Easier testing and maintenance
✅ Improved user experience with focused UI
✅ Better state management flow
✅ Foundation for future enhancements (routing, global state, etc.)
