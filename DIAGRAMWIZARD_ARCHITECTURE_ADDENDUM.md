# DiagramWizard Architecture Addendum: LangGraph + Provider Integration

**Date:** 2025-11-15
**Purpose:** Clarify the architectural relationship between LangGraph workflow and Provider system

---

## Executive Summary

**Key Principle:** LangGraph is the orchestration engine; Provider system is the execution engine.

- **LangGraph** owns the conversational workflow, intelligence, and decision-making
- **Provider System** provides robust, multi-provider diagram rendering and validation
- **Integration** happens at specific workflow nodes where execution is needed

This architecture preserves DiagramWizard's conversational strength while gaining ArchitectureGenStudio's provider robustness.

---

## Architectural Vision

### Current Architecture (Before Enhancement)

```
┌─────────────────────────────────────────────────────────┐
│                    DiagramWizard                         │
│                                                          │
│  ┌──────────────────────────────────────────────────┐  │
│  │           LangGraph Workflow                      │  │
│  │                                                   │  │
│  │  analyze_request → clarify_prompt →              │  │
│  │  determine_type → generate_code →                │  │
│  │  validate_code → refine_code → render_diagram    │  │
│  │                                                   │  │
│  │  (Each node has custom validation/rendering)     │  │
│  └──────────────────────────────────────────────────┘  │
│                                                          │
│  Custom Rendering Logic (Limited providers)             │
└─────────────────────────────────────────────────────────┘
```

### Target Architecture (After Enhancement)

```
┌──────────────────────────────────────────────────────────────────────┐
│                         DiagramWizard                                 │
│                                                                       │
│  ┌────────────────────────────────────────────────────────────────┐ │
│  │                   LangGraph Workflow                            │ │
│  │                 (Orchestration Layer)                           │ │
│  │                                                                 │ │
│  │  analyze_request → clarify_prompt → determine_type →           │ │
│  │  generate_code → validate_code → refine_code → render_diagram  │ │
│  │                      │                 │              │         │ │
│  │                      └─────────────────┴──────────────┘         │ │
│  │                                    │                            │ │
│  └────────────────────────────────────┼────────────────────────────┘ │
│                                       │                               │
│                                       ▼                               │
│  ┌────────────────────────────────────────────────────────────────┐ │
│  │              Provider Registry (Execution Layer)                │ │
│  │                                                                 │ │
│  │  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐            │ │
│  │  │  Mermaid    │  │     D2      │  │  PlantUML   │            │ │
│  │  │  (CLI+Kroki)│  │ (CLI+Kroki) │  │   (Kroki)   │            │ │
│  │  └─────────────┘  └─────────────┘  └─────────────┘            │ │
│  │                                                                 │ │
│  │  • 3-Tier Validation (CLI → Pattern → LLM)                     │ │
│  │  • Auto-fix (Pattern-based + LLM-based)                        │ │
│  │  • Multi-format Output (SVG, PNG, PDF)                         │ │
│  │  • Extensible Provider System                                  │ │
│  └────────────────────────────────────────────────────────────────┘ │
│                                                                       │
└──────────────────────────────────────────────────────────────────────┘
```

---

## Integration Points: LangGraph Nodes → Provider System

### Node 1: `validate_code`

**LangGraph Responsibility:**
- Decide when validation is needed
- Track validation attempts
- Handle validation state transitions
- Determine next steps based on results

**Provider System Responsibility:**
- Execute actual validation (CLI or pattern-based)
- Return structured validation results
- Provide error details with line numbers

**Integration:**

```python
# backend/app/utils/diagram_wizard/nodes.py

async def validate_code(state: GraphState) -> GraphState:
    """
    LangGraph node that validates diagram code using provider system
    """
    session_id = state.get("session_id")
    diagram_code = state.get("diagram_code")
    diagram_type = state.get("diagram_type")

    logger.info(f"[{session_id}] Validating {diagram_type.value} code via provider system")

    # Call provider system for validation
    provider_registry = ProviderRegistry.get_instance()
    provider = provider_registry.get_provider_for_type(diagram_type.value)

    if not provider:
        logger.warning(f"[{session_id}] No provider found for {diagram_type.value}, skipping validation")
        return {
            **state,
            "is_valid": True,  # Optimistic - will fail at render if invalid
            "validation_warning": f"No validator available for {diagram_type.value}",
        }

    # Use provider's validation capability
    validation_result = await provider.validate_code(diagram_code)

    if validation_result.is_valid:
        logger.info(f"[{session_id}] Validation passed")
        return {
            **state,
            "is_valid": True,
            "validation_error": None,
            "current_state": SessionState.VALIDATING,
        }
    else:
        logger.warning(f"[{session_id}] Validation failed: {len(validation_result.errors)} errors")
        return {
            **state,
            "is_valid": False,
            "validation_error": "; ".join([err.message for err in validation_result.errors]),
            "validation_details": validation_result,  # Store full details for refine node
            "current_state": SessionState.VALIDATING,
        }
```

