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

    Supported Diagrams:
    - C4 System Context (C1) diagrams
    - C4 Container (C2) diagrams
    - C4 Component (C3) diagrams
    - C4 Code (C4) diagrams

    Capabilities:
    - VALIDATE: Check C4 syntax via Kroki
    - RENDER_SVG: Generate SVG output
    - RENDER_PNG: Generate PNG output
    - AUTO_FIX: Pattern-based syntax correction
    - LLM_CORRECTION: AI-powered diagram correction

    Configuration:
    - server_url: Kroki server URL (default: http://localhost:8000)
    - timeout_seconds: Request timeout (default: 30)
    - diagram_endpoint: API endpoint for C4 (c4)

    Installation:
    - Requires local Kroki server running at configured URL
    - No additional dependencies beyond requests library
    """

    @property
    def provider_id(self) -> str:
        """Unique identifier matching folder name: 'krokic4'"""
        return "krokic4"

    @property
    def provider_name(self) -> str:
        """Human-readable name shown in UI"""
        return "Kroki C4 Renderer"

    @property
    def diagram_type(self) -> str:
        """Primary diagram type: 'c4'"""
        return "c4"

    @property
    def diagram_endpoint(self) -> str:
        """Kroki API endpoint for C4 diagrams (uses PlantUML)"""
        return "plantuml"

    def get_llm_correction_rules(self) -> Optional[str]:
        """Provide C4-specific rules for LLM correction"""
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
