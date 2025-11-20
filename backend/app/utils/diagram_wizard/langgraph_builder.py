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


def route_after_clarify(state: GraphState) -> str:
    # Determine routing after clarification phase
    # If LLM is ready (user confirmed or timeout), proceed to JSON generation
    # Otherwise, end graph and wait for user response (either answer to question or confirmation)
    # The graph will resume when user provides input via handle_clarification or confirm_ready
    if state.get("llm_ready", False):
        return "generate_json"
    else:
        # Not ready - end graph and wait for user input
        # Graph will resume from analyze_request (which skips re-analysis) when user responds
        return END


def route_after_diagram_type(state: GraphState) -> str:
    # Determine routing after diagram type determination
    # If user has selected their preferred diagram type, proceed to code generation
    # Otherwise, end graph and wait for user selection via select_diagram_type endpoint
    if state.get("user_selected_diagram_type", False):
        return "generate_code"
    else:
        # Wait for user to select diagram type
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
    workflow.add_edge("generate_code", "validate_code")
    workflow.add_edge("refine_code", "validate_code")
    workflow.add_edge("render_diagram", END)

    # Add conditional routing between nodes
    # Uses custom routing functions to dynamically determine next steps
    workflow.add_edge("analyze_request", "clarify_prompt")

    workflow.add_conditional_edges(
        "clarify_prompt",
        route_after_clarify,
        {
            "generate_json": "generate_json_representation",
            END: END  # End when waiting for user input (question or confirmation)
        },
    )

    workflow.add_edge("generate_json_representation", "determine_diagram_type")

    workflow.add_conditional_edges(
        "determine_diagram_type",
        route_after_diagram_type,
        {
            "generate_code": "generate_code",
            END: END  # End when waiting for user diagram type selection
        },
    )

    workflow.add_conditional_edges(
        "validate_code",
        route_validation,
        {"render_diagram": "render_diagram", "refine_code": "refine_code"},
    )

    # Compile the workflow into an executable graph
    return workflow.compile()


# Use lazy loading to cache compiled graph and avoid repeated compilation
# Note: The graph is rebuilt for each service instance to ensure proper state isolation
# This prevents issues with shared state between concurrent sessions

def get_diagram_factory_graph(service):
    # Build a fresh graph for each service instance
    # This ensures proper state isolation between concurrent diagram generation sessions
    # and allows the graph to use the correct service instance for callbacks
    return build_diagram_factory_graph(service)
