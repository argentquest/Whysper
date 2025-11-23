# DiagramWizard: Model Selection at Start

## Overview

Instead of auto-detecting the LLM provider from environment variables, the system should **ask the user to select which model version they want** before starting the diagram generation process.

This allows users to choose between optimized prompt versions:
- **GPT-5** – Long-context reasoning & deep analysis
- **Grok** – Fast, deterministic responses
- **Claude Sonnet 4.5** – Structured thinking & transparency
- **Gemini 2.5 Pro** – Efficiency & pragmatism

---

## Architecture: Model Selection Flow

```
┌─────────────────────────────────────────────────────┐
│                    START                            │
├─────────────────────────────────────────────────────┤
│  User opens DiagramWizard                           │
└────────────────────┬────────────────────────────────┘
                     │
                     ▼
        ┌────────────────────────────┐
        │  MODEL SELECTION SCREEN    │
        │                            │
        │  Choose AI Provider:       │
        │  ☐ GPT-5                   │
        │  ☐ Grok                    │
        │  ☐ Claude Sonnet 4.5       │
        │  ☐ Gemini 2.5 Pro          │
        │                            │
        │  [Select] [Cancel]         │
        └────────────┬───────────────┘
                     │
        ┌────────────▼──────────────┐
        │ Store Selected Model       │
        │ in Session State           │
        └────────────┬───────────────┘
                     │
        ┌────────────▼──────────────┐
        │ Load Corresponding         │
        │ ANALYSE_CONFIRM Prompt     │
        │ (model-specific version)   │
        └────────────┬───────────────┘
                     │
        ┌────────────▼──────────────┐
        │ User Describes System      │
        │ (Initial Prompt)           │
        └────────────┬───────────────┘
                     │
        ┌────────────▼──────────────┐
        │ ANALYSE_CONFIRM Node       │
        │ (using selected version)   │
        │                            │
        │ Returns:                   │
        │ • structurizr_workspace    │
        │ • clean_d2                 │
        │ • clarity_score (1-10)     │
        │ • question                 │
        └────────────┬───────────────┘
                     │
        ┌────────────▼──────────────┐
        │ clarify_prompt (Loop)      │
        │ (same model version)       │
        │ continues clarification    │
        └────────────┬───────────────┘
                     │
        ┌────────────▼──────────────┐
        │ determine_diagram_type     │
        │ generate_code              │
        │ validate_code              │
        │ render_diagram             │
        └────────────┬───────────────┘
                     │
                     ▼
        ┌────────────────────────────┐
        │   SUCCESS - SVG Output     │
        └────────────────────────────┘
```

---

## Frontend Implementation

### 1. Model Selection UI Component

**File location:** `frontend/src/components/DiagramWizard/ModelSelector.tsx` (new)

```typescript
interface ModelOption {
  id: 'gpt5' | 'grok' | 'claude' | 'gemini';
  name: string;
  description: string;
  strengths: string[];
  provider: string;
  model: string;
}

const MODEL_OPTIONS: ModelOption[] = [
  {
    id: 'gpt5',
    name: 'GPT-5',
    description: 'Long-context reasoning & deep analysis',
    strengths: ['Complex systems', 'Deep cross-checking', 'Large context'],
    provider: 'openrouter',
    model: 'gpt-5-*'
  },
  {
    id: 'grok',
    name: 'Grok',
    description: 'Fast, deterministic responses',
    strengths: ['Quick decisions', 'Consistent output', 'Lean responses'],
    provider: 'xai',
    model: 'grok-*'
  },
  {
    id: 'claude',
    name: 'Claude Sonnet 4.5',
    description: 'Structured thinking & transparency',
    strengths: ['Clear reasoning', 'Detailed explanations', 'Consistent patterns'],
    provider: 'anthropic',
    model: 'claude-sonnet-4.5-*'
  },
  {
    id: 'gemini',
    name: 'Gemini 2.5 Pro',
    description: 'Efficiency & pragmatism',
    strengths: ['Fast generation', 'Size efficient', 'Practical results'],
    provider: 'google',
    model: 'gemini-2.5-pro-*'
  }
];

export const ModelSelector: React.FC<{
  onSelect: (modelId: string) => void;
}> = ({ onSelect }) => {
  return (
    <div className="model-selector">
      <h2>Select AI Model</h2>
      <div className="model-grid">
        {MODEL_OPTIONS.map((model) => (
          <div
            key={model.id}
            className="model-card"
            onClick={() => onSelect(model.id)}
          >
            <h3>{model.name}</h3>
            <p>{model.description}</p>
            <ul>
              {model.strengths.map((strength) => (
                <li key={strength}>✓ {strength}</li>
              ))}
            </ul>
          </div>
        ))}
      </div>
    </div>
  );
};
```

