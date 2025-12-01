"""
Kroki C4 Provider Implementation

Renders C4 model diagrams using Kroki service at http://localhost:8000

This provider delegates all HTTP-based operations to KrokiBaseProvider.
"""

from typing import Optional

from diagrams.kroki_base import KrokiBaseProvider


class KrokiC4Provider(KrokiBaseProvider):
    """
    Kroki C4 Provider - C4 model diagrams via Kroki service

    This provider uses Kroki (https://kroki.io) to render C4 model diagrams
    via HTTP API calls to a local Kroki server.

    The C4 model is a simple hierarchical set of diagrams for depicting
    the static structures and interactions of a software system.

    Architecture:
    - HTTP-based: Sends diagram code to Kroki server via POST
    - No local dependencies: All rendering happens on Kroki server
    - Fast response: Direct API calls without CLI overhead
    - Error handling: Parses Kroki error responses

    Attributes:
        provider_id (str): Unique identifier for this provider.
        provider_name (str): Human-readable name for this provider.
        diagram_type (str): Primary diagram type this provider handles.
        diagram_endpoint (str): Specific Kroki API endpoint for C4 (uses PlantUML).
    """

    @property
    def provider_id(self) -> str:
        """
        Unique identifier for this provider (same as folder name).

        Returns:
            str: "krokic4"
        """
        return "krokic4"

    @property
    def provider_name(self) -> str:
        """
        Human-readable name for this provider.

        Returns:
            str: "Kroki C4 Renderer"
        """
        return "Kroki C4 Renderer"

    @property
    def diagram_type(self) -> str:
        """
        Primary diagram type this provider handles.

        Returns:
            str: "c4"
        """
        return "c4"

    @property
    def diagram_endpoint(self) -> str:
        """
        Kroki API endpoint for C4 diagrams (uses PlantUML).

        Returns:
            str: "plantuml"
        """
        return "plantuml"

    def get_llm_correction_rules(self) -> Optional[str]:
        """
        Provide C4-specific rules for LLM correction.

        Returns:
            str: A string containing specific rules and hints for the LLM to generate valid C4/PlantUML syntax.
        """
        self.logger.info("Retrieving C4-specific LLM correction rules.")
        return """
C4-SPECIFIC RULES:
- Use C4 DSL syntax for system architecture diagrams
- Define system boundaries and containers
- Show relationships between elements
- Use proper C4 element syntax
- Properly indent nested structures
- Use quotes for labels with spaces or special characters
- Ensure all opening braces have corresponding closing braces
- Keep syntax simple and standard C4 format
- Use Person, SoftwareSystem, Container, Component elements
- Define proper relationships between elements
""".strip()
