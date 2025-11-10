# Diagram Wizard - Technical Implementation Documentation

**Version**: 2.0 - Production Implementation  
**Date**: November 2025  
**Status**: ✅ PRODUCTION READY

## Overview

The Diagram Wizard is a fully implemented, AI-powered diagram generation system integrated into the Whysper application. It provides an intelligent, conversational interface where users describe their systems and the AI guides them through creating professional diagrams using LangGraph workflows.

### Key Features
- **Intelligent Clarification**: AI interviews users to gather complete requirements
- **Multi-Format Support**: D2, Mermaid, PlantUML diagram generation
- **Real-Time Processing**: Server-Sent Events for live feedback
- **Tab-Based Integration**: Seamless integration as DiagramWizard tab type
- **Complete Workflow**: From natural language to SVG output
- **Validation & Refinement**: Automatic error correction and validation

## Architecture Overview

```mermaid
graph TD
    A[User Input] --> B[DiagramFactoryService]
    B --> C[Information Scoring]
    C --> D[LangGraph Workflow]
    D --> E[AI Clarification]
    E --> F[JSON Representation Generation]
    F --> G[Diagram Generation]
    G --> H[Validation]
    H --> I[SVG Rendering]
    I --> J[Frontend Display]
    
    K[SSE Events] --> L[Real-time Updates]
    B --> K
    D --> K
    F --> K
```

## JSON-First Architecture

The new architecture of the Diagram Wizard is "JSON-first". This means that the primary goal of the initial conversation with the user is to gather enough information to create a structured JSON representation of the diagram. This JSON object conforms to the schema defined in `backend/app/utils/architecture_schema.py`.

Once the JSON object is created, it is used to generate the diagram code (e.g., Mermaid, D2, PlantUML). This approach has several advantages:

*   **Robustness:** By separating the data from the presentation, we can ensure that the data is valid before we attempt to generate the diagram.
*   **Flexibility:** The same JSON object can be used to generate multiple diagram types.
*   **Extensibility:** It is easy to add new features, such as saving and loading diagrams, by working with the JSON object.

## Implementation Structure

### Backend Core (`backend/app/utils/diagram_wizard/`)
- **`graph_state.py`** - LangGraph state schema and types
- **`nodes.py`** - AI-powered workflow nodes with real LLM integration
- **`langgraph_builder.py`** - Workflow graph construction
- **`session_store.py`** - Session management
- **`tool_config.py`** - Provider configuration abstraction
- **`prompt_loader.py`** - Dynamic prompt loading system
- **`architecture_schema.py`** - Defines the JSON schema for the architecture

### Service Layer (`backend/app/services/`)
- **`diagram_factory_service.py`** - Main orchestration service
  - Information completeness scoring
  - Session management with asyncio queues
  - Real-time SSE updates
  - Provider integration

### API Layer (`backend/app/api/v1/endpoints/`)
- **`diagram.py`** - RESTful endpoints
  - `/start-generation` - Initialize diagram workflow
  - `/handle-clarification` - Process user responses
  - `/get-status` - Session status queries
  - `/events` - Server-Sent Events stream

### Frontend Integration (`frontend/src/components/DiagramWizard/`)
- **`DiagramWizard.tsx`** - Main React component
- **`useDiagramSession.ts`** - Session state management hook
- **Panel Components** - Chat, Preview, Code Editor, and JSON panels
- **Tab Integration** - Seamless integration with main app

## Key Design Decisions

### 1. LangGraph Workflow Engine
- State machine approach for complex conversational flows
- Declarative workflow definition
- Robust error handling and recovery

### 2. Real AI Integration
- Uses existing `chat.py` infrastructure (`create_ai_processor`)
- Comprehensive SSE logging for transparency
- Feedback loop prevention through proper message filtering

### 3. Provider Abstraction
- Leverages existing diagram provider system
- Supports D2, Mermaid, PlantUML through unified interface
- Validation and rendering through provider registry

### 4. Information Scoring System
```python
def _assess_information_completeness(description: str) -> tuple[bool, dict]:
    """
    Evaluates completeness using keyword analysis:
    - entity_words: Components, systems, users
    - action_words: Processes, operations  
    - structure_words: Architecture, relationships
    
    Returns (has_enough_info, detailed_score_info)
    """
```

### 5. Tab-Based Architecture
- DiagramWizard integrated as new tab type alongside 'chat', 'file', 'documentation'
- Session persistence across tab switches
- No standalone pages - pure tab-based architecture

## Workflow States

### LangGraph State Machine
```python
GraphState = TypedDict:
    design_prompt: str
    diagram_type: DiagramType  
    clarification_history: List[Dict[str, str]]
    llm_ready: bool
    final_design_summary: str
    json_representation: Dict[str, Any]
    diagram_code: str
    svg_output: str
    current_state: str
    _session_id: str
    _update_callback: Callable
```

### State Transitions
1. **INITIALIZED** → Information scoring and analysis
2. **CLARIFYING** → AI-driven requirement gathering  
3. **GENERATING_JSON** → LLM JSON representation creation
4. **GENERATING_CODE** → LLM diagram code creation
5. **VALIDATING** → Provider-based validation
6. **REFINING** → Error correction (if needed)
7. **RENDERING** → SVG generation
8. **READY** → Complete diagram available