**Benefits:**
- LangGraph maintains workflow control
- Provider system provides robust validation
- Easy to add new diagram types (just register provider)
- Validation logic centralized and reusable

---

### Node 2: `refine_code`

**LangGraph Responsibility:**
- Track refinement attempts (max 3)
- Decide between pattern-based and LLM-based correction
- Handle timeout and max attempts
- Update state with refined code

**Provider System Responsibility:**
- Execute pattern-based auto-fix
- Execute LLM-based correction
- Return corrected code
- Track corrections applied

**Integration:**

```python
async def refine_code(state: GraphState) -> GraphState:
    """
    LangGraph node that refines invalid code using provider system's
    3-tier correction strategy
    """
    session_id = state.get("session_id")
    diagram_code = state.get("diagram_code")
    diagram_type = state.get("diagram_type")
    refinement_attempt = state.get("refinement_attempt", 0)
    validation_details = state.get("validation_details")

    # Check max attempts (LangGraph workflow decision)
    if refinement_attempt >= 3:
        logger.error(f"[{session_id}] Max refinement attempts reached")
        return {
            **state,
            "current_state": SessionState.ERROR,
            "validation_error": "Failed to fix code after 3 attempts",
        }

    logger.info(f"[{session_id}] Refinement attempt {refinement_attempt + 1}/3")

    # Use provider system's correction capabilities
    provider_registry = ProviderRegistry.get_instance()
    provider = provider_registry.get_provider_for_type(diagram_type.value)

    if not provider:
        return {
            **state,
            "current_state": SessionState.ERROR,
            "validation_error": "No provider available for correction",
        }

    # Strategy decision (LangGraph orchestration)
    if refinement_attempt == 0:
        # Attempt 1: Pattern-based auto-fix (fast, free)
        logger.info(f"[{session_id}] Attempting pattern-based auto-fix")
        corrected_code = await provider.auto_fix_pattern_based(
            diagram_code,
            validation_details.errors if validation_details else []
        )
    else:
        # Attempt 2-3: LLM-based correction (intelligent, slower)
        logger.info(f"[{session_id}] Attempting LLM-based correction")

        # Get LLM correction service (from provider system)
        llm_service = provider_registry.get_llm_correction_service()

        corrected_code = await llm_service.correct_code(
            code=diagram_code,
            diagram_type=diagram_type.value,
            errors=validation_details.errors if validation_details else [],
            context={
                "attempt": refinement_attempt,
                "session_id": session_id,
                "design_prompt": state.get("design_prompt"),
            }
        )

    # LangGraph updates state and decides next step
    return {
        **state,
        "diagram_code": corrected_code,
        "refinement_attempt": refinement_attempt + 1,
        "current_state": SessionState.REFINING,
        "corrections_applied": True,
    }
    # Workflow will route back to validate_code node to check if fix worked
```

**Benefits:**
- LangGraph controls retry strategy
- Provider system provides multiple correction tiers
- Intelligent escalation (pattern → LLM)
- Context-aware corrections using conversation history

---

### Node 3: `render_diagram`

**LangGraph Responsibility:**
- Decide when rendering is appropriate
- Track rendering state
- Handle rendering errors
- Store rendered output in state

**Provider System Responsibility:**
- Execute actual rendering (CLI or API)
- Handle multiple output formats
- Apply final auto-fixes if needed
- Save files to static directory

**Integration:**

