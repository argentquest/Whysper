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
    determine_diagram_type_node,
    generate_code,
    validate_code,
    refine_code,
    render_diagram,
)


def route_to_diagram_type_determination(state: GraphState) -> str:
    """
    Route from clarification node based on llm_ready flag.

    If llm_ready is True, proceed to determine diagram type.
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
    workflow.add_node("determine_diagram_type", determine_diagram_type_node)
    workflow.add_node("generate_code", generate_code)
    workflow.add_node("validate_code", validate_code)
    workflow.add_node("refine_code", refine_code)
    workflow.add_node("render_diagram", render_diagram)

    # Set entry point
    workflow.set_entry_point("analyze_request")

    # Add edges
    workflow.add_edge("determine_diagram_type", "generate_code")
    workflow.add_edge("generate_code", "validate_code")
    workflow.add_edge("refine_code", "validate_code")
    workflow.add_edge("render_diagram", END)

    # Add conditional edges
    # ANALYZE always routes to CLARIFY (which is the first clarification turn)
    workflow.add_edge("analyze_request", "clarify_prompt")

    # CLARIFY routes to JSON_GENERATION when ready (llm_ready=True), or END if waiting for user
    workflow.add_conditional_edges(
        "clarify_prompt",
        route_to_diagram_type_determination,
        {"generate_code": "generate_json_representation", END: END},
    )

    # JSON_GENERATION always routes to DETERMINE_DIAGRAM_TYPE
    workflow.add_edge("generate_json_representation", "determine_diagram_type")

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
