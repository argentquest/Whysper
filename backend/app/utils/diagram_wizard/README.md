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
├── keyword_scorer.py           # Diagram type determination (NEW)
├── prompt_loader.py            # Prompt loading and caching
├── session_store.py            # Session management
└── prompts/                    # Prompt storage (markdown)
    ├── __init__.py
    ├── ANALYZE_PROMPT.md       # Initial analysis prompt (NEW)
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
Seven core LangGraph nodes (async functions):

1. **analyze_request**
   - Initial analysis of user's design prompt
   - Calls LLM to score request fitness to architecture schema (1-10)
   - Generates initial JSON representation (schema-compliant)
   - Always routes to clarify_prompt (no diagram type selected yet)
   - Returns: assessment_score, json_representation

2. **clarify_prompt**
   - Iterative user clarification loop
   - Combines ANALYZE_PROMPT (schema context) + CLARIFY_PROMPTS (loop guidance) for each turn
   - LLM returns clarity_score (1-10) for each turn
   - Tracks clarity_scores list across all turns
   - Sets `llm_ready` flag when clarity_score >= 8
   - Returns: json_representation, final_design_summary, clarity_scores
   - **Context**: Each LLM call includes full schema (~9.3KB) to prevent constraint forgetting

3. **determine_diagram_type**
   - Runs after clarification completes (when llm_ready=True)
   - Uses keyword scoring to analyze final_design_summary
   - Loads base keywords from keywords.json (entity_words, action_words, structure_words)
   - Combines with diagram-specific keywords (flowchart, architecture, class, etc.)
   - Automatically selects best diagram type (no user input)
   - Returns: diagram_type, keyword_scores

4. **generate_code**
   - Generates diagram code from design summary
   - Uses type-specific generation prompts
   - Now has diagram_type available from previous node
   - Returns raw diagram code

5. **validate_code**
   - Validates code using appropriate tool
   - Classifies errors
   - Suggests recovery actions
   - Returns `is_valid` flag

6. **refine_code**
   - Fixes invalid code using LLM
   - Error-specific refinement prompts
   - Increments refinement counter
   - Returns improved code

7. **render_diagram**
   - Renders valid code to SVG
   - Manages temporary files
   - Returns SVG output

### keyword_scorer.py

Automatic diagram type determination (NEW):

- `KeywordScorer` class for text analysis
- Loads base keywords from keywords.json (entity_words, action_words, structure_words)
- Diagram-specific keywords for Mermaid, D2, PlantUML
- Heuristic scoring combining base and diagram-specific keywords
- `determine_diagram_type()`: Analyzes text and returns (DiagramType, scores_dict)
- Used by determine_diagram_type node after clarification completes

### langgraph_builder.py

Builds the state machine graph:

- Registers all nodes (including determine_diagram_type)
- Defines edges and conditional routing
- Compilation and lazy loading
- Graph flow: analyze → clarify (loop) → determine_diagram_type → generate → validate → refine → render

### prompt_loader.py

Dynamic prompt management:

- Loads markdown prompts from prompts/ directory
- Caches prompts in memory for performance
- Supports both section-based extraction and full-file loading
- `get_prompt(name)`: Retrieve prompt by name

### session_store.py

Thread-safe session management:

- Create/read/update/delete operations
- TTL-based expiration (default 1 hour)
- Async lock for thread safety
- Automatic cleanup of expired sessions

### prompts/

All LLM prompts stored as markdown files (NOT hardcoded):

1. **ANALYZE_PROMPT.md** (NEW)
   - Initial request analysis instructions
   - Schema fitness scoring (1-10)
   - JSON representation generation
   - Returns: payload, assessment_score, architecture_json

2. **CLARIFY_PROMPTS.md**
   - Universal clarification prompt (combined with ANALYZE_PROMPT for schema context)
   - One question per turn
   - Clarity scoring (1-10) and JSON evolution
   - Readiness criteria (clarity_score >= 8)
   - Returns: question, clarity_score, ready, json_representation, design_summary
   - **Note**: In clarify_prompt node, this is combined with ANALYZE_PROMPT to provide persistent schema context