```python
async def render_diagram(state: GraphState) -> GraphState:
    """
    LangGraph node that renders diagram using provider system
    """
    session_id = state.get("session_id")
    diagram_code = state.get("diagram_code")
    diagram_type = state.get("diagram_type")

    logger.info(f"[{session_id}] Rendering {diagram_type.value} diagram via provider system")

    # Call provider system for rendering
    provider_registry = ProviderRegistry.get_instance()
    provider = provider_registry.get_provider_for_type(diagram_type.value)

    if not provider:
        return {
            **state,
            "current_state": SessionState.ERROR,
            "validation_error": f"No renderer available for {diagram_type.value}",
        }

    try:
        # Use provider's render_with_validation for final safety check
        result = await provider.render_with_validation(
            code=diagram_code,
            output_format="svg",
            auto_fix=True,  # Last chance auto-fix
            llm_correction=False,  # Already tried in refine_code
            save_to_file=True,  # Save to backend/static/diagrams/
            metadata={
                "session_id": session_id,
                "diagram_type": diagram_type.value,
                "workflow": "langgraph",
            }
        )

        # LangGraph updates state with successful render
        return {
            **state,
            "svg_output": result.svg,
            "diagram_code": result.code,  # May be auto-corrected
            "is_valid": True,
            "current_state": SessionState.READY,
            "render_metadata": {
                "provider_id": result.metadata.get("provider_id"),
                "file_path": result.metadata.get("file_path"),
                "format": result.metadata.get("format"),
                "corrections_applied": result.metadata.get("corrections_applied", []),
            },
        }

    except Exception as e:
        logger.error(f"[{session_id}] Rendering failed: {e}")
        return {
            **state,
            "current_state": SessionState.ERROR,
            "validation_error": f"Rendering failed: {str(e)}",
        }
```

**Benefits:**
- LangGraph maintains state consistency
- Provider system handles all rendering complexity
- Automatic fallback between providers (if configured)
- Metadata returned for UI display

---

## Workflow Routing: LangGraph as Orchestrator

### Current LangGraph Workflow with Provider Integration

```python
# backend/app/utils/diagram_wizard/langgraph_builder.py

def get_diagram_factory_graph() -> Graph:
    """
    Build LangGraph workflow that orchestrates provider system
    """
    workflow = StateGraph(GraphState)

    # Add nodes (workflow steps)
    workflow.add_node("analyze_request", analyze_request)
    workflow.add_node("clarify_prompt", clarify_prompt)
    workflow.add_node("determine_diagram_type", determine_diagram_type_node)
    workflow.add_node("generate_code", generate_code)

    # These nodes now use provider system internally
    workflow.add_node("validate_code", validate_code)  # Uses provider.validate_code()
    workflow.add_node("refine_code", refine_code)      # Uses provider.auto_fix() + llm_correction
    workflow.add_node("render_diagram", render_diagram) # Uses provider.render_with_validation()

    # Define edges (workflow routing - LangGraph's strength)
    workflow.add_edge("analyze_request", "clarify_prompt")

    # Conditional routing based on clarification completeness
    workflow.add_conditional_edges(
        "clarify_prompt",
        route_to_diagram_type_determination,  # LangGraph decides when ready
        {
            "continue_clarification": "clarify_prompt",  # Loop back
            "proceed_to_generation": "determine_diagram_type",  # Move forward
        }
    )

    workflow.add_edge("determine_diagram_type", "generate_code")
    workflow.add_edge("generate_code", "validate_code")

    # Conditional routing based on validation result (from provider)
    workflow.add_conditional_edges(
        "validate_code",
        route_validation,  # LangGraph decides next step
        {
            "valid": "render_diagram",  # Success path
            "invalid": "refine_code",   # Correction path
        }
    )

    # After refinement, always re-validate
    workflow.add_edge("refine_code", "validate_code")

    # Terminal node
    workflow.add_edge("render_diagram", END)

    workflow.set_entry_point("analyze_request")

    return workflow.compile()
```

**Key Points:**
- LangGraph controls the workflow logic (when to validate, when to refine, when to render)
- Provider system provides the execution primitives (validate, fix, render)
- Decisions stay in LangGraph; execution delegated to providers

---

## Benefits of This Architecture

### 1. Separation of Concerns

**LangGraph (Orchestration Layer):**
- Conversational intelligence
- Workflow state management
- Decision-making (when to proceed, retry, fail)
- User interaction (clarifications, confirmations)
- Session lifecycle
- Timeout and retry logic

**Provider System (Execution Layer):**
- Multi-provider support (Mermaid, D2, PlantUML, etc.)
- Validation (CLI, pattern, LLM-based)
- Rendering (CLI, Kroki API)
- Auto-correction (pattern + LLM)
- Error handling and logging
- Output format conversion

### 2. Best of Both Worlds

**From DiagramWizard (Keep):**
- ✅ Conversational clarification workflow
- ✅ Information scoring system
- ✅ User confirmation before generation
- ✅ Persistent schema context across turns
- ✅ Intelligent diagram type detection
- ✅ Session-based SSE updates

