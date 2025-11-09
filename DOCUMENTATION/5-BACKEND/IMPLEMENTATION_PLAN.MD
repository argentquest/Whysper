# Diagram Wizard - Detailed Implementation Plan

---

## Project Structure

```
Whysper/
├── backend/
│   └── app/
│       ├── api/v1/endpoints/
│       │   └── diagram.py                 # NEW: Diagram endpoints
│       ├── services/
│       │   └── diagram_factory_service.py # NEW: Diagram factory service
│       └── utils/
│           └── diagram_wizard/            # NEW: Diagram wizard utilities
│               ├── __init__.py
│               ├── graph_state.py         # Graph state schema
│               ├── nodes.py               # LangGraph nodes
│               ├── tool_config.py         # Tool configuration & execution
│               ├── langgraph_builder.py   # Graph compilation
│               ├── session_store.py       # Session management
│               └── prompts/               # NEW: Prompt storage
│                   ├── __init__.py
│                   ├── CLARIFY_PROMPTS.md
│                   ├── GENERATE_PROMPTS.md
│                   └── REFINE_PROMPTS.md
│
├── frontend/
│   └── src/
│       └── components/
│           └── DiagramWizard/             # NEW: Diagram wizard components
│               ├── DiagramWizard.tsx      # Main wrapper component
│               ├── Panel1_Chat.tsx        # Chat/Q&A panel
│               ├── Panel2_Preview.tsx     # SVG preview panel
│               ├── Panel3_CodeEditor.tsx  # Code editor panel
│               ├── hooks/
│               │   ├── useSSEStream.ts    # SSE connection hook
│               │   ├── useDiagramSession.ts # Session management hook
│               │   └── useDiagramState.ts # State machine hook
│               ├── services/
│               │   ├── diagramApi.ts      # API client
│               │   └── sse.ts             # SSE helper functions
│               ├── types/
│               │   └── diagram.ts         # TypeScript types
│               └── styles/
│                   └── diagram-wizard.css # Styling
│
└── docs/
    └── IMPLEMENTATION_TASKS.md            # This file (detailed task breakdown)
```

---

## Phase 1: Backend Foundation (Weeks 1-2)

### Task 1.1: Set Up Diagram Wizard Directory Structure
**Assigned to:** Backend Developer
**Estimated Time:** 2 hours
**Dependencies:** None

**Deliverables:**
- [ ] Create `backend/app/utils/diagram_wizard/` directory
- [ ] Create `backend/app/utils/diagram_wizard/prompts/` directory
- [ ] Create all `__init__.py` files with proper imports
- [ ] Create `.gitignore` entry for diagram wizard logs

**Acceptance Criteria:**
- Directory structure matches specification
- All imports work without errors
- No linting violations

---

### Task 1.2: Create Prompt Storage Files (MD Format)
**Assigned to:** Backend/Prompt Engineer
**Estimated Time:** 4 hours
**Dependencies:** Task 1.1

**Deliverables:**
- [ ] `backend/app/utils/diagram_wizard/prompts/CLARIFY_PROMPTS.md`
- [ ] `backend/app/utils/diagram_wizard/prompts/GENERATE_PROMPTS.md`
- [ ] `backend/app/utils/diagram_wizard/prompts/REFINE_PROMPTS.md`

**File Structure:** Each MD file should contain:
```markdown
# [Prompt Category] Prompts

## Mermaid Prompts

### Clarification Questions
[questions here]

### Generation Template
[template here]

### Refinement Instructions
[instructions here]

---

## D2 Prompts

### Clarification Questions
[questions here]

### Generation Template
[template here]

### Refinement Instructions
[instructions here]

---

## PlantUML Prompts

### Clarification Questions
[questions here]

### Generation Template
[template here]

### Refinement Instructions
[instructions here]
```

**Acceptance Criteria:**
- All 3 prompt files created
- Format is clean and well-organized
- Prompts are specific to each diagram type
- Ready to be parsed by Python code

---

### Task 1.3: Implement Prompt Loader Utility
**Assigned to:** Backend Developer
**Estimated Time:** 3 hours
**Dependencies:** Task 1.2

**File:** `backend/app/utils/diagram_wizard/__init__.py`

**Code Specification:**
```python
"""
Prompt loader utility for diagram wizard.
Loads prompts from markdown files.
"""

import os
from pathlib import Path
from typing import Dict, Any

def load_prompts() -> Dict[str, Dict[str, str]]:
    """
    Load all prompts from markdown files.

    Returns:
        {
            'clarify': {...},
            'generate': {...},
            'refine': {...}
        }
    """
    # Load CLARIFY_PROMPTS.md
    # Load GENERATE_PROMPTS.md
    # Load REFINE_PROMPTS.md
    # Parse markdown and extract per-diagram-type prompts
    # Return as nested dict
    pass

def get_prompt(category: str, diagram_type: str, prompt_type: str) -> str:
    """
    Retrieve a specific prompt.

    Args:
        category: 'clarify', 'generate', 'refine'
        diagram_type: 'Mermaid', 'D2', 'PlantUML'
        prompt_type: 'questions', 'template', 'instructions'
    """
    pass
```

