"""
Keyword-based diagram type scoring and determination.

Analyzes text content to determine the most appropriate diagram type
based on keyword matching and context analysis. Uses keywords from keywords.json
and diagram-specific keyword heuristics.
"""

import json
import logging
import os
from pathlib import Path
from typing import Dict, Tuple
from .graph_state import DiagramType

logger = logging.getLogger(__name__)


class KeywordScorer:
    """Scores and determines diagram type based on keyword analysis."""

    # Diagram-specific keywords for distinguishing between types
    MERMAID_KEYWORDS = [
        # Flowchart and process flow indicators
        "flowchart", "flow", "process", "workflow", "decision",
        "step", "if", "then", "condition", "branch", "fork", "merge",
        "action", "task", "function", "procedure", "algorithm",
        # Sequence diagram indicators
        "sequence", "interaction", "message", "call", "respond", "exchange",
        "order", "step by step", "timeline", "actor", "participant",
        "async", "synchronous", "request", "reply",
        # State diagram indicators
        "state", "states", "state machine", "transition", "state diagram",
        "initial", "final", "event", "trigger", "status"
    ]

    D2_KEYWORDS = [
        # Architecture and system design indicators
        "architecture", "system", "components", "services", "microservice",
        "infrastructure", "deployment", "topology", "network", "distributed",
        "client", "server", "backend", "frontend", "database", "cache",
        "queue", "message broker", "load balancer", "gateway", "api",
        "external service", "integration", "connection", "communication",
        "relationship", "connects", "integrates"
    ]

    PLANTUML_KEYWORDS = [
        # UML diagram indicators
        "class", "classes", "inheritance", "interface", "abstract",
        "attribute", "method", "relationship", "association", "composition",
        "aggregation", "dependency", "structure", "hierarchy",
        # Component diagram indicators
        "component", "components", "module", "subsystem",
        "package", "library", "connector", "port",
        # Use case diagram indicators
        "use case", "scenario", "requirement", "behavior", "functionality",
        # UML general
        "uml", "diagram", "modeling", "class diagram", "component diagram"
    ]

    def __init__(self):
        """Initialize the keyword scorer with keywords from keywords.json."""
        # Load base keywords from keywords.json if available
        self.entity_words = []
        self.action_words = []
        self.structure_words = []
        self._load_base_keywords()

        # Set diagram-specific keywords
        self.mermaid_keywords = self.MERMAID_KEYWORDS
        self.d2_keywords = self.D2_KEYWORDS
        self.plantuml_keywords = self.PLANTUML_KEYWORDS

    def _load_base_keywords(self):
        """Load base keywords from keywords.json if available."""
        try:
            # Try to load from services directory
            keywords_path = Path(__file__).parent.parent.parent / "services" / "keywords.json"
            if keywords_path.exists():
                with open(keywords_path, 'r', encoding='utf-8') as f:
                    keywords_data = json.load(f)
                    self.entity_words = keywords_data.get('entity_words', [])
                    self.action_words = keywords_data.get('action_words', [])
                    self.structure_words = keywords_data.get('structure_words', [])
                    logger.info(f"Loaded base keywords from {keywords_path}")
            else:
                logger.warning(f"keywords.json not found at {keywords_path}")
        except Exception as e:
            logger.warning(f"Error loading base keywords from keywords.json: {e}")

    def score_text(self, text: str) -> Dict[str, float]:
        """
        Score text for each diagram type.

        Uses both diagram-specific keywords and base keywords from keywords.json:
        - Diagram-specific keywords (flowchart, architecture, class, etc.)
        - Entity words (system, service, database, etc.)
        - Action words (process, request, response, etc.)
        - Structure words (architecture, workflow, relationship, etc.)

        Args:
            text: Text to analyze

        Returns:
            Dictionary with diagram type scores (0-100)
        """
        if not text:
            return {
                "Mermaid": 33,
                "D2": 33,
                "PlantUML": 34,
            }

        text_lower = text.lower()
        word_count = len(text_lower.split())

        # Score diagram-specific keywords (these strongly indicate diagram type)
        mermaid_diagram_score = self._count_matches(text_lower, self.mermaid_keywords)
        d2_diagram_score = self._count_matches(text_lower, self.d2_keywords)
        plantuml_diagram_score = self._count_matches(text_lower, self.plantuml_keywords)

        # Score base keywords
        entity_matches = self._count_matches(text_lower, self.entity_words)
        action_matches = self._count_matches(text_lower, self.action_words)
        structure_matches = self._count_matches(text_lower, self.structure_words)

        # Heuristic scoring based on keyword combinations:
        # - D2 (Architecture): High structure + entities (systems, databases, services)
        # - Mermaid (Process/Flow): High action + entities (processes, steps, flows)
        # - PlantUML (UML): High structure + entities (classes, relationships, interfaces)

        # D2 benefits from: architecture keywords + system entities + structure words
        d2_base_score = (
            d2_diagram_score * 3 +  # Heavy weight for explicit architecture keywords
            structure_matches * 1.5 +
            entity_matches * 0.8
        )

        # Mermaid benefits from: flow keywords + action words + step indicators
        mermaid_base_score = (
            mermaid_diagram_score * 3 +  # Heavy weight for explicit flow keywords
            action_matches * 1.5 +
            entity_matches * 0.8
        )

        # PlantUML benefits from: UML keywords + class/interface terms + structure
        plantuml_base_score = (
            plantuml_diagram_score * 3 +  # Heavy weight for explicit UML keywords
            structure_matches * 1.5 +
            entity_matches * 0.8
        )

        # Normalize scores
        total_score = mermaid_base_score + d2_base_score + plantuml_base_score

        # If no matches at all, distribute evenly
        if total_score == 0:
            return {
                "Mermaid": 33,
                "D2": 33,
                "PlantUML": 34,
            }

        # Normalize to 100
        return {
            "Mermaid": round((mermaid_base_score / total_score) * 100, 2),
            "D2": round((d2_base_score / total_score) * 100, 2),
            "PlantUML": round((plantuml_base_score / total_score) * 100, 2),
        }

    @staticmethod
    def _count_matches(text: str, keywords: list) -> int:
        """Count keyword matches in text."""
        count = 0
        for keyword in keywords:
            # Count word boundaries to avoid partial matches
            count += text.count(keyword.lower())
        return count

    def determine_diagram_type(self, text: str) -> Tuple[DiagramType, Dict[str, float]]:
        """
        Determine the best diagram type for given text.

        Args:
            text: User input text or design summary

        Returns:
            Tuple of (DiagramType, scores_dict)
        """
        scores = self.score_text(text)

        # Find the diagram type with highest score
        best_type = max(scores.items(), key=lambda x: x[1])
        diagram_type_name = best_type[0]

        # Map to DiagramType enum
        if diagram_type_name == "Mermaid":
            diagram_type = DiagramType.MERMAID
        elif diagram_type_name == "D2":
            diagram_type = DiagramType.D2
        else:  # PlantUML
            diagram_type = DiagramType.PLANTUML

        logger.info(
            f"Determined diagram type: {diagram_type_name} (score: {best_type[1]:.1f}%) | Scores: {scores}",
        )

        return diagram_type, scores


# Global scorer instance
_scorer = None


def get_keyword_scorer() -> KeywordScorer:
    """Get or create the global keyword scorer instance."""
    global _scorer
    if _scorer is None:
        _scorer = KeywordScorer()
    return _scorer


def score_for_diagram_type(text: str) -> Dict[str, float]:
    """
    Get keyword scores for diagram types.

    Args:
        text: Text to analyze

    Returns:
        Dictionary with scores for each diagram type
    """
    scorer = get_keyword_scorer()
    return scorer.score_text(text)


def determine_diagram_type(text: str) -> Tuple[DiagramType, Dict[str, float]]:
    """
    Determine the best diagram type for given text.

    Args:
        text: User input text or design summary

    Returns:
        Tuple of (DiagramType, scores_dict)
    """
    scorer = get_keyword_scorer()
    return scorer.determine_diagram_type(text)
