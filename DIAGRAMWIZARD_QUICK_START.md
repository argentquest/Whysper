# DiagramWizard Refactored - Quick Start Guide

## TL;DR - What Changed

**Before:** 1000+ line monolithic component
**After:** 4 focused components (orchestrator + 3 screens)

| Screen | Purpose | Lines |
|--------|---------|-------|
| **ModelSelectionScreen** | Choose AI model | ~150 |
| **SystemDescriptionScreen** | Input + clarification | ~250 |
| **GenerationScreen** | Generate & export | ~250 |
| **DiagramWizardRefactored** | Orchestrator | ~400 |

---

## Files to Copy

```
📁 frontend/src/components/DiagramWizard/

New Folder:
📁 screens/
  📄 ModelSelectionScreen.tsx
  📄 SystemDescriptionScreen.tsx
  📄 GenerationScreen.tsx
  📄 index.ts

New File:
📄 DiagramWizardRefactored.tsx
```

---

## Usage

### Drop-in Replacement

```typescript
// Old (still works)
import { DiagramWizard } from './components/DiagramWizard';

// New (recommended)
import { DiagramWizardRefactored } from './components/DiagramWizard/DiagramWizardRefactored';

export default function App() {
  return <DiagramWizardRefactored />;
}
```

### Props

```typescript
interface DiagramWizardProps {
  onDiagramGenerated?: (code: string, svg: string) => void;
  initialPrompt?: string;
}
```

---

## Screen Flow

```
START
  ↓
ModelSelectionScreen
  (Pick AI model)
  ↓
SystemDescriptionScreen
  (Describe system, answer questions)
  ↓
GenerationScreen
  (View generated diagram, export)
  ↓
END (or start new diagram)
```

---

## Three Screens Explained

### 1️⃣ ModelSelectionScreen
- **When:** First screen, always shown
- **Shows:** 4 model cards (GPT-5, Grok, Claude, Gemini)
- **Action:** User clicks a model
- **Next:** SystemDescriptionScreen

### 2️⃣ SystemDescriptionScreen
- **When:** After model selected
- **Phase 1:** TextArea (user enters system description)
- **Phase 2:** ChatPanel (AI asks clarifying questions)
- **Action:** User clicks "Start" or "Confirm Ready"
- **Next:** GenerationScreen

### 3️⃣ GenerationScreen
- **When:** After user confirms ready
- **Shows:** Three-panel layout
  - Left: Chat (conversation history)
  - Center: Preview (SVG diagram)
  - Right: Code (diagram code editor)
- **Actions:** Export or "New Diagram"
- **Next:** Back to ModelSelectionScreen (if new diagram)

---

## Component Structure

```
DiagramWizardRefactored
├── State Management
│   ├── currentScreen: 'model' | 'description' | 'generation'
│   ├── selectedModel: ModelId (gpt5, grok, claude, gemini)
│   ├── userInput: string
│   └── ...more state...
├── SSE Integration
│   └── useDiagramSession hook
├── Event Handlers
│   ├── handleModelSelect
│   ├── handleStartDiagram
│   ├── handleSubmitClarification
│   ├── handleConfirmReady
│   └── ...more handlers...
└── Render Logic
    ├── if (!selectedModel) → ModelSelectionScreen
    ├── else if (currentScreen === 'description') → SystemDescriptionScreen
    └── else → GenerationScreen
```

---

## State Flow

```
App State (in DiagramWizardRefactored)
│
├── Navigation State
│   ├── currentScreen
│   └── selectedModel
│
├── User Input State
│   ├── userInput
│   └── clarificationInput
│
├── Session State (from useDiagramSession)
│   ├── sessionId
│   ├── status
│   ├── chatHistory
│   ├── diagramCode
│   └── svgOutput
│
└── UI State
    ├── currentPhase
    ├── score
    └── exportModalVisible
```

---

## Key Events

### ModelSelectionScreen
```
User clicks model
  ↓
onSelect(modelId)
  ↓
setSelectedModel(modelId)
setCurrentScreen('description')
  ↓
SystemDescriptionScreen appears
```

### SystemDescriptionScreen
```
User enters description + clicks "Start"
  ↓
onStartDiagram(userInput)
  ↓
startSession(input, diagramType, selectedModel)
  ↓
Analysis begins (AI calls start)
  ↓
Clarification loop (AI asks questions)
  ↓
User answers + confirms ready
  ↓
onConfirmReady()
  ↓
setCurrentScreen('generation')
  ↓
GenerationScreen appears
```

### GenerationScreen
```
onExportClick()
  → Open export modal
  → User fills export form
  → Diagram saved

onNewDiagram()
  → Reset state
  → setCurrentScreen('model')
  → Back to ModelSelectionScreen
```

---

## Common Tasks

### Show Only Specific Screen

```typescript
// Show only model selection
import { ModelSelectionScreen } from './screens';

function ModelPicker() {
  return (
    <ModelSelectionScreen
      onSelect={(model) => console.log(model)}
      loading={false}
    />
  );
}
```

