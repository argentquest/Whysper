"""
LangGraph state machine builder for diagram factory.

Constructs and compiles the diagram generation workflow graph.
"""

from functools import partial
from langgraph.graph import StateGraph, END
from .graph_state import GraphState
from .nodes import (
    analyze_request,
    clarify_prompt,
    generate_json_representation,
    generate_code,
    validate_code,
    refine_code,
    render_diagram,
)


def route_analysis(state: GraphState) -> str:
    """
    Route from analysis node based on next_action.
    """
    if state.get("next_action") == "clarify":
        return "clarify_prompt"
    else:
        return "generate_json_representation"


def route_clarification(state: GraphState) -> str:
    """
    Route from clarification node based on llm_ready flag.

    If llm_ready is True, proceed to JSON generation.
    If False, end and wait for user response.
    """
    if state.get("llm_ready", False):
        return "generate_json_representation"
    else:
        return END


def route_validation(state: GraphState) -> str:
    """
    Route from validation node based on is_valid flag.

    If valid and user has approved, proceed to rendering.
    If valid and user has not approved, end and wait for user input.
    If invalid, proceed to refinement.
    """
    if state.get("is_valid", False):
        if state.get("user_approved_render", False):
            return "render_diagram"
        else:
            return END
    else:
        return "refine_code"


def build_diagram_factory_graph(service) -> StateGraph:
    """
    Build and compile the diagram factory LangGraph state machine.
    """
    # Create state graph
    workflow = StateGraph(GraphState)

    # Add nodes
    workflow.add_node("analyze_request", partial(analyze_request, service=service))
    workflow.add_node("clarify_prompt", clarify_prompt)
    workflow.add_node("generate_json_representation", generate_json_representation)
    workflow.add_node("generate_code", generate_code)
    workflow.add_node("validate_code", validate_code)
    workflow.add_node("refine_code", refine_code)
    workflow.add_node("render_diagram", render_diagram)

    # Set entry point
    workflow.set_entry_point("analyze_request")

    # Add edges
    workflow.add_edge("generate_json_representation", "generate_code")
    workflow.add_edge("generate_code", "validate_code")
    workflow.add_edge("refine_code", "validate_code")
    workflow.add_edge("render_diagram", END)

    # Add conditional edges
    workflow.add_conditional_edges(
        "analyze_request",
        route_analysis,
        {"clarify_prompt": "clarify_prompt", "generate_json_representation": "generate_json_representation"},
    )

    workflow.add_conditional_edges(
        "clarify_prompt",
        route_clarification,
        {"generate_json_representation": "generate_json_representation", END: END},
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


def get_diagram_factory_graph(service):
    """
    Get or create the compiled diagram factory graph.

    Uses lazy loading to avoid recompiling on every import.
    """
    global _compiled_graph
    if _compiled_graph is None:
        _compiled_graph = build_diagram_factory_graph(service)
    return _compiled_graph
