"""Diagram Factory Service - Orchestrates LangGraph-based diagram generation.

This service manages the entire lifecycle of AI-powered diagram generation
sessions. It provides an intelligent, conversational interface where users
describe their systems and the AI guides them through creating professional
diagrams.

Key Features:
- Session-based workflow management
- Intelligent information scoring and clarification
- Multi-diagram type support (Mermaid, D2, PlantUML)
- Real-time status updates via asyncio queues
- LangGraph integration for complex diagram generation workflows
"""

import uuid
import asyncio
import logging
import json
import os
import time
from typing import Dict, Any, List, Tuple, Optional

from app.utils.diagram_wizard.langgraph_builder import get_diagram_factory_graph
from app.utils.diagram_wizard.graph_state import GraphState, DiagramType
from common.logging_decorator import log_method_call

logger = logging.getLogger(__name__)


class ToastToSSEHandler(logging.Handler):
    """Logging handler that forwards TOAST* messages to the session SSE queue."""

    def __init__(self, session: "DiagramSession"):
        super().__init__(level=logging.INFO)
        self.session = session

    def emit(self, record: logging.LogRecord):
        try:
            message = self.format(record)
            if "TOAST" not in message:
                return

            try:
                loop = asyncio.get_event_loop()
            except RuntimeError:
                return

            async def push_to_queue():
                await self.session.update_queue.put(
                    {
                        "status": record.levelname.lower(),
                        "message": message,
                        "session_id": self.session.session_id,
                    }
                )

            loop.create_task(push_to_queue())
        except Exception:
            # Avoid breaking logging pipeline on handler errors
            pass


class DiagramSession:
    """Represents a single diagram generation session.

    This class encapsulates all state information for a user's diagram
    generation session, including conversation history, current progress,
    generated code, and real-time update queues for SSE communication.

    Attributes:
        session_id: Unique identifier for the session
        history: List of conversation messages (role, content tuples)
        current_state: Current session state information
        clarifications: List of clarification questions asked by AI
        diagram_code: Generated diagram source code
        svg_output: Rendered SVG output
        errors: List of any errors encountered
        update_queue: Async queue for real-time status updates
        diagram_type: Selected diagram type (Mermaid, D2, PlantUML)
        graph_state: Current LangGraph state
        graph_task: Async task running the diagram generation
        is_running: Whether the session is currently processing
    """

    def __init__(self, session_id: str):
        self.session_id = session_id
        self.history: List[Tuple[str, str]] = []  # [(role, message), ...]
        self.current_state: Dict[str, Any] = {}  # Current session state
        self.clarifications: List[str] = []  # AI clarification questions
        self.diagram_code: str = ""  # Generated diagram code
        self.svg_output: str = ""  # Rendered SVG output
        self.errors: List[str] = []  # Error messages
        self.update_queue: asyncio.Queue = asyncio.Queue()  # Real-time updates
        self.diagram_type: str = "Mermaid"  # Selected diagram type
        self.graph_state: Optional[GraphState] = None  # LangGraph state
        self.graph_task: Optional[asyncio.Task] = None  # Generation task
        self.is_running: bool = False  # Processing status
        self.toast_handler: Optional[logging.Handler] = None


