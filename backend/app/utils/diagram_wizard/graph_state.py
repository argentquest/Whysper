"""
Graph state schema for diagram factory LangGraph.

Defines the central state object that flows through all graph nodes.
"""

from typing import TypedDict, List, Dict, Optional, Any
from enum import Enum


class DiagramType(str, Enum):
    """Supported diagram types."""

    # Enumerate supported diagram visualization formats
    MERMAID = "Mermaid"
    D2 = "D2"
    PLANTUML = "PlantUML"
    STRUCTURIZR = "Structurizr"


class SessionState(str, Enum):
    """Session state throughout the diagram wizard workflow."""

    # Define possible states in the diagram generation workflow
    CLARIFYING = "clarifying"       # Gathering and refining requirements
    GENERATING = "generating"        # Creating diagram code
    VALIDATING = "validating"        # Checking diagram code quality
    VALIDATION_ERROR = "validation_error"  # Error in diagram code
    RENDERING = "rendering"          # Converting diagram to visual format
    READY = "ready"                  # Workflow complete
    ERROR = "error"                  # General error state


class GraphState(TypedDict, total=False):
    """
    Central state for the diagram factory LangGraph.

    This TypedDict flows through all nodes in the state machine,
    accumulating information as it progresses through the workflow.
    """

    # Session metadata for tracking and authentication
    session_id: str
    user_id: str
    conversation_id: str
    created_at: str

    # Input phase tracking user's design requirements
    design_prompt: str
    diagram_type: DiagramType  # Determined in determine_diagram_type_node, not user input
    provider_id: Optional[str]
    model_id: Optional[str]  # AI model to use (gpt5, grok, claude, gemini)
    keyword_scores: Optional[Dict[str, float]]  # Scoring breakdown for diagram type recommendations
    user_selected_diagram_type: bool  # User has selected their preferred diagram type

    # Clarification loop to ensure accurate design understanding
    clarification_history: List[Dict[str, str]]  # Track clarification interactions
    clarity_scores: List[int]  # Measure design clarity over iterations
    clarification_timeout: bool  # Flag for excessive clarification time
    llm_ready: bool  # Language model prepared for next step
    user_confirmed_ready: bool  # User agrees with design
    awaiting_user_confirmation: bool  # Waiting for user input
    final_design_summary: str  # Condensed design description
    question_count: int  # Number of clarification questions asked

    # Generation & Validation loop for diagram creation
    diagram_code: str  # Generated diagram representation
    json_representation: Dict[str, Any]  # Structured diagram data
    validation_error: str  # Details of validation failure
    validation_error_type: str  # Categorization of validation error
    recovery_suggestions: List[str]  # Proposed fixes for errors
    is_valid: bool  # Indicates diagram code validity
    refinement_attempt: int  # Number of refinement iterations

    # Output tracking
    svg_output: str  # Final rendered diagram

    # State and error management
    current_state: SessionState  # Current workflow state
    error_message: Optional[str]  # Descriptive error information
    clarification_start_time: Optional[float]  # Runtime: tracks clarification start time
    _session_id: Optional[str]  # Runtime: injected for logging/callbacks
    _update_callback: Optional[Any]  # Runtime: injected for SSE updates
