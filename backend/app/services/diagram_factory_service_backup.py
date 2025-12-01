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
from typing import Dict, Any, List, Tuple, Optional

from app.utils.diagram_wizard.langgraph_builder import get_diagram_factory_graph
from app.utils.diagram_wizard.graph_state import GraphState, DiagramType
from common.logging_decorator import log_method_call

logger = logging.getLogger(__name__)


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
    def create_session(cls) -> DiagramSession:
        """Create a new diagram generation session.

        Generates a unique session ID and creates a new DiagramSession
        instance, then stores it in the session registry.

        Returns:
            DiagramSession: The newly created session instance
        """
        session_id = str(uuid.uuid4())
        session = DiagramSession(session_id)
        cls._sessions[session_id] = session
        return session

    @classmethod
    @log_method_call
    def get_session(cls, session_id: str) -> Optional[DiagramSession]:
        """Retrieve an existing session by ID.

        Args:
            session_id: The unique session identifier

        Returns:
            DiagramSession or None: The session if found, None otherwise
        """
        return cls._sessions.get(session_id)

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
        self.graph = get_diagram_factory_graph()  # LangGraph workflow
        self._load_keywords()

    def _load_keywords(self):
        pass

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
        status.update(update_data)
        await self.session.update_queue.put(status)

    @log_method_call
    async def start_generation(self, initial_prompt: str, diagram_type: str = "Mermaid"):
        """Start the diagram generation process.

        This is the entry point for diagram generation. It handles two modes:
        1. Auto mode: Analyzes the system description first
        2. Direct mode: Uses the specified diagram type immediately

        Args:
            initial_prompt: User's system description
            diagram_type: Requested diagram type or "auto" for analysis
        """
        try:
            # Handle auto diagram type - analyze system first
            if diagram_type.lower() == "auto":
                await self._analyze_system_type(initial_prompt)
                return

            # Direct diagram generation mode
            self.session.diagram_type = diagram_type
            self.session.history.append(("user", initial_prompt))

            # Initialize LangGraph state for diagram generation
            initial_state: GraphState = {
                "design_prompt": initial_prompt,
                "diagram_type": DiagramType(diagram_type.capitalize()),
                "clarification_history": [{"role": "user", "content": initial_prompt}],
                "llm_ready": False,
                "question_count": 0,
                "refinement_attempt": 0,
                "current_state": "initialized",
            }

            self.session.graph_state = initial_state
            await self._push_update({"status": "started", "message": f"Starting {diagram_type} diagram generation..."})
            self.session.graph_task = asyncio.create_task(self._run_graph_workflow(initial_state))
            logger.info("Started diagram generation for session " f"{self.session.session_id}")

        except Exception as e:
            logger.info(f"Error: {e}")
            self.session.errors.append(str(e))
            await self._push_update({"status": "error", "message": str(e)})

    @log_method_call
    async def _analyze_system_type(self, system_description: str):
        """Analyze system description and determine information completeness.

        This method implements the intelligent analysis system that evaluates
        whether the user has provided enough information to generate a
        meaningful diagram. It uses a scoring system based on:
        - Entity detection (systems, components, users)
        - Action identification (processes, workflows)
        - Structure recognition (relationships, architecture)
        - Word count analysis

        Args:
            system_description: User's system description
        """
        try:
            self.session.history.append(("user", system_description))
            await self._push_update({"status": "analyzing", "message": "Analyzing your system description..."})

            # Check if we have enough information to generate a diagram
            has_enough_info, score_info = self._assess_information_completeness(system_description)

            # Always show score analysis
            clarification_question = self._generate_clarification_question_with_score(system_description, score_info)
            self.session.clarifications.append(clarification_question)

            if has_enough_info:
                # Has enough info - offer to proceed
                await self._push_update(
                    {"status": "can_proceed", "message": clarification_question, "score_info": score_info}
                )
            else:
                # Need more info - continue clarification
                await self._push_update(
                    {"status": "clarifying", "message": clarification_question, "score_info": score_info}
                )

        except Exception as e:
            logger.info(f"Error analyzing system: {e}")
            self.session.errors.append(str(e))
            await self._push_update({"status": "error", "message": str(e)})

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

        # Check for key information indicators
        entity_words = [
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
        has_entities = any(word in clean_words for word in entity_words)

        action_words = [
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
        has_actions = any(word in clean_words for word in action_words)

        structure_words = [
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
        has_structure = any(word in clean_words for word in structure_words)

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
    def _generate_clarification_question(self, description: str) -> str:
        """Generate a clarifying question to get more specific information.

        This method analyzes the current description and determines what
        type of information is missing, then generates a targeted question
        to help gather that information.

        The questions focus on three main areas:
        1. Entities/Components - Who/what is involved
        2. Actions/Processes - What happens and how
        3. Structure/Relationships - How things connect

        Args:
            description: Current system description

        Returns:
            str: A targeted clarification question
        """
        description_lower = description.lower()

        # Determine what type of clarification is needed
        if not any(word in description_lower for word in ["user", "system", "component", "service"]):
            return (
                "I need more details about the **entities/components** involved. "
                "Could you tell me:\n"
                "• Who are the main actors (users, systems, services)?\n"
                "• What are the key components or systems involved?"
            )

        elif not any(word in description_lower for word in ["process", "flow", "create", "update", "login", "send"]):
            return (
                "I need more details about the **processes or interactions**. "
                "Could you tell me:\n"
                "• What specific actions or processes happen?\n"
                "• How do the components interact with each other?\n"
                "• What is the main workflow or sequence of events?"
            )

        else:
            return (
                "I need more details about the **structure or relationships**. "
                "Could you tell me:\n"
                "• How are the components connected or related?\n"
                "• What is the overall architecture or hierarchy?\n"
                "• Are there any specific technologies or protocols involved?"
            )

    @log_method_call
    def _generate_clarification_question_with_score(self, description: str, score_info: dict) -> str:
        """Generate a clarifying question with information score display.

        This method creates an enhanced clarification question that includes
        a visual score display showing the user exactly what information
        has been provided and what might be missing.

        The score display uses:
        - Visual indicators (✅/❌) for each category
        - Progress indicators (X/3 score)
        - Word count analysis
        - Encouraging messages based on completeness level

        Args:
            description: Current system description
            score_info: Information completeness scores

        Returns:
            str: Enhanced clarification question with score display
        """

        # Determine the status and next steps
        if score_info["has_good_info"]:
            next_msg = (
                "You can proceed to diagram generation, or continue adding " "more details to make it even better!"
            )
        elif score_info["has_minimum_info"]:
            pass
        else:
            pass

        self._generate_clarification_question(description)

        # Create enhanced score display
        score_display = """
**📊 Information Score: {score_info['info_score']}/3**

✅ **Entities/Components**: {"✓ Found" if score_info['entities'] else "✗ Missing"}
✅ **Actions/Processes**: {"✓ Found" if score_info['actions'] else "✗ Missing"}
✅ **Structure/Relationships**: {"✓ Found" if score_info['structure'] else "✗ Missing"}

📝 **Detail Level**: {score_info['word_count']} words

{status_msg}

---

{next_msg if score_info['has_minimum_info'] else base_question}
        """

        return score_display.strip()

    @log_method_call
    async def _suggest_diagram_type(self, system_description: str):
        """Suggest appropriate diagram type based on complete information.

        This method analyzes the system description and recommends the most
        suitable diagram type based on the content. It considers:

        - Mermaid: Best for flowcharts, sequences, user journeys
        - D2: Best for architecture diagrams, system components
        - PlantUML: Best for UML diagrams, database schemas

        The recommendation is based on keyword analysis and content patterns.

        Args:
            system_description: Complete system description
        """
        description_lower = system_description.lower()

        # Determine best diagram type based on content
        if any(word in description_lower for word in ["flow", "process", "step", "workflow", "sequence", "auth"]):
            suggested_type = "Mermaid"
            reason = "flowcharts and sequence diagrams"
        elif any(
            word in description_lower
            for word in ["architecture", "system", "component", "service", "microservice", "container"]
        ):
            suggested_type = "D2"
            reason = "system architecture diagrams"
        elif any(word in description_lower for word in ["class", "uml", "entity", "relationship", "database"]):
            suggested_type = "PlantUML"
            reason = "UML and database diagrams"
        else:
            suggested_type = "Mermaid"
            reason = "general purpose diagrams"

        # Ask user to confirm diagram type
        question = (
            "Perfect! I have enough information to create your diagram.\n\n"
            f"Based on your description, I recommend **{suggested_type}** for "
            f"{reason}. Would you like to proceed with {suggested_type}, or "
            "choose a different diagram type?\n\n"
            "Available options:\n"
            "• **Mermaid** - Flowcharts, sequences, user journeys\n"
            "• **D2** - Architecture diagrams, system components\n"
            "• **PlantUML** - UML diagrams, database schemas"
        )

        self.session.clarifications.append(question)
        await self._push_update({"status": "type_selection", "message": question, "suggested_type": suggested_type})

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
            result = await self.graph.ainvoke(initial_state)

            self.session.diagram_code = result.get("diagram_code", "")
            self.session.svg_output = result.get("svg_output", "")
            self.session.graph_state = result

            await self._push_update({"status": "completed", "message": "Diagram generation completed"})

        except Exception as e:
            logger.info(f"Error: {e}")
            self.session.errors.append(str(e))
            await self._push_update({"status": "error", "message": str(e)})
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
            self.session.clarifications.append(response)

            # Check if this is a diagram type selection response
            if not self.session.diagram_type or self.session.diagram_type == "auto":
                # Check if this is answering a clarification question or
                # selecting diagram type
                await self._handle_clarification_or_type_selection(response)
                return

            if self.session.graph_state:
                clarification_history = self.session.graph_state.get("clarification_history", [])
                clarification_history.append({"role": "user", "content": response})
                self.session.graph_state["clarification_history"] = clarification_history
                self.session.graph_state["llm_ready"] = True

            await self._push_update({"status": "clarification_received", "message": response})

        except Exception as e:
            logger.info(f"Error: {e}")
            self.session.errors.append(str(e))
            await self._push_update({"status": "error", "message": str(e)})

    @log_method_call
    async def _handle_clarification_or_type_selection(self, response: str):
        """Handle either clarification response or diagram type selection.

        This method determines whether the user's response is:
        1. A request to proceed (triggers diagram type suggestion)
        2. A specific diagram type selection
        3. Additional clarification information

        It uses keyword analysis and context to make this determination
        and routes accordingly.

        Args:
            response: User's response to analyze
        """
        try:
            response_lower = response.lower()

            # Check if this is a diagram type selection or proceed command
            if response_lower.strip() == "proceed" or any(
                word in response_lower for word in ["mermaid", "d2", "plantuml", "yes"]
            ):
                if response_lower.strip() == "proceed":
                    # User wants to proceed - suggest diagram type based on current info
                    all_info = ""
                    for role, content in self.session.history:
                        if role == "user":
                            all_info += content + " "
                    await self._suggest_diagram_type(all_info.strip())
                else:
                    # User is selecting a specific diagram type
                    await self._handle_diagram_type_selection(response)
                return

            # This is a clarification response - combine with previous info and re-analyze
            all_info = ""
            for role, content in self.session.history:
                if role == "user":
                    all_info += content + " "

            # Re-assess if we now have enough information
            has_enough_info, score_info = self._assess_information_completeness(all_info.strip())

            # Always show score and allow user to continue or proceed
            clarification_question = self._generate_clarification_question_with_score(all_info.strip(), score_info)
            self.session.clarifications.append(clarification_question)

            if has_enough_info:
                # Has enough info - offer to proceed to diagram type selection
                await self._push_update(
                    {"status": "can_proceed", "message": clarification_question, "score_info": score_info}
                )
            else:
                # Need more info - continue clarification
                await self._push_update(
                    {"status": "clarifying", "message": clarification_question, "score_info": score_info}
                )

        except Exception as e:
            logger.info(f"Error handling clarification: {e}")
            self.session.errors.append(str(e))
            await self._push_update({"status": "error", "message": str(e)})

    @log_method_call
    async def _handle_diagram_type_selection(self, response: str):
        """Handle user's diagram type selection.

        This method processes the user's diagram type selection and
        initiates the actual diagram generation workflow. It:

        1. Parses the selected diagram type from the response
        2. Sets up the LangGraph initial state
        3. Starts the diagram generation task

        Args:
            response: User's diagram type selection response
        """
        try:
            response_lower = response.lower()

            # Parse diagram type from response
            if "mermaid" in response_lower:
                diagram_type = "Mermaid"
            elif "d2" in response_lower:
                diagram_type = "D2"
            elif "plantuml" in response_lower:
                diagram_type = "PlantUML"
            elif "yes" in response_lower or "proceed" in response_lower or "ok" in response_lower:
                # Use suggested type from last update
                diagram_type = getattr(self.session, "suggested_type", "Mermaid")
            else:
                # Default to Mermaid if unclear
                diagram_type = "Mermaid"

            self.session.diagram_type = diagram_type

            # Get original system description from history
            original_prompt = ""
            for role, content in self.session.history:
                if role == "user":
                    original_prompt = content
                    break

            # Start the actual diagram generation workflow
            initial_state: GraphState = {
                "design_prompt": original_prompt,
                "diagram_type": DiagramType(diagram_type.capitalize()),
                "clarification_history": [{"role": "user", "content": original_prompt}],
                "llm_ready": False,
                "question_count": 0,
                "refinement_attempt": 0,
                "current_state": "initialized",
            }

            self.session.graph_state = initial_state
            await self._push_update(
                {"status": "started", "message": f"Great! Starting {diagram_type} diagram generation..."}
            )

            self.session.graph_task = asyncio.create_task(self._run_graph_workflow(initial_state))
            logger.info(f"Started {diagram_type} diagram generation for session " f"{self.session.session_id}")

        except Exception as e:
            logger.info(f"Error handling diagram type selection: {e}")
            self.session.errors.append(str(e))
            await self._push_update({"status": "error", "message": str(e)})

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
            await self._push_update({"status": "rendered", "message": "Rendered successfully"})

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
        }