class DiagramSessionStore:
    """Thread-safe session management for multiple concurrent diagram sessions.

    This class provides a simple in-memory store for managing multiple
    diagram generation sessions. In production, this would typically
    be replaced with a persistent database or Redis store.

    Note: This is a simple implementation using a class variable.
    For production use, consider using a proper session store with
    expiration, persistence, and better concurrency handling.
    """

    _sessions: Dict[str, DiagramSession] = {}

    @classmethod
    @log_method_call
    def create_session(cls, session_id: str = None) -> DiagramSession:
        """Create a new diagram generation session.

        If session_id is provided (from frontend tab), uses that ID;
        otherwise generates a unique UUID-based session ID.
        Creates a new DiagramSession instance and stores it in the
        session registry.

        Also performs cleanup of old sessions (simple TTL implementation)
        to prevent memory leaks.

        Args:
            session_id: Optional pre-assigned session ID from frontend tab.
                       If not provided, a UUID will be generated.

        Returns:
            DiagramSession: The newly created session instance
        """
        # Periodic cleanup: Check on every session creation for simplicity
        # In high-load production, this should be a background task
        cls._cleanup_stale_sessions()

        # Use provided session_id or generate a new UUID
        if not session_id:
            session_id = str(uuid.uuid4())

        session = DiagramSession(session_id)
        # Store creation time for TTL using standard time.time() for consistency
        session.created_at = time.time()

        cls._sessions[session_id] = session
        logger.debug(f"✅ Created session {session_id}")
        logger.debug(f"📊 Total sessions in store: {len(cls._sessions)}")
        return session

    @classmethod
    def _cleanup_stale_sessions(cls, ttl_seconds: int = 3600):
        """
        Remove sessions older than ttl_seconds.
        Default TTL is 1 hour (3600 seconds).
        """
        try:
            current_time = time.time()
            keys_to_delete = []

            for sid, session in cls._sessions.items():
                # Check created_at if it exists (for backward compatibility)
                created_at = getattr(session, "created_at", 0)
                # Ensure we don't compare monotonic time with epoch time
                # If created_at seems too small (monotonic), ignore it or treat as very old
                # But since we standardized on time.time(), this should be consistent now.
                if created_at > 0 and (current_time - created_at > ttl_seconds):
                    keys_to_delete.append(sid)

            if keys_to_delete:
                logger.info(f"🧹 Cleaning up {len(keys_to_delete)} stale sessions")
                for sid in keys_to_delete:
                    del cls._sessions[sid]

        except Exception as e:
            # Don't let cleanup crash the request
            logger.info(f"Error during session cleanup: {e}")

    @classmethod
    @log_method_call
    def get_session(cls, session_id: str) -> Optional[DiagramSession]:
        """Retrieve an existing session by ID.

        Args:
            session_id: The unique identifier

        Returns:
            DiagramSession or None: The session if found, None otherwise
        """
        logger.debug(f"🔍 get_session called for: {session_id}")
        logger.debug(f"📦 Available sessions: {list(cls._sessions.keys())}")
        session = cls._sessions.get(session_id)
        logger.debug(f"🎯 Found session: {session is not None}")
        return session

    @classmethod
    @log_method_call
    def delete_session(cls, session_id: str):
        """Remove a session from the store.

        Args:
            session_id: The session ID to remove
        """
        if session_id in cls._sessions:
            del cls._sessions[session_id]


