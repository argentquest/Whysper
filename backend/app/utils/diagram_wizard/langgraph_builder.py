"""
LangGraph state machine builder for diagram factory.

Constructs and compiles the diagram generation workflow graph.
"""

from functools import partial
from langgraph.graph import StateGraph, END
from .graph_state import GraphState
from common.logger import get_logger
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

logger = get_logger(__name__)


def route_after_clarify(state: GraphState) -> str:
    """
    Route after clarification phase to next stage.
    
    Args:
        state (GraphState): The current graph state.

    Returns:
        str: The next node to transition to ("generate_json_representation" or END).
    """
    if state.get("llm_ready", False):
        logger.debug(
            f"Routing from clarify_prompt to generate_json_representation "
            f"(llm_ready=True, user_confirmed={state.get('user_confirmed_ready', False)})",
            extra={'session_id': state.get("_session_id")}
        )
        return "generate_json_representation"
    else:
        logger.debug(
            "Routing from clarify_prompt to END (waiting for user input)",
            extra={'session_id': state.get("_session_id")}
        )
        return END


def route_after_diagram_type(state: GraphState) -> str:
    """
    Route after diagram type determination to next stage.
    
    Args:
        state (GraphState): The current graph state.

    Returns:
        str: The next node to transition to ("generate_code" or END).
    """
    if state.get("user_selected_diagram_type", False):
        logger.debug(
            f"Routing from determine_diagram_type to generate_code "
            f"(user_selected={state.get('diagram_type', 'unknown')})",
            extra={'session_id': state.get("_session_id")}
        )
        return "generate_code"
    else:
        logger.debug(
            "Routing from determine_diagram_type to END (waiting for user selection)",
            extra={'session_id': state.get("_session_id")}
        )
        return END


def route_validation(state: GraphState) -> str:
    """
    Route after validation to next stage.
    
    Args:
        state (GraphState): The current graph state.

    Returns:
        str: The next node to transition to ("render_diagram" or "refine_code").
    """
    if state.get("is_valid", False):
        logger.debug(
            "Routing from validate_code to render_diagram (code is valid)",
            extra={'session_id': state.get("_session_id")}
        )
        return "render_diagram"
    else:
        logger.debug(
            f"Routing from validate_code to refine_code (validation_error: {state.get('validation_error', 'unknown')})",
            extra={'session_id': state.get("_session_id")}
        )
        return "refine_code"


def build_diagram_factory_graph(service) -> StateGraph:
    """
    Build the LangGraph state machine for the diagram factory.

    Constructs the graph with all nodes, edges, and conditional routing logic.

    Args:
        service: The DiagramFactoryService instance.

    Returns:
        StateGraph: The compiled LangGraph workflow.
    """
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
            "generate_json_representation": "generate_json_representation",
            "determine_diagram_type": "determine_diagram_type",
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
    """
    Get a new instance of the diagram factory graph.

    This function acts as a factory for creating the graph, ensuring
    a fresh instance is built for each service request.

    Args:
        service: The DiagramFactoryService instance.

    Returns:
        StateGraph: The compiled LangGraph workflow.
    """
    # Build a fresh graph for each service instance
    # This ensures proper state isolation between concurrent diagram generation sessions
    # and allows the graph to use the correct service instance for callbacks
    return build_diagram_factory_graph(service)
