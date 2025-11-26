# DiagramWizard Architecture - Canonical Reference

**Last Updated:** 2025-11-17
**Status:** ✅ Production Ready
**Canonical Document:** This is the single source of truth for DiagramWizard architecture

---

## Overview

DiagramWizard uses a **3-screen modular architecture** orchestrated by LangGraph workflows and powered by a multi-provider diagram rendering system.

---

## Component Architecture

### Frontend: 3-Screen Pattern

```
DiagramWizardRefactored.tsx (Orchestrator)
├── Screen 1: ModelSelectionScreen.tsx
│   └── Purpose: AI model selection (GPT-5, Grok, Claude, Gemini)
├── Screen 2: SystemDescriptionScreen.tsx
│   └── Purpose: System description + AI clarification loop
└── Screen 3: GenerationScreen.tsx
    └── Purpose: Code generation, preview, and export
```

**File Locations:**
- Orchestrator: `frontend/src/components/DiagramWizard/DiagramWizardRefactored.tsx`
- Screens: `frontend/src/components/DiagramWizard/screens/`
- Shared panels: `frontend/src/components/DiagramWizard/panels/`
- Hooks: `frontend/src/components/DiagramWizard/hooks/`

### Backend: LangGraph Workflow

```
7 LangGraph Nodes:
1. analyze_request        → Initial analysis
2. clarify_prompt         → Clarification loop
3. determine_diagram_type → Type selection
4. generate_code          → Code generation
5. validate_code          → Syntax validation
6. refine_code            → Auto-fix errors
7. render_diagram         → SVG rendering
```

**File Locations:**
- Nodes: `backend/app/utils/diagram_wizard/nodes.py`
- State: `backend/app/utils/diagram_wizard/graph_state.py`
- Graph: `backend/app/utils/diagram_wizard/langgraph_builder.py`

### Provider System

```
Provider Registry
├── MermaidV1 (CLI + Kroki)
├── D2V1 (CLI + Kroki)
└── PlantUML (Kroki)
```

**File Locations:**
- Registry: `backend/diagrams/provider_registry.py`
- Base: `backend/diagrams/base_diagram.py`
- Providers: `backend/diagrams/providers/`

---

## Data Flow

```
User Input
    ↓
Frontend (React) → SSE Connection
    ↓
API Gateway (FastAPI)
    ↓
LangGraph Workflow (Orchestration)
    ↓
Provider System (Execution)
    ↓
SSE Stream → Frontend
    ↓
User sees result
```

---

## State Management

### Frontend State

```typescript
// Screen navigation
currentScreen: 'model' | 'description' | 'generation'
selectedModel: ModelId | null

// Session state (from useDiagramSession)
sessionId: string | null
status: DiagramUpdate | null
chatHistory: Message[]
diagramCode: string
svgOutput: string

// UI state
currentPhase: number
score: number
loading: boolean
```

### Backend State (GraphState)

```python
class GraphState(TypedDict):
    session_id: str
    clarification_history: List[Dict]
    clarity_score: int
    json_representation: Dict
    diagram_type: DiagramType
    diagram_code: str
    svg_output: str
    is_valid: bool
    current_state: SessionState
```

---

## Communication: SSE (Server-Sent Events)

**Frontend Hook:** `frontend/src/hooks/useSSE.ts`

**Features:**
- Automatic reconnection (exponential backoff)
- Keep-alive timeout (30s)
- Connection status tracking
- Message queuing

**Backend Endpoint:** `/api/v1/diagram/stream/{session_id}`

---

## Key Architectural Decisions

### 1. Why 3 Screens?

**Before:** 1000+ line monolithic component
**After:** 3 focused screens (~250 lines each)

**Benefits:**
- Easier to test
- Easier to maintain
- Clear separation of concerns
- Easier to extend

### 2. Why LangGraph?

**Reason:** Complex conditional workflow

- Clarification loop (0-10 iterations)
- Validation + refinement loop (0-3 attempts)
- Conditional branching based on state

**Alternative Rejected:** Simple API chain (not flexible enough)

### 3. Why Provider System?

**Reason:** Multi-format support with different validation needs

- Mermaid: CLI validation
- D2: CLI validation
- PlantUML: Pattern validation
- Each has different error handling

**Alternative Rejected:** Monolithic validator (not extensible)

### 4. Why SSE over WebSocket?

**Reasons:**
- Simpler (one-way communication)
- Built-in reconnection
- HTTP/2 friendly
- No need for bidirectional messaging

**Use Case:** Server streams updates to client, client sends HTTP requests

---

## Related Documents

- **Quick Start:** [DIAGRAMWIZARD_QUICK_START.md](./DIAGRAMWIZARD_QUICK_START.md)
- **Complete Docs:** [DIAGRAMWIZARD_COMPLETE.md](./DIAGRAMWIZARD_COMPLETE.md)
- **Refactored Details:** [DIAGRAMWIZARD_REFACTORED_ARCHITECTURE.md](./DIAGRAMWIZARD_REFACTORED_ARCHITECTURE.md)
- **Sequence Diagram:** [DIAGRAMWIZARD_SEQUENCE_DIAGRAM.md](./DIAGRAMWIZARD_SEQUENCE_DIAGRAM.md)
- **Master Index:** [3-DIAGRAM_SYSTEM/DIAGRAM_WIZARD/DIAGRAMWIZARD_MASTER_INDEX.md](./3-DIAGRAM_SYSTEM/DIAGRAM_WIZARD/DIAGRAMWIZARD_MASTER_INDEX.md)

---

**Note:** This is a canonical reference. When architecture changes, update THIS document first, then update references in other documents.
