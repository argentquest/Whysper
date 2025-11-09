"""Diagram Factory Service - Orchestrates LangGraph-based diagram generation."""

import uuid
import asyncio
import logging
from typing import Dict, Any, List, Tuple, Optional

from app.utils.diagram_wizard.langgraph_builder import get_diagram_factory_graph
from app.utils.diagram_wizard.graph_state import GraphState, DiagramType

logger = logging.getLogger(__name__)


class DiagramSession:
    def __init__(self, session_id: str):
        self.session_id = session_id
        self.history: List[Tuple[str, str]] = []
        self.current_state: Dict[str, Any] = {}
        self.clarifications: List[str] = []
        self.diagram_code: str = ""
        self.svg_output: str = ""
        self.errors: List[str] = []
        self.update_queue: asyncio.Queue = asyncio.Queue()
        self.diagram_type: str = "Mermaid"
        self.graph_state: Optional[GraphState] = None
        self.graph_task: Optional[asyncio.Task] = None
        self.is_running: bool = False


class DiagramSessionStore:
    _sessions: Dict[str, DiagramSession] = {}

    @classmethod
    def create_session(cls) -> DiagramSession:
        session_id = str(uuid.uuid4())
        session = DiagramSession(session_id)
        cls._sessions[session_id] = session
        return session

    @classmethod
    def get_session(cls, session_id: str) -> Optional[DiagramSession]:
        return cls._sessions.get(session_id)

    @classmethod
    def delete_session(cls, session_id: str):
        if session_id in cls._sessions:
            del cls._sessions[session_id]


class DiagramFactoryService:
    def __init__(self, session: DiagramSession):
        self.session = session
        self.graph = get_diagram_factory_graph()

    async def _push_update(self, update_data: Dict[str, Any]):
        status = self.get_status()
        status.update(update_data)
        await self.session.update_queue.put(status)

    async def start_generation(self, initial_prompt: str, diagram_type: str = "Mermaid"):
        try:
            self.session.diagram_type = diagram_type
            self.session.history.append(("user", initial_prompt))

            initial_state: GraphState = {
                "design_prompt": initial_prompt,
                "diagram_type": DiagramType(diagram_type.capitalize()),
                "clarification_history": [{"role": "user", "content": initial_prompt}],
                "llm_ready": False,
                "question_count": 0,
                "refinement_attempt": 0,
                "current_state": "initialized"
            }

            self.session.graph_state = initial_state
            await self._push_update({"status": "started", "message": f"Starting {diagram_type} diagram generation..."})
            self.session.graph_task = asyncio.create_task(self._run_graph_workflow(initial_state))
            logger.info(f"Started diagram generation for session {self.session.session_id}")

        except Exception as e:
            logger.error(f"Error: {e}")
            self.session.errors.append(str(e))
            await self._push_update({"status": "error", "message": str(e)})

    async def _run_graph_workflow(self, initial_state: GraphState):
        try:
            self.session.is_running = True
            result = await self.graph.ainvoke(initial_state)

            self.session.diagram_code = result.get("diagram_code", "")
            self.session.svg_output = result.get("svg_output", "")
            self.session.graph_state = result

            await self._push_update({"status": "completed", "message": "Diagram generation completed"})

        except Exception as e:
            logger.error(f"Error: {e}")
            self.session.errors.append(str(e))
            await self._push_update({"status": "error", "message": str(e)})
        finally:
            self.session.is_running = False

    async def handle_clarification(self, response: str):
        try:
            self.session.history.append(("assistant", response))
            self.session.clarifications.append(response)
            
            if self.session.graph_state:
                clarification_history = self.session.graph_state.get("clarification_history", [])
                clarification_history.append({"role": "user", "content": response})
                self.session.graph_state["clarification_history"] = clarification_history
                self.session.graph_state["llm_ready"] = True

            await self._push_update({"status": "clarification_received", "message": response})

        except Exception as e:
            logger.error(f"Error: {e}")
            self.session.errors.append(str(e))
            await self._push_update({"status": "error", "message": str(e)})

    async def render_diagram(self, diagram_code: Optional[str] = None):
        try:
            code_to_render = diagram_code if diagram_code is not None else self.session.diagram_code

            if not code_to_render:
                raise ValueError("No diagram code available")

            if diagram_code:
                self.session.diagram_code = diagram_code

            self.session.current_state = {"status": "completed"}
            await self._push_update({"status": "rendered", "message": "Rendered successfully"})

        except Exception as e:
            logger.error(f"Error: {e}")
            self.session.errors.append(str(e))
            await self._push_update({"status": "error", "message": str(e)})

    def get_status(self) -> Dict[str, Any]:
        return {
            "session_id": self.session.session_id,
            "history": self.session.history,
            "currentState": self.session.current_state,
            "clarifications": self.session.clarifications,
            "diagramCode": self.session.diagram_code,
            "svgOutput": self.session.svg_output,
            "errors": self.session.errors,
            "diagramType": self.session.diagram_type,
            "isRunning": self.session.is_running
        }