**Acceptance Criteria:**
- Loads all 3 MD files without errors
- Parses markdown correctly
- Returns prompts keyed by diagram type
- No hardcoded prompts in Python files
- Unit tests pass (95%+ coverage)

---

### Task 1.4: Implement Graph State Schema
**Assigned to:** Backend Developer
**Estimated Time:** 2 hours
**Dependencies:** Task 1.1

**File:** `backend/app/utils/diagram_wizard/graph_state.py`

**Code Specification:**
```python
from typing import TypedDict, List, Dict, Optional
from enum import Enum

class DiagramType(str, Enum):
    MERMAID = "Mermaid"
    D2 = "D2"
    PLANTUML = "PlantUML"

class SessionState(str, Enum):
    INITIALIZED = "initialized"
    INPUT_PHASE = "input_phase"
    CLARIFYING = "clarifying"
    GENERATING = "generating"
    VALIDATING = "validating"
    VALIDATION_ERROR = "validation_error"
    RENDERING = "rendering"
    READY = "ready"
    EDIT_MODE = "edit_mode"
    COMPLETED = "completed"
    ERROR = "error"

class GraphState(TypedDict, total=False):
    """Central state for the diagram factory graph."""

    # Session metadata
    session_id: str
    user_id: str
    conversation_id: str
    created_at: str

    # Input phase
    design_prompt: str
    diagram_type: DiagramType

    # Clarification loop
    clarification_history: List[Dict[str, str]]
    clarification_timeout: bool
    llm_ready: bool
    final_design_summary: str
    question_count: int

    # Generation & Validation loop
    diagram_code: str
    validation_error: str
    validation_error_type: str
    recovery_suggestions: List[str]
    is_valid: bool
    refinement_attempt: int

    # Output
    svg_output: str

    # State tracking
    current_state: SessionState
    error_message: Optional[str]
```

**Acceptance Criteria:**
- All required fields defined
- Enums for diagram types and states
- Type hints are correct
- Can be imported without errors

---

### Task 1.5: Implement Tool Configuration & Safe Execution
**Assigned to:** Backend Developer (Security-focused)
**Estimated Time:** 5 hours
**Dependencies:** Task 1.1

**File:** `backend/app/utils/diagram_wizard/tool_config.py`

**Code Specification:**

Must include:
1. Tool path validation
2. Safe subprocess execution (NO `shell=True`)
3. File cleanup with context managers
4. Timeout enforcement
5. Tool availability detection at startup
6. Argument whitelist validation
7. Comprehensive error handling

**Key Classes:**
- `DiagramToolConfig` - Tool configuration
- `DiagramToolRunner` - Safe execution
- `ToolValidationError` - Custom exception

**Tests Required:**
- Tool availability detection
- Safe command construction
- Timeout handling
- File cleanup on error
- Argument validation

**Acceptance Criteria:**
- Zero uses of `shell=True`
- All files cleaned up on error
- Timeouts enforced
- 100% test coverage
- Security review passed

---

### Task 1.6: Implement Session Store (In-Memory)
**Assigned to:** Backend Developer
**Estimated Time:** 4 hours
**Dependencies:** Task 1.4

**File:** `backend/app/utils/diagram_wizard/session_store.py`

**Code Specification:**

```python
class DiagramSessionStore:
    """Thread-safe session management for diagram factory."""

    async def create_session(
        self,
        user_id: str,
        conversation_id: str,
        initial_prompt: str,
        diagram_type: str
    ) -> str:
        """Create and return session_id."""
        pass

    async def get_session(self, session_id: str) -> GraphState:
        """Retrieve session, checking expiration."""
        pass

    async def update_session(
        self,
        session_id: str,
        updates: Dict[str, Any]
    ) -> None:
        """Update session state."""
        pass

    async def delete_session(self, session_id: str) -> None:
        """Delete session."""
        pass

    async def cleanup_expired(self) -> int:
        """Remove expired sessions. Returns count."""
        pass
```

**Features:**
- Thread-safe with asyncio.Lock
- TTL management (1 hour default)
- Automatic cleanup
- Session history tracking

**Tests Required:**
- Create/read/update/delete operations
- Expiration handling
- Concurrent access
- Cleanup functionality

**Acceptance Criteria:**
- All async operations work correctly
- No race conditions under load
- Proper cleanup of expired sessions
- 100% test coverage

---

### Task 1.7: Implement LangGraph Nodes
**Assigned to:** Backend Developer
**Estimated Time:** 8 hours
**Dependencies:** Tasks 1.3, 1.4, 1.5, 1.6

**File:** `backend/app/utils/diagram_wizard/nodes.py`

**Nodes to Implement:**

#### Node 1: `clarify_prompt`
- Takes clarification history
- Calls LLM with CLARIFY_PROMPT
- Returns next question OR "READY:" marker
- Handles timeout

#### Node 2: `generate_code`
- Takes final_design_summary + diagram_type
- Calls LLM with GENERATE_PROMPT (diagram-type-specific)
- Returns diagram_code

