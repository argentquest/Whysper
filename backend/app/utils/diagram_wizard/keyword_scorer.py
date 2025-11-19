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

    # Pre-defined keywords for each diagram type to help with classification
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
        # Initialize empty lists for base keywords from external source
        self.entity_words = []
        self.action_words = []
        self.structure_words = []
        # Load additional keywords from external JSON file
        self._load_base_keywords()

        # Set diagram-specific keywords from class-level constants
        self.mermaid_keywords = self.MERMAID_KEYWORDS
        self.d2_keywords = self.D2_KEYWORDS
        self.plantuml_keywords = self.PLANTUML_KEYWORDS

    def _load_base_keywords(self):
        # Attempt to load additional keywords from a JSON file
        try:
            # Construct path to keywords file
            keywords_path = Path(__file__).parent.parent.parent / "services" / "keywords.json"
            
            # Check if keywords file exists
            if keywords_path.exists():
                # Load keywords from JSON file
                with open(keywords_path, 'r', encoding='utf-8') as f:
                    keywords_data = json.load(f)
                    # Extract different types of keywords
                    self.entity_words = keywords_data.get('entity_words', [])
                    self.action_words = keywords_data.get('action_words', [])
                    self.structure_words = keywords_data.get('structure_words', [])
                    logger.info(f"Loaded base keywords from {keywords_path}")
            else:
                logger.warning(f"keywords.json not found at {keywords_path}")
        except Exception as e:
            logger.warning(f"Error loading base keywords from keywords.json: {e}")

    def score_text(self, text: str) -> Dict[str, float]:
        # Handle empty text case with default even distribution
        if not text:
            return {
                "Mermaid": 33,
                "D2": 33,
                "PlantUML": 34,
            }

        # Prepare text for analysis
        text_lower = text.lower()
        word_count = len(text_lower.split())

        # Count matches for different keyword sets
        mermaid_diagram_score = self._count_matches(text_lower, self.mermaid_keywords)
        d2_diagram_score = self._count_matches(text_lower, self.d2_keywords)
        plantuml_diagram_score = self._count_matches(text_lower, self.plantuml_keywords)

        # Score base keywords for additional context
        entity_matches = self._count_matches(text_lower, self.entity_words)
        action_matches = self._count_matches(text_lower, self.action_words)
        structure_matches = self._count_matches(text_lower, self.structure_words)

        # Calculate weighted scores for each diagram type
        # Considers both specific keywords and contextual keywords
        d2_base_score = (
            d2_diagram_score * 3 +  # Heavy weight for explicit architecture keywords
            structure_matches * 1.5 +
            entity_matches * 0.8
        )

        mermaid_base_score = (
            mermaid_diagram_score * 3 +  # Heavy weight for explicit flow keywords
            action_matches * 1.5 +
            entity_matches * 0.8
        )

        plantuml_base_score = (
            plantuml_diagram_score * 3 +  # Heavy weight for explicit UML keywords
            structure_matches * 1.5 +
            entity_matches * 0.8
        )

        # Calculate total score for normalization
        total_score = mermaid_base_score + d2_base_score + plantuml_base_score

        # Handle case with no matches
        if total_score == 0:
            return {
                "Mermaid": 33,
                "D2": 33,
                "PlantUML": 34,
            }

        # Normalize scores to 100% and return
        return {
            "Mermaid": round((mermaid_base_score / total_score) * 100, 2),
            "D2": round((d2_base_score / total_score) * 100, 2),
            "PlantUML": round((plantuml_base_score / total_score) * 100, 2),
        }

    @staticmethod
    def _count_matches(text: str, keywords: list) -> int:
        # Simple keyword matching method
        count = 0
        for keyword in keywords:
            # Count exact keyword matches in text
            count += text.count(keyword.lower())
        return count

    def determine_diagram_type(self, text: str) -> Tuple[DiagramType, Dict[str, float]]:
        # Score the text to determine best diagram type
        scores = self.score_text(text)

        # Find the diagram type with the highest score
        best_type = max(scores.items(), key=lambda x: x[1])
        diagram_type_name = best_type[0]

        # Map string result to DiagramType enum
        if diagram_type_name == "Mermaid":
            diagram_type = DiagramType.MERMAID
        elif diagram_type_name == "D2":
            diagram_type = DiagramType.D2
        else:  # PlantUML
            diagram_type = DiagramType.PLANTUML

        # Log the determination for debugging
        logger.info(
            f"Determined diagram type: {diagram_type_name} (score: {best_type[1]:.1f}%) | Scores: {scores}",
        )

        return diagram_type, scores

# Module-level function for convenience (used by nodes.py)
_scorer = KeywordScorer()

def determine_diagram_type(text: str) -> Tuple[DiagramType, Dict[str, float]]:
    """
    Convenience function to determine diagram type from text.

    This is a module-level wrapper around KeywordScorer.determine_diagram_type()
    for use in diagram wizard nodes.

    Args:
        text: Analysis text (design summary, component descriptions, etc.)

    Returns:
        Tuple of (DiagramType, keyword_scores dictionary)
    """
    return _scorer.determine_diagram_type(text)
