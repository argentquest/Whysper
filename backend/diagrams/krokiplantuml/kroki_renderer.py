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

    Supported Diagrams:
    - Use case diagrams
    - Sequence diagrams
    - Class diagrams
    - Activity diagrams
    - Component diagrams
    - Deployment diagrams
    - State diagrams
    - Object diagrams
    - All PlantUML diagram types

    Capabilities:
    - VALIDATE: Check PlantUML syntax via Kroki
    - RENDER_SVG: Generate SVG output
    - RENDER_PNG: Generate PNG output
    - AUTO_FIX: Pattern-based syntax correction
    - LLM_CORRECTION: AI-powered diagram correction

    Configuration:
    - server_url: Kroki server URL (default: http://localhost:8000)
    - timeout_seconds: Request timeout (default: 30)
    - diagram_endpoint: API endpoint for PlantUML (plantuml)

    Installation:
    - Requires local Kroki server running at configured URL
    - No additional dependencies beyond requests library
    """

    @property
    def provider_id(self) -> str:
        """Unique identifier matching folder name: 'krokiplantuml'"""
        return "krokiplantuml"

    @property
    def provider_name(self) -> str:
        """Human-readable name shown in UI"""
        return "Kroki PlantUML Renderer"

    @property
    def diagram_type(self) -> str:
        """Primary diagram type: 'plantuml'"""
        return "plantuml"

    @property
    def diagram_endpoint(self) -> str:
        """Kroki API endpoint for PlantUML diagrams"""
        return "plantuml"

    def get_llm_correction_rules(self) -> Optional[str]:
        """Provide PlantUML-specific rules for LLM correction"""
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