#### Node 3: `validate_code`
- Takes diagram_code + diagram_type
- Executes appropriate tool (d2 validate, mmdc --validate, etc.)
- Returns is_valid + validation_error (if any)

#### Node 4: `refine_code`
- Takes validation_error + diagram_code + design_summary
- Calls LLM with REFINE_PROMPT
- Returns refined diagram_code

#### Node 5: `render_diagram`
- Takes valid diagram_code + diagram_type
- Executes render command
- Returns svg_output + file cleanup

**Tests Required:**
- Each node in isolation
- All node transitions
- Error handling in each node
- Timeout scenarios

**Acceptance Criteria:**
- All 5 nodes implement correctly
- Proper error handling
- No hardcoded prompts
- LLM integration works
- 100% test coverage

---

### Task 1.8: Build LangGraph State Machine
**Assigned to:** Backend Developer
**Estimated Time:** 3 hours
**Dependencies:** Task 1.7

**File:** `backend/app/utils/diagram_wizard/langgraph_builder.py`

**Code Specification:**

```python
from langgraph.graph import StateGraph, END

def build_diagram_factory_graph() -> StateGraph:
    """
    Build and return compiled LangGraph state machine.

    Flow:
    clarify_prompt
        ├─ if llm_ready: generate_code
        └─ if not ready: END (wait for user response)

    generate_code → validate_code

    validate_code
        ├─ if valid: render_diagram
        └─ if invalid: refine_code → validate_code

    render_diagram → END
    """
    pass

# Should be callable as:
# graph = build_diagram_factory_graph()
# result = await graph.ainvoke(initial_state)
```

**Features:**
- Proper node registration
- Conditional edge routing
- State persistence
- Error propagation

**Tests Required:**
- Graph compilation
- All paths through graph
- State transitions
- Error scenarios

**Acceptance Criteria:**
- Graph compiles without errors
- All paths tested
- Proper state handling
- Ready for service integration

---

## Phase 2: Backend Service Integration (Week 3)

### Task 2.1: Implement Diagram Factory Service
**Assigned to:** Backend Developer
**Estimated Time:** 6 hours
**Dependencies:** Tasks 1.1-1.8

**File:** `backend/app/services/diagram_factory_service.py`

**Code Specification:**

```python
class DiagramFactoryService:
    """Orchestrates diagram generation workflow."""

    async def start_clarification(
        self,
        user_id: str,
        conversation_id: str,
        initial_prompt: str,
        diagram_type: str
    ) -> Dict[str, Any]:
        """Initialize clarification workflow."""
        pass

    async def submit_clarification_response(
        self,
        session_id: str,
        user_response: str
    ) -> Dict[str, Any]:
        """Process user response in clarification loop."""
        pass

    async def get_clarification_status(
        self,
        session_id: str
    ) -> Dict[str, Any]:
        """Get current clarification status (for polling)."""
        pass

    async def auto_refine_diagram(
        self,
        session_id: str
    ) -> Dict[str, Any]:
        """Automatically refine diagram code."""
        pass

    async def manual_render(
        self,
        session_id: str,
        diagram_code: str
    ) -> Dict[str, Any]:
        """Render manually edited diagram code."""
        pass

    async def restart_clarification(
        self,
        session_id: str
    ) -> Dict[str, Any]:
        """Restart clarification workflow."""
        pass

    async def get_session(
        self,
        session_id: str
    ) -> Dict[str, Any]:
        """Retrieve full session state (for resume)."""
        pass
```

**Features:**
- LangGraph integration
- Session management
- Error handling
- Logging and monitoring

**Tests Required:**
- All public methods
- Error scenarios
- Session lifecycle
- Concurrent operations

**Acceptance Criteria:**
- All methods working
- Proper error handling
- Session state consistency
- 95%+ test coverage

---

### Task 2.2: Add Configuration for Diagram Factory
**Assigned to:** Backend Developer
**Estimated Time:** 1 hour
**Dependencies:** None

**File:** `backend/app/core/config.py` (UPDATE)

**Add Fields:**
```python
# Diagram Factory Configuration
diagram_factory_enabled: bool = True
diagram_timeout: int = 30
diagram_max_refinements: int = 3
diagram_languages: List[str] = ["Mermaid", "D2", "PlantUML"]
diagram_default_language: str = "Mermaid"

# Tool Paths
d2_path: str = "d2"
mmdc_path: str = "mmdc"
plantuml_path: str = "plantuml"

# LLM Settings for Diagram Generation
diagram_llm_provider: str = "anthropic"
diagram_llm_model: str = "claude-3-haiku"
diagram_llm_temperature: float = 0.2

# Session Management
diagram_session_ttl: int = 3600
diagram_session_max_history: int = 50
```

**Acceptance Criteria:**
- All fields added with defaults
- Environment variable overrides work
- Validation on startup
- Documentation updated

---

## Phase 3: Backend API Endpoints (Week 4)

### Task 3.1: Implement Diagram Endpoints
**Assigned to:** Backend Developer
**Estimated Time:** 6 hours
**Dependencies:** Tasks 2.1, 2.2