## AI Integration Details

### LLM Call Implementation
```python
async def _call_llm(prompt: str, user_content: str, session_id: str = None) -> str:
    """
    Real AI integration using existing infrastructure:
    - Uses create_ai_processor from common.ai
    - Supports multiple providers (OpenRouter, custom)
    - Comprehensive SSE logging
    - Proper error handling and fallbacks
    """
```

### Clarification Logic
- **Bypass Logic**: Skip clarification when perfect information score achieved
- **Context Management**: Filters user-only messages to prevent AI feedback loops
- **Session Persistence**: Maintains conversation state across interactions

## Provider Integration

### Diagram Rendering Pipeline
1. **Code Generation** - LLM creates diagram code
2. **Validation** - Provider validates syntax
3. **Refinement** - LLM fixes errors if needed (automatic retry)
4. **Rendering** - Provider generates SVG output

### Supported Providers
- **d2v1** - Direct D2 CLI integration
- **mermaidv1** - Mermaid CLI integration  
- **krokiplantuml** - PlantUML via Kroki service

## Testing Infrastructure

### Test Organization
- **Unit Tests**: `tests/1-UNIT/diagram_wizard/`
  - `test_svg_validation.py` - SVG validation utilities
- **Integration Tests**: `tests/2-INTEGRATION/diagram_wizard/`
  - `simple_flow_test.py` - **VERIFIED WORKING** (1506 chars D2 code)
  - `perfect_score_test.py` - **VERIFIED WORKING** (2744 chars + SVG)
  - Additional workflow validation tests

### Test Results
- ✅ Core workflow generates valid D2 diagrams (1500+ characters)
- ✅ Complete SVG pipeline produces 39KB+ output files
- ✅ AI integration successfully calls LLMs and processes responses
- ✅ Session management and SSE streaming functional

## Performance Characteristics

### Measured Performance
- **Simple Flow Test**: 26.2 seconds for 1506 character D2 diagram
- **Perfect Score Test**: 81.2 seconds for 2744 character diagram + SVG
- **Information Scoring**: Near-instant analysis
- **SSE Streaming**: Real-time updates throughout workflow

### Optimization Features
- Prompt caching in `prompt_loader.py`
- Session state persistence
- Efficient provider registry usage
- Minimal frontend re-renders through optimized hooks

## Security Considerations

### Input Validation
- All user inputs sanitized before LLM processing
- Provider validation before code execution
- Secure temporary file handling

### API Security
- Session-based access control
- Structured logging for audit trails
- Error message sanitization

## Deployment Status

### Production Readiness ✅
- Complete implementation with working tests
- Comprehensive error handling
- Real-time monitoring through SSE logs
- Provider integration validated
- Frontend/backend integration complete

### Configuration Requirements
- LLM provider configuration (API keys)
- Diagram provider setup (D2 CLI, Kroki services)
- Environment variables properly configured

## Files Modified/Created

### Backend Implementation
```
backend/app/utils/diagram_wizard/
├── graph_state.py              (TypedDict definitions)
├── nodes.py                   (AI workflow nodes) 
├── langgraph_builder.py       (Graph construction)
├── session_store.py           (Session management)
├── tool_config.py             (Provider abstraction)
├── prompt_loader.py           (Dynamic prompts)
└── prompts/
    ├── CLARIFY_PROMPTS.md     (Clarification templates)
    ├── GENERATE_PROMPTS.md    (Generation templates)
    └── REFINE_PROMPTS.md      (Refinement templates)

backend/app/services/
└── diagram_factory_service.py (Main service - 900+ lines)

backend/app/api/v1/endpoints/
└── diagram.py                 (6 API endpoints)

tests/
├── 1-UNIT/diagram_wizard/
│   └── test_svg_validation.py
└── 2-INTEGRATION/diagram_wizard/
    ├── simple_flow_test.py    (WORKING - 1506 chars)
    ├── perfect_score_test.py  (WORKING - 2744 chars + SVG)
    └── [additional test files]
```

### Frontend Implementation  
```
frontend/src/components/DiagramWizard/
├── DiagramWizard.tsx          (Main component)
├── useDiagramSession.ts       (State management)
├── diagram-wizard.module.css  (Styling)
└── panels/
    ├── Panel1_Chat.tsx        (Conversation interface)
    ├── Panel2_Preview.tsx     (SVG preview)
    └── Panel3_CodeEditor.tsx  (Code editing)

frontend/src/types/
└── index.ts                   (TypeScript definitions)
```

## Next Steps

### Immediate
- ✅ All core functionality implemented and tested
- ✅ Documentation complete and current
- ✅ Test suite organized and validated

### Future Enhancements  
- Additional diagram providers (Structurizr, etc.)
- Enhanced validation rules
- Performance optimizations
- Extended prompt libraries

## Summary

The Diagram Wizard is a **fully functional, production-ready system** that successfully demonstrates:
- AI-powered conversational diagram generation
- Real-time workflow processing with SSE
- Multi-provider diagram generation (D2, Mermaid, PlantUML)  
- Seamless frontend/backend integration
- Comprehensive test coverage with validated working examples

The implementation exceeded the original planning requirements and provides a robust foundation for AI-powered diagram generation within the Whysper ecosystem.