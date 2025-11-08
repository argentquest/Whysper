"""
Graph state schema for diagram factory LangGraph.

Defines the central state object that flows through all graph nodes.
"""

from typing import TypedDict, List, Dict, Optional
from enum import Enum


class DiagramType(str, Enum):
    """Supported diagram types."""

    MERMAID = "Mermaid"
    D2 = "D2"
    PLANTUML = "PlantUML"


class SessionState(str, Enum):
    """Session state throughout the diagram wizard workflow."""

    INITIALIZED = "initialized"
    INPUT_PHASE = "input_phase"
    CLARIFYING = "clarifying"
    GENERATING = "generating"
    VALIDATING = "validating"
    VALIDATION_ERROR = "validation_error"
    RENDERING = "rendering"
    READY = "ready"
    EDIT_MODE = "edit_mode"
    COMPLETED = "completed"
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
    diagram_type: DiagramType

    # Clarification loop
    clarification_history: List[Dict[str, str]]
    clarification_timeout: bool
    llm_ready: bool
    final_design_summary: str
    question_count: int

    # Generation & Validation loop
    diagram_code: str
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
