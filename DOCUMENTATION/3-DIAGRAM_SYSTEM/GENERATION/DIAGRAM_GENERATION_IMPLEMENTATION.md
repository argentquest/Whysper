# Diagram Generation Implementation - ArchStudio LLM Integration

## Overview

The diagram generation system has been fully implemented with LLM integration using the provider infrastructure. The system follows an async workflow:

1. **Frontend Request** → POST `/diagrams/v2/generate` with agentId, prompt, diagramType
2. **Immediate Response** → Returns requestId for tracking
3. **Background Processing** → Async task calls LLM, generates diagram code, renders it
4. **Real-time Streaming** → Frontend polls SSE endpoint to receive diagram

## Architecture

### Request Flow

```
┌─────────────────────────────────────────────────────────────┐
│ 1. Frontend: Submit Prompt                                  │
│    POST /api/v1/diagrams/v2/generate                        │
│    Body: {agentId, prompt, diagramType}                     │
└─────────────────────────────────────────────────────────────┘
                         ↓
┌─────────────────────────────────────────────────────────────┐
│ 2. Backend: Synchronous Task Scheduling                     │
│    - Load agent system prompt from markdown                 │
│    - Get provider registry                                  │
│    - Find all providers for diagram type                    │
│    - Select default provider                               │
│    - Schedule background task                              │
│    - Return immediately with requestId                     │
└─────────────────────────────────────────────────────────────┘
                         ↓
┌─────────────────────────────────────────────────────────────┐
│ 3. Frontend: Open SSE Stream                                │
│    GET /api/v1/diagrams/v2/stream?requestId={id}           │
│    Connection stays open, polling for updates               │
└─────────────────────────────────────────────────────────────┘
                         ↓
┌─────────────────────────────────────────────────────────────┐
│ 4. Background Task: LLM Diagram Generation                  │
│                                                              │
│    Step 1: Call LLM                                         │
│    ├─ Combine: agent system prompt + user prompt           │
│    └─ Use OpenRouter API                                   │
│                                                              │
│    Step 2: Extract Diagram Code                            │
│    ├─ Parse markdown code blocks                           │
│    └─ Extract code based on diagram type                   │
│                                                              │
│    Step 3: Validate & Render (Provider)                    │
│    ├─ validate_code() - Check syntax                       │
│    ├─ auto_fix_pattern_based() - Fix common errors        │
│    ├─ LLM correction - Intelligent fixes with retry        │
│    └─ render() - Convert to SVG/PNG                        │
│                                                              │
│    Step 4: Store Result                                    │
│    └─ _pending_requests[requestId] = {                     │
│        status, diagram_code, render_result,                │
│        metadata, timestamp                                 │
│      }                                                      │
└─────────────────────────────────────────────────────────────┘
                         ↓
┌─────────────────────────────────────────────────────────────┐
│ 5. SSE Stream: Send Diagram to Frontend                     │
│                                                              │
│    SSE Events:                                              │
│    - connected: Connection confirmed                        │
│    - diagram: Diagram ready (success)                       │
│    - error: Generation failed                               │
│    - complete: Stream finished                              │
│    - timeout: Exceeded 5-min wait                           │
│    - keepalive: Every 10 seconds                            │
│                                                              │
│    Response includes:                                       │
│    ├─ diagramCode: Generated source code                   │
│    ├─ content: Rendered SVG                                │
│    ├─ validationResult: {isValid, autoFixed, llmCorrected} │
│    ├─ metadata: Provider, timing, etc.                     │
│    └─ success: true/false                                  │
└─────────────────────────────────────────────────────────────┘
```

## Implementation Details

### 1. POST /diagrams/v2/generate