**File:** `backend/app/api/v1/endpoints/diagram.py` (NEW)

**Endpoints to Implement:**

1. **POST /api/v1/diagram/start**
   - Initialize session
   - Return session_id + first question

2. **GET /api/v1/diagram/stream/{session_id}** (SSE)
   - Stream clarification questions
   - Stream generation/validation events
   - Stream final diagram

3. **POST /api/v1/diagram/clarify**
   - Submit user response
   - Trigger next node
   - Return status

4. **POST /api/v1/diagram/render**
   - Render manually edited code
   - Return SVG + validation status

5. **POST /api/v1/diagram/restart**
   - Restart clarification
   - Return new first question

6. **GET /api/v1/diagram/session/{session_id}**
   - Retrieve full session state
   - For resume functionality

7. **GET /api/v1/diagram/{session_id}/download**
   - Download diagram (PNG/SVG/PDF)

**Pydantic Models:**
```python
class DiagramStartRequest(BaseModel):
    initial_prompt: str
    diagram_type: Literal["Mermaid", "D2", "PlantUML"]

class DiagramClarifyRequest(BaseModel):
    session_id: str
    response: str

class DiagramRenderRequest(BaseModel):
    session_id: str
    diagram_code: str
```

**Tests Required:**
- All endpoints respond correctly
- Error handling
- SSE streaming
- File downloads
- Authentication/authorization

**Acceptance Criteria:**
- All 7 endpoints implemented
- Proper error responses
- OpenAPI docs auto-generated
- 100% endpoint test coverage

---

### Task 3.2: Implement SSE Event Streaming
**Assigned to:** Backend Developer
**Estimated Time:** 4 hours
**Dependencies:** Task 3.1

**File:** `backend/app/api/v1/endpoints/diagram.py` (UPDATE)

**Events to Stream:**

```python
# Event types:
- "clarification_question" → {"question": str}
- "clarification_complete" → {"final_design_summary": str}
- "code_generated" → {"diagram_code": str, "language": str}
- "validation_error" → {"error": str, "recovery_suggestions": List[str]}
- "diagram_ready" → {"svg_output": str, "code": str}
```

**Implementation:**
- Use FastAPI StreamingResponse
- Proper SSE formatting
- Keepalive pings
- Error event handling

**Tests Required:**
- Events stream correctly
- Client disconnection handling
- Timeout handling
- Multiple concurrent streams

**Acceptance Criteria:**
- All events stream in correct format
- Proper SSE format compliance
- Client-side compatible
- Load tested with 10+ concurrent clients

---

## Phase 4: Frontend Implementation (Weeks 5-6)

### Task 4.1: Set Up Frontend Directory Structure
**Assigned to:** Frontend Developer
**Estimated Time:** 1 hour
**Dependencies:** None

**Directory Structure:**
```
frontend/src/components/DiagramWizard/
├── DiagramWizard.tsx
├── Panel1_Chat.tsx
├── Panel2_Preview.tsx
├── Panel3_CodeEditor.tsx
├── hooks/
│   ├── useSSEStream.ts
│   ├── useDiagramSession.ts
│   └── useDiagramState.ts
├── services/
│   ├── diagramApi.ts
│   └── sse.ts
├── types/
│   └── diagram.ts
└── styles/
    └── diagram-wizard.css
```

**Acceptance Criteria:**
- All directories and files created
- Proper TypeScript configuration
- No import errors

---

### Task 4.2: Define TypeScript Types
**Assigned to:** Frontend Developer
**Estimated Time:** 2 hours
**Dependencies:** Task 4.1

**File:** `frontend/src/components/DiagramWizard/types/diagram.ts`

**Types to Define:**
```typescript
// Diagram types
export type DiagramType = "Mermaid" | "D2" | "PlantUML";

// Session state
export type SessionState =
  | "initialized"
  | "input_phase"
  | "clarifying"
  | "generating"
  | "validating"
  | "validation_error"
  | "rendering"
  | "ready"
  | "edit_mode"
  | "completed"
  | "error";

// API responses
export interface DiagramStartResponse {
  session_id: string;
  status: string;
  message: string;
}

export interface ClarificationQuestion {
  question: string;
}

export interface DiagramCode {
  diagram_code: string;
  language: DiagramType;
}

// SSE events
export interface SSEEvent {
  type: string;
  data: any;
}

// Session data
export interface DiagramSession {
  session_id: string;
  created_at: string;
  expires_at: string;
  diagram_type: DiagramType;
  initial_prompt: string;
  clarification_history: Array<{
    role: "user" | "ai";
    content: string;
  }>;
  current_state: SessionState;
  diagram_code: string;
  svg_output: string;
}
```

**Acceptance Criteria:**
- All types properly defined
- Matches backend API contracts
- No TypeScript errors

---

### Task 4.3: Implement SSE Stream Hook
**Assigned to:** Frontend Developer
**Estimated Time:** 3 hours
**Dependencies:** Task 4.2

**File:** `frontend/src/components/DiagramWizard/hooks/useSSEStream.ts`