**From ArchitectureGenStudio (Gain):**
- ✅ Multi-provider support (easy to add providers)
- ✅ 3-tier validation (CLI → Pattern → LLM)
- ✅ Robust auto-correction
- ✅ Multiple output formats
- ✅ Extensible provider architecture
- ✅ Production-ready error handling

### 3. Extensibility

**Adding a new diagram type is now trivial:**

1. Register provider in `backend/diagrams/`:
   ```
   backend/diagrams/graphviz/
   ├── config.json
   ├── graphviz_renderer.py
   └── README.md
   ```

2. LangGraph workflow automatically uses it:
   - No changes to workflow nodes
   - No changes to state machine
   - Provider registry auto-discovers it
   - Works immediately in all nodes (validate, refine, render)

**Adding new validation/correction logic:**

1. Update provider's `validate_code()` method
2. LangGraph workflow benefits immediately
3. No workflow code changes needed

### 4. Maintainability

**Clear boundaries:**
- Workflow developers work on LangGraph (`.py` files in `diagram_wizard/`)
- Provider developers work on providers (`.py` files in `diagrams/`)
- Changes don't cascade across boundaries
- Easy to test in isolation

**Upgrade paths:**
- Upgrade LangGraph without touching providers
- Upgrade providers without touching workflow
- Swap providers (e.g., Kroki → PlantUML CLI) without workflow changes

---

## Updated Implementation Plan: Phase 1.3

### Step 1.3.1: Update LangGraph Nodes (NOT replace workflow)

**Goal:** Keep LangGraph workflow intact, enhance nodes to use provider system

**Files to Modify:**

1. **`backend/app/utils/diagram_wizard/nodes.py`**
   - Update `validate_code()` to call `provider.validate_code()`
   - Update `refine_code()` to call `provider.auto_fix()` and `llm_correction_service`
   - Update `render_diagram()` to call `provider.render_with_validation()`
   - Keep all other nodes unchanged (analyze, clarify, determine_type, generate)

2. **`backend/app/utils/diagram_wizard/graph_state.py`**
   - Add optional fields for provider metadata:
     ```python
     class GraphState(TypedDict):
         # ... existing fields ...

         # New provider-related fields
         provider_metadata: Optional[Dict[str, Any]]
         validation_details: Optional[ValidationResult]
         corrections_applied: Optional[List[str]]
         render_provider_id: Optional[str]
     ```

3. **`backend/app/services/diagram_factory_service.py`**
   - No major changes needed
   - LangGraph workflow already returns state with all data
   - Just ensure provider metadata is included in SSE updates

**DO NOT CHANGE:**
- LangGraph workflow structure (`langgraph_builder.py`)
- Clarification loop logic
- Information scoring system
- User confirmation flow
- Session management
- SSE streaming architecture

### Step 1.3.2: Integration Testing

**Test that LangGraph workflow:**
1. Still performs clarification loop correctly
2. Calls provider system for validation
3. Calls provider system for correction
4. Calls provider system for rendering
5. Returns all metadata to frontend
6. SSE updates include provider info

**Example Test:**

```python
# tests/integration/test_langgraph_provider_integration.py

async def test_langgraph_uses_provider_system():
    """
    Verify LangGraph workflow calls provider system correctly
    """
    # Start session
    session = await diagram_factory_service.start_generation(
        initial_prompt="A simple login flow",
        diagram_type="Mermaid"
    )

    # Skip clarification (for testing)
    session.graph_state["llm_ready"] = True
    session.graph_state["user_confirmed_ready"] = True

    # Run workflow
    result = await diagram_factory_service.run_workflow(session)

    # Verify provider system was used
    assert result["provider_metadata"] is not None
    assert result["provider_metadata"]["provider_id"] == "mermaidv1"
    assert result["svg_output"] is not None

    # Verify LangGraph state is consistent
    assert result["current_state"] == SessionState.READY
    assert result["is_valid"] == True
```

---

## Clarifications on Architecture Decisions

### Q: Should LangGraph call provider system directly or via API endpoints?

**A: Direct function calls (internal API), not HTTP**

**Reason:**
- LangGraph and providers are in the same backend
- No need for HTTP overhead
- Better error handling
- Easier to pass complex objects
- Faster execution

**Implementation:**
```python
# Good: Direct import and call
from diagrams.provider_registry import ProviderRegistry

provider = ProviderRegistry.get_instance().get_provider_for_type("Mermaid")
result = await provider.validate_code(code)

# Avoid: HTTP call to own backend
# response = await http.post("/diagrams/v2/validate", {...})
```

### Q: Should provider system be aware of LangGraph?

