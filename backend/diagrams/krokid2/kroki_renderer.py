"""
Kroki D2 Provider Implementation

Renders D2 diagrams using Kroki service at http://localhost:8000

This provider delegates all HTTP-based operations to KrokiBaseProvider.
"""

from typing import Optional

from diagrams.kroki_base import KrokiBaseProvider


class KrokiD2Provider(KrokiBaseProvider):
    """
    Kroki D2 Provider - D2 diagrams via Kroki service

    This provider uses Kroki (https://kroki.io) to render D2 diagrams
    via HTTP API calls to a local Kroki server.

    Architecture:
    - HTTP-based: Sends diagram code to Kroki server via POST
    - No local dependencies: All rendering happens on Kroki server
    - Fast response: Direct API calls without CLI overhead
    - Error handling: Parses Kroki error responses

    Attributes:
        provider_id (str): Unique identifier for this provider.
        provider_name (str): Human-readable name for this provider.
        diagram_type (str): Primary diagram type this provider handles.
        diagram_endpoint (str): Specific Kroki API endpoint for D2.
    """

    @property
    def provider_id(self) -> str:
        """
        Unique identifier for this provider (same as folder name).

        Returns:
            str: "krokid2"
        """
        return "krokid2"

    @property
    def provider_name(self) -> str:
        """
        Human-readable name for this provider.

        Returns:
            str: "Kroki D2 Renderer"
        """
        return "Kroki D2 Renderer"

    @property
    def diagram_type(self) -> str:
        """
        Primary diagram type this provider handles.

        Returns:
            str: "d2"
        """
        return "d2"

    @property
    def diagram_endpoint(self) -> str:
        """
        Kroki API endpoint for D2 diagrams.

        Returns:
            str: "d2"
        """
        return "d2"

    def get_llm_correction_rules(self) -> Optional[str]:
        """
        Provide D2-specific rules for LLM correction.

        Returns:
            str: A string containing specific rules and hints for the LLM to generate valid D2 syntax.
        """
        self.logger.info("Retrieving D2-specific LLM correction rules.")
        return """
D2-SPECIFIC RULES:
- Use proper connection syntax: A -> B or A -- B
- Use proper shape syntax: shape_name: "text" { shape: circle }
- Use proper style syntax: shape.style.fill: "#color"
- Properly indent nested structures
- Use quotes for labels with spaces or special characters
- Ensure all opening braces have corresponding closing braces
- Use direction: right|down|left|up at the start if needed
- Keep syntax simple and standard D2 format
- Use proper container syntax: container_name { ... }
- Use proper link syntax: A -> B: "label"
""".strip()