**Hook Specification:**
```typescript
export interface UseSSEStreamOptions {
  sessionId: string;
  onEvent: (event: SSEEvent) => void;
  onError: (error: Error) => void;
  authToken?: string;
}

export function useSSEStream(options: UseSSEStreamOptions) {
  // - Open SSE connection on mount
  // - Parse incoming events
  // - Call onEvent callback for each event
  // - Handle connection errors
  // - Cleanup on unmount
  // - Auto-reconnect on disconnect

  return {
    isConnected: boolean;
    error: Error | null;
    close: () => void;
  };
}
```

**Features:**
- Automatic reconnection
- Error handling
- Proper cleanup
- Event parsing

**Tests Required:**
- Connection establishment
- Event parsing
- Disconnection handling
- Reconnection logic

**Acceptance Criteria:**
- Connects to SSE endpoint
- Parses events correctly
- Handles errors gracefully
- Cleans up resources

---

### Task 4.4: Implement Diagram Session State Hook
**Assigned to:** Frontend Developer
**Estimated Time:** 3 hours
**Dependencies:** Task 4.3

**File:** `frontend/src/components/DiagramWizard/hooks/useDiagramSession.ts`

**Hook Specification:**
```typescript
export function useDiagramSession(sessionId: string) {
  // - Fetch session state on load
  // - Handle resume functionality
  // - Track clarification history
  // - Manage diagram code
  // - Track SVG output

  return {
    session: DiagramSession | null;
    loading: boolean;
    error: Error | null;
    refreshSession: () => Promise<void>;
  };
}
```

**Features:**
- Fetches session from backend
- Updates local state
- Handles resume

**Acceptance Criteria:**
- Loads session correctly
- Updates on changes
- Handles errors

---

### Task 4.5: Implement Diagram State Machine Hook
**Assigned to:** Frontend Developer
**Estimated Time:** 4 hours
**Dependencies:** Tasks 4.3, 4.4

**File:** `frontend/src/components/DiagramWizard/hooks/useDiagramState.ts`

**Hook Specification:**
```typescript
export function useDiagramState() {
  // - Manage wizard state machine
  // - Track current phase
  // - Update on events
  // - Manage transitions

  return {
    currentState: SessionState;
    phase: "clarifying" | "generating" | "validating" | "rendering" | "ready";
    transitionTo: (state: SessionState) => void;
    updateFromEvent: (event: SSEEvent) => void;
  };
}
```

**State Transitions:**
- Input → Clarifying → Generating → Validating → Rendering → Ready
- Validation Error → Edit Mode → Validating
- Validation Error → Clarifying (restart)

**Acceptance Criteria:**
- Proper state transitions
- Matches backend state machine
- No invalid transitions

---

### Task 4.6: Implement API Client Service
**Assigned to:** Frontend Developer
**Estimated Time:** 3 hours
**Dependencies:** Task 4.2

**File:** `frontend/src/components/DiagramWizard/services/diagramApi.ts`

**Functions to Implement:**
```typescript
export const diagramApi = {
  // Start new diagram session
  startDiagram: (prompt: string, type: DiagramType) => Promise<DiagramStartResponse>;

  // Submit clarification response
  submitClarification: (sessionId: string, response: string) => Promise<any>;

  // Render edited code
  renderCode: (sessionId: string, code: string) => Promise<any>;

  // Restart clarification
  restartClarification: (sessionId: string) => Promise<any>;

  // Get session state
  getSession: (sessionId: string) => Promise<DiagramSession>;

  // Download diagram
  downloadDiagram: (sessionId: string, format: "svg" | "png" | "pdf") => Promise<Blob>;
};
```

**Features:**
- Proper error handling
- Base URL configuration
- Auth token inclusion
- Type-safe responses

**Acceptance Criteria:**
- All API methods work
- Proper error handling
- Types are correct

---

### Task 4.7: Implement Panel 1 - Chat Panel Component
**Assigned to:** Frontend Developer
**Estimated Time:** 4 hours
**Dependencies:** Tasks 4.5, 4.6

**File:** `frontend/src/components/DiagramWizard/Panel1_Chat.tsx`

**Features:**
- Display initial prompt input (read-only after submission)
- Display clarification Q&A history
- Input field for responses
- Submit button (or Ctrl+Enter)
- Phase indicator ("Clarifying requirements...")
- Restart button
- Close button

**Props:**
```typescript
interface Panel1Props {
  sessionId: string;
  clarificationHistory: Array<{role: "user" | "ai"; content: string}>;
  currentPhase: string;
  isLoading: boolean;
  onSubmitResponse: (response: string) => Promise<void>;
  onRestart: () => Promise<void>;
  onClose: () => void;
}
```

**UI Layout:**
```
┌─ Panel 1: Chat ────┐
│                    │
│ [Close]            │
│                    │
│ Q: Initial prompt? │
│                    │
│ A: User response   │
│                    │
│ Q: Next question?  │
│                    │
│ [Input field...]   │
│ [Submit] [Restart] │
│                    │
│ Clarifying... ✓    │
│                    │
└────────────────────┘
```

