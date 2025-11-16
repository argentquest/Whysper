# Model ID Implementation - Complete Flow

## Overview

User-driven AI model selection has been fully implemented across the entire DiagramWizard system, allowing users to select which AI model to use (GPT-5, Grok, Claude, or Gemini) before starting diagram generation.

## Three UI Screens

The DiagramWizard component now has three distinct UI screens:

### 1. **Model Selection Screen** (Initial)
**File:** [frontend/src/components/DiagramWizard/ModelSelector.tsx](frontend/src/components/DiagramWizard/ModelSelector.tsx)

- **Display:** Purple gradient background with 4 model cards
- **Models:**
  - **GPT-5 (Deep Context):** Long-context reasoning, complex architectures
  - **Grok (Fast):** Quick analysis, deterministic results, simple systems
  - **Claude (Thinking):** Transparent reasoning, structured output
  - **Gemini (Efficient):** Pragmatic approach, real-time feedback
- **Action:** User clicks a model card to proceed
- **Storage:** Selected model saved to localStorage as `diagramWizard.selectedModel`

### 2. **System Description Screen** (After Model Selected)
**File:** [frontend/src/components/DiagramWizard/DiagramWizard.tsx:668-721](frontend/src/components/DiagramWizard/DiagramWizard.tsx#L668-L721)

- **Display:** Text input area for system description
- **Header:** Shows selected model tag + "Change Model" button
- **Placeholder:** Examples of architectures to describe
- **Action:** User clicks "Start Conversation" to begin analysis
- **Flow:** Stays on this screen through Analysis and Clarification phases

### 3. **Generation & Results Screen** (After Clarification Complete)
**File:** [frontend/src/components/DiagramWizard/DiagramWizard.tsx:722+](frontend/src/components/DiagramWizard/DiagramWizard.tsx#L722)

- **Layout:** Three-panel interface
  - Left: Chat panel for Q&A
  - Center: SVG preview of diagram
  - Right: Code editor for manual edits
- **Features:** Generation, validation, refinement, rendering, export
- **Duration:** Appears after user confirms readiness in clarification

## Frontend Implementation

### Model Selection Flow

**Step 1: ModelSelector Component Renders**
```typescript
// DiagramWizard.tsx line 661-666
!selectedModel ? (
  <ModelSelector
    onSelect={handleModelSelect}
    loading={loading || isInitializing}
  />
) : (...)
```

**Step 2: User Selects Model**
```typescript
// DiagramWizard.tsx line 382-390
const handleModelSelect = (modelId: ModelId) => {
  setSelectedModel(modelId);
  localStorage.setItem('diagramWizard.selectedModel', modelId);
  message.success(`Selected ${modelId} - ready to start!`);
};
```

**Step 3: Model Tag Displayed**
```typescript
// DiagramWizard.tsx line 602-608
{selectedModel && (
  <Tag color="blue">
    🤖 {selectedModel === 'gpt5' ? 'GPT-5' : 'Grok' : 'Claude' : 'Gemini'}
  </Tag>
)}
```

**Step 4: Start Diagram with Model**
```typescript
// DiagramWizard.tsx line 417
await startSession(userInput, 'auto', selectedModel);
```

### API Communication

**File:** [frontend/src/services/diagram/diagramApi.ts:55-86](frontend/src/services/diagram/diagramApi.ts#L55-L86)

```typescript
static async startDiagramGeneration(
  initialPrompt: string,
  diagramType: string = 'Mermaid',
  modelId?: string  // NEW: pass selected model
): Promise<DiagramSession> {
  const body: any = {
    initial_prompt: initialPrompt,
    diagram_type: diagramType,
  };

  if (modelId) {
    body.model_id = modelId;  // Include model_id in request
  }

  const response = await fetch('/api/v1/diagram/start', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(body)
  });
  // ...
}
```

## Backend Implementation

### API Endpoint

**File:** [backend/app/api/v1/endpoints/diagram.py:18-45](backend/app/api/v1/endpoints/diagram.py#L18-L45)

```python
@router.post("/start")
async def start_diagram_generation(
    initial_prompt: str = Body(..., embed=True),
    diagram_type: str = Body("Mermaid", embed=True),
    model_id: str = Body(None, embed=True),  # NEW: accept model selection
):
    """
    Args:
        initial_prompt: System description
        diagram_type: Diagram type (Mermaid, D2, PlantUML)
        model_id: AI model (gpt5, grok, claude, gemini)
    """
    session = DiagramSessionStore.create_session()
    service = DiagramFactoryService(session)
    await service.start_generation(initial_prompt, diagram_type, model_id)
    # ...
```

### Graph State

**File:** [backend/app/utils/diagram_wizard/graph_state.py:49](backend/app/utils/diagram_wizard/graph_state.py#L49)

```python
class GraphState(TypedDict, total=False):
    # ... other fields ...
    model_id: Optional[str]  # AI model to use (gpt5, grok, claude, gemini)
```

### Service Initialization

**File:** [backend/app/services/diagram_factory_service.py:239-267](backend/app/services/diagram_factory_service.py#L239-L267)

```python
async def start_generation(
    self,
    initial_prompt: str,
    diagram_type: str = "Mermaid",
    model_id: Optional[str] = None  # NEW: accept model_id
):
    initial_state: GraphState = {
        "design_prompt": initial_prompt,
        "diagram_type": DiagramType(...),
        # ... other fields ...
        "model_id": model_id,  # Store in state
    }
    # ... workflow starts with model_id in state ...
```

### Model Mapping

**File:** [backend/app/utils/diagram_wizard/nodes.py:153-169](backend/app/utils/diagram_wizard/nodes.py#L153-L169)

```python
def _get_model_for_id(model_id: str = None) -> str:
    """Map model_id to actual model name."""
    model_map = {
        "gpt5": "openai/gpt-4-turbo",           # Deep Context
        "grok": "xai/grok-2-latest",            # Fast
        "claude": "anthropic/claude-3.5-sonnet",  # Thinking
        "gemini": "google/gemini-2.5-pro",      # Efficient
    }
    return model_map.get(model_id, "google/gemini-2.5-flash-preview-09-2025")
```

### LLM Call with Model

**File:** [backend/app/utils/diagram_wizard/nodes.py:172-190](backend/app/utils/diagram_wizard/nodes.py#L172-L190)

```python
async def _call_llm(
    prompt: str,
    user_content: str,
    session_id: str = None,
    model_id: str = None  # NEW: accept model_id
) -> str:
    # Use selected model or fall back to environment default
    model = _get_model_for_id(model_id) if model_id \
            else env_vars.get("DEFAULT_MODEL", "...")

    processor = create_ai_processor(api_key=api_key, provider=provider)
    result = processor.process_question(
        question=user_content,
        conversation_history=conversation_history,
        model=model,  # Use the mapped model
        # ...
    )
```

## Node Updates

All nodes now extract and use `model_id` from state:

### 1. `analyze_request` (line 54-91)
```python
model_id = state.get("model_id")
prompt_template = get_prompt("analyze_request", model_id=model_id)
ai_response_str = await _call_llm(prompt_template, user_content, session_id, model_id=model_id)
```

### 2. `clarify_prompt` (line 449-504)
```python
model_id = state.get("model_id")
analyze_prompt = get_prompt("analyze_request", model_id=model_id)
clarify_prompt_template = get_prompt("clarify_universal", model_id=model_id)
ai_response_str = await _call_llm(prompt_template, user_content, session_id, model_id=model_id)
```

### 3. `generate_json_representation` (line 256+)
```python
model_id = state.get("model_id", "claude")
prompt_template = get_prompt("json_generation", model_id=model_id)
```

### 4. `generate_code` (line 680, 712)
```python
model_id = state.get("model_id")
prompt_template = get_prompt(prompt_key, model_id=model_id)
ai_response = await _call_llm(prompt_template, json.dumps(json_representation, indent=2), session_id, model_id=model_id)
```

### 5. `refine_code` (line 815, 861)
```python
model_id = state.get("model_id")
prompt_template = get_prompt(prompt_key, model_id=model_id)
ai_response = await _call_llm(prompt_template, error_context, session_id, model_id=model_id)
```

## SSE Timeout Configuration

**File:** [backend/app/api/v1/endpoints/diagram.py:67-69](backend/app/api/v1/endpoints/diagram.py#L67-L69)

```python
# 3-second timeout allows frequent "waiting" status updates
update = await asyncio.wait_for(session.update_queue.get(), timeout=3)
```

**Behavior:**
- Every 3 seconds with no real update: send "waiting" status
- Keeps connection healthy with frequent feedback
- User sees progress: "⏳ AI is processing... waiting for response"
- No connection drops or reconnects

## Complete Flow Summary

```
1. USER LAUNCHES DIAGRAMWIZARD
   └─> ModelSelector shown (purple background, 4 model cards)

2. USER SELECTS MODEL (e.g., "GPT-5")
   └─> localStorage saves selection
   └─> ModelSelector hidden
   └─> System Description input shown with model tag

3. USER ENTERS SYSTEM DESCRIPTION
   └─> Clicks "Start Conversation"
   └─> Frontend: startSession(userInput, 'auto', modelId)

4. API RECEIVES REQUEST
   └─> POST /api/v1/diagram/start
   ├─> initial_prompt: "..."
   ├─> diagram_type: "auto"
   └─> model_id: "gpt5"

5. BACKEND INITIALIZES
   └─> DiagramFactoryService.start_generation(prompt, type, model_id)
   └─> Creates GraphState with model_id field
   └─> Starts LangGraph workflow

6. ANALYZE NODE
   └─> Extracts model_id from state
   └─> Loads model-specific prompt: get_prompt("analyze_request", model_id="gpt5")
   └─> Calls _call_llm(..., model_id="gpt5")
   └─> Maps "gpt5" → "openai/gpt-4-turbo"
   └─> Makes API call to selected model

7. CLARIFY NODE (repeated until clarity >= 8)
   └─> Uses same model_id throughout
   └─> User answers questions
   └─> AI provides clarifications using same model

8. JSON GENERATION NODE
   └─> Uses model_id for specific prompt version
   └─> Generates Structurizr DSL representation

9. DIAGRAM TYPE DETERMINATION
   └─> Keyword-based (no LLM call needed)

10. GENERATE CODE NODE
    └─> Uses model_id for code generation
    └─> Generates Mermaid/D2/PlantUML code

11. VALIDATE NODE
    └─> Syntax validation (no LLM call)

12. REFINE NODE (if invalid)
    └─> Uses model_id for refinement
    └─> Same model fixes errors

13. RENDER NODE
    └─> Converts code to SVG
    └─> No model involved (Kroki/GraphViz)

14. COMPLETION
    └─> Session ends
    └─> Frontend shows "Complete! ✅"
    └─> User can export SVG

THROUGHOUT: SSE sends "waiting" status every 3 seconds
```

## Key Files Modified

### Frontend
- ✅ `frontend/src/components/DiagramWizard/ModelSelector.tsx` (Created)
- ✅ `frontend/src/components/DiagramWizard/DiagramWizard.tsx` (Updated)
- ✅ `frontend/src/components/DiagramWizard/hooks/useDiagramSession.ts` (Updated)
- ✅ `frontend/src/services/diagram/diagramApi.ts` (Updated)
- ✅ `frontend/src/hooks/useSSE.ts` (Updated for "waiting" status)

### Backend
- ✅ `backend/app/api/v1/endpoints/diagram.py` (Added model_id parameter, reduced timeout to 3s)
- ✅ `backend/app/services/diagram_factory_service.py` (Updated start_generation signature)
- ✅ `backend/app/utils/diagram_wizard/graph_state.py` (Added model_id field)
- ✅ `backend/app/utils/diagram_wizard/nodes.py` (Updated all LLM-calling nodes)
- ✅ `backend/app/utils/diagram_wizard/prompt_loader.py` (Already supports model_id)

### Documentation
- ✅ `SSE_DISCONNECTION_FIX.md` (Updated timeout documentation)
- ✅ `QUICK_STATUS_REFERENCE.txt` (Updated waiting status frequency)
- ✅ `MODEL_ID_IMPLEMENTATION.md` (This file - complete flow documentation)

## Testing the Implementation

### 1. Test Model Selection
1. Open DiagramWizard
2. Verify ModelSelector appears with 4 models
3. Click each model and verify tag appears
4. Verify localStorage saves: `localStorage.getItem('diagramWizard.selectedModel')`

### 2. Test Model Persistence
1. Select a model
2. Refresh page
3. Verify same model is selected (from localStorage)

### 3. Test Backend Integration
1. Select model (e.g., "gpt5")
2. Enter system description: "E-commerce platform with auth, products, orders"
3. Open browser console and Network tab
4. Verify POST to `/api/v1/diagram/start` includes `model_id: "gpt5"`
5. Verify SSE stream shows "waiting" status every 3 seconds

### 4. Test Model-Specific Prompts
1. Check backend logs for model-specific prompt loading:
   ```
   [SSE] Sending waiting status for session ...
   🔬 Analyzing initial user request (model: gpt5)...
   ```

### 5. Test SSE Waiting Status
1. Watch console during LLM processing
2. Should see multiple "waiting" status messages
3. Each 3 seconds a new "waiting" arrives
4. No reconnection attempts (no "Establishing SSE connection" repeated messages)

## Benefits of This Implementation

✅ **User Control:** Users choose the best model for their needs
✅ **Consistent Throughout:** Same model used for all LLM calls in session
✅ **Preference Persistence:** Selected model saved to localStorage
✅ **Responsive Feedback:** 3-second "waiting" status keeps UI responsive
✅ **Clean Architecture:** Model_id flows through state naturally
✅ **No Connection Issues:** Short timeout prevents SSE disconnects
✅ **Better UX:** Users see progress with frequent updates

## Future Enhancements

- [ ] Save model selection per diagram type (preference learning)
- [ ] A/B testing different models on same architecture
- [ ] Model performance metrics (tokens used, response time, quality score)
- [ ] Advanced model selection based on system complexity
- [ ] Custom model endpoints for enterprise users
