# Module Comparison Report: DiagramWizard vs ArchitectureGenStudio

**Date:** 2025-11-15
**Purpose:** Comprehensive comparison of two diagram generation modules in the Whysper project

---

## Executive Summary

Both **DiagramWizard** and **ArchitectureGenStudio** are AI-powered diagram generation modules within the same codebase. While they share common infrastructure (provider system, LangGraph, SSE streaming), they serve different use cases with distinct user experiences:

- **DiagramWizard**: Conversational, wizard-style interface with guided clarification loops
- **ArchitectureGenStudio**: Professional studio interface with three-column layout and agent-based generation

---

## Table of Contents

1. [Frontend Comparison](#frontend-comparison)
2. [Backend Comparison](#backend-comparison)
3. [Shared Infrastructure](#shared-infrastructure)
4. [Key Differences Summary](#key-differences-summary)
5. [Recommendations](#recommendations)

---

## Frontend Comparison

### DiagramWizard Frontend

**Location:** `frontend/src/components/DiagramWizard/DiagramWizard.tsx`

#### Architecture

- **Component Type:** React Functional Component with hooks
- **UI Framework:** Ant Design (antd)
- **State Management:** Local state with custom hook `useDiagramSession`
- **File Count:** 4+ files (main component, panels, hooks, CSS)
- **Lines of Code:** ~960 lines (main component)

#### UI Layout

**Phase-Based Wizard Interface:**
1. **Phase 0: Describe** - Initial system description input
2. **Phase 1: Analyze** - AI analysis and clarification conversation
3. **Phase 2: Generate** - Diagram code generation
4. **Phase 3: Visualize** - Final diagram rendering

**Layout Structure:**
- **Header:** Title, session ID, running status indicator
- **Progress Steps:** Visual stepper showing current phase
- **Main Content:**
  - Initial screen: Large text area for system description
  - Conversation mode: Two-panel layout (chat history + response panel)
  - Multi-panel mode: Three panels (Chat, Preview, Code Editor)
- **Action Bar:** Download SVG, Copy Code, End Session buttons

#### Key Features

1. **Conversational Flow:**
   - Chat-style message interface (user/assistant bubbles)
   - Persistent conversation history display
   - AI assistant responses with "View full response" modal
   - Clarification questions with visual feedback
   - Information progress indicator (entities, actions, structure)

2. **AI Scoring System:**
   - Information score (0-3): Entities, Actions, Structure
   - AI clarity score (0-10)
   - Word count tracking (minimum 12 words)
   - Visual status indicators (checkmarks, colors)
   - "Can proceed" vs "needs more info" states

3. **Diagram Type Selection:**
   - Four options presented after analysis:
     - AI Recommendation (auto)
     - Mermaid (flowcharts, sequences)
     - D2 (architecture, systems)
     - PlantUML (UML, databases)
   - Icon-based selection buttons

4. **Phase Management:**
   - Automatic phase progression based on LangGraph state
   - No manual phase skipping
   - Visual progress indicators (steps component)
   - Status messages aligned with phases

5. **Session Management:**
   - Session ID display (truncated)
   - Running status spinner
   - Session cleanup on end
   - State reset on new session

6. **Real-Time Updates:**
   - SSE integration via `useDiagramSession` hook
   - Live conversation updates
   - Progress notifications (Ant Design messages)
   - Automatic UI state synchronization

#### Component Structure

```
DiagramWizard/
├── DiagramWizard.tsx (main component)
├── diagram-wizard.module.css (styles)
├── hooks/
│   └── useDiagramSession.ts (session management)
└── panels/
    ├── Panel1_Chat.tsx (chat interface)
    ├── Panel2_Preview.tsx (SVG preview)
    └── Panel3_CodeEditor.tsx (code editing)
```

#### State Management

**Local State Variables:**
- `diagramType`: Selected diagram type (Mermaid, D2, PlantUML)
- `userInput`: Initial prompt text
- `isInitializing`: Loading state for session start
- `currentPhase`: Current wizard phase (0-3)
- `isInAnalysisPhase`: Flag for conversation mode
- `clarificationInput`: User's clarification response
- `score`: AI assessment score (0-10)
- `assistantResponses`: Cached AI responses with metadata
- `selectedResponse`: Modal state for viewing full responses

**Hook-Managed State (useDiagramSession):**
- `sessionId`: Unique session identifier
- `status`: Full session status object
- `loading`: Loading indicator
- `error`: Error state
- Actions: `startSession`, `submitClarification`, `renderDiagram`, `approveRender`, `endSession`

#### User Experience Flow

1. User enters system description
2. Clicks "Start Conversation"
3. AI analyzes and asks clarification questions
4. User responds with additional details
5. Information score increases with each response
6. When ready, user chooses to proceed or add more details
7. User selects diagram type (or accepts AI recommendation)
8. AI generates diagram code
9. Diagram renders automatically
10. User can download SVG or copy code

#### Strengths

- Guided, beginner-friendly experience
- Clear visual feedback on information completeness
- Prevents premature diagram generation
- Chat-style interface feels natural
- Excellent progress visibility
- Mobile-friendly single-column layout

#### Limitations

- Limited manual control over process
- Cannot skip clarification phase
- No simultaneous view of chat + diagram + code
- Less suitable for expert users
- No code editing during generation

---

### ArchitectureGenStudio Frontend

**Location:** `frontend/src/components/architectureGenStudio/index.tsx`

#### Architecture

- **Component Type:** React Functional Component with hooks
- **UI Framework:** Ant Design (antd)
- **State Management:** Custom hook `useArchitectureStudioState` with centralized state
- **File Count:** 40+ files (modular component structure)
- **Lines of Code:** ~315 lines (main component, highly modular)

#### UI Layout

**Three-Column Studio Layout:**
- **Header:** Agent selector, notifications, branding, user menu
- **Left Column:** Prompt editor, agent options, submit button
- **Center Column:** Diagram rendering area with zoom controls
- **Right Column:** Code editor, validate/render buttons, error panel
- **Footer:** Status, SSE messages, system links

**Layout Features:**
- Resizable columns with width persistence
- Collapsible columns for focus mode
- Responsive design with minimum widths
- Accessibility features (skip links, ARIA labels)

#### Key Features

1. **Agent System:**
   - Dynamic agent loading from backend
   - Agent-specific options/prompts
   - Agent selector in header
   - Options list in left column
   - Agent context persists across sessions

2. **Multi-View Workspace:**
   - Simultaneous view of prompts, diagrams, and code
   - Independent column operations
   - Focus mode (collapse unused columns)
   - Synchronized state across columns

3. **Prompt Management:**
   - Rich text editor for prompts
   - Unsaved changes tracking
   - Agent option templates
   - Pre-configured prompts per agent

4. **Diagram Interaction:**
   - Live diagram preview
   - Zoom controls (in/out/reset/fit)
   - Export options (SVG, PNG, PDF)
   - Diagram type selector
   - Loading states with spinners

5. **Code Editing:**
   - Syntax-highlighted code editor
   - Manual code editing
   - Validate button (check code without rendering)
   - Render button (generate diagram from code)
   - Unsaved changes indicator
   - Validation error panel

6. **SSE Integration:**
   - Real-time message streaming
   - Unread message count
   - Connection status indicator
   - Message filtering by session

7. **State Persistence:**
   - LocalStorage integration via `useLocalStorage` hook
   - Column widths saved
   - Collapsed states saved
   - Agent selection saved

#### Component Structure

```
architectureGenStudio/
├── index.tsx (main orchestrator)
├── types/
│   ├── index.ts
│   └── architectureStudio.ts
├── hooks/
│   ├── index.ts
│   ├── useArchitectureStudioState.ts (state management)
│   ├── useAPIClient.ts (API integration)
│   ├── useSSE.ts (SSE streaming)
│   └── useLocalStorage.ts (persistence)
├── components/
│   ├── Header/
│   │   ├── Header.tsx
│   │   ├── AgentSelector.tsx
│   │   ├── BrandingSection.tsx
│   │   ├── NavigationMenu.tsx
│   │   ├── NotificationBadge.tsx
│   │   └── UserAccountMenu.tsx
│   ├── LeftColumn/
│   │   ├── LeftColumn.tsx
│   │   ├── PromptEditor.tsx
│   │   ├── AgentOptionList.tsx
│   │   └── SubmitButton.tsx
│   ├── CenterColumn/
│   │   ├── CenterColumn.tsx
│   │   ├── DiagramRenderingArea.tsx
│   │   └── ZoomControls.tsx
│   ├── RightColumn/
│   │   ├── RightColumn.tsx
│   │   ├── CodeEditor.tsx
│   │   ├── ValidateButton.tsx
│   │   ├── RenderButton.tsx
│   │   └── ErrorPanel.tsx
│   └── Footer/
│       ├── Footer.tsx
│       ├── LinksColumn.tsx
│       ├── StatusColumn.tsx
│       └── SSEMessagesColumn.tsx
├── styles/
│   └── architectureStudio.module.css
├── __tests__/
│   ├── integration.test.ts
│   ├── errorHandling.test.ts
│   ├── stateSynchronization.test.ts
│   ├── componentTesting.guide.md
│   ├── workflowTesting.guide.md
│   └── accessibility.audit.md
├── README.md
├── CHANGELOG.md
└── DEPLOYMENT_GUIDE.md
```

#### State Management

**Centralized State Hook (useArchitectureStudioState):**

```typescript
interface ArchitectureStudioState {
  // Agent management
  agents: Agent[]
  currentAgent: Agent | null
  agentsLoading: boolean
  agentsError: string | null
  currentAgentOptions: AgentOption[]
  selectedAgentOption: AgentOption | null
  optionsLoading: boolean
  optionsError: string | null

  // Layout
  columnWidths: { left: number; center: number; right: number }
  collapsedColumns: { left: boolean; center: boolean; right: boolean }
  zoomLevel: number

  // Content
  currentPrompt: string
  promptHasUnsavedChanges: boolean
  codeEditorContent: string
  codeEditorHasUnsavedChanges: boolean
  selectedDiagramType: string
  generatedDiagrams: Map<string, DiagramData>

  // Processing
  isProcessing: boolean
  isValidating: boolean
  isRendering: boolean
  processingRequestId: string | null
  processingError: string | null
  validationResult: ValidationResult | null

  // Status
  currentStatus: { message: string; type: string }
  sseMessages: SSEMessage[]
}
```

**API Client Hook (useAPIClient):**
- Centralized API calls
- Error handling
- Token management
- Request cancellation

**SSE Hook (useSSE):**
- Connection management
- Message queue
- Auto-reconnect
- Session filtering

#### User Experience Flow

1. User selects agent from header dropdown
2. Agent options load in left column
3. User selects option or writes custom prompt
4. User clicks Submit
5. AI generates diagram (SSE updates in footer)
6. Diagram appears in center column
7. Code appears in right column
8. User can:
   - Edit code and re-render
   - Validate code before rendering
   - Export diagram in multiple formats
   - Zoom/pan diagram
   - Adjust column sizes for focus

#### Strengths

- Professional, IDE-like experience
- Excellent for expert users
- Simultaneous view of all artifacts
- Manual control over every step
- Highly modular and maintainable codebase
- Comprehensive test coverage
- Accessibility features built-in
- State persistence across sessions
- Advanced error handling

#### Limitations

- Steeper learning curve for beginners
- No guided clarification process
- Requires more screen real estate
- Agent system adds complexity
- Less mobile-friendly (needs wide screen)

---

## Backend Comparison

### DiagramWizard Backend

**Primary Files:**
- `backend/app/api/v1/endpoints/diagram.py` (API endpoints)
- `backend/app/services/diagram_factory_service.py` (orchestration)
- `backend/app/utils/diagram_wizard/` (LangGraph workflow)

#### API Endpoints

**Diagram Wizard Specific:**
```
POST   /api/v1/diagram/start              # Start new session
GET    /api/v1/diagram/stream/{session_id} # SSE updates
POST   /api/v1/diagram/clarify            # Submit clarification
POST   /api/v1/diagram/approve_render     # Approve rendering
POST   /api/v1/diagram/render             # Render diagram
GET    /api/v1/diagram/{session_id}       # Get status
DELETE /api/v1/diagram/{session_id}       # End session
```

#### Core Services

**DiagramFactoryService:**
- **Purpose:** Orchestrates LangGraph-based diagram generation
- **Session Management:** In-memory store with TTL expiration
- **Workflow Execution:** Async task-based LangGraph runner
- **Information Scoring:** Entity/action/structure keyword analysis
- **Update Delivery:** AsyncIO queue-based SSE streaming

**DiagramSession Class:**
```python
class DiagramSession:
    session_id: str
    history: List[Tuple[str, str]]  # Role-content pairs
    clarifications: List[str]
    diagram_code: str
    svg_output: str
    update_queue: asyncio.Queue
    graph_state: GraphState
    graph_task: asyncio.Task
    is_running: bool
```

**DiagramSessionStore:**
- Thread-safe session storage
- TTL-based expiration (default 1 hour)
- Lock-based concurrency control
- User-based session listing

#### LangGraph Workflow

**Graph State:**
```python
class GraphState(TypedDict):
    session_id: str
    design_prompt: str
    diagram_type: DiagramType
    clarification_history: List[Dict[str, str]]
    clarity_scores: List[int]
    llm_ready: bool
    user_confirmed_ready: bool
    awaiting_user_confirmation: bool
    final_design_summary: str
    diagram_code: str
    json_representation: Dict
    validation_error: Optional[str]
    is_valid: bool
    refinement_attempt: int
    svg_output: str
    current_state: SessionState
    _update_callback: Callable
```

**Workflow Nodes:**
1. `analyze_request` - Initial analysis with scoring
2. `clarify_prompt` - Iterative clarification loop (max 10 questions or 5 min)
3. `determine_diagram_type` - Keyword-based type detection
4. `generate_code` - LLM-based code generation from JSON
5. `validate_code` - Provider-based validation
6. `refine_code` - LLM-based error correction (max 3 attempts)
7. `render_diagram` - Final SVG/PNG rendering

**Workflow Flow:**
```
Entry: analyze_request
  ↓
clarify_prompt (loop until llm_ready=true)
  ↓
determine_diagram_type
  ↓
generate_code
  ↓
validate_code
  ↓ (if valid)
render_diagram → END
  ↓ (if invalid)
refine_code → validate_code (retry)
```

**Conditional Routing:**
- `route_to_diagram_type_determination()`: Checks `llm_ready` flag
- `route_validation()`: Checks `is_valid` flag

#### Information Scoring System

**Categories:**
- **Entity words** (1.5x weight): system, database, service, user, component, module, API
- **Action words** (1.0x weight): login, process, send, validate, authenticate, fetch, store
- **Structure words** (1.2x weight): architecture, workflow, relationship, hierarchy, flow

**Thresholds:**
- **Minimum info**: 2/3 categories present + 15 words
- **Good info**: 3/3 categories present + 20 words

**Scoring Logic:**
```python
info_score = (
    (1 if entities_found else 0) +
    (1 if actions_found else 0) +
    (1 if structure_found else 0)
)

has_minimum_info = info_score >= 2 and word_count >= 15
has_good_info = info_score >= 3 and word_count >= 20
```

#### SSE Implementation

**Event Types:**
- `analyzing` - Initial analysis phase
- `clarifying` - Asking clarification question
- `can_proceed` - Sufficient info, awaiting confirmation
- `type_selection` - Diagram type selection phase
- `generating` - Code generation in progress
- `code_generated` - Code ready
- `validating` - Validation in progress
- `rendering` - Rendering in progress
- `completed` - Success
- `error` - Error occurred

**Update Payload:**
```python
{
    "status": "clarifying",
    "message": "What are the main user roles?",
    "session_id": "uuid",
    "score": 6,
    "clarity_score": 7,
    "score_info": {
        "info_score": 2,
        "entities": true,
        "actions": true,
        "structure": false,
        "word_count": 18,
        "has_minimum_info": true,
        "has_good_info": false
    },
    "json_representation": {...},
    "history": [["user", "..."], ["assistant", "..."]]
}
```

#### Key Features

1. **Persistent Schema Context:**
   - Combined ANALYZE + CLARIFY prompts
   - JSON schema maintained across all clarification turns
   - Ensures LLM remembers structure requirements

2. **User Confirmation Flow:**
   - AI sets `llm_ready=true` when satisfied
   - Sets `awaiting_user_confirmation=true`
   - Waits for user to explicitly approve
   - User can continue adding details instead

3. **Keyword-Based Type Detection:**
   - `KeywordScorer` analyzes text
   - Scores each diagram type (Mermaid, D2, PlantUML)
   - Returns confidence percentages
   - Determines best match

4. **Three-Tier Error Correction:**
   - Tier 1: Provider validation (if available)
   - Tier 2: Pattern-based auto-fix
   - Tier 3: LLM-based correction with context

5. **Session Lifecycle Management:**
   - Automatic cleanup on completion
   - TTL-based expiration for abandoned sessions
   - Graceful error recovery
   - Session state persistence

#### Configuration

**Prompts:**
- `ANALYSE_CLARIFY.md` - Combined analyze + clarify prompt
- `GENERATE_PROMPTS.md` - Code generation (per diagram type)
- `REFINE_PROMPTS.md` - Code refinement (per diagram type)
- `JSON_GENERATION_PROMPT.md` - Structured representation

**Keywords:**
- `keywords.json` - Diagram type keywords with weights
- Categories: diagram_specific, structure, entities, actions

**Environment Variables:**
- `API_KEY` - LLM API key
- `PROVIDER` - AI provider (openrouter, anthropic, etc.)
- `DEFAULT_MODEL` - Model selection
- `MAX_TOKENS` - Generation limit
- `TEMPERATURE` - Creativity setting

#### Integration Points

**Shared with ArchStudio:**
- Provider registry for diagram rendering
- Base diagram provider classes
- LLM correction service
- Validation utilities
- SSE infrastructure (partially)

**Unique to DiagramWizard:**
- DiagramFactoryService
- DiagramSessionStore
- LangGraph workflow nodes and builder
- Information scoring system
- Clarification loop logic

---

### ArchitectureGenStudio Backend

**Primary Files:**
- `backend/app/api/v1/endpoints/diagram_provider.py` (unified API)
- `backend/app/services/conversation_service.py` (conversation management)
- `backend/diagrams/provider_registry.py` (provider system)

#### API Endpoints

**Architecture Gen Studio Specific:**
```
POST /api/v1/diagrams/v2/generate    # Agent-based generation
GET  /api/v1/diagrams/v2/stream      # SSE stream for generation
GET  /api/v1/diagrams/v2/providers   # List providers
GET  /api/v1/diagrams/v2/health      # Health check
```

**Shared Diagram API:**
```
POST /api/v1/diagrams/v2/render      # Render with validation
POST /api/v1/diagrams/v2/validate    # Validate code
GET  /api/v1/diagrams/v2/download    # Download rendered diagram
```

**Conversation API:**
```
POST /api/v1/chat                    # Non-streaming chat
POST /api/v1/chat/stream             # Streaming chat
GET  /api/v1/logs/stream             # Real-time log streaming
POST /api/v1/conversations           # Create conversation
GET  /api/v1/conversations/{id}/history  # Get history
POST /api/v1/conversations/{id}/clear    # Clear history
```

#### Core Services

**ConversationService:**
- **Purpose:** Manages multi-turn chat with file context
- **Session Management:** In-memory conversation store
- **AI Integration:** Factory-based provider selection
- **File Context:** Path-safe file loading with persistence
- **System Message Injection:** Agent prompts + file context

**ConversationManager:**
```python
class ConversationManager:
    conversations: Dict[str, ConversationSession]

    def create_conversation(user_id: str) -> str:
        # Creates new session with AI processor

    def add_file(session_id: str, file_path: str):
        # Adds file to context with security checks

    def _inject_system_message(session_id: str):
        # Updates system message with current context
```

**ConversationSession:**
```python
class ConversationSession:
    session_id: str
    user_id: str
    ai_processor: AIProcessor
    conversation_history: List[Dict[str, str]]
    file_context: List[Dict[str, str]]
    app_state: Dict[str, Any]
    file_hash: str  # Detects file context changes
```

#### Agent System

**Agent Prompts:**
- Loaded from `backend/prompts/agents/` directory
- Agent-specific instructions for diagram generation
- System message format with role definition
- Injected into conversation before LLM call

**Agent Workflow:**
1. Frontend selects agent (e.g., "Architecture Diagram Expert")
2. Backend loads agent prompt from file
3. Agent prompt + user prompt combined
4. LLM generates diagram code
5. Code extracted from LLM response
6. Code validated and rendered
7. Result stored in `_pending_requests` dict
8. Frontend polls via SSE stream endpoint

**Agent Options:**
- Pre-configured prompts per agent
- Loaded dynamically from backend
- Frontend displays as selectable options
- User can override with custom prompt

#### Provider System Architecture

**ProviderRegistry (Singleton):**
- Auto-discovers providers from `backend/diagrams/` subdirectories
- Loads `config.json` from each provider folder
- Dynamically imports renderer modules
- Registers providers with capabilities
- Manages provider lifecycle

**Provider Discovery:**
```python
def _discover_providers():
    for provider_dir in (DIAGRAMS_DIR).iterdir():
        if provider_dir.is_dir():
            config_path = provider_dir / "config.json"
            if config_path.exists():
                config = json.loads(config_path.read_text())
                provider = _load_provider_class(provider_dir, config)
                registry.register(provider)
```

**Provider Structure:**
```
backend/diagrams/{provider_id}/
├── config.json          # Metadata and settings
├── {type}_renderer.py   # Implementation
└── README.md            # Documentation
```

**Provider Capabilities:**
- `VALIDATION` - Syntax checking
- `RENDERING` - Code → SVG/PNG
- `AUTO_FIX` - Pattern-based correction
- `LLM_CORRECTION` - AI-powered fixes
- `MULTIPLE_FORMATS` - SVG, PNG, etc.

**Rendering Pipeline:**
```python
def render_with_validation(code, diagram_type, options):
    # 1. Validate code
    validation_result = provider.validate_code(code)

    # 2. Auto-fix if invalid (optional)
    if not validation_result.is_valid and auto_fix:
        code = provider.auto_fix_pattern_based(code)
        validation_result = provider.validate_code(code)

    # 3. LLM correction if still invalid (optional)
    if not validation_result.is_valid and llm_correction:
        code = llm_service.correct_code(code, errors)
        validation_result = provider.validate_code(code)

    # 4. Render to output format
    if validation_result.is_valid:
        result = provider.render(code, output_format)

        # 5. Save to file if requested
        if save_to_file:
            file_path = save_diagram(result.svg, diagram_type)

        return result
```

#### SSE Implementation

**Log Broadcasting:**
- Global `LogBroadcaster` singleton
- Custom logging handler captures INFO logs
- Session-based filtering for privacy
- AsyncIO queue per connected client

**SSE Handler:**
```python
class SSELoggingHandler(logging.Handler):
    def emit(self, record):
        session_id = getattr(record, 'session_id', None)
        if session_id:
            broadcaster.broadcast(session_id, {
                "level": record.levelname,
                "message": record.getMessage(),
                "timestamp": record.created
            })
```

**Client Connection:**
```python
@router.get("/logs/stream")
async def stream_logs(session_id: str):
    queue = asyncio.Queue()
    broadcaster.register(session_id, queue)

    async def event_generator():
        try:
            while True:
                log_entry = await queue.get()
                yield f"data: {json.dumps(log_entry)}\n\n"
        finally:
            broadcaster.unregister(session_id, queue)

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream"
    )
```

**Diagram Generation SSE:**
```python
@router.get("/diagrams/v2/stream")
async def stream_diagram(requestId: str):
    async def event_generator():
        timeout = 300  # 5 minutes
        start_time = time.time()

        while time.time() - start_time < timeout:
            if requestId in _pending_requests:
                result = _pending_requests.pop(requestId)
                yield f"data: {json.dumps(result)}\n\n"
                break

            yield f"data: {json.dumps({'status': 'processing'})}\n\n"
            await asyncio.sleep(1)

    return StreamingResponse(...)
```

#### Key Features

1. **Unified Diagram API:**
   - Single endpoint for all diagram types
   - Consistent request/response format
   - Modular provider backend
   - Extensible for new diagram types

2. **Multi-Provider Support:**
   - Mermaid (CLI v1, Kroki API)
   - D2 (CLI v1, Kroki API)
   - PlantUML (Kroki API)
   - C4 (Kroki API)
   - Structurizr (Kroki API)
   - Easy to add new providers

3. **Three-Tier Validation:**
   - CLI-based validation (when available)
   - Pattern-based validation (fallback)
   - LLM-based correction (optional)

4. **AI Provider Abstraction:**
   - Factory pattern for provider selection
   - Support for: OpenRouter, Anthropic, OpenAI
   - Automatic provider discovery from environment
   - Secure API key management
   - Token usage tracking

5. **File Context Management:**
   - Security-first file loading (path traversal protection)
   - Persistent file context across conversation
   - Change detection via hashing
   - Automatic system message updates

6. **Background Task Processing:**
   - Async task queue for long operations
   - Non-blocking API responses
   - Polling-based result retrieval
   - Timeout handling

7. **Comprehensive Logging:**
   - Structured JSON logging
   - Real-time log streaming
   - Session-based filtering
   - Method call tracing

#### Configuration

**Provider Configuration (`diagrams/config.json`):**
```json
{
  "default_providers": {
    "Mermaid": "mermaidv1",
    "D2": "d2v1",
    "PlantUML": "krokiplantuml"
  },
  "llm_correction": {
    "enabled": true,
    "max_retries": 3
  }
}
```

**Provider-Specific Config:**
```json
{
  "id": "mermaidv1",
  "name": "Mermaid CLI v1",
  "diagram_type": "Mermaid",
  "capabilities": ["VALIDATION", "RENDERING", "AUTO_FIX"],
  "cli_path": "mmdc",
  "cli_args": ["-i", "{input_file}", "-o", "{output_file}"],
  "supported_formats": ["svg", "png"],
  "validation": {
    "patterns": ["graph", "sequenceDiagram", "classDiagram"]
  }
}
```

**Environment Variables:**
- `API_KEY` - LLM API key
- `PROVIDER` - AI provider name
- `DEFAULT_MODEL` - Model selection
- `STATIC_DIR` - Directory for saved diagrams
- `MAX_RETRIES` - Validation retry limit
- `TEMPERATURE` - LLM creativity

#### Integration Points

**Shared with DiagramWizard:**
- Provider registry and base classes
- LLM correction service
- Validation utilities
- Rendering infrastructure
- Configuration management

**Unique to ArchStudio:**
- ConversationService and ConversationManager
- Agent system and prompts
- Log broadcasting with SSE
- Background task processing
- File context management
- Unified diagram API (`/diagrams/v2`)

---

## Shared Infrastructure

Both modules leverage common backend infrastructure, avoiding code duplication:

### 1. Provider Registry System

**Location:** `backend/diagrams/provider_registry.py`

**Shared Functionality:**
- Auto-discovery of diagram providers
- Provider registration and lookup
- Capability management
- Configuration loading
- Provider lifecycle management

**Provider Interface:**
```python
class BaseDiagramProvider:
    def validate_code(code: str) -> ValidationResult
    def render(code: str, format: str) -> RenderResult
    def auto_fix_pattern_based(code: str) -> str
```

### 2. LLM Correction Service

**Location:** `backend/diagrams/llm_correction_service.py`

**Shared Functionality:**
- AI-powered code correction
- Iterative correction with retries
- Provider-specific correction prompts
- Error context analysis

### 3. Base Diagram Provider

**Location:** `backend/diagrams/base_diagram.py`

**Shared Functionality:**
- Common validation logic
- Pattern-based auto-fix
- Output format conversion
- Error handling utilities

### 4. AI Processor Factory

**Location:** `backend/common/ai.py`

**Shared Functionality:**
- Dynamic AI provider loading
- API key management
- Token usage tracking
- Model configuration
- Request/response formatting

### 5. Logging Infrastructure

**Location:** `backend/common/logger.py`

**Shared Functionality:**
- Structured JSON logging
- Context injection (session_id, user_id)
- Log level management
- File and console handlers

### 6. Diagram Providers

**Shared Providers:**
- `mermaidv1` - Mermaid CLI renderer
- `d2v1` - D2 CLI renderer
- `krokimermaid` - Kroki Mermaid API
- `krokid2` - Kroki D2 API
- `krokiplantuml` - Kroki PlantUML API
- `krokic4` - Kroki C4 API
- `krokistructurizr` - Kroki Structurizr API

### 7. Configuration Management

**Location:** `backend/app/core/config.py`

**Shared Functionality:**
- Environment variable loading
- Pydantic-based validation
- Default values
- Type safety

### 8. Security Utilities

**Location:** `backend/app/utils/security.py`

**Shared Functionality:**
- Path traversal protection
- API key masking
- Input sanitization

### 9. SSE Infrastructure (Partially Shared)

**DiagramWizard Approach:**
- Session-specific update queues
- Direct queue-based streaming
- Workflow-triggered updates

**ArchStudio Approach:**
- Global log broadcaster
- Session-filtered log streaming
- Polling-based result retrieval

**Common Patterns:**
- AsyncIO-based streaming
- Keep-alive messages
- Timeout handling
- Graceful disconnection

---

## Key Differences Summary

### Frontend Differences

| Aspect | DiagramWizard | ArchitectureGenStudio |
|--------|--------------|----------------------|
| **Layout** | Wizard-style, phase-based | Three-column studio |
| **User Flow** | Guided, sequential | Flexible, non-linear |
| **Target User** | Beginners, guided workflows | Experts, power users |
| **State Management** | Hook-based local state | Centralized state hook |
| **File Structure** | 4-5 files, monolithic | 40+ files, highly modular |
| **LOC (main)** | ~960 lines | ~315 lines |
| **Columns** | Single column (dynamic) | Three resizable columns |
| **Agent System** | No | Yes (agent selector) |
| **Clarification UI** | Chat bubbles, conversational | Prompt editor, professional |
| **Code Editing** | Post-generation only | During and post-generation |
| **Diagram View** | Tabbed (Preview/Code/JSON) | Simultaneous in center column |
| **Progress Indicator** | Visual stepper with phases | Status bar + SSE messages |
| **Information Scoring** | Prominent visual display | Not shown |
| **Mobile Support** | Better (single column) | Requires wide screen |
| **Accessibility** | Good | Excellent (WCAG compliant) |
| **State Persistence** | No | Yes (localStorage) |
| **Testing** | Minimal | Comprehensive test suite |
| **Documentation** | Basic README | README, CHANGELOG, deployment guide |

### Backend Differences

| Aspect | DiagramWizard | ArchitectureGenStudio |
|--------|--------------|----------------------|
| **API Endpoints** | 7 diagram-specific endpoints | 4 arch-specific + 6 conversation endpoints |
| **Workflow Engine** | LangGraph with 7 nodes | Agent-based with background tasks |
| **Session Management** | DiagramSessionStore | ConversationManager |
| **State Structure** | GraphState (TypedDict) | ConversationSession (class) |
| **Clarification Loop** | Built-in, multi-turn | Not present |
| **Information Scoring** | Keyword-based (entities/actions/structure) | Not used |
| **User Confirmation** | Required before generation | Not required |
| **Diagram Type Detection** | Automatic (keyword scoring) | User/agent selects |
| **SSE Approach** | Update queue per session | Global log broadcaster |
| **File Context** | Not supported | File loading with security |
| **Agent System** | Not present | Agent prompts from files |
| **LLM Integration** | Workflow nodes call LLM | Agent prompts + chat service |
| **Error Correction** | Built into workflow (refine node) | Separate validation endpoint |
| **Session Lifecycle** | Automatic TTL cleanup | Manual management |
| **Background Tasks** | LangGraph async tasks | FastAPI BackgroundTasks |
| **Prompt Management** | Markdown files in wizard utils | Agents directory |
| **Code Complexity** | Higher (state machine logic) | Lower (simple request-response) |

### Workflow Differences

**DiagramWizard Workflow:**
```
User Input
  ↓
AI Analysis (automatic)
  ↓
Clarification Loop (iterative)
  ├─ AI asks questions
  ├─ User responds
  ├─ Score increases
  └─ Continue until AI satisfied
  ↓
User Confirmation (required)
  ↓
Diagram Type Selection (AI suggests, user chooses)
  ↓
Code Generation (automatic)
  ↓
Validation (automatic)
  ↓ (if invalid)
Refinement (automatic, max 3 attempts)
  ↓
Rendering (automatic)
  ↓
Final Diagram
```

**ArchitectureGenStudio Workflow:**
```
Agent Selection (user choice)
  ↓
Prompt Input (user writes or selects option)
  ↓
Submit (user initiated)
  ↓
AI Generation (single-shot)
  ↓
Code + Diagram Display (simultaneous)
  ↓
Optional: User edits code
  ↓
Optional: Validate (user initiated)
  ↓
Optional: Re-render (user initiated)
  ↓
Export (user initiated)
```

### Data Flow Differences

**DiagramWizard:**
```
Frontend                  Backend                    LangGraph
  |                         |                          |
  |-- POST /start --------->|                          |
  |                         |-- create_session ------->|
  |                         |-- run_workflow --------->|
  |<---- session_id --------|                          |
  |                         |                          |
  |-- GET /stream --------->|                          |
  |<---- SSE: analyzing ----|<---- update_callback ----|
  |<---- SSE: clarifying ---|<---- update_callback ----|
  |                         |                          |
  |-- POST /clarify ------->|                          |
  |                         |-- resume_workflow ------>|
  |<---- SSE: generating ---|<---- update_callback ----|
  |<---- SSE: completed ----|<---- update_callback ----|
```

**ArchitectureGenStudio:**
```
Frontend                  Backend                    Provider
  |                         |                          |
  |-- POST /generate ------>|                          |
  |                         |-- background_task ------>|
  |<---- requestId ---------|                          |
  |                         |-- call_llm ------------->|
  |                         |<---- diagram_code -------|
  |-- GET /stream --------->|                          |
  |<---- SSE: processing ---|                          |
  |                         |-- render_diagram ------->|
  |                         |<---- svg_output ---------|
  |<---- SSE: completed ----|                          |
  |                         |                          |
  |-- POST /validate ------>|-- provider.validate ---->|
  |<---- validation_result -|<---- result -------------|
  |                         |                          |
  |-- POST /render -------->|-- provider.render ------>|
  |<---- svg ---------------|<---- svg ----------------|
```

---

## Recommendations

### When to Use DiagramWizard

**Best For:**
- First-time users unfamiliar with diagram syntax
- Complex requirements needing clarification
- Situations where requirements are unclear
- Users who prefer guided workflows
- Mobile or tablet users
- Quick diagram generation without manual editing

**Advantages:**
- Prevents poorly-defined diagrams
- Educational (teaches good requirement gathering)
- Lower cognitive load
- Clear progress visibility
- Better mobile experience

**Use Cases:**
- "I have a vague idea and need help clarifying it"
- "I'm new to diagram creation"
- "I want AI to guide me through the process"
- "I don't know which diagram type to use"

### When to Use ArchitectureGenStudio

**Best For:**
- Expert users familiar with diagram syntax
- Users who know exactly what they want
- Iterative editing and refinement
- Complex diagrams requiring manual tweaks
- Professional/enterprise environments
- Users who want full control

**Advantages:**
- Faster for experienced users
- More control over every step
- Better for iterative refinement
- Professional IDE-like interface
- Advanced features (validate, export, zoom)
- State persistence across sessions

**Use Cases:**
- "I know exactly what diagram I need"
- "I want to manually edit the code"
- "I need to validate before rendering"
- "I want to switch between agents"
- "I need multiple export formats"

### Future Considerations

**Potential Convergence:**
1. **Hybrid Mode:** Allow ArchStudio to optionally use DiagramWizard's clarification flow
2. **Shared Components:** Extract common UI elements (code editor, preview, export)
3. **Unified API:** Merge diagram endpoints under single versioned API
4. **Feature Parity:** Bring best features from each to the other
   - Add agent support to DiagramWizard
   - Add clarification mode to ArchStudio
   - Unified SSE implementation

**Codebase Optimization:**
1. **DRY Principle:** Extract duplicated logic to shared utilities
2. **Component Library:** Create shared UI component library
3. **State Management:** Consider Redux/Zustand for both
4. **Testing:** Unified testing strategy across both

**User Experience:**
1. **Mode Switcher:** Allow users to switch between wizard and studio modes
2. **Preferences:** Remember user's preferred mode
3. **Onboarding:** Show wizard mode to new users, studio to returning users
4. **In-App Guidance:** Tooltips and help system in ArchStudio

---

## Conclusion

Both modules are well-architected and serve distinct purposes:

- **DiagramWizard** excels at **guided, conversational diagram generation** with excellent beginner support through its clarification loop and information scoring system.

- **ArchitectureGenStudio** excels at **professional, flexible diagram creation** with advanced features like agent selection, manual code editing, and simultaneous multi-view layout.

They share substantial backend infrastructure (provider system, LLM services, validation) but differ significantly in user experience and workflow philosophy. The choice between them depends on user expertise, use case complexity, and preference for guidance vs. control.

Both modules demonstrate production-quality code with proper separation of concerns, comprehensive error handling, and extensible architectures. The shared infrastructure enables code reuse and consistent behavior across diagram types.

---

**Report Generated:** 2025-11-15
**Codebase Location:** C:\Code2025\Whysper
**Total Frontend Files Analyzed:** 45+
**Total Backend Files Analyzed:** 50+