3. **GENERATE_PROMPTS.md**
   - Instructions for code generation
   - Format-specific templates (Mermaid, D2, PlantUML)
   - Best practices for each format

4. **REFINE_PROMPTS.md**
   - Error-specific refinement instructions
   - Common issues and fixes
   - Syntax reminders

## Workflow

```
User Input
    ↓
[ANALYZE PHASE]
analyze_request
    - Score request fitness to schema (1-10)
    - Generate initial JSON representation
    - Always route to clarify (no diagram type selected)
    ↓
[CLARIFICATION PHASE] ← → User (via SSE)
clarify_prompt (loop)
    - Ask clarifying questions (type-specific)
    - Track clarity_score for each turn (1-10)
    - Update JSON representation each turn
    - Exit when clarity_score >= 8 (llm_ready=True)
    ↓
[DIAGRAM TYPE DETECTION]
determine_diagram_type
    - Analyze final design summary + JSON metadata
    - Keyword scoring: base keywords + diagram-specific keywords
    - Automatically select best diagram type
    - Return keyword scores for transparency
    ↓
[CODE GENERATION]
generate_code
    - Generate diagram code using determined diagram type
    - Use type-specific generation prompts
    - Return raw diagram code
    ↓
[VALIDATION & REFINEMENT] (loop if invalid)
validate_code
    - Validate diagram code syntax
    - Classify errors
    - Return is_valid flag
    ↓
(is_valid?) → No → refine_code → back to validate (max 3 attempts)
    ↓
Yes → render_diagram
    ↓
[RENDERING]
render_diagram
    - Convert diagram code to SVG
    - Manage temporary files
    ↓
END (svg_output ready)
```

**Key Flow Properties:**
- Diagram type is determined AFTER clarification (not during analysis)
- Clarity scores are tracked throughout clarification to show user progress
- JSON representation evolves through each clarification turn
- Keyword scoring is automatic (no user input needed for diagram type selection)

## Recent Enhancements

### Persistent Schema Context in Clarification Loop

- ANALYZE_PROMPT combined with CLARIFY_PROMPTS in each clarification turn
- LLM sees full schema definition (~7KB) + clarification guidance (~2KB) per turn
- Benefits:
  - Prevents LLM from forgetting schema constraints between turns
  - Ensures consistent enum matching (component types, protocols)
  - Maintains awareness of required vs. optional fields
  - Provides component ID auto-generation rules on every turn
  - ~9.3KB context overhead per turn (acceptable for clarity/consistency tradeoff)

### Clarity Score Tracking

- Added `clarity_scores: List[int]` to GraphState
- Each clarification turn records its clarity_score (1-10)
- Allows users to see improvement progression through clarification loop
- Scores sent to frontend via SSE callbacks for real-time feedback

### Keyword-Based Diagram Type Detection

- **New module**: `keyword_scorer.py`
- Loads base keywords from `backend/app/services/keywords.json`
  - entity_words: user, system, database, service, component, etc.
  - action_words: login, create, update, process, send, etc.
  - structure_words: architecture, workflow, relationship, etc.
- Diagram-specific keywords:
  - Mermaid: flowchart, flow, process, sequence, state, etc.
  - D2: architecture, microservice, infrastructure, deployment, etc.
  - PlantUML: class, inheritance, interface, component, use case, etc.
- Heuristic scoring combines base + diagram-specific keywords
- Automatically selects best diagram type after clarification completes
- Returns keyword scores for transparency to user

### Enhanced Workflow

- **New node**: `determine_diagram_type` (runs after clarification)
- **New prompt**: `ANALYZE_PROMPT.md` for initial request scoring
- **Updated clarification prompts**: Now return JSON with clarity_score each turn
- Flow: analyze → clarify (loop) → determine_type → generate → validate → refine → render

## Integration Points

### Backend Service (app/services/diagram_factory_core.py)
- Orchestrates graph execution
- Handles LLM integration

### Session Store (app/services/diagram_factory_session.py)
- Manages sessions
- Provides public API

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