**Location**: [diagram_provider.py:586-679](c:\Code2025\Whysper\backend\app\api\v1\endpoints\diagram_provider.py#L586-L679)

**Request Model**:
```python
class GenerateDiagramRequest(BaseModel):
    agentId: str           # e.g., "c4-architecture"
    prompt: str            # User's description
    diagramType: Optional[str] = "mermaid"  # Type to generate
```

**Response Model**:
```python
class GenerateDiagramResponse(BaseModel):
    requestId: str                           # UUID for tracking
    diagram: Optional[DiagramRenderResponse] = None
```

**Implementation Steps**:

1. Load agent system prompt:
   ```python
   agent_prompt_filename = f"{request.agentId}.md"
   agent_system_prompt = settings_service.get_agent_prompt_content(agent_prompt_filename)
   ```

2. Get provider registry and find providers:
   ```python
   registry = get_registry()
   providers_for_type = registry.find_by_diagram_type(request.diagramType)
   default_provider = registry.get_default_provider(request.diagramType)
   ```
   Note: Multiple providers can support same diagram type (user specified this)

3. Schedule background task:
   ```python
   background_tasks.add_task(
       _generate_diagram_async,
       request_id=request_id,
       agent_id=request.agentId,
       agent_system_prompt=agent_system_prompt,
       user_prompt=request.prompt,
       diagram_type=request.diagramType,
       provider=default_provider
   )
   ```

4. Return immediately with requestId

### 2. Background Task: _generate_diagram_async()

**Location**: [diagram_provider.py:689-799](c:\Code2025\Whysper\backend\app\api\v1\endpoints\diagram_provider.py#L689-L799)

**Step 1: Call LLM**
```python
openrouter = OpenRouterProvider(api_key=settings.openrouter_api_key)
llm_response = openrouter.process_question(
    question=user_prompt,
    conversation_history=[],
    codebase_content="",
    model=settings.openrouter_model or "openai/gpt-4"
)
```

**Step 2: Extract Diagram Code**
```python
diagram_code = _extract_diagram_code(llm_response, diagram_type)
```

Uses regex to find markdown code blocks:
- ` ```mermaid...``` `
- ` ```d2...``` `
- ` ```plantuml...``` `

**Step 3: Validate & Render Using Provider Infrastructure**

This is the **key part** - uses provider's built-in capabilities:

```python
render_result = provider.render_with_validation(
    code=diagram_code,
    output_format="svg",
    auto_fix=True,
    llm_correction=True
)
```

The provider's `render_with_validation()` method:
- ✅ Validates code syntax
- ✅ Attempts pattern-based auto-fix (regex fixes)
- ✅ Uses LLM-based correction with retry loop if pattern-fix fails
- ✅ Renders final output (SVG, PNG, etc.)

**Step 4: Store for SSE Streaming**
```python
_pending_requests[request_id] = {
    "status": "completed",
    "diagram_code": diagram_code,
    "render_result": render_result,
    "agent_id": agent_id,
    "diagram_type": diagram_type,
    "provider_id": provider.provider_id,
    "timestamp": datetime.now().isoformat()
}
```

### 3. Helper: _extract_diagram_code()

**Location**: [diagram_provider.py:803-854](c:\Code2025\Whysper\backend\app\api\v1\endpoints\diagram_provider.py#L803-L854)

Extracts diagram code from LLM response using regex patterns:

1. Try exact match with diagram type:
   ```python
   pattern = rf"```{re.escape(diagram_type_lower)}\s*\n(.*?)\n```"
   ```

2. Try plain code block:
   ```python
   pattern = r"```\s*\n(.*?)\n```"
   ```

3. Fallback to indented code detection

Returns extracted code or None if not found.

### 4. GET /diagrams/v2/stream

**Location**: [diagram_provider.py:865-985](c:\Code2025\Whysper\backend\app\api\v1\endpoints\diagram_provider.py#L865-L985)

**Polling Strategy**:
- Polls `_pending_requests[requestId]` every 1 second
- Max wait time: 5 minutes (300 seconds)
- Keepalive every 10 seconds

**SSE Events**:

1. **connected** - Initial connection confirmation
   ```json
   {
     "requestId": "uuid-here",
     "message": "Connected to diagram stream"
   }
   ```

2. **diagram** - Diagram ready (success)
   ```json
   {
     "requestId": "uuid-here",
     "success": true,
     "diagramCode": "mermaid code here",
     "diagramType": "mermaid",
     "providerId": "mermaidv1",
     "content": "<svg>...</svg>",
     "outputFormat": "svg",
     "validationResult": {
       "isValid": true,
       "error": null,
       "autoFixed": false,
       "llmCorrected": false,
       "correctionMethod": null
     },
     "metadata": {...},
     "timestamp": "2025-11-05T12:34:56"
   }
   ```

3. **error** - Generation failed
   ```json
   {
     "requestId": "uuid-here",
     "error": "Error message here"
   }
   ```

4. **complete** - Stream finished
   ```json
   {
     "requestId": "uuid-here",
     "message": "Diagram generation complete"
   }
   ```

5. **timeout** - Exceeded 5 minutes
   ```json
   {
     "requestId": "uuid-here",
     "error": "Diagram generation timed out"
   }
   ```

6. **keepalive** - Ping every 10 seconds
   ```
   : keepalive
   ```

## Provider Infrastructure Integration

The implementation properly leverages the provider system:

### Provider Registry
```python
from diagrams.provider_registry import get_registry

registry = get_registry()

# Find all providers for diagram type (multiple possible)
providers = registry.find_by_diagram_type("mermaid")

# Get default provider (respects preferences, v1 fallback, etc.)
provider = registry.get_default_provider("mermaid")
```

### Provider Methods Used

1. **render_with_validation()** - Comprehensive pipeline
   - Validates code
   - Auto-fixes with pattern-based rules
   - Uses LLM correction with retry logic (configurable)
   - Renders to output format

2. **validate_code()** - Syntax validation only

3. **auto_fix_pattern_based()** - Regex-based fixes

4. **render()** - Render to SVG/PNG

## Data Storage

**In-Memory Request Storage**:
```python
_pending_requests: Dict[str, Dict[str, Any]] = {}
```

Each entry stores:
- `status`: "completed", "error", or "processing"
- `diagram_code`: Generated source code
- `render_result`: RenderResult from provider
- `agent_id`, `diagram_type`, `provider_id`: Metadata
- `timestamp`: When completed

**Note**: For production, this should use:
- Redis for distributed caching
- Database for persistence
- Message queue (Celery, RabbitMQ) for async processing

## Error Handling

**Backend Exceptions**:
- Agent prompt not found → 404 HTTPException
- No providers for diagram type → 404 HTTPException
- LLM API error → Stored in _pending_requests, sent via SSE
- Code extraction fails → ValueError in background task
- Provider rendering fails → Stored with error flag, sent via SSE

**SSE Timeout**:
- If diagram not ready after 300 seconds → Send timeout event
- Connection closes

## Logging

All operations use prefixed logging for easy debugging:

- `[GENERATE]` - Endpoint request processing
- `[GENERATE_ASYNC]` - Background task execution
- `[STREAM]` - SSE stream updates

Example log flow:
```
[GENERATE] =============== DIAGRAM GENERATION REQUEST ===============
[GENERATE] Request ID: uuid-here
[GENERATE] Agent ID: 'c4-architecture'
[GENERATE] Diagram Type: 'mermaid'
[GENERATE] User Prompt Length: 150 characters
[GENERATE] Agent System Prompt Length: 2500 characters
[GENERATE] Found 2 provider(s) for 'mermaid'
[GENERATE] Using default provider: mermaidv1
[GENERATE] Background task scheduled for request uuid-here
[GENERATE] ========================================================

[GENERATE_ASYNC] Starting diagram generation for request uuid-here
[GENERATE_ASYNC] Using provider: mermaidv1
[GENERATE_ASYNC] Calling OpenRouter LLM...
[GENERATE_ASYNC] LLM Response Length: 500 characters
[GENERATE_ASYNC] Extracting mermaid diagram code from response...
[GENERATE_ASYNC] Extracted diagram code length: 250 characters
[GENERATE_ASYNC] Rendering diagram using mermaidv1...
[GENERATE_ASYNC] ✅ Diagram generation completed successfully

[STREAM] Client connected to stream for request: uuid-here
[STREAM] Sending completed diagram for request uuid-here
[STREAM] Client disconnected from stream
```

## Frontend Integration

The frontend should:

1. Submit prompt:
   ```typescript
   const response = await fetch(`${API_BASE_URL}/diagrams/v2/generate`, {
     method: 'POST',
     body: JSON.stringify({
       agentId: 'c4-architecture',
       prompt: 'Create a C4 diagram for...',
       diagramType: 'mermaid'
     })
   });
   const { requestId } = await response.json();
   ```

2. Open SSE stream:
   ```typescript
   const eventSource = new EventSource(
     `${API_BASE_URL}/diagrams/v2/stream?requestId=${requestId}`
   );

   eventSource.addEventListener('diagram', (event) => {
     const data = JSON.parse(event.data);
     // Render data.content (SVG) in diagram viewer
   });

   eventSource.addEventListener('error', (event) => {
     const data = JSON.parse(event.data);
     // Show error message to user
   });
   ```

## Key Features

✅ **Multiple Provider Support**: Registry handles multiple providers per diagram type
✅ **Async Processing**: Non-blocking request/response
✅ **Real-time Streaming**: SSE for live updates
✅ **Automatic Error Correction**: Pattern-based + LLM-based fixes
✅ **Rich Logging**: Detailed debugging logs with prefixes
✅ **Timeout Handling**: 5-minute max wait with cleanup
✅ **Provider Infrastructure**: Uses built-in validation and retry logic
✅ **Markdown Code Extraction**: Robust parsing of LLM responses

## Files Modified

- `backend/app/api/v1/endpoints/diagram_provider.py` - Main implementation
- `backend/app/api/v1/endpoints/settings.py` - Agent/option endpoints (already in place)
- `backend/app/services/settings_service.py` - Agent loading (already in place)

## Dependencies

Required imports already present:
- `fastapi` - Web framework
- `pydantic` - Data validation
- `providers.openrouter_provider` - LLM provider
- `diagrams.provider_registry` - Provider system
- `diagrams.base_diagram` - Provider base class
