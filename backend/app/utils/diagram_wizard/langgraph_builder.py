"""
LangGraph state machine builder for diagram factory.

Constructs and compiles the diagram generation workflow graph.
"""

from langgraph.graph import StateGraph, END
from .graph_state import GraphState
from .nodes import (
    clarify_prompt,
    generate_code,
    validate_code,
    refine_code,
    render_diagram,
)


def route_clarification(state: GraphState) -> str:
    """
    Route from clarification node based on llm_ready flag.

    If llm_ready is True, proceed to code generation.
    If False, end and wait for user response.
    """
    if state.get("llm_ready", False):
        return "generate_code"
    else:
        return END


def route_validation(state: GraphState) -> str:
    """
    Route from validation node based on is_valid flag.

    If valid, proceed to rendering.
    If invalid, proceed to refinement.
    """
    if state.get("is_valid", False):
        return "render_diagram"
    else:
        return "refine_code"


def build_diagram_factory_graph() -> StateGraph:
    """
    Build and compile the diagram factory LangGraph state machine.

    Flow:
    ```
    clarify_prompt
        ├─ (if llm_ready=True) → generate_code
        └─ (if llm_ready=False) → END (wait for user)

    generate_code → validate_code

    validate_code
        ├─ (if is_valid=True) → render_diagram
        └─ (if is_valid=False) → refine_code → validate_code

    render_diagram → END
    ```

    Returns:
        Compiled StateGraph ready for execution
    """
    # Create state graph
    workflow = StateGraph(GraphState)

    # Add nodes
    workflow.add_node("clarify_prompt", clarify_prompt)
    workflow.add_node("generate_code", generate_code)
    workflow.add_node("validate_code", validate_code)
    workflow.add_node("refine_code", refine_code)
    workflow.add_node("render_diagram", render_diagram)

    # Set entry point
    workflow.set_entry_point("clarify_prompt")

    # Add edges
    workflow.add_edge("generate_code", "validate_code")
    workflow.add_edge("refine_code", "validate_code")
    workflow.add_edge("render_diagram", END)

    # Add conditional edges
    workflow.add_conditional_edges(
        "clarify_prompt",
        route_clarification,
        {"generate_code": "generate_code", END: END},
    )

    workflow.add_conditional_edges(
        "validate_code",
        route_validation,
        {"render_diagram": "render_diagram", "refine_code": "refine_code"},
    )

    # Compile and return
    return workflow.compile()


# Lazy load compiled graph
_compiled_graph = None


def get_diagram_factory_graph():
    """
    Get or create the compiled diagram factory graph.

    Uses lazy loading to avoid recompiling on every import.
    """
    global _compiled_graph
    if _compiled_graph is None:
        _compiled_graph = build_diagram_factory_graph()
    return _compiled_graph
