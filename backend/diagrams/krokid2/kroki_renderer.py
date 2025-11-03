"""
Kroki D2 Provider Implementation

Renders D2 diagrams using Kroki service at http://localhost:8000

This provider delegates all HTTP-based operations to KrokiBaseProvider.
"""

from pathlib import Path
from typing import List, Optional

from diagrams.kroki_base import KrokiBaseProvider
from diagrams.models import ProviderCapability

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

    Supported Diagrams:
    - Architecture diagrams (boxes and arrows)
    - Network topology diagrams
    - Database schemas (ER diagrams)
    - Cloud infrastructure diagrams
    - Sequence diagrams
    - Any diagram that can be described as nodes and connections

    Capabilities:
    - VALIDATE: Check D2 syntax via Kroki
    - RENDER_SVG: Generate SVG output
    - RENDER_PNG: Generate PNG output
    - AUTO_FIX: Pattern-based syntax correction
    - LLM_CORRECTION: AI-powered diagram correction

    Configuration:
    - server_url: Kroki server URL (default: http://localhost:8000)
    - timeout_seconds: Request timeout (default: 30)
    - diagram_endpoint: API endpoint for D2 (d2)

    Installation:
    - Requires local Kroki server running at configured URL
    - No additional dependencies beyond requests library
    """

    @property
    def provider_id(self) -> str:
        """Unique identifier matching folder name: 'krokid2'"""
        return "krokid2"

    @property
    def provider_name(self) -> str:
        """Human-readable name shown in UI"""
        return "Kroki D2 Renderer"

    @property
    def diagram_type(self) -> str:
        """Primary diagram type: 'd2'"""
        return "d2"

    @property
    def diagram_endpoint(self) -> str:
        """Kroki API endpoint for D2 diagrams"""
        return "d2"

    def get_llm_correction_rules(self) -> Optional[str]:
        """Provide D2-specific rules for LLM correction"""
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
