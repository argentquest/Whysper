# Diagram Wizard Implementation - Summary

## What Was Created

A comprehensive implementation plan for integrating LangGraph-based Diagram Factory with Whysper Web2 Backend.

### Documents Created

1. **UPGRADEPLAN.MD** - High-level upgrade strategy
   - Current state analysis (Whysper + Diagram Factory)
   - Vision and goals
   - Architecture integration (backend layers)
   - **Frontend Integration** (3-panel layout, SSE, API endpoints, state management)
   - Implementation roadmap (6 phases, 8 weeks)
   - Technical specifications (security, timeouts, error handling)
   - Migration strategy
   - Risk assessment
   - Success metrics

2. **IMPLEMENTATION_PLAN.MD** - Detailed task breakdown
   - Complete project structure (backend + frontend)
   - **42 specific implementation tasks**
   - Phase-by-phase breakdown (1-8 weeks)
   - Dependencies map
   - Resource allocation (7-8 person team)
   - Success criteria
   - Risk mitigation

### Backend Code Structure Created

```
backend/app/utils/diagram_wizard/
├── __init__.py
├── README.md
├── graph_state.py
├── tool_config.py
├── nodes.py
├── langgraph_builder.py
├── session_store.py
└── prompts/
    ├── __init__.py
    ├── CLARIFY_PROMPTS.md
    ├── GENERATE_PROMPTS.md
    └── REFINE_PROMPTS.md
```

### Key Implementation Files

#### Backend

1. **graph_state.py**
   - `GraphState` TypedDict (central state object)
   - `DiagramType` enum (Mermaid, D2, PlantUML)
   - `SessionState` enum (workflow stages)

2. **tool_config.py**
   - `DiagramToolConfig` - Tool configurations
   - `DiagramToolRunner` - Safe tool execution (NO shell=True)
   - `ToolValidationError` - Custom exception

3. **nodes.py**
   - `clarify_prompt()` - Iterative clarification
   - `generate_code()` - Code generation
   - `validate_code()` - Code validation
   - `refine_code()` - Error correction
   - `render_diagram()` - SVG rendering

4. **langgraph_builder.py**
   - `build_diagram_factory_graph()` - Graph construction
   - `get_diagram_factory_graph()` - Lazy-loaded compiled graph

5. **session_store.py**
   - `DiagramSessionStore` - Thread-safe session management
   - Async create/read/update/delete
   - TTL-based expiration (1 hour default)