**Acceptance Criteria:**
- Displays all elements
- Input field works
- Submit triggers callback
- Scrollable history
- Phase indicator shows

---

### Task 4.8: Implement Panel 2 - Preview Panel Component
**Assigned to:** Frontend Developer
**Estimated Time:** 3 hours
**Dependencies:** Tasks 4.2

**File:** `frontend/src/components/DiagramWizard/Panel2_Preview.tsx`

**Features:**
- Display SVG diagram
- Download button (PNG/SVG/PDF)
- Display errors if validation fails
- Show recovery suggestions
- Loading state
- Centered SVG with proper scaling

**Props:**
```typescript
interface Panel2Props {
  svgOutput?: string;
  error?: string;
  recoverySuggestions?: string[];
  currentPhase: string;
  isLoading: boolean;
  onDownload: (format: "svg" | "png" | "pdf") => Promise<void>;
}
```

**UI Layout:**
```
┌─ Panel 2: Preview ────────┐
│                           │
│        [SVG Diagram]      │
│                           │
│ [Download ▼]              │
│   - SVG                   │
│   - PNG                   │
│   - PDF                   │
│                           │
│ Rendering diagram...      │
│                           │
│ Error: Syntax error       │
│ Recovery:                 │
│ • Check brackets          │
│ • Review syntax           │
│                           │
└───────────────────────────┘
```

**Acceptance Criteria:**
- SVG renders correctly
- Download button works
- Error messages display
- Loading state shows
- Proper sizing/scaling

---

### Task 4.9: Implement Panel 3 - Code Editor Component
**Assigned to:** Frontend Developer
**Estimated Time:** 5 hours
**Dependencies:** Tasks 4.2

**File:** `frontend/src/components/DiagramWizard/Panel3_CodeEditor.tsx`

**Features:**
- Code editor with syntax highlighting (use monaco-editor or similar)
- Line numbers
- Read-only until diagram is ready
- Edit mode when ready
- Ctrl+S to submit changes
- Live preview updates as user types
- Language detection (Mermaid/D2/PlantUML)

**Props:**
```typescript
interface Panel3Props {
  diagramCode: string;
  diagramType: DiagramType;
  isEditable: boolean;
  isLoading: boolean;
  onCodeChange: (code: string) => Promise<void>;
  onSaveCode?: () => void;
}
```

**UI Layout:**
```
┌─ Panel 3: Code ────────────────┐
│                                │
│ 1  | diagram {                 │
│ 2  |   A -> B                  │
│ 3  |   B -> C                  │
│ 4  | }                          │
│                                │
│ Language: Mermaid (dropdown)   │
│ [Save] [Copy] [Revert]         │
│                                │
└────────────────────────────────┘
```

**Dependencies:**
- monaco-editor OR
- react-simple-code-editor

**Acceptance Criteria:**
- Code displays with syntax highlighting
- Editable in ready state
- Keyboard shortcuts work
- Changes trigger re-render in Panel 2
- Language selector works

---

### Task 4.10: Implement Main DiagramWizard Component
**Assigned to:** Frontend Developer
**Estimated Time:** 4 hours
**Dependencies:** Tasks 4.7, 4.8, 4.9

**File:** `frontend/src/components/DiagramWizard/DiagramWizard.tsx`

**Features:**
- 3-panel layout (25/40/35 split)
- Manages overall state
- Coordinates between panels
- SSE stream handling
- Session management
- Error boundary

**Props:**
```typescript
interface DiagramWizardProps {
  onClose: () => void;
  conversationId?: string;
  userId?: string;
}
```

**UI Layout:**
```
┌─────────────────────────────────────────┐
│  Diagram Wizard ✕                       │
├──────────┬──────────────┬───────────────┤
│ Panel 1  │  Panel 2     │  Panel 3      │
│  (25%)   │   (40%)      │   (35%)       │
│          │              │               │
│          │              │               │
│          │              │               │
│          │              │               │
│          │              │               │
│          │              │               │
│          │              │               │
└──────────┴──────────────┴───────────────┘
```

**Acceptance Criteria:**
- 3 panels render correctly
- Proper sizing
- All state flows work
- SSE connected
- No memory leaks

---

### Task 4.11: Implement Styling
**Assigned to:** Frontend Developer
**Estimated Time:** 3 hours
**Dependencies:** Task 4.10

**File:** `frontend/src/components/DiagramWizard/styles/diagram-wizard.css`

**Requirements:**
- 3-panel layout responsive
- Panel 1: Chat scrollable, input at bottom
- Panel 2: SVG centered, buttons above/below
- Panel 3: Code editor with syntax highlighting
- Dark/light theme support
- Proper spacing and typography
- Mobile view (if applicable)
- Accessibility (proper contrast, focus states)

**Acceptance Criteria:**
- Layout matches specification
- Responsive and usable
- Accessible
- Dark/light theme works

---

### Task 4.12: Add "Diagram Wizard" Button to Main UI
**Assigned to:** Frontend Developer
**Estimated Time:** 2 hours
**Dependencies:** Task 4.10

