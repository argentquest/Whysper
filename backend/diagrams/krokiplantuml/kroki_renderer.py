"""
Kroki PlantUML Provider Implementation

Renders PlantUML diagrams using Kroki service at http://localhost:8000

This provider delegates all HTTP-based operations to KrokiBaseProvider.
"""

from typing import Optional

from diagrams.kroki_base import KrokiBaseProvider


class KrokiPlantUMLProvider(KrokiBaseProvider):
    """
    Kroki PlantUML Provider - PlantUML diagrams via Kroki service

    This provider uses Kroki (https://kroki.io) to render PlantUML
    diagrams via HTTP API calls to a local Kroki server.

    Architecture:
    - HTTP-based: Sends diagram code to Kroki server via POST
    - No local dependencies: All rendering happens on Kroki server
    - Fast response: Direct API calls without CLI overhead
    - Error handling: Parses Kroki error responses

    Attributes:
        provider_id (str): Unique identifier for this provider.
        provider_name (str): Human-readable name for this provider.
        diagram_type (str): Primary diagram type this provider handles.
        diagram_endpoint (str): Specific Kroki API endpoint for PlantUML.
    """

    @property
    def provider_id(self) -> str:
        """
        Unique identifier for this provider (same as folder name).

        Returns:
            str: "krokiplantuml"
        """
        return "krokiplantuml"

    @property
    def provider_name(self) -> str:
        """
        Human-readable name for this provider.

        Returns:
            str: "Kroki PlantUML Renderer"
        """
        return "Kroki PlantUML Renderer"

    @property
    def diagram_type(self) -> str:
        """
        Primary diagram type this provider handles.

        Returns:
            str: "plantuml"
        """
        return "plantuml"

    @property
    def diagram_endpoint(self) -> str:
        """
        Kroki API endpoint for PlantUML diagrams.

        Returns:
            str: "plantuml"
        """
        return "plantuml"

    def get_llm_correction_rules(self) -> Optional[str]:
        """
        Provide PlantUML-specific rules for LLM correction.

        Returns:
            str: A string containing specific rules and hints for the LLM to generate valid PlantUML syntax.
        """
        self.logger.info("Retrieving PlantUML-specific LLM correction rules.")
        return """
PLANTUML-SPECIFIC RULES:
- Start with @startuml and end with @enduml
- Use proper PlantUML element syntax
- Define relationships between elements
- Properly indent nested structures
- Use quotes for labels with spaces or special characters
- Ensure all blocks are properly closed
- Keep syntax simple and standard PlantUML format
- Use proper arrow syntax for relationships
- Use standard PlantUML diagram elements
- Define actors, entities, and relationships clearly
""".strip()