### 2. DiagramWizard Component Update

```typescript
const DiagramWizard: React.FC = () => {
  const [selectedModel, setSelectedModel] = useState<string | null>(null);

  // Show model selector if not yet selected
  if (!selectedModel) {
    return (
      <ModelSelector onSelect={(modelId) => {
        setSelectedModel(modelId);
        // Start session with selected model
        startDiagramSession(modelId);
      }} />
    );
  }

  // Continue with diagram wizard using selected model
  return (
    <div>
      {/* Existing wizard UI */}
      {/* Pass selectedModel to all API calls */}
    </div>
  );
};
```

---

## Backend Implementation

### 1. Update Session Initialization

**File:** `backend/app/utils/diagram_wizard/main.py` or entry point

```python
@app.post("/api/diagram-wizard/start-session")
async def start_diagram_session(request: StartSessionRequest):
    """
    Start a new diagram wizard session.

    Request body:
    {
        "initial_prompt": "User's system description",
        "model_id": "gpt5" | "grok" | "claude" | "gemini"
    }
    """
    model_id = request.model_id  # USER'S CHOICE
    initial_prompt = request.initial_prompt

    # Map model_id to provider/model
    MODEL_MAPPING = {
        'gpt5': {
            'provider': 'openrouter',
            'model': 'openai/gpt-5-*',
            'prompt_version': 'diagram-wizard-gpt5'
        },
        'grok': {
            'provider': 'xai',
            'model': 'grok-*',
            'prompt_version': 'diagram-wizard-grok'
        },
        'claude': {
            'provider': 'anthropic',
            'model': 'claude-sonnet-4.5-*',
            'prompt_version': 'diagram-wizard-sonet45'
        },
        'gemini': {
            'provider': 'google',
            'model': 'gemini-2.5-pro-*',
            'prompt_version': 'diagram-wizardgemini25pro'
        }
    }

    config = MODEL_MAPPING.get(model_id)
    if not config:
        raise ValueError(f"Unknown model: {model_id}")

    session_id = generate_session_id()

    # Store model choice in session
    session_state = {
        'session_id': session_id,
        'model_id': model_id,  # STORE USER'S CHOICE
        'provider': config['provider'],
        'model': config['model'],
        'prompt_version': config['prompt_version'],
        'initial_prompt': initial_prompt,
        'created_at': datetime.now(),
    }

    # Save session
    await session_store.set(session_id, session_state)

    # Start graph execution with selected model
    return await run_diagram_wizard_graph(
        initial_prompt=initial_prompt,
        session_id=session_id,
        model_id=model_id,
        prompt_version=config['prompt_version']
    )
```

### 2. Update Prompt Loader

**File:** `backend/app/utils/diagram_wizard/prompt_loader.py`

```python
def get_prompt(prompt_key: str, model_id: str = None) -> str:
    """
    Load a prompt, optionally model-specific version.

    Args:
        prompt_key: Base prompt name (e.g., "analyze_request", "clarify_universal")
        model_id: Optional model ID to get version-specific prompt

    Examples:
        get_prompt("analyze_request")  # Generic version
        get_prompt("analyze_request", "gpt5")  # GPT-5 specific
    """

    # If model_id provided, try model-specific version first
    if model_id:
        model_specific_key = f"{prompt_key}_{model_id}"
        if model_specific_key in PROMPTS_CACHE:
            return PROMPTS_CACHE[model_specific_key]

    # Fall back to generic version
    if prompt_key in PROMPTS_CACHE:
        return PROMPTS_CACHE[prompt_key]

    # Load from file if not cached
    # ...existing file loading logic...
```

### 3. Update clarify_prompt Node

**File:** `backend/app/utils/diagram_wizard/nodes.py`

