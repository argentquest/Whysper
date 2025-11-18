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
    # Determine routing based on LLM readiness
    # If LLM is ready, proceed to code generation, otherwise wait for user
    if state.get("llm_ready", False):
        return "generate_code"
    else:
        return END


def route_validation(state: GraphState) -> str:
    # Validate generated code and route to next step
    # If code is valid, render diagram; if invalid, refine code
    if state.get("is_valid", False):
        return "render_diagram"
    else:
        return "refine_code"


def build_diagram_factory_graph(service) -> StateGraph:
    # Initialize state graph for diagram generation workflow
    # Creates a structured workflow with multiple nodes and conditional routing
    workflow = StateGraph(GraphState)

    # Add nodes representing different stages of diagram generation
    # Each node is a specific function with a clear responsibility
    workflow.add_node("analyze_request", partial(analyze_request, service=service))
    workflow.add_node("clarify_prompt", clarify_prompt)
    workflow.add_node("generate_json_representation", generate_json_representation)
    workflow.add_node("determine_diagram_type", determine_diagram_type_node)
    workflow.add_node("generate_code", generate_code)
    workflow.add_node("validate_code", validate_code)
    workflow.add_node("refine_code", refine_code)
    workflow.add_node("render_diagram", render_diagram)

    # Set the initial entry point for the workflow
    workflow.set_entry_point("analyze_request")

    # Define deterministic edges between nodes
    # These represent guaranteed transitions in the workflow
    workflow.add_edge("determine_diagram_type", "generate_code")
    workflow.add_edge("generate_code", "validate_code")
    workflow.add_edge("refine_code", "validate_code")
    workflow.add_edge("render_diagram", END)

    # Add conditional routing between nodes
    # Uses custom routing functions to dynamically determine next steps
    workflow.add_edge("analyze_request", "clarify_prompt")

    workflow.add_conditional_edges(
        "clarify_prompt",
        route_to_diagram_type_determination,
        {"generate_code": "generate_json_representation", END: END},
    )

    workflow.add_edge("generate_json_representation", "determine_diagram_type")

    workflow.add_conditional_edges(
        "validate_code",
        route_validation,
        {"render_diagram": "render_diagram", "refine_code": "refine_code"},
    )

    # Compile the workflow into an executable graph
    return workflow.compile()


# Use lazy loading to cache compiled graph and avoid repeated compilation
_compiled_graph = None


def get_diagram_factory_graph(service):
    # Retrieve or create compiled graph, implementing singleton-like behavior
    # Ensures graph is only compiled once and reused across calls
    global _compiled_graph
    if _compiled_graph is None:
        _compiled_graph = build_diagram_factory_graph(service)
    return _compiled_graph