class DiagramFactoryService:
    """Main service orchestrating diagram generation workflows.

    This service manages the entire diagram generation process, from initial
    user input through clarification questions to final diagram generation.
    It integrates with LangGraph for complex workflow orchestration and
    provides real-time updates via asyncio queues.

    The service follows a conversational approach:
    1. Analyze initial user description
    2. Score information completeness
    3. Ask clarifying questions if needed
    4. Suggest appropriate diagram type
    5. Generate diagram using LangGraph workflow
    6. Provide real-time status updates
    """

    @log_method_call
    def __init__(self, session: DiagramSession):
        """Initialize the service with a diagram session.

        Args:
            session: The DiagramSession instance to manage
        """
        self.session = session
        self.graph = get_diagram_factory_graph(self)  # LangGraph workflow
        self._load_keywords()

        # Attach logging handler to forward TOAST* log lines to SSE queue
        if not self.session.toast_handler:
            handler = ToastToSSEHandler(self.session)
            handler.setLevel(logging.INFO)
            logging.getLogger().addHandler(handler)
            self.session.toast_handler = handler

    def _load_keywords(self):
        """Load keywords from JSON file for runtime configuration.

        This method loads entity, action, and structure words from a JSON
        configuration file, allowing for easy modification without code changes.
        """
        try:
            # Get the directory path of the current file
            current_dir = os.path.dirname(os.path.abspath(__file__))
            keywords_file = os.path.join(current_dir, "keywords.json")

            # Load keywords from JSON file
            with open(keywords_file, "r") as f:
                keywords_data = json.load(f)

            # Store keywords as instance variables
            self.entity_words = keywords_data.get("entity_words", [])
            self.action_words = keywords_data.get("action_words", [])
            self.structure_words = keywords_data.get("structure_words", [])

            logger.info(
                f"Loaded {len(self.entity_words)} entity words, "
                f"{len(self.action_words)} action words, "
                f"{len(self.structure_words)} structure words from keywords.json"
            )

        except FileNotFoundError:
            logger.info("keywords.json file not found, using default keywords")
            # Fallback to default keywords if file not found
            self.entity_words = [
                "user",
                "system",
                "database",
                "service",
                "component",
                "server",
                "api",
                "frontend",
                "backend",
                "client",
                "admin",
                "customer",
            ]
            self.action_words = [
                "login",
                "register",
                "create",
                "update",
                "delete",
                "process",
                "send",
                "receive",
                "authenticate",
                "authorize",
                "validate",
                "flow",
            ]
            self.structure_words = [
                "architecture",
                "workflow",
                "sequence",
                "hierarchy",
                "relationship",
                "contains",
                "connects",
                "depends",
                "interacts",
                "communicates",
            ]
        except json.JSONDecodeError as e:
            logger.info(f"Error parsing keywords.json: {e}, using default keywords")
            # Fallback to default keywords if JSON parsing fails
            self.entity_words = [
                "user",
                "system",
                "database",
                "service",
                "component",
                "server",
                "api",
                "frontend",
                "backend",
                "client",
                "admin",
                "customer",
            ]
            self.action_words = [
                "login",
                "register",
                "create",
                "update",
                "delete",
                "process",
                "send",
                "receive",
                "authenticate",
                "authorize",
                "validate",
                "flow",
            ]
            self.structure_words = [
                "architecture",
                "workflow",
                "sequence",
                "hierarchy",
                "relationship",
                "contains",
                "connects",
                "depends",
                "interacts",
                "communicates",
            ]

    @log_method_call
    async def _push_update(self, update_data: Dict[str, Any]):
        """Push a status update to the session's update queue.

        This method is used to send real-time updates to the frontend
        via Server-Sent Events. It combines the current session status
        with new update data and queues it for transmission.

        Args:
            update_data: Dictionary containing update information
        """
        status = self.get_status()

        # Append AI/user messages to the visible history unless explicitly skipped.
        history_message = update_data.get("message")
        if history_message and not update_data.get("skip_history"):
            role = update_data.get("message_role", "assistant")
            if not self.session.history or self.session.history[-1] != (role, history_message):
                self.session.history.append((role, history_message))
                status["history"] = self.session.history

        question_text = update_data.get("question")
        if question_text:
            self.session.clarifications.append(question_text)
            status["clarifications"] = self.session.clarifications

        status.update(update_data)
        await self.session.update_queue.put(status)

    @log_method_call
    async def start_generation(
        self, initial_prompt: str, diagram_type: str = "Mermaid", model_id: Optional[str] = None
    ):
        """Start the diagram generation process.

        This is the entry point for diagram generation. It handles two modes:
        1. Auto mode: Analyzes the system description first
        2. Direct mode: Uses the specified diagram type immediately

        Args:
            initial_prompt: User's system description
            diagram_type: Requested diagram type or "auto" for analysis
            model_id: Prompt System to use (gpt5, grok, claude, gemini)
        """
        try:
            self.session.history.append(("user", initial_prompt))

            # Initialize LangGraph state for diagram generation
            initial_state: GraphState = {
                "design_prompt": initial_prompt,
                "diagram_type": (
                    DiagramType(diagram_type.capitalize()) if diagram_type.lower() != "auto" else DiagramType.MERMAID
                ),
                "clarification_history": [{"role": "user", "content": initial_prompt}],
                "llm_ready": False,
                "question_count": 0,
                "refinement_attempt": 0,
                "current_state": "analyzing",
                "model_id": model_id,  # Store selected model for use in nodes
            }

            self.session.graph_state = initial_state
            await self._push_update(
                {"status": "started", "message": "Starting diagram analysis...", "message_role": "assistant"}
            )
            self.session.graph_task = asyncio.create_task(self._run_graph_workflow(initial_state))
            logger.info("Started diagram generation for session " f"{self.session.session_id}")

        except Exception as e:
            logger.info(f"Error: {e}")
            self.session.errors.append(str(e))
            await self._push_update({"status": "error", "message": str(e), "message_role": "assistant"})

    @log_method_call
    def _assess_information_completeness(self, description: str) -> tuple[bool, dict]:
        """Assess if we have enough information to generate a meaningful diagram.

        This method implements a sophisticated scoring system that evaluates
        the completeness of user-provided information. It looks for:

        1. Entities/Components: Systems, users, services, databases
        2. Actions/Processes: Workflows, interactions, operations
        3. Structure/Relationships: Architecture, connections, dependencies

        The scoring is designed to be encouraging while still ensuring
        quality output. Users can proceed even with minimum information
        but are encouraged to add more details for better results.

        Args:
            description: User's system description

        Returns:
            tuple: (has_enough_info, score_info_dict)
        """
        import re

        # Clean description and extract words (remove punctuation)
        description_lower = description.lower()
        clean_words = re.findall(r"\b\w+\b", description_lower)

        # Check for key information indicators using loaded keywords
        has_entities = any(word in clean_words for word in self.entity_words)
        has_actions = any(word in clean_words for word in self.action_words)
        has_structure = any(word in clean_words for word in self.structure_words)

        # Calculate scores
        info_score = sum([has_entities, has_actions, has_structure])
        word_count = len(description.split())
        is_detailed_enough = word_count >= 12  # Increased from 8 to 12 words

        # More flexible scoring - allow users to continue improving
        # We'll still suggest when to proceed, but let users continue if want
        has_minimum_info = (info_score >= 2 and word_count >= 15) or (info_score >= 3)
        has_good_info = info_score >= 3 and word_count >= 20

        # For now, use has_good_info for automatic progression
        has_enough_info = has_good_info

        score_info = {
            "entities": has_entities,
            "actions": has_actions,
            "structure": has_structure,
            "info_score": info_score,
            "word_count": word_count,
            "is_detailed_enough": is_detailed_enough,
            "has_enough_info": has_enough_info,
            "has_minimum_info": has_minimum_info,
            "has_good_info": has_good_info,
            "needed_score": "3/3 + 20 words for best results",
        }

        return has_enough_info, score_info

    @log_method_call
    async def _run_graph_workflow(self, initial_state: GraphState):
        """Execute the LangGraph workflow for diagram generation.

        This method runs the actual diagram generation workflow using LangGraph.
        It takes the initial state, processes it through the graph, and captures
        the final diagram code and SVG output.

        The workflow typically involves:
        1. LLM analysis of the system description
        2. Diagram code generation
        3. Code validation and refinement
        4. SVG rendering

        Args:
            initial_state: Initial LangGraph state with design prompt and
                          parameters
        """
        try:
            self.session.is_running = True

            # Add update callback and session info to state so nodes can push updates
            initial_state["_update_callback"] = self._push_update
            initial_state["_session_id"] = self.session.session_id

            result = await self.graph.ainvoke(initial_state)

            # Always update session with latest results first
            self.session.graph_state = result
            self.session.diagram_code = result.get("diagram_code", "")
            self.session.svg_output = result.get("svg_output", "")

            # Check if the result is the end of the graph
            if result.get("message") == "__end__":
                await self._push_update(
                    {"status": "completed", "message": "Diagram generation completed", "message_role": "assistant"}
                )
                return

            # If the graph is still waiting for clarification, do not progress further yet.
            if not result.get("llm_ready"):
                logger.info(
                    "LangGraph awaiting additional user clarification before continuing",
                    extra={"session_id": self.session.session_id},
                )
                return

            # If we're waiting on the user to confirm the AI summary, pause as well.
            if result.get("awaiting_user_confirmation"):
                logger.info(
                    "LangGraph ready but waiting for user confirmation to proceed",
                    extra={"session_id": self.session.session_id},
                )
                return

            # If we're waiting for the user to select a diagram type, pause as well.
            if not result.get("user_selected_diagram_type", True):
                logger.info(
                    "LangGraph awaiting user diagram type selection before continuing",
                    extra={"session_id": self.session.session_id},
                )
                return

            self.session.diagram_code = result.get("diagram_code", "")
            self.session.svg_output = result.get("svg_output", "")

            # Check for AI responses from nodes and display them
            if result.get("ai_response"):
                ai_message = result.get("ai_response", "")
                message_type = result.get("ai_message_type", "info")

                # Add AI response to clarifications so user can see it
                self.session.clarifications.append(f"🤖 AI: {ai_message}")

                await self._push_update(
                    {
                        "status": "ai_response",
                        "message": ai_message,
                        "message_type": message_type,
                        "message_role": "assistant",
                    }
                )

            await self._push_update(
                {"status": "completed", "message": "Diagram generation completed", "message_role": "assistant"}
            )

        except Exception as e:
            logger.info(f"Error: {e}")
            self.session.errors.append(str(e))
            await self._push_update({"status": "error", "message": str(e), "message_role": "assistant"})
        finally:
            self.session.is_running = False

    @log_method_call
    async def handle_clarification(self, response: str):
        """Handle user responses to clarification questions.

        This method processes user responses and determines whether they are:
        1. Answering clarification questions (providing more system details)
        2. Selecting a diagram type
        3. Requesting to proceed with generation

        The method routes the response to the appropriate handler based
        on the current session state and response content.

        Args:
            response: User's response to clarification question
        """
        try:
            self.session.history.append(("user", response))

            if self.session.graph_state:
                clarification_history = self.session.graph_state.get("clarification_history", [])
                clarification_history.append({"role": "user", "content": response})
                self.session.graph_state["clarification_history"] = clarification_history
                self.session.graph_state["llm_ready"] = False

            await self._push_update(
                {"status": "clarification_received", "message": response, "message_role": "user", "skip_history": False}
            )

            # Resume the LangGraph workflow now that we have more information.
            self._resume_graph_if_idle("clarification response")

        except Exception as e:
            logger.info(f"Error: {e}")
            self.session.errors.append(str(e))
            await self._push_update({"status": "error", "message": str(e)})

    @log_method_call
    async def confirm_ready(self):
        """
        User confirms they are ready to proceed with diagram generation.
        Sets the user_confirmed_ready flag and resumes the graph workflow.
        """
        try:
            if self.session.graph_state:
                self.session.graph_state["user_confirmed_ready"] = True
                self.session.graph_state["llm_ready"] = True
                # Clear awaiting_user_confirmation flag to allow graph to proceed
                self.session.graph_state["awaiting_user_confirmation"] = False

            await self._push_update(
                {
                    "status": "confirmed_ready",
                    "message": "User confirmed ready. Proceeding with diagram generation...",
                    "message_role": "assistant",
                }
            )

            # Resume the workflow now that the user confirmed they're ready
            self._resume_graph_if_idle("user confirmed ready")

        except Exception as e:
            logger.info(f"Error confirming ready: {e}")
            self.session.errors.append(str(e))
            await self._push_update({"status": "error", "message": str(e), "message_role": "assistant"})

    @log_method_call
    async def select_diagram_type(self, diagram_type: str):
        """
        User selects their preferred diagram type from the available options.
        Sets the diagram_type in state and resumes the graph workflow.

        Args:
            diagram_type: Selected diagram type (Mermaid, D2, PlantUML, Structurizr)
        """
        try:
            logger.info(
                f"[select_diagram_type] received selection: {diagram_type} for session {self.session.session_id}"
            )
            if self.session.graph_state:
                # Import DiagramType enum to validate and set the selection
                from app.utils.diagram_wizard.graph_state import DiagramType

                # Map string to enum
                diagram_type_map = {
                    "Mermaid": DiagramType.MERMAID,
                    "D2": DiagramType.D2,
                    "PlantUML": DiagramType.PLANTUML,
                    "Structurizr": DiagramType.STRUCTURIZR,
                }

                if diagram_type not in diagram_type_map:
                    raise ValueError(
                        f"Invalid diagram type: {diagram_type}. Must be one of: Mermaid, D2, PlantUML, Structurizr"
                    )

                # Set the user's selected diagram type
                self.session.graph_state["diagram_type"] = diagram_type_map[diagram_type]
                self.session.graph_state["user_selected_diagram_type"] = True
                # Keep session-level diagram type in sync for status responses
                self.session.diagram_type = diagram_type
                logger.info(
                    f"[select_diagram_type] graph_state updated with type {
                        diagram_type_map[diagram_type]} for session {
                        self.session.session_id}"
                )

            await self._push_update(
                {
                    "status": "diagram_type_selected",
                    "message": f"Generating {diagram_type} diagram...",
                    "diagram_type": diagram_type,
                    "message_role": "assistant",
                }
            )
            logger.info(
                f"[select_diagram_type] pushed diagram_type_selected update for session {self.session.session_id}"
            )

            # Resume the workflow now that the user selected diagram type
            self._resume_graph_if_idle("user selected diagram type")
            logger.info(f"[select_diagram_type] resumed graph workflow for session {self.session.session_id}")

        except Exception as e:
            logger.info(f"Error selecting diagram type: {e}")
            self.session.errors.append(str(e))
            await self._push_update({"status": "error", "message": str(e), "message_role": "assistant"})

    @log_method_call
    async def approve_render(self):
        """Approve the diagram for rendering."""
        try:
            if self.session.graph_state:
                self.session.graph_state["user_approved_render"] = True

            await self._push_update(
                {
                    "status": "rendering",
                    "message": "User approved render. Starting diagram rendering...",
                    "message_role": "assistant",
                }
            )

            # Ensure the workflow continues now that the user approved rendering.
            self._resume_graph_if_idle("render approval")

        except Exception as e:
            logger.info(f"Error: {e}")
            self.session.errors.append(str(e))
            await self._push_update({"status": "error", "message": str(e), "message_role": "assistant"})

    def _resume_graph_if_idle(self, reason: str):
        """Resume the LangGraph workflow if no task is currently running.

        This method ensures that the workflow continues after a user interaction
        or state change, provided that it's not already processing. It avoids
        creating duplicate tasks.

        Args:
            reason (str): The reason for resuming (for logging purposes).
        """
        if not self.session.graph_state:
            logger.info("Cannot resume LangGraph workflow without state", extra={"session_id": self.session.session_id})
            return

        if self.session.graph_task and not self.session.graph_task.done():
            logger.info(
                "LangGraph workflow already running; skipping resume request.",
                extra={"session_id": self.session.session_id},
            )
            return

        logger.info("Re-invoking LangGraph workflow (%s)", reason, extra={"session_id": self.session.session_id})
        self.session.graph_task = asyncio.create_task(self._run_graph_workflow(self.session.graph_state))

    @log_method_call
    async def render_diagram(self, diagram_code: Optional[str] = None):
        """Render diagram with provided code or existing session code.

        This method handles re-rendering diagrams with updated code.
        It's used when users manually edit the diagram code and want
        to see the changes reflected in the SVG output.

        Args:
            diagram_code: Optional custom diagram code to render
        """
        try:
            code_to_render = diagram_code if diagram_code is not None else self.session.diagram_code

            if not code_to_render:
                raise ValueError("No diagram code available")

            if diagram_code:
                self.session.diagram_code = diagram_code

            self.session.current_state = {"status": "completed"}
            await self._push_update(
                {"status": "rendered", "message": "Rendered successfully", "message_role": "assistant"}
            )

        except Exception as e:
            logger.info(f"Error: {e}")
            self.session.errors.append(str(e))
            await self._push_update({"status": "error", "message": str(e)})

    @log_method_call
    def get_status(self) -> Dict[str, Any]:
        """Get the current status of the diagram generation session.

        This method compiles all session information into a dictionary
        that can be serialized and sent to the frontend. It includes:
        - Session identification
        - Conversation history
        - Current state information
        - Generated outputs
        - Error information
        - Processing status

        Returns:
            Dict[str, Any]: Complete session status information
        """
        return {
            "session_id": self.session.session_id,
            "history": self.session.history,
            "currentState": self.session.current_state,
            "clarifications": self.session.clarifications,
            "diagramCode": self.session.diagram_code,
            "svgOutput": self.session.svg_output,
            "errors": self.session.errors,
            "diagramType": self.session.diagram_type,
            "isRunning": self.session.is_running,
            "jsonRepresentation": (
                self.session.graph_state.get("json_representation") if self.session.graph_state else None
            ),
            "structurizr_workspace": (
                self.session.graph_state.get("structurizr_workspace") if self.session.graph_state else None
            ),
            "clean_structurizr": (
                self.session.graph_state.get("clean_structurizr") if self.session.graph_state else None
            ),
            "json_generation_output": (
                self.session.graph_state.get("json_generation_output") if self.session.graph_state else None
            ),
            # Expose graph state for debugging/inspection; remove runtime-only fields
            "graphState": self._get_serializable_graph_state(),
        }

    def _get_serializable_graph_state(self) -> Optional[Dict[str, Any]]:
        """
        Return a JSON-serializable copy of the LangGraph state without runtime-only fields.
        """
        if not self.session.graph_state:
            return None

        try:
            state_copy: Dict[str, Any] = dict(self.session.graph_state)
            # Drop runtime helpers that are not serializable or useful for display
            state_copy.pop("_update_callback", None)
            state_copy.pop("_session_id", None)
            return state_copy
        except Exception as exc:
            logger.info(f"Failed to serialize graph state: {exc}")
            return None