```python
@log_method_call
async def clarify_prompt(state: GraphState) -> Dict[str, Any]:
    """
    Clarification loop node.
    Uses the model version selected at session start.
    """
    model_id = state.get("model_id")  # From session

    # Get model-specific prompt
    analyze_prompt = get_prompt("analyze_request", model_id)
    clarify_prompt_template = get_prompt("clarify_universal", model_id)

    # Rest of implementation uses selected model's prompts
    # ...
```

### 4. Update AI Processor

**File:** `backend/app/utils/diagram_wizard/nodes.py` - `_call_llm()` function

```python
async def _call_llm(
    prompt: str,
    user_content: str,
    session_id: str = None,
    model_id: str = None
) -> str:
    """
    Call AI with the selected model from session.
    """

    # If model_id provided, use it; otherwise use env defaults
    if model_id:
        env_vars = MODEL_MAPPING.get(model_id, {})
        provider = env_vars.get('provider')
        model = env_vars.get('model')
    else:
        # Fallback to environment
        env_vars = env_manager.load_env_file()
        provider = env_vars.get("PROVIDER", "openrouter")
        model = env_vars.get("DEFAULT_MODEL", "google/gemini-2.5-flash")

    # Create processor with selected model
    processor = create_ai_processor(api_key=api_key, provider=provider)

    # Make call with selected model
    result = processor.process_question(
        question=user_content,
        conversation_history=[...],
        model=model,  # USER'S SELECTED MODEL
        ...
    )

    return result
```

---

## State Management Update

### GraphState Enhanced

**File:** `backend/app/utils/diagram_wizard/graph_state.py`

```python
class GraphState(TypedDict, total=False):
    # ... existing fields ...

    # Model Selection (NEW)
    model_id: str  # "gpt5" | "grok" | "claude" | "gemini"
    provider: str  # "openrouter" | "xai" | "anthropic" | "google"
    model: str     # Full model name
    prompt_version: str  # e.g., "diagram-wizard-gpt5"
```

---

## API Changes

### New Endpoint

```
POST /api/diagram-wizard/start-session
Content-Type: application/json

{
  "initial_prompt": "I have a microservices architecture with...",
  "model_id": "gpt5"  // USER'S SELECTION
}

Response:
{
  "session_id": "uuid-xxx",
  "status": "started",
  "model_id": "gpt5"
}
```

### Updated Existing Endpoint

```
POST /api/diagram-wizard/{session_id}/clarify
Content-Type: application/json

{
  "clarification": "We have 5 microservices..."
}

// Uses model_id from session (user's initial choice)
```

---

## Implementation Checklist

- [ ] Create `ModelSelector.tsx` component with 4 model options
- [ ] Update `DiagramWizard.tsx` to show selector first
- [ ] Add `model_id` to `GraphState`
- [ ] Update session initialization to accept `model_id`
- [ ] Create `MODEL_MAPPING` dict in backend
- [ ] Update `prompt_loader.py` to handle model-specific prompts
- [ ] Update `clarify_prompt` node to use selected model's prompts
- [ ] Update `_call_llm()` to use selected model
- [ ] Update all 4 ANALYSE_CONFIRM prompts (already done ✓)
- [ ] Create 4 versions of `clarify_universal` prompt (new task)
- [ ] Update API documentation
- [ ] Add session storage for model choice

---

## Benefits of This Approach

1. **User Control** – Users choose which AI they prefer
2. **Model-Optimized** – Each model gets specialized prompts
3. **Consistent Sessions** – Same model used throughout session
4. **Fallback Handling** – If selected model unavailable, clear error message
5. **A/B Testing** – Can compare model quality over time
6. **Cost Control** – Users can choose cheaper/faster models
7. **Future Extensible** – Easy to add new models

---

## Next Steps

1. Finish updating all 4 ANALYSE_CONFIRM prompts (in progress)
2. **Create 4 versions of `clarify_universal` prompt** (next task)
   - `clarify_universal_gpt5.md`
   - `clarify_universal_grok.md`
   - `clarify_universal_sonet45.md`
   - `clarify_universal_gemini25pro.md`
3. Implement frontend ModelSelector component
4. Update backend session handling
5. Create MODEL_MAPPING and prompt loader updates
6. Test with all 4 models