**Location:** Main chat/conversation component

**Changes:**
- Add button: "🧙 Diagram Wizard"
- Button opens DiagramWizard modal/component
- Button closes when wizard closes
- Properly positioned in toolbar

**Acceptance Criteria:**
- Button visible and clickable
- Opens diagram wizard
- Closes properly

---

## Phase 5: Testing & Documentation (Week 7)

### Task 5.1: Backend Unit Tests
**Assigned to:** Backend Developer
**Estimated Time:** 8 hours
**Dependencies:** All Phase 1-3 tasks

**Test Coverage:**
- [ ] Tool configuration (100%)
- [ ] Session store (100%)
- [ ] Graph nodes (100%)
- [ ] Graph builder (100%)
- [ ] Service methods (95%+)
- [ ] API endpoints (95%+)

**Test Files:**
```
tests/
├── test_app/
│   ├── test_utils/
│   │   └── test_diagram_wizard/
│   │       ├── test_tool_config.py
│   │       ├── test_graph_state.py
│   │       ├── test_nodes.py
│   │       ├── test_session_store.py
│   │       └── test_prompts.py
│   ├── test_services/
│   │   └── test_diagram_factory_service.py
│   └── test_api/
│       └── test_v1/
│           └── test_endpoints/
│               └── test_diagram.py
```

**Acceptance Criteria:**
- 95%+ overall coverage
- All critical paths tested
- Error scenarios covered
- Fixtures provided

---

### Task 5.2: Frontend Unit Tests
**Assigned to:** Frontend Developer
**Estimated Time:** 6 hours
**Dependencies:** All Phase 4 tasks

**Test Coverage:**
- [ ] Hooks (useSSEStream, useDiagramSession, useDiagramState)
- [ ] Components (all 3 panels + main)
- [ ] API client
- [ ] State transitions

**Test Framework:** Jest + React Testing Library

**Acceptance Criteria:**
- 80%+ coverage
- All critical paths tested
- Component behavior verified

---

### Task 5.3: Integration Tests
**Assigned to:** QA/Backend Developer
**Estimated Time:** 8 hours
**Dependencies:** All implementation tasks

**Scenarios to Test:**
- [ ] Full flow: prompt → clarification → generation → validation → render
- [ ] Manual code edit → re-render
- [ ] Restart clarification
- [ ] Session resume
- [ ] Download formats
- [ ] Error scenarios
- [ ] Concurrent sessions

**Tools:** Postman/Insomnia, Jest, Playwright (frontend)

**Acceptance Criteria:**
- All user flows work end-to-end
- Error handling verified
- Performance acceptable

---

### Task 5.4: Security & Performance Review
**Assigned to:** Security Engineer + DevOps
**Estimated Time:** 4 hours
**Dependencies:** All implementation tasks

**Review Checklist:**
- [ ] No SQL injection risks
- [ ] No XSS vulnerabilities
- [ ] No shell command injection
- [ ] File upload/temp file safety
- [ ] Authentication/authorization
- [ ] Rate limiting considerations
- [ ] Performance benchmarks
- [ ] Load testing (100+ concurrent sessions)

**Acceptance Criteria:**
- Security review passed
- No critical issues
- Performance meets SLAs
- Load test successful

---

### Task 5.5: Documentation
**Assigned to:** Technical Writer + Developer
**Estimated Time:** 4 hours
**Dependencies:** All implementation tasks

**Documentation to Create:**
- [ ] API Reference (auto-generated + manual)
- [ ] Frontend Developer Guide
- [ ] Backend Developer Guide
- [ ] Deployment Guide
- [ ] Troubleshooting Guide
- [ ] Architecture Diagram
- [ ] User Guide (for end users)

**Acceptance Criteria:**
- Comprehensive coverage
- Examples provided
- Clear and accurate
- Hosted in docs directory

---

## Phase 6: Staging & Production (Week 8)

### Task 6.1: Deploy to Staging
**Assigned to:** DevOps Engineer
**Estimated Time:** 2 hours
**Dependencies:** All implementation tasks

**Steps:**
- [ ] Build Docker images
- [ ] Deploy backend to staging
- [ ] Deploy frontend to staging
- [ ] Configure environment variables
- [ ] Test health checks
- [ ] Verify monitoring

**Acceptance Criteria:**
- Services running in staging
- Health checks passing
- Logs accessible
- Monitoring configured

---

### Task 6.2: Staging Validation Testing
**Assigned to:** QA Engineer
**Estimated Time:** 6 hours
**Dependencies:** Task 6.1

**Test Plan:**
- [ ] Full user workflows
- [ ] Cross-browser testing (Chrome, Firefox, Safari)
- [ ] SSE connection reliability
- [ ] File downloads work
- [ ] Error messages display
- [ ] Session persistence
- [ ] Performance under load

**Acceptance Criteria:**
- All tests pass
- No critical bugs
- Performance acceptable
- Ready for production

---

### Task 6.3: Production Rollout
**Assigned to:** DevOps Engineer
**Estimated Time:** 2 hours
**Dependencies:** Task 6.2