**A: No - one-way dependency only**

**Reason:**
- Providers should be reusable (e.g., ArchStudio can use same providers)
- Keeps providers simple and testable
- LangGraph depends on providers; providers don't know about LangGraph

**Dependency Graph:**
```
┌─────────────────┐
│   LangGraph     │ ─depends on─┐
│   Workflow      │             │
└─────────────────┘             │
                                ▼
                        ┌─────────────────┐
                        │  Provider       │
                        │  Registry       │
                        └─────────────────┘
                                │
                    ┌───────────┼───────────┐
                    ▼           ▼           ▼
            ┌─────────┐  ┌─────────┐  ┌─────────┐
            │Mermaid  │  │   D2    │  │PlantUML │
            │Provider │  │Provider │  │Provider │
            └─────────┘  └─────────┘  └─────────┘
```

### Q: Can ArchitectureGenStudio still use provider system?

**A: Yes - that's the beauty of this architecture!**

**Two workflows, one provider system:**

```
┌──────────────────────┐         ┌──────────────────────┐
│  DiagramWizard       │         │ ArchitectureGenStudio│
│                      │         │                      │
│  LangGraph Workflow  │         │  Agent-based         │
│  (Conversational)    │         │  (Direct)            │
└──────────┬───────────┘         └──────────┬───────────┘
           │                                 │
           └─────────────┬───────────────────┘
                         │
                         ▼
                ┌────────────────────┐
                │  Provider Registry │
                │  (Shared)          │
                └────────────────────┘
```

**Both can coexist:**
- DiagramWizard: `POST /diagram/start` → LangGraph → Providers
- ArchStudio: `POST /diagrams/v2/generate` → Agent → Providers

---

## Migration Path: Zero Breaking Changes

**Phase 1.3 Implementation (Updated):**

### Week 1: Prepare Provider Integration (No Breaking Changes)

**Day 1-2: Add Provider Registry to LangGraph Context**
```python
# backend/app/utils/diagram_wizard/graph_state.py

# Add to state
_provider_registry: Optional[ProviderRegistry]  # Internal use only

# Initialize in DiagramFactoryService
async def start_generation(self, initial_prompt: str, diagram_type: str):
    initial_state = {
        # ... existing state ...
        "_provider_registry": ProviderRegistry.get_instance(),
    }
```

**Day 3-4: Update `validate_code` Node**
```python
# Keep existing validation as fallback
# Add provider validation as primary

async def validate_code(state: GraphState) -> GraphState:
    provider_registry = state.get("_provider_registry")

    # Try provider validation first
    if provider_registry:
        try:
            provider = provider_registry.get_provider_for_type(diagram_type)
            if provider and provider.supports_validation:
                result = await provider.validate_code(code)
                # Use provider result
        except Exception as e:
            logger.warning(f"Provider validation failed, using fallback: {e}")
            # Fall back to existing validation

    # Existing validation logic as fallback
    # ... (keep unchanged for now)
```

**Day 5: Test with Feature Flag**
```python
# Environment variable to enable/disable provider system
USE_PROVIDER_SYSTEM = os.getenv("USE_PROVIDER_SYSTEM", "false") == "true"

if USE_PROVIDER_SYSTEM and provider_registry:
    # Use provider system
else:
    # Use legacy validation
```

### Week 2: Full Provider Integration (Tested & Enabled)

**Day 1-3: Update remaining nodes (refine, render)**
**Day 4-5: Integration testing**
**Day 6-7: Enable for 10% of users, monitor, rollout**

---

## Conclusion

**This architecture preserves the best of both worlds:**

1. **DiagramWizard keeps its soul:** LangGraph conversational workflow
2. **Gains ArchStudio's muscles:** Provider system robustness
3. **Future-proof:** Easy to add providers, diagram types, validation logic
4. **Maintainable:** Clear separation of concerns
5. **Backward compatible:** Can roll out incrementally with feature flags

**Next Steps:**
1. Review and approve this architectural approach
2. Update Phase 1.3 implementation plan with this strategy
3. Begin implementation with provider integration in LangGraph nodes
4. Test thoroughly with feature flags
5. Gradual rollout

**Key Takeaway:** LangGraph orchestrates; Providers execute. Best of both worlds.

---

**Document Control:**
- **Author:** AI Assistant
- **Date Created:** 2025-11-15
- **Status:** DRAFT - Architectural Clarification
- **Related:** DIAGRAMWIZARD_ENHANCEMENT_PLAN.md
- **Approvers:** Tech Lead, Architect
