# Whysper System Upgrade Plan
## Integrating Diagram Factory with Web2 Backend

---

## Executive Summary

This document combines the **Whysper Web2 Backend Architecture** with the proposed **Diagram Factory** system (powered by LangGraph) to create an integrated solution for advanced diagram generation within the Whysper platform. The upgrade plan outlines how to seamlessly integrate LLM-driven diagram clarification, generation, validation, and rendering into the existing FastAPI backend.

---

## Table of Contents

1. [Current State Analysis](#current-state-analysis)
2. [Vision & Goals](#vision--goals)
3. [Architecture Integration](#architecture-integration)
4. [Frontend Integration](#frontend-integration)
5. [Implementation Roadmap](#implementation-roadmap)
6. [Technical Specifications](#technical-specifications)
7. [Migration Strategy](#migration-strategy)
8. [Risk Assessment & Mitigation](#risk-assessment--mitigation)
9. [Success Metrics](#success-metrics)

---

## Current State Analysis

### Whysper Web2 Backend (Baseline)

**Strengths:**
- Modern FastAPI framework with async/await support
- Multi-provider AI integration (OpenRouter, Anthropic, OpenAI)
- Modular service-oriented architecture with clear separation of concerns
- Comprehensive testing (59% coverage, 65 tests)
- Production-ready with health checks and monitoring
- Full backward compatibility with legacy frontend

**Current Diagram Capabilities:**
- Basic Mermaid rendering via `mermaid_helpers.py`
- Single-pass diagram generation without validation loop
- Limited error recovery (no refinement mechanism)
- No user clarification workflow

**Limitations:**
- No iterative diagram refinement
- No structured clarification phase for ambiguous requirements
- Limited support for multi-format diagram languages (D2, PlantUML)
- Passive error handling in diagram generation
- No LLM-driven diagram optimization

### Proposed Diagram Factory (Overlay)

**Strengths:**
- LangGraph-based state machine architecture
- Iterative clarification loop before generation
- Validation and refinement cycle
- Multi-language diagram support (D2, Mermaid, PlantUML)
- Extensible tool configuration
- Clear separation of concerns with nodes, prompts, and tooling

**Gaps in Current Design:**
- No integration with FastAPI endpoints
- Missing persistent conversation context
- No user session management
- Security concerns with `shell=True` in subprocess calls
- File cleanup issues on validation failures
- No timeout controls on clarification loops
- PlantUML validation deferred to render time

---

## Vision & Goals

### Primary Objectives

1. **Enhanced Diagram Generation**: Integrate LangGraph-based iterative diagram generation into Whysper backend
2. **User Clarification Workflow**: Implement multi-turn conversation for capturing diagram requirements
3. **Multi-Format Support**: Add D2 and PlantUML alongside existing Mermaid support
4. **Improved Validation**: Implement validation loop with automatic refinement
5. **Seamless Integration**: Maintain Whysper's modular architecture and API design patterns

### Success Criteria

- Diagram generation accuracy improved by 40% (fewer invalid diagrams on first pass)
- 95% of diagrams pass validation within 2 refinement cycles
- Support for 3+ diagram languages (Mermaid, D2, PlantUML)
- API response time <5 seconds for diagram generation (including clarification)
- 100% test coverage for new diagram factory code
- Zero breaking changes to existing API contracts

---

## Architecture Integration

### High-Level Design

```
┌─────────────────────────────────────────────────────────┐
│             FastAPI Application (main.py)               │
├─────────────────────────────────────────────────────────┤
│                                                          │
│  ┌──────────────────────────────────────────────────┐  │
│  │  API Layer (app/api/v1/endpoints/)               │  │
│  │  ├── chat.py        (existing)                  │  │
│  │  ├── mermaid.py     (existing - refactored)     │  │
│  │  ├── diagram.py     (NEW - diagram factory)     │  │
│  │  ├── code.py        (existing)                  │  │
│  │  ├── files.py       (existing)                  │  │
│  │  └── settings.py    (existing)                  │  │
│  └──────────────────────────────────────────────────┘  │
│                         ↓                               │
│  ┌──────────────────────────────────────────────────┐  │
│  │  Services Layer (app/services/)                  │  │
│  │  ├── conversation_service.py (existing)          │  │
│  │  ├── diagram_factory_service.py (NEW)            │  │
│  │  │   ├── Clarification Loop                      │  │
│  │  │   ├── Code Generation                         │  │
│  │  │   ├── Validation Loop                         │  │
│  │  │   └── Rendering Pipeline                      │  │
│  │  ├── file_service.py (existing)                  │  │
│  │  └── theme_service.py (existing)                 │  │
│  └──────────────────────────────────────────────────┘  │
│                         ↓                               │
│  ┌──────────────────────────────────────────────────┐  │
│  │  Utilities & Factory (app/utils/)                │  │
│  │  ├── mermaid_helpers.py (refactored)             │  │
│  │  ├── diagram_factory/               (NEW)        │  │
│  │  │   ├── graph_state.py                          │  │
│  │  │   ├── nodes.py                                │  │
│  │  │   ├── prompts.py                              │  │
│  │  │   ├── tool_config.py                          │  │
│  │  │   └── langgraph_builder.py                    │  │
│  │  ├── code_extraction.py (existing)               │  │
│  │  └── language_detection.py (existing)            │  │
│  └──────────────────────────────────────────────────┘  │
│                                                         │
│  ┌──────────────────────────────────────────────────┐  │
│  │  Configuration (app/core/)                       │  │
│  │  └── config.py (extended with diagram settings)  │  │
│  └──────────────────────────────────────────────────┘  │
│                                                         │
└─────────────────────────────────────────────────────────┘
```

### Key Integration Points

#### 1. API Endpoints (app/api/v1/endpoints/diagram.py)

**New Endpoints:**

```python
POST /api/v1/diagram/start
  - Initiates diagram clarification workflow
  - Returns: session_id, initial_question

POST /api/v1/diagram/clarify
  - Submits user response to clarification question
  - Returns: next_question or ready_status

POST /api/v1/diagram/generate
  - Generates diagram from finalized design summary
  - Returns: diagram_code, language, validation_status

POST /api/v1/diagram/render
  - Renders valid diagram to SVG
  - Returns: svg_output

GET /api/v1/diagram/languages
  - Returns supported diagram languages (D2, Mermaid, PlantUML)

GET /api/v1/diagram/session/{session_id}
  - Retrieves clarification history and current state
```

**Refactored Endpoints (backward compatible):**

```python
POST /api/v1/mermaid/render
  - Now uses diagram factory validation internally
  - Automatically refines on validation failure

POST /api/v1/mermaid/validate
  - Enhanced with D2 and PlantUML support
```

#### 2. Service Layer (app/services/diagram_factory_service.py)

**Core Service Class:**

```python
class DiagramFactoryService:
    """
    Orchestrates LangGraph-based diagram generation workflow.
    Manages clarification, generation, validation, and rendering.
    """

    async def start_clarification(
        self,
        initial_prompt: str,
        target_language: str = "Mermaid"
    ) -> Dict[str, Any]:
        """Initiates the clarification loop."""

    async def submit_clarification_response(
        self,
        session_id: str,
        user_response: str
    ) -> Dict[str, Any]:
        """Processes user response and continues clarification."""

    async def finalize_design(
        self,
        session_id: str
    ) -> str:
        """Returns final design summary when ready."""

    async def generate_diagram_code(
        self,
        session_id: str
    ) -> Dict[str, Any]:
        """Generates diagram code from finalized design."""

    async def validate_and_refine(
        self,
        session_id: str,
        max_refinements: int = 3
    ) -> Dict[str, Any]:
        """Validates code and refines on failure."""

    async def render_diagram(
        self,
        session_id: str
    ) -> str:
        """Renders final valid diagram to SVG."""
```

#### 3. Diagram Factory Utilities (app/utils/diagram_factory/)

**New Modules:**

1. **graph_state.py** - State schema
   - Extends with Whysper-specific fields (user_id, conversation_id, timestamp)
   - Integrates with FastAPI dependency injection

2. **nodes.py** - Node implementations
   - Integrates with conversation_service for AI calls
   - Uses existing config.py for LLM client setup
   - Proper error handling and timeout mechanisms

3. **prompts.py** - LLM prompts
   - Context-aware prompting with conversation history
   - Diagram-specific system instructions
   - Output validation patterns

4. **tool_config.py** - Diagram tool configuration
   - Production-safe subprocess execution (no shell=True)
   - Proper file handling with context managers
   - Timeout enforcement per tool
   - Tool availability detection at startup

5. **langgraph_builder.py** - Graph construction
   - Builds and compiles LangGraph state machine
   - Integrates with FastAPI lifecycle
   - Caching for performance

### Configuration Management (app/core/config.py)

**New Configuration Fields:**

```python
class Settings(BaseSettings):
    # Diagram Factory Configuration
    diagram_factory_enabled: bool = True
    diagram_timeout: int = 30  # seconds
    diagram_max_refinements: int = 3
    diagram_languages: List[str] = ["Mermaid", "D2", "PlantUML"]
    diagram_default_language: str = "Mermaid"

    # Tool Paths
    d2_path: str = "d2"
    mmdc_path: str = "mmdc"
    plantuml_path: str = "plantuml"

    # LLM Settings for Diagram Generation
    diagram_llm_provider: str = "anthropic"  # or openrouter, openai
    diagram_llm_model: str = "claude-3-haiku"
    diagram_llm_temperature: float = 0.2

    # Session Management
    diagram_session_ttl: int = 3600  # seconds
    diagram_session_max_history: int = 50  # messages per session
```

---

## Frontend Integration

This section details the user-facing interface and communication patterns for the Diagram Wizard feature.

### Overview

The Diagram Wizard is a **desktop-only feature** that provides a dedicated UI for generating diagrams through an iterative clarification process. The interface uses a **3-panel layout** with real-time communication via Server-Sent Events (SSE).

### User Flow

**Step 1: Initialize Diagram Wizard**
- User clicks "Diagram Wizard" button in the main UI
- Frontend opens the 3-panel interface
- User enters initial prompt (e.g., "I need a diagram of my e-commerce system")
- User selects diagram type from dropdown: **Mermaid** | **D2** | **PlantUML**
- Frontend sends `POST /api/v1/diagram/start` with prompt + type

**Step 2: Diagram Type-Specific Clarification**
- Backend starts LLM-driven clarification loop
- Questions are **specific to the selected diagram type**
  - Example for **Mermaid**: "What are the main components and their relationships?"
  - Example for **D2**: "What are the external systems and APIs?"
  - Example for **PlantUML sequence**: "What are the main actors and their interactions?"
- Frontend opens SSE stream: `GET /api/v1/diagram/stream/{session_id}`
- Questions arrive via SSE as `event: clarification_question`
- User types responses in Panel 1 (Chat Panel)
- Frontend sends responses via `POST /api/v1/diagram/clarify`

**Step 3: Clarification Complete**
- When LLM is satisfied, it sends `event: clarification_complete` via SSE
- Backend includes `final_design_summary` in the event
- Frontend displays "Generating diagram code..." (Phase indicator)

**Step 4: Code Generation & Validation**
- Backend generates diagram code in the selected format
- Sends `event: code_generated` with the code
- Panel 2 (Preview) shows SVG rendering in real-time
- Panel 3 (Code Editor) shows the raw diagram code
- If validation fails, backend sends `event: validation_error` with error details
- Frontend shows:
  - Actual validation error message
  - Guided recovery suggestions (e.g., "Check syntax in line 5")

**Step 5: Refinement Options**
- User can:
  - **Option A:** Manually edit code in Panel 3 (text editor) → Preview updates in real-time
  - **Option B:** Click "Restart Clarification" → Repeat Step 2 with new questions

**Step 6: Download & Export**
- Once diagram is valid and rendering successfully:
  - Panel 2 shows download button: "Download as PNG | SVG | PDF"
  - User can download the diagram

### 3-Panel Layout

```
┌─────────────────────────────────────────────────────┐
│  Diagram Wizard - [Close X]                         │
├─────────────────┬─────────────────┬─────────────────┤
│                 │                 │                 │
│   PANEL 1       │   PANEL 2       │   PANEL 3       │
│   Chat Panel    │   Preview Panel │   Code Editor   │
│                 │                 │                 │
│  - Initial      │  - Displays SVG │  - Raw diagram  │
│    prompt input │    rendering    │    code         │
│  - Questions &  │  - Real-time    │  - Syntax       │
│    answers      │    updates as   │    highlighting │
│  - Phase        │    code changes │  - Line numbers │
│    indicators   │  - Download btn │  - Edit mode    │
│  - Refresh or   │    (PNG/SVG/    │                 │
│    Restart btns │    PDF)         │                 │
│                 │  - Error msgs   │                 │
│                 │                 │                 │
└─────────────────┴─────────────────┴─────────────────┘
```

### API Endpoints for Frontend

#### 1. Initialize Diagram Session

```http
POST /api/v1/diagram/start
Content-Type: application/json

{
  "initial_prompt": "I need a diagram of my microservices architecture",
  "diagram_type": "D2"
}

Response:
{
  "session_id": "diagram_user123_1730000000",
  "status": "clarification_started",
  "message": "Tell me more about your system..."
}
```

#### 2. Stream Clarification Questions (SSE)

```http
GET /api/v1/diagram/stream/{session_id}

Headers:
- Accept: text/event-stream
- Authorization: Bearer {token}

Events:
  event: clarification_question
  data: {"question": "What are the external dependencies?"}

  event: clarification_complete
  data: {"final_design_summary": "..."}

  event: code_generated
  data: {"diagram_code": "...", "language": "D2"}

  event: validation_error
  data: {"error": "...", "recovery_suggestions": [...]}

  event: diagram_ready
  data: {"svg_output": "...", "code": "..."}
```

#### 3. Submit Clarification Response

```http
POST /api/v1/diagram/clarify
Content-Type: application/json

{
  "session_id": "diagram_user123_1730000000",
  "response": "We have 5 microservices communicating via Kafka"
}

Response:
{
  "status": "response_received",
  "next_action": "awaiting_clarification" | "generating_code"
}
```

#### 4. Render Diagram (Manual Code Edit)

```http
POST /api/v1/diagram/render
Content-Type: application/json

{
  "session_id": "diagram_user123_1730000000",
  "diagram_code": "diagram { ... }"
}

Response:
{
  "success": true,
  "svg_output": "...",
  "validation_status": "valid"
}
```

#### 5. Restart Clarification

```http
POST /api/v1/diagram/restart
Content-Type: application/json

{
  "session_id": "diagram_user123_1730000000"
}

Response:
{
  "status": "clarification_restarted",
  "message": "Let's refine the design. What's the first thing to change?"
}
```

#### 6. Get Session State (for resume)

```http
GET /api/v1/diagram/session/{session_id}

Response:
{
  "session_id": "diagram_user123_1730000000",
  "created_at": "2024-11-08T10:30:00Z",
  "expires_at": "2024-11-08T11:30:00Z",
  "diagram_type": "D2",
  "initial_prompt": "...",
  "clarification_history": [
    {"role": "ai", "content": "Tell me about..."},
    {"role": "user", "content": "We have..."}
  ],
  "current_state": "diagram_ready", // or "clarifying", "generating", "validating", etc.
  "diagram_code": "...",
  "svg_output": "..."
}
```

#### 7. Download Diagram

```http
GET /api/v1/diagram/{session_id}/download?format=svg

Response:
- Content-Type: image/svg+xml (or image/png, application/pdf)
- Binary file content
```

### Frontend State Management

**Session State Machine:**

```
┌─────────────────────────────────────────────────────────┐
│  Diagram Wizard State Machine                           │
└─────────────────────────────────────────────────────────┘

  [Initialized]
       ↓
  [Input Phase]
   (user enters prompt + chooses type)
       ↓
  [Clarifying]
   (SSE receives questions, user answers)
   ├─ Display: "Clarifying requirements..."
   ├─ Panel 1: Chat with Q&A
   └─ Can: Restart at any time
       ↓
  [Generating]
   (backend generates code)
   ├─ Display: "Generating diagram code..."
   └─ Waiting for SSE: code_generated event
       ↓
  [Validating]
   (backend validates code)
   ├─ Display: "Validating syntax..."
   └─ Waiting for SSE: diagram_ready or validation_error
       ↓
  [Validation Error]
   ├─ Display: Error message + recovery suggestions
   ├─ Options: Auto-refine or restart clarification
   └─ Can: Edit code manually
       ↓
  [Rendering]
   (backend renders to SVG)
   ├─ Display: "Rendering diagram..."
   ├─ Panel 2: SVG preview appears
   └─ Panel 3: Code editor populated
       ↓
  [Ready]
   ├─ Display: "Diagram complete!"
   ├─ Panel 2: Full SVG with download button
   ├─ Panel 3: Editable code with syntax highlighting
   └─ Can: Edit code, restart, or download

  [Edit Mode] ← From [Ready]
   ├─ User edits Panel 3 code
   ├─ On change: POST /diagram/render
   ├─ Panel 2: Live preview updates
   └─ Return to [Ready] when valid
```

### Loading Indicators (Phase-Based)

Frontend displays current phase as a simple status message:

- "Clarifying requirements..." - During clarification loop
- "Generating diagram code..." - During code generation
- "Validating syntax..." - During validation
- "Rendering diagram..." - During SVG rendering
- "Diagram complete!" - Ready state

No estimated times or progress bars—just indicate which phase is active.

### Error Handling & Recovery

**Validation Error Display:**

```
┌─────────────────────────────────────────┐
│ ⚠ Diagram Validation Failed             │
├─────────────────────────────────────────┤
│                                         │
│ Error: "Syntax error on line 5"         │
│ Expected: bracket closing               │
│                                         │
│ Recovery Suggestions:                   │
│ • Check closing brackets on line 5      │
│ • Ensure all identifiers are quoted     │
│ • Review D2 syntax documentation        │
│                                         │
│ [Edit Code] [Restart Clarification]     │
│                                         │
└─────────────────────────────────────────┘
```

**Error Classification & Suggestions:**

| Error Type | Suggestion |
|------------|-----------|
| Syntax Error | "Check closing brackets and quotes" |
| Missing Element | "Ensure all referenced nodes are defined" |
| Invalid Reference | "Check that all variable names are correct" |
| Tool Timeout | "Diagram is too complex, simplify and retry" |

### Session Persistence

- Session ID stored in browser `sessionStorage` (not localStorage)
- Session lasts **1 hour** on backend
- If user closes Diagram Wizard and returns within 1 hour:
  - Click "Resume Session" → `GET /api/v1/diagram/session/{session_id}`
  - Full state restored (clarification history, code, preview)
- After 1 hour: Session expires, user starts fresh

### Responsive Design Considerations

- **Desktop-only** - Optimize for 1920×1080+ screens
- **Panel sizing:**
  - Panel 1 (Chat): 25% width, scrollable
  - Panel 2 (Preview): 40% width, centered SVG
  - Panel 3 (Code): 35% width, monospace font
- **Minimum supported:** 1400px width

### Accessibility Features

- All buttons have `aria-labels`
- Keyboard shortcuts:
  - `Ctrl+Enter` to submit response in Panel 1
  - `Ctrl+S` to download diagram
  - `Esc` to close wizard
- Code editor uses proper syntax highlighting
- Error messages readable by screen readers

---

## Implementation Roadmap

### Phase 1: Foundation (Weeks 1-2)

**Objectives:**
- Set up diagram factory utility structure
- Implement tool configuration with security hardening
- Create graph state and basic node stubs
- Add configuration to Settings

**Deliverables:**
1. Create `app/utils/diagram_factory/` directory structure
2. Implement `tool_config.py` with safe subprocess execution
3. Implement `graph_state.py` with TypedDict schema
4. Add diagram factory configuration to `app/core/config.py`
5. Add tests for tool configuration

**Success Criteria:**
- All tools (D2, mermaid-cli, PlantUML) detectable at startup
- No shell=True usage in subprocess calls
- Proper file cleanup with context managers
- Configuration validates on startup

### Phase 2: Core Nodes & LangGraph (Weeks 3-4)

**Objectives:**
- Implement all five nodes (clarify, generate, validate, refine, render)
- Build LangGraph state machine
- Integrate with existing AI provider system
- Implement proper error handling and timeouts

**Deliverables:**
1. `prompts.py` with context-aware clarification and generation prompts
2. `nodes.py` with all five node functions
3. `langgraph_builder.py` with graph compilation
4. Integration with `conversation_service.py` for LLM calls
5. Comprehensive node unit tests
6. Integration tests for graph flow

**Success Criteria:**
- All nodes execute correctly in isolation
- Graph compiles without errors
- Clarification loop terminates within configurable timeout
- Validation loop completes with max refinements
- 100% test coverage for nodes

### Phase 3: Service Layer Integration (Week 5)

**Objectives:**
- Create `diagram_factory_service.py`
- Implement session management
- Add conversation context integration
- Implement cleanup and resource management

**Deliverables:**
1. `diagram_factory_service.py` with all public methods
2. Session state management (in-memory or Redis)
3. Integration with user and conversation context
4. Error handling and logging
5. Service-level unit tests
6. Integration tests with mocked LLM responses

**Success Criteria:**
- Service supports multi-user concurrent sessions
- Sessions persist clarification history
- Proper cleanup on timeout or completion
- All service methods properly documented

### Phase 4: API Endpoints (Week 6)

**Objectives:**
- Create diagram endpoints in FastAPI
- Implement backward-compatible mermaid endpoint updates
- Add WebSocket support for real-time clarification (optional Phase 2)
- Generate OpenAPI documentation

**Deliverables:**
1. `app/api/v1/endpoints/diagram.py` with all new endpoints
2. Updated `mermaid.py` to use diagram factory validation
3. Request/response models with Pydantic
4. Proper error handling and status codes
5. Endpoint integration tests
6. API documentation

**Success Criteria:**
- All endpoints respond correctly
- Error responses match existing patterns
- API documentation auto-generates
- Backward compatibility maintained
- 100% endpoint test coverage

### Phase 5: Testing & Documentation (Week 7)

**Objectives:**
- Comprehensive testing across all layers
- Performance benchmarking
- Documentation and guides
- Security audit

**Deliverables:**
1. Fixture library for diagram testing
2. End-to-end test scenarios
3. Performance benchmarks
4. Security review and fixes
5. API guide for diagram factory endpoints
6. Configuration guide
7. Troubleshooting guide

**Success Criteria:**
- 95%+ overall test coverage
- All security issues resolved
- Performance benchmarks meet SLAs
- Documentation complete and clear

### Phase 6: Production Deployment (Week 8)

**Objectives:**
- Staging validation
- Production rollout
- Monitoring setup
- Training and support

**Deliverables:**
1. Staging environment testing
2. Production configuration templates
3. Monitoring alerts and dashboards
4. Rollback procedures
5. Changelog and release notes

**Success Criteria:**
- Zero critical issues in staging
- Smooth production deployment
- Monitoring capturing all metrics
- Team trained on new system

---

## Technical Specifications

### 1. Security Hardening (Critical)

#### Subprocess Execution (tool_config.py)

**Current Issue:**
```python
# UNSAFE - DO NOT USE
result = subprocess.run(
    command,
    shell=True,  # Vulnerable to injection
    ...
)
```

**Improved Implementation:**
```python
import shlex
import subprocess
from pathlib import Path
from typing import Tuple

class DiagramToolRunner:
    """Safely executes diagram rendering tools."""

    TOOL_PATHS = {
        "d2": "/usr/bin/d2",
        "mmdc": "/usr/local/bin/mmdc",
        "plantuml": "/usr/local/bin/plantuml"
    }

    @staticmethod
    def validate_tool_available(tool: str) -> bool:
        """Check if tool is available and in whitelist."""
        path = DiagramToolRunner.TOOL_PATHS.get(tool)
        if not path:
            return False
        return Path(path).exists() and os.access(path, os.X_OK)

    @staticmethod
    def run_tool(
        tool: str,
        args: List[str],
        timeout: int = 30
    ) -> Tuple[bool, str]:
        """
        Safely executes tool with strict argument validation.

        Args:
            tool: Tool name (d2, mmdc, plantuml)
            args: List of arguments (properly validated)
            timeout: Execution timeout in seconds

        Returns:
            (success: bool, output: str)
        """
        # Whitelist tools
        if tool not in DiagramToolRunner.TOOL_PATHS:
            return False, f"Unknown tool: {tool}"

        # Whitelist arguments (no shell metacharacters)
        for arg in args:
            if any(c in arg for c in ['$', '`', '|', ';', '&', '>', '<', '\n']):
                return False, f"Forbidden character in argument: {arg}"

        tool_path = DiagramToolRunner.TOOL_PATHS[tool]

        try:
            result = subprocess.run(
                [tool_path] + args,  # NO shell=True
                capture_output=True,
                text=True,
                timeout=timeout,
                cwd=tempfile.gettempdir()  # Restrict working directory
            )

            if result.returncode == 0:
                return True, result.stdout
            else:
                return False, result.stderr or result.stdout

        except subprocess.TimeoutExpired:
            return False, f"Timeout after {timeout}s"
        except Exception as e:
            return False, f"Execution error: {str(e)}"
```

#### File Handling (nodes.py)

**Proper Resource Management:**
```python
import tempfile
import contextlib
from pathlib import Path

@contextlib.contextmanager
def managed_temp_file(content: str, suffix: str):
    """Context manager for safe temp file handling."""
    temp_file = None
    try:
        with tempfile.NamedTemporaryFile(
            mode='w',
            suffix=suffix,
            delete=False,
            encoding='utf-8'
        ) as f:
            f.write(content)
            temp_file = f.name
        yield temp_file
    finally:
        if temp_file and Path(temp_file).exists():
            Path(temp_file).unlink(missing_ok=True)

# Usage in validate_code node:
def validate_code(state: GraphState) -> Dict[str, Any]:
    code = state['diagram_code']
    lang = state['target_language']

    with managed_temp_file(code, '.mmd') as temp_path:
        success, output = DiagramToolRunner.run_tool(
            'mmdc',
            ['--validate', temp_path]
        )

    return {
        'is_valid': success,
        'validation_error': output if not success else ''
    }
```

### 2. Timeout Management (Critical)

**Clarification Loop Timeout:**
```python
import asyncio
from datetime import datetime, timedelta

class ClarificationTimeout:
    """Manages clarification loop timeout."""

    def __init__(self, session_id: str, timeout_seconds: int = 300):
        self.session_id = session_id
        self.timeout_seconds = timeout_seconds
        self.started_at = datetime.utcnow()

    def is_expired(self) -> bool:
        """Check if clarification has exceeded timeout."""
        elapsed = (datetime.utcnow() - self.started_at).total_seconds()
        return elapsed > self.timeout_seconds

    def get_remaining(self) -> int:
        """Get remaining time in seconds."""
        elapsed = (datetime.utcnow() - self.started_at).total_seconds()
        return max(0, self.timeout_seconds - int(elapsed))

# In clarify_prompt node:
async def clarify_prompt(state: GraphState) -> Dict[str, Any]:
    timeout = ClarificationTimeout(
        state['session_id'],
        timeout_seconds=300
    )

    if timeout.is_expired():
        return {
            'llm_ready': True,
            'final_design_summary': 'TIMEOUT: Using provided design with clarifications so far.',
            'clarification_timeout': True
        }

    # Continue with normal clarification
    ...
```

### 3. Session Management

**In-Memory Session Store:**
```python
from typing import Dict, Any
import json
from datetime import datetime, timedelta

class DiagramSessionStore:
    """Thread-safe session management for diagram factory."""

    def __init__(self, ttl_seconds: int = 3600):
        self._sessions: Dict[str, Dict[str, Any]] = {}
        self._ttl = ttl_seconds
        self._lock = asyncio.Lock()

    async def create_session(
        self,
        user_id: str,
        conversation_id: str,
        initial_prompt: str,
        target_language: str = "Mermaid"
    ) -> str:
        """Create new diagram session."""
        async with self._lock:
            session_id = f"diagram_{user_id}_{int(time.time())}"
            self._sessions[session_id] = {
                'user_id': user_id,
                'conversation_id': conversation_id,
                'created_at': datetime.utcnow(),
                'expires_at': datetime.utcnow() + timedelta(seconds=self._ttl),
                'initial_prompt': initial_prompt,
                'target_language': target_language,
                'state': {},  # GraphState content
                'history': [{'role': 'user', 'content': initial_prompt}]
            }
            return session_id

    async def get_session(self, session_id: str) -> Dict[str, Any]:
        """Retrieve session, checking expiration."""
        async with self._lock:
            session = self._sessions.get(session_id)
            if not session:
                raise ValueError(f"Session not found: {session_id}")

            if datetime.utcnow() > session['expires_at']:
                del self._sessions[session_id]
                raise ValueError(f"Session expired: {session_id}")

            return session

    async def update_session(
        self,
        session_id: str,
        updates: Dict[str, Any]
    ) -> None:
        """Update session state."""
        async with self._lock:
            session = self._sessions.get(session_id)
            if not session:
                raise ValueError(f"Session not found: {session_id}")
            session.update(updates)

    async def delete_session(self, session_id: str) -> None:
        """Delete session."""
        async with self._lock:
            self._sessions.pop(session_id, None)

    async def cleanup_expired(self) -> int:
        """Remove expired sessions. Returns count cleaned."""
        async with self._lock:
            now = datetime.utcnow()
            expired = [
                sid for sid, sess in self._sessions.items()
                if now > sess['expires_at']
            ]
            for sid in expired:
                del self._sessions[sid]
            return len(expired)
```

### 4. Error Handling & Recovery

**Validation Error Classification:**
```python
from enum import Enum

class ValidationErrorType(str, Enum):
    SYNTAX_ERROR = "syntax_error"
    MISSING_ELEMENT = "missing_element"
    INVALID_REFERENCE = "invalid_reference"
    TOOL_ERROR = "tool_error"
    TIMEOUT = "timeout"
    UNKNOWN = "unknown"

def classify_validation_error(error_output: str) -> ValidationErrorType:
    """Classify validation error for targeted refinement."""
    error_lower = error_output.lower()

    if 'syntax' in error_lower or 'parse' in error_lower:
        return ValidationErrorType.SYNTAX_ERROR
    elif 'undefined' in error_lower or 'not found' in error_lower:
        return ValidationErrorType.MISSING_ELEMENT
    elif 'reference' in error_lower or 'unknown' in error_lower:
        return ValidationErrorType.INVALID_REFERENCE
    elif 'timeout' in error_lower:
        return ValidationErrorType.TIMEOUT
    else:
        return ValidationErrorType.UNKNOWN

# Update REFINE_PROMPT based on error type:
REFINE_PROMPT_TEMPLATE = """
The diagram generation failed with a {error_type} error:

Error Details:
{validation_error}

Original Design:
{final_design_summary}

Invalid Code:
{diagram_code}

Correction Instructions:
Based on the {error_type} error type, please:
1. Analyze the error in the context of {target_language} syntax
2. Identify the root cause in the original design or code
3. Provide corrected {target_language} code

Return ONLY the corrected code block without explanation.
"""
```

---

## Migration Strategy

### Phase A: Dual System (Week 1-2)

**Goal:** Run both systems in parallel, validate new system

```python
# In mermaid.py endpoints:

@router.post("/render")
async def render_mermaid(request: MermaidRenderRequest):
    """
    Enhanced render with fallback to old system.
    """
    try:
        # Try new diagram factory system
        if settings.diagram_factory_enabled:
            result = await diagram_factory_service.render_simple(
                code=request.code,
                theme=request.theme,
                language="Mermaid"
            )
            # Log result for comparison
            logger.info(f"diagram_factory result: {result['success']}")
            return result
    except Exception as e:
        logger.warning(f"Diagram factory failed: {e}")

    # Fallback to legacy system
    return await legacy_mermaid_render(request)
```

### Phase B: Gradual Cutover (Week 3-4)

**Goal:** Shift traffic to new system, monitor quality

```python
# In config.py:
diagram_factory_traffic_percentage: int = 10  # Start at 10%

# In endpoint:
import random

if random.random() < settings.diagram_factory_traffic_percentage / 100:
    # Use new system
    return await diagram_factory_service.render(...)
else:
    # Use legacy system
    return await legacy_mermaid_render(...)
```

### Phase C: Complete Migration (Week 5+)

**Goal:** Full transition, deprecate legacy code

```python
# In config.py:
diagram_factory_traffic_percentage: int = 100
legacy_mermaid_enabled: bool = False  # Deprecate

# Remove legacy code paths in Week 6
```

---

## Risk Assessment & Mitigation

### Critical Risks

| Risk | Impact | Mitigation |
|------|--------|-----------|
| **Subprocess Injection** | Security breach | Use argument lists, no shell=True; whitelist tools |
| **File Handle Leaks** | Resource exhaustion | Context managers; cleanup on error |
| **Clarification Loop Hangs** | User stuck | Timeout mechanism; max questions limit |
| **LLM API Overuse** | Cost spike | Rate limiting; input validation; caching |
| **Validation Failure Loops** | Infinite refinement | Max refinements limit; escalation to user |

### High Risks

| Risk | Impact | Mitigation |
|------|--------|-----------|
| **Tool Not Available** | Service failure | Tool detection at startup; graceful degradation |
| **Memory Leak** | Performance degradation | Session cleanup; resource limits |
| **Session Concurrency** | Data corruption | Async locks; thread-safe storage |
| **Large Diagram Timeout** | Timeout errors | Configurable timeouts per complexity |

### Medium Risks

| Risk | Impact | Mitigation |
|------|--------|-----------|
| **Third-party Tool Updates** | Incompatibility | Version pinning; compatibility tests |
| **API Rate Limits** | Service degradation | Exponential backoff; retry logic |
| **Incomplete Clarification** | Poor diagram quality | Max refinements; user confirmation |

---

## Success Metrics

### Quantitative Metrics

1. **Diagram Generation Success Rate**
   - Target: 95% valid diagrams within 2 refinement cycles
   - Measurement: Count of diagrams passing validation / total attempts

2. **Performance (Response Time)**
   - Target: <5 seconds for complete flow (clarification + generation + validation)
   - Measurement: End-to-end latency from API request to SVG output

3. **User Satisfaction**
   - Target: 90%+ of diagrams match user intent on first pass
   - Measurement: User feedback survey; refinement count histogram

4. **System Reliability**
   - Target: 99.5% uptime for diagram endpoints
   - Measurement: Monitoring dashboards; error rate tracking

5. **Code Quality**
   - Target: 100% test coverage for new code
   - Measurement: Coverage reports; code review checklist

6. **Cost Efficiency**
   - Target: <$0.01 per diagram generation (LLM API cost)
   - Measurement: LLM token usage tracking; cost attribution

### Qualitative Metrics

1. **Architecture Quality**
   - Clear separation of concerns maintained
   - Easy to extend with new diagram languages
   - Security best practices followed

2. **Documentation**
   - API documentation auto-generated and clear
   - Implementation guide for developers
   - Troubleshooting guide for operators

3. **Developer Experience**
   - Clear error messages for debugging
   - Easy to test and mock
   - Good logging and observability

---

## Deployment Checklist

### Pre-Deployment (Staging)

- [ ] All unit tests pass (100% coverage target)
- [ ] Integration tests pass
- [ ] Performance benchmarks meet SLAs
- [ ] Security audit completed and issues resolved
- [ ] Load testing with concurrent users
- [ ] Backup and rollback procedures documented
- [ ] Monitoring alerts configured
- [ ] Team trained on new system

### Deployment Steps

1. Deploy new code to production (feature-flagged disabled)
2. Enable diagram factory for 10% of requests
3. Monitor error rates and performance for 24 hours
4. Increase to 25% traffic for next 24 hours
5. Increase to 50% traffic for next 24 hours
6. Roll out to 100% traffic
7. Monitor for 1 week before considering migration complete

### Post-Deployment

- [ ] All success metrics tracking
- [ ] Legacy code still available for rollback
- [ ] Support team trained on new error scenarios
- [ ] Documentation updated
- [ ] Customer communication sent

---

## Conclusion

This upgrade plan provides a comprehensive roadmap for integrating LangGraph-powered Diagram Factory with Whysper's Web2 backend. The phased approach mitigates risk, maintains backward compatibility, and ensures high quality through rigorous testing and validation.

The integration will significantly enhance Whysper's diagram generation capabilities while maintaining the architectural principles and code quality standards of the existing system.

**Total Estimated Timeline:** 8 weeks
**Total Estimated Effort:** 320 person-hours
**Risk Level:** Medium (with proper mitigation)
**Expected ROI:** 40% improvement in diagram accuracy; 10x better user experience