**Steps:**
- [ ] Deploy to production (feature-flagged)
- [ ] Enable for 10% traffic
- [ ] Monitor error rates
- [ ] Scale to 100%
- [ ] Verify all endpoints
- [ ] Document deployment

**Acceptance Criteria:**
- Smooth rollout
- Error rates normal
- Monitoring active
- Rollback procedure ready

---

### Task 6.4: Post-Deployment Monitoring
**Assigned to:** DevOps/SRE Engineer
**Estimated Time:** Ongoing

**Metrics to Monitor:**
- [ ] API response times (<5s)
- [ ] Error rates (<0.1%)
- [ ] SSE connection stability
- [ ] Session success rate
- [ ] Diagram validation rate
- [ ] User feedback/support tickets

**Acceptance Criteria:**
- All metrics within SLA
- Issues resolved promptly
- Regular reporting

---

## Task Timeline Summary

| Phase | Week | Tasks | Duration |
|-------|------|-------|----------|
| 1: Backend Foundation | 1-2 | 1.1-1.8 | 30 hours |
| 2: Service Integration | 3 | 2.1-2.2 | 7 hours |
| 3: API Endpoints | 4 | 3.1-3.2 | 10 hours |
| 4: Frontend | 5-6 | 4.1-4.12 | 35 hours |
| 5: Testing & Docs | 7 | 5.1-5.5 | 30 hours |
| 6: Deployment | 8 | 6.1-6.4 | 10 hours |
| **TOTAL** | **8 weeks** | **42 tasks** | **~120 hours** |

---

## Resource Allocation

**Recommended Team:**
- 2x Backend Developers
- 1x Backend/Prompt Engineer
- 1x Security Engineer
- 1x Frontend Developer
- 1x QA/Test Engineer
- 1x DevOps Engineer
- 1x Technical Writer

**Total: 7-8 people**

---

## Success Criteria

### Functional Requirements
- ✓ Diagram Wizard button visible and clickable
- ✓ 3-panel layout implemented correctly
- ✓ SSE streaming works for real-time Q&A
- ✓ Type-specific clarification questions work
- ✓ Code generation and validation loop works
- ✓ Manual code editing works
- ✓ Diagram rendering to SVG works
- ✓ Download functionality works (PNG/SVG/PDF)
- ✓ Session persistence (1 hour TTL)
- ✓ Error handling and recovery suggestions

### Quality Requirements
- ✓ 95%+ test coverage (backend)
- ✓ 80%+ test coverage (frontend)
- ✓ Security review passed
- ✓ Performance: <5s end-to-end response time
- ✓ 99.5% uptime SLA
- ✓ Zero hardcoded prompts in code

### Documentation
- ✓ API documentation
- ✓ Developer guides
- ✓ User documentation
- ✓ Deployment guide

---

## Risk Mitigation

| Risk | Probability | Impact | Mitigation |
|------|-------------|--------|-----------|
| LLM API cost spike | Medium | High | Rate limiting, input validation, monitoring |
| Tool unavailability | Low | High | Graceful degradation, fallback messages |
| Session state corruption | Low | High | Async locks, comprehensive testing |
| SSE connection drops | Medium | Medium | Auto-reconnect, polling fallback |
| File handle leaks | Low | Medium | Context managers, comprehensive cleanup |
| Performance degradation | Medium | Medium | Load testing, caching, optimization |

---

## Dependencies Map

```
1.1 Setup Dirs
  ├─→ 1.2 Prompts MD
  │    ├─→ 1.3 Prompt Loader
  │    │    ├─→ 1.7 Nodes
  │    │    │    ├─→ 1.8 Graph Builder
  │    │    │    │    ├─→ 2.1 Service
  │    │    │    │    │    ├─→ 3.1 Endpoints
  │    │    │    │    │    │    └─→ 3.2 SSE Streaming
  │    │    │    │    │    └─→ 4.6 API Client
  │    │    │    │    │         └─→ 4.10 Main Component
  │    │    │    │    │              └─→ 4.12 Button
  │
  ├─→ 1.4 Graph State
  │    ├─→ 1.6 Session Store
  │    │    └─→ 1.7 Nodes
  │
  ├─→ 1.5 Tool Config
  │    └─→ 1.7 Nodes
  │
  └─→ 2.2 Config
       └─→ 3.1 Endpoints

4.1 Frontend Dirs
  ├─→ 4.2 Types
  │    ├─→ 4.3 SSE Hook
  │    ├─→ 4.4 Session Hook
  │    ├─→ 4.5 State Hook
  │    ├─→ 4.6 API Client
  │    ├─→ 4.7 Panel 1
  │    ├─→ 4.8 Panel 2
  │    ├─→ 4.9 Panel 3
  │    └─→ 4.10 Main Component
  │         ├─→ 4.11 Styling
  │         └─→ 4.12 Button
```

---

## Next Steps

1. Assign team members to tasks
2. Create GitHub/GitLab issues for each task
3. Set up sprint planning
4. Begin Phase 1 tasks in parallel where possible
5. Daily standup meetings
6. Weekly progress reviews