6. **prompts/** - ALL prompts stored as markdown
   - `CLARIFY_PROMPTS.md` - Diagram-type-specific questions
   - `GENERATE_PROMPTS.md` - Code generation templates
   - `REFINE_PROMPTS.md` - Error-specific refinement instructions

#### Frontend (Specified in IMPLEMENTATION_PLAN.MD)

1. **DiagramWizard.tsx** - Main component (3-panel layout)
2. **Panel1_Chat.tsx** - Q&A panel
3. **Panel2_Preview.tsx** - SVG preview
4. **Panel3_CodeEditor.tsx** - Code editor
5. **Hooks** - useSSEStream, useDiagramSession, useDiagramState
6. **Services** - diagramApi, SSE helper
7. **Types** - TypeScript definitions
8. **Styles** - CSS for 3-panel layout

---

## Frontend Integration (Detailed)

### 3-Panel Layout

```
┌─────────────────────────────────────────────┐
│  Diagram Wizard ✕                           │
├──────────────┬───────────────┬──────────────┤
│  Panel 1     │   Panel 2     │  Panel 3     │
│  Chat        │   Preview     │  Code Editor │
│  (25%)       │   (40%)       │  (35%)       │
├──────────────┼───────────────┼──────────────┤
│ Q: Initial   │ [SVG Diagram] │ 1 | diagram │
│ A: Response  │               │ 2 |   {     │
│ Q: Next?     │ [Download▼]   │ 3 |   }     │
│ [Submit]     │               │             │
│ [Restart]    │ Rendering...  │ [Save]      │
│              │               │             │
└──────────────┴───────────────┴──────────────┘
```

### Communication Protocol

**Server-Sent Events (SSE)** - Real-time updates from backend

```
GET /api/v1/diagram/stream/{session_id}

Events:
- clarification_question
- clarification_complete
- code_generated
- validation_error
- diagram_ready
```

### API Endpoints

| Endpoint | Method | Purpose |
|----------|--------|---------|
| /diagram/start | POST | Initialize session |
| /diagram/stream/{id} | GET | SSE stream |
| /diagram/clarify | POST | Submit response |
| /diagram/render | POST | Manual code edit |
| /diagram/restart | POST | Restart clarification |
| /diagram/session/{id} | GET | Resume session |
| /diagram/{id}/download | GET | Download diagram |

### State Machine

```
Input Phase
    ↓
Clarifying (type-specific questions)
    ↓
Generating (code generation)
    ↓
Validating (syntax check)
    ├─ Valid → Rendering → Ready
    └─ Invalid → Refine → Validating

Ready
    ├─ Edit Code → Validating
    └─ Restart → Clarifying
```

### Loading Indicators (Phase-Based)

Just show the phase:
- "Clarifying requirements..."
- "Generating diagram code..."
- "Validating syntax..."
- "Rendering diagram..."
- "Diagram complete!"

---

## Backend Integration (Specified in UPGRADEPLAN.MD)

### Service Layer

**DiagramFactoryService** (app/services/diagram_factory_service.py)

```python
async def start_clarification(prompt, diagram_type)
async def submit_clarification_response(session_id, response)
async def auto_refine_diagram(session_id)
async def manual_render(session_id, diagram_code)
async def restart_clarification(session_id)
async def get_session(session_id)
```

### API Endpoints

**app/api/v1/endpoints/diagram.py**
- All 7 endpoints specified
- Proper error handling
- OpenAPI documentation

### Configuration

**app/core/config.py** additions:
- `diagram_factory_enabled`
- `diagram_timeout`
- `diagram_max_refinements`
- `diagram_languages`
- Tool paths (d2, mmdc, plantuml)
- LLM settings
- Session TTL

---

## Key Features

### 1. Type-Specific Clarification
- Questions are specific to chosen diagram format
- Mermaid: "What are the main components?"
- D2: "What are external systems?"
- PlantUML: "What are the main actors?"

### 2. Real-Time Updates
- SSE streaming for instant feedback
- Live preview updates as code changes
- Phase indicators during processing

### 3. Automatic Refinement
- Validation with error classification
- Automatic code refinement up to 3 times
- Recovery suggestions to guide users

### 4. Manual Editing
- Once diagram is valid, users can edit code directly
- Live preview in Panel 2
- Easy refinement loop

### 5. Session Persistence
- 1-hour session TTL
- Resume capability
- Full history preserved

### 6. Multi-Format Support
- Mermaid (flowcharts, sequences, states)
- D2 (architecture diagrams)
- PlantUML (UML diagrams)

### 7. Security Hardened
- No command injection possible
- Proper file cleanup
- Timeout enforcement
- Safe subprocess execution

---

## Implementation Timeline

| Phase | Duration | Focus |
|-------|----------|-------|
| 1 | Weeks 1-2 | Backend foundation (30 hrs) |
| 2 | Week 3 | Service integration (7 hrs) |
| 3 | Week 4 | API endpoints & SSE (10 hrs) |
| 4 | Weeks 5-6 | Frontend (35 hrs) |
| 5 | Week 7 | Testing & docs (30 hrs) |
| 6 | Week 8 | Deployment (10 hrs) |
| **TOTAL** | **8 weeks** | **~120 hrs** |

---

## Success Criteria

### Functional
- ✓ Diagram Wizard button visible
- ✓ 3-panel layout works
- ✓ SSE streaming real-time updates
- ✓ Type-specific clarification
- ✓ Code generation & validation
- ✓ Manual editing
- ✓ SVG rendering
- ✓ Download (PNG/SVG/PDF)
- ✓ Session persistence
- ✓ Error recovery

### Quality
- ✓ 95%+ test coverage (backend)
- ✓ 80%+ test coverage (frontend)
- ✓ Security review passed
- ✓ <5s response time
- ✓ 99.5% uptime SLA
- ✓ No hardcoded prompts

---

## Prompt Management

All prompts stored in **markdown files** (not hardcoded):

### CLARIFY_PROMPTS.md
- Mermaid clarification questions
- D2 clarification questions
- PlantUML clarification questions
- Generic framework
- Readiness criteria

### GENERATE_PROMPTS.md
- Mermaid generation instructions
- D2 generation instructions
- PlantUML generation instructions
- Best practices per format
- Common pitfalls to avoid

### REFINE_PROMPTS.md
- Mermaid refinement guidance
- D2 refinement guidance
- PlantUML refinement guidance
- Error-specific instructions
- Quality checklist

**Advantage:** Prompts can be updated without code changes

---

## File Structure Summary

```
Whysper/
├── backend/
│   ├── UPGRADEPLAN.MD                 ← System design
│   ├── IMPLEMENTATION_PLAN.MD          ← Task breakdown
│   └── app/
│       ├── api/v1/endpoints/
│       │   └── diagram.py              (to implement)
│       ├── services/
│       │   └── diagram_factory_service.py (to implement)
│       └── utils/diagram_wizard/       ✓ CREATED
│           ├── __init__.py
│           ├── README.md
│           ├── graph_state.py
│           ├── tool_config.py
│           ├── nodes.py
│           ├── langgraph_builder.py
│           ├── session_store.py
│           └── prompts/
│               ├── CLARIFY_PROMPTS.md
│               ├── GENERATE_PROMPTS.md
│               └── REFINE_PROMPTS.md
│
└── frontend/
    └── src/components/
        └── DiagramWizard/             (to implement)
            ├── DiagramWizard.tsx
            ├── Panel1_Chat.tsx
            ├── Panel2_Preview.tsx
            ├── Panel3_CodeEditor.tsx
            ├── hooks/
            ├── services/
            ├── types/
            └── styles/
```

---

## Next Steps

1. **Review the Documents**
   - Read UPGRADEPLAN.MD (architecture overview)
   - Read IMPLEMENTATION_PLAN.MD (detailed tasks)

2. **Assign Team**
   - 2x Backend Developers
   - 1x Backend/Prompt Engineer
   - 1x Security Engineer
   - 1x Frontend Developer
   - 1x QA Engineer
   - 1x DevOps Engineer

3. **Start Phase 1**
   - Tasks 1.1-1.8
   - Duration: 2 weeks
   - Focus: Backend foundation

4. **Create GitHub Issues**
   - One issue per task
   - Link to IMPLEMENTATION_PLAN.MD
   - Set dependencies

5. **Daily Standup**
   - Progress tracking
   - Blocker resolution
   - Plan adjustments

---

## Key Decisions Made

1. **SSE over WebSocket** - Real-time but simpler
2. **In-memory sessions** - Easy to start, scale later with Redis
3. **Markdown prompts** - Maintainable, versionable
4. **3-panel layout** - Clear separation of concerns
5. **Type-specific questions** - Better diagram quality
6. **No hardcoded anything** - All config/prompts in files

---

## Questions for Review

1. Are 8 weeks realistic with your team?
2. Should we use Redis for sessions from start?
3. Do the prompt files match your team's style?
4. Any specific frontend framework requirements (React, Vue, etc.)?
5. Should we prioritize any phase?

---

**Status:** Ready for implementation ✓
**Created:** 2024-11-08
**Last Updated:** Implementation plan complete
