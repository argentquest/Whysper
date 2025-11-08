# Diagram Wizard Module

LangGraph-based diagram generation system for Whysper.

## Overview

The Diagram Wizard enables users to generate diagrams through an iterative, AI-driven clarification process. It supports multiple diagram formats (Mermaid, D2, PlantUML) and provides automatic validation and refinement.

## Directory Structure

```
app/utils/diagram_wizard/
├── __init__.py                 # Module initialization
├── README.md                   # This file
├── graph_state.py              # State schema (TypedDict)
├── tool_config.py              # Tool configuration & execution
├── nodes.py                    # LangGraph node implementations
├── langgraph_builder.py        # Graph compilation
├── session_store.py            # Session management
└── prompts/                    # Prompt storage (markdown)
    ├── __init__.py
    ├── CLARIFY_PROMPTS.md      # Clarification prompts
    ├── GENERATE_PROMPTS.md     # Code generation prompts
    └── REFINE_PROMPTS.md       # Refinement prompts
```

## Key Components

### graph_state.py
Defines the central state object (TypedDict) that flows through all nodes:
- Session metadata (session_id, user_id, conversation_id)
- Input (design_prompt, diagram_type)
- Clarification state (history, llm_ready, design_summary)
- Generation/validation state (code, errors, suggestions)
- Output (svg_output)

Enums:
- `DiagramType`: MERMAID, D2, PLANTUML
- `SessionState`: INITIALIZED → CLARIFYING → GENERATING → VALIDATING → RENDERING → READY

### tool_config.py
Safe execution of diagram rendering tools:
- `DiagramToolConfig`: Tool configurations (commands, extensions, timeouts)
- `DiagramToolRunner`: Safe subprocess execution
  - NO shell=True
  - Argument validation
  - Timeout enforcement
  - Proper file cleanup
- `ToolValidationError`: Custom exception

### nodes.py
Five core LangGraph nodes (async functions):

1. **clarify_prompt**
   - Iterative user clarification
   - Type-specific questions
   - Calls LLM with clarification prompts
   - Sets `llm_ready` flag when done

2. **generate_code**
   - Generates diagram code from design summary
   - Uses type-specific generation prompts
   - Returns raw diagram code

3. **validate_code**
   - Validates code using appropriate tool
   - Classifies errors
   - Suggests recovery actions
   - Returns `is_valid` flag

4. **refine_code**
   - Fixes invalid code using LLM
   - Error-specific refinement prompts
   - Increments refinement counter
   - Returns improved code

5. **render_diagram**
   - Renders valid code to SVG
   - Manages temporary files
   - Returns SVG output

### langgraph_builder.py
Builds the state machine graph:
- Registers all nodes
- Defines edges and conditional routing
- Compilation and lazy loading

### session_store.py
Thread-safe session management:
- Create/read/update/delete operations
- TTL-based expiration (default 1 hour)
- Async lock for thread safety
- Automatic cleanup of expired sessions

### prompts/
All LLM prompts stored as markdown files (NOT hardcoded):

1. **CLARIFY_PROMPTS.md**
   - System instructions for clarification phase
   - Type-specific questions for Mermaid, D2, PlantUML
   - Readiness criteria

2. **GENERATE_PROMPTS.md**
   - Instructions for code generation
   - Format-specific templates
   - Best practices for each format

3. **REFINE_PROMPTS.md**
   - Error-specific refinement instructions
   - Common issues and fixes
   - Syntax reminders

## Workflow

```
User Input
    ↓
START (clarify_prompt)
    ↓
[Clarifying] ← → User (via SSE)
    ↓
(llm_ready?) → No → Wait for user response
    ↓
Yes → generate_code
    ↓
[Generating] Generate diagram code
    ↓
validate_code
    ↓
(is_valid?) → No → refine_code → back to validate
    ↓
Yes → render_diagram
    ↓
[Rendering] Convert to SVG
    ↓
END (svg_output ready)
```

## Integration Points

### Backend Service (app/services/diagram_factory_service.py)
- Orchestrates graph execution
- Manages sessions
- Provides public API
- Handles LLM integration

### API Endpoints (app/api/v1/endpoints/diagram.py)
- POST /diagram/start - Initialize session
- GET /diagram/stream/{session_id} - SSE events
- POST /diagram/clarify - Submit responses
- POST /diagram/render - Manual edits
- etc.

### Configuration (app/core/config.py)
- Tool paths (d2, mmdc, plantuml)
- LLM settings
- Session TTL
- Timeout values

## Development Tasks

See `IMPLEMENTATION_PLAN.MD` in the backend root for detailed task breakdown:

**Phase 1: Backend Foundation**
- 1.1-1.8: Setup, prompts, state, tools, nodes, graph

**Phase 2: Service Integration**
- 2.1-2.2: Service class, configuration

**Phase 3: API Endpoints**
- 3.1-3.2: REST endpoints, SSE streaming

**Phase 4: Frontend**
- 4.1-4.12: React components, hooks, styling

**Phase 5: Testing & Docs**
- 5.1-5.5: Unit/integration tests, security review, documentation

**Phase 6: Deployment**
- 6.1-6.4: Staging, production rollout, monitoring

## Key Design Decisions

1. **Prompts in Markdown**: All prompts stored in MD files, loaded at runtime
   - Easier to maintain and iterate
   - Separates content from code
   - Version-control friendly

2. **No shell=True**: Tool execution uses argument lists
   - Prevents command injection
   - More secure and reliable

3. **Async/Await**: All operations are async-ready
   - Scales to thousands of concurrent users
   - Integrates with FastAPI's async model

4. **Session TTL**: 1-hour default lifetime
   - Balances memory usage with usability
   - Auto-cleanup of expired sessions

5. **Error Classification**: Validation errors are categorized
   - Enables targeted refinement
   - Better user feedback

## Testing

### Unit Tests
- Tool configuration and execution
- Session store operations
- Node state transitions
- Error handling

### Integration Tests
- Full workflow (prompt → code → validate → render)
- SSE event streaming
- Session lifecycle
- Concurrent sessions

### Security Tests
- No shell injection possible
- File handle cleanup
- Timeout enforcement

## Monitoring & Observability

Metrics to track:
- Diagram generation success rate
- Average time per phase
- Error rates by type
- User satisfaction

Logs should include:
- Session lifecycle events
- LLM API calls and costs
- Tool execution times
- Validation errors

## Future Enhancements

1. **Caching**: Cache successful diagram patterns
2. **Redis Backend**: Replace in-memory session store
3. **Multi-step Refinement**: Allow more than 3 refinement attempts
4. **Custom Prompts**: Per-organization prompt templates
5. **Analytics**: Track diagram generation patterns
6. **Streaming Generation**: Stream code generation to frontend in real-time

## References

- LangGraph Documentation: https://docs.smith.langchain.com/langgraph
- Mermaid Syntax: https://mermaid.js.org/
- D2 Language: https://d2lang.com/
- PlantUML: https://plantuml.com/
- UPGRADEPLAN.MD: Full system design
- IMPLEMENTATION_PLAN.MD: Detailed task breakdown