### Customize Screen Appearance

Edit the individual screen files:
- `ModelSelectionScreen.tsx` - Change colors, layout
- `SystemDescriptionScreen.tsx` - Modify input UI
- `GenerationScreen.tsx` - Adjust three-panel layout

### Add New Handler

In `DiagramWizardRefactored.tsx`:

```typescript
// Add new handler
const handleMyCustomAction = () => {
  console.log('Custom action!');
  // Update state, call API, etc.
};

// Pass to screen
<GenerationScreen
  onMyCustomAction={handleMyCustomAction}
  {...otherProps}
/>
```

---

## Testing Quick Start

```typescript
// Test ModelSelectionScreen
import { render, screen } from '@testing-library/react';
import { ModelSelectionScreen } from './screens';

test('renders 4 models', () => {
  render(<ModelSelectionScreen onSelect={jest.fn()} />);
  expect(screen.getByText('GPT-5')).toBeInTheDocument();
  expect(screen.getByText('Grok')).toBeInTheDocument();
  expect(screen.getByText('Claude')).toBeInTheDocument();
  expect(screen.getByText('Gemini')).toBeInTheDocument();
});
```

---

## File Locations

```
frontend/
└── src/
    └── components/
        └── DiagramWizard/
            ├── DiagramWizardRefactored.tsx      ← NEW Main file
            ├── screens/                         ← NEW Folder
            │   ├── ModelSelectionScreen.tsx     ← NEW
            │   ├── SystemDescriptionScreen.tsx  ← NEW
            │   ├── GenerationScreen.tsx         ← NEW
            │   └── index.ts                     ← NEW
            ├── panels/                          ← (unchanged)
            │   ├── Panel1_Chat.tsx
            │   ├── Panel2_Preview.tsx
            │   └── Panel3_CodeEditor.tsx
            ├── components/                      ← (unchanged)
            │   ├── ExportModal.tsx
            │   └── Footer.tsx
            ├── hooks/                           ← (unchanged)
            │   └── useDiagramSession.ts
            ├── types/                           ← (unchanged)
            ├── diagram-wizard.module.css        ← (unchanged)
            └── (old files still work)
```

---

## Keyboard Shortcuts (Future)

Currently not implemented, but easy to add:

```typescript
useEffect(() => {
  const handleKey = (e: KeyboardEvent) => {
    if (e.key === 'Escape') handleNewDiagram();
  };
  window.addEventListener('keydown', handleKey);
  return () => window.removeEventListener('keydown', handleKey);
}, []);
```

---

## Troubleshooting

### ModelSelectionScreen doesn't appear
```typescript
// Check that currentScreen is initialized to 'model'
const [currentScreen, setCurrentScreen] = useState<'model' | 'description' | 'generation'>('model');
```

### ChatPanel shows instead of textarea
```typescript
// Check isInAnalysisPhase flag
// Only show textarea when NOT in analysis
if (!isInAnalysisPhase) {
  // Show textarea
}
```

### GenerationScreen not updating
```typescript
// Check that svgOutput is being passed
const { svgOutput } = useDiagramSession(...);
// Pass to component
<GenerationScreen svgOutput={svgOutput} {...props} />
```

---

## Performance Tips

✅ Components already optimized with:
- Focused rendering (only active screen renders)
- Prop drilling minimized
- No unnecessary re-renders
- TypeScript for compile-time checks

🎯 If you want more optimization:
```typescript
// Wrap screens in React.memo
export const ModelSelectionScreen = React.memo(function ModelSelectionScreen(props) {
  // ...
});
```

---

## What's Next

1. ✅ Copy files to your codebase
2. ✅ Update imports
3. ✅ Test the flow
4. ✅ Deploy!

---

## Key Differences from Old Component

| Feature | Old | New |
|---------|-----|-----|
| Lines in main file | 1000+ | 400 |
| Files | 1 | 5 |
| Component coupling | High | Low |
| Testability | Difficult | Easy |
| Readability | Hard | Clear |
| Screen transitions | Implicit | Explicit |

---

## Documentation

- 📖 Full architecture: `DIAGRAMWIZARD_REFACTORED_ARCHITECTURE.md`
- 🛠️ Implementation guide: `DIAGRAMWIZARD_REFACTORED_IMPLEMENTATION.md`
- 📊 Before/after: `DIAGRAMWIZARD_BEFORE_AFTER_COMPARISON.md`
- 📝 Summary: `DIAGRAMWIZARD_REFACTOR_SUMMARY.md`

---

## Questions?

Refer to:
1. Component code (well-commented)
2. Full documentation files
3. Props interfaces (TypeScript types)
4. Example usage in DiagramWizardRefactored.tsx

---

## Summary

✅ Refactored DiagramWizard into 3 focused screens
✅ Easier to understand, test, and maintain
✅ Same functionality, better organization
✅ Ready to use immediately
✅ Fully documented

**Start using it today!** 🚀
