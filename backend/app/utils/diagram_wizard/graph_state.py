"""
Graph state schema for diagram factory LangGraph.

Defines the central state object that flows through all graph nodes.
"""

from typing import TypedDict, List, Dict, Optional, Any
from enum import Enum


class DiagramType(str, Enum):
    """Supported diagram types."""

    MERMAID = "Mermaid"
    D2 = "D2"
    PLANTUML = "PlantUML"


class SessionState(str, Enum):
    """Session state throughout the diagram wizard workflow."""

    CLARIFYING = "clarifying"
    GENERATING = "generating"
    VALIDATING = "validating"
    VALIDATION_ERROR = "validation_error"
    RENDERING = "rendering"
    READY = "ready"
    ERROR = "error"


class GraphState(TypedDict, total=False):
    """
    Central state for the diagram factory LangGraph.

    This TypedDict flows through all nodes in the state machine,
    accumulating information as it progresses through the workflow.
    """

    # Session metadata
    session_id: str
    user_id: str
    conversation_id: str
    created_at: str

    # Input phase
    design_prompt: str
    diagram_type: DiagramType  # Determined in determine_diagram_type_node, not user input
    provider_id: Optional[str]
    model_id: Optional[str]  # AI model to use (gpt5, grok, claude, gemini)

    # Clarification loop
    clarification_history: List[Dict[str, str]]
    clarity_scores: List[int]
    clarification_timeout: bool
    llm_ready: bool
    user_confirmed_ready: bool
    awaiting_user_confirmation: bool
    final_design_summary: str
    question_count: int

    # Generation & Validation loop
    diagram_code: str
    json_representation: Dict[str, Any]
    validation_error: str
    validation_error_type: str
    recovery_suggestions: List[str]
    is_valid: bool
    refinement_attempt: int

    # Output
    svg_output: str

    # State tracking
    current_state: SessionState
    error_message: Optional[str]
    clarification_start_time: Optional[float]  # Runtime: tracks clarification start time
    _session_id: Optional[str]  # Runtime: injected for logging/callbacks
    _update_callback: Optional[Any]  # Runtime: injected for SSE updates
