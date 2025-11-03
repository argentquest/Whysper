"""
Kroki Mermaid Provider Implementation

Renders Mermaid diagrams using Kroki service at http://localhost:8000

This provider delegates all HTTP-based operations to KrokiBaseProvider.
Includes Mermaid-specific pattern-based fixes.
"""

from typing import Optional

from diagrams.kroki_base import KrokiBaseProvider
from diagrams.models import ValidationResult


class KrokiMermaidProvider(KrokiBaseProvider):
    """
    Kroki Mermaid Provider - Mermaid diagrams via Kroki service

    This provider uses Kroki (https://kroki.io) to render Mermaid diagrams
    via HTTP API calls to a local Kroki server.

    Architecture:
    - HTTP-based: Sends diagram code to Kroki server via POST
    - No local dependencies: All rendering happens on Kroki server
    - Fast response: Direct API calls without CLI overhead
    - Error handling: Parses Kroki error responses

    Supported Diagrams:
    - Flowcharts (graph, flowchart)
    - Sequence diagrams
    - Gantt charts
    - Class diagrams
    - State diagrams
    - Pie charts
    - Journey diagrams
    - All Mermaid diagram types

    Capabilities:
    - VALIDATE: Check Mermaid syntax via Kroki
    - RENDER_SVG: Generate SVG output
    - RENDER_PNG: Generate PNG output
    - AUTO_FIX: Pattern-based syntax correction
    - LLM_CORRECTION: AI-powered diagram correction

    Configuration:
    - server_url: Kroki server URL (default: http://localhost:8000)
    - timeout_seconds: Request timeout (default: 30)
    - diagram_endpoint: API endpoint for Mermaid (mermaid)

    Installation:
    - Requires local Kroki server running at configured URL
    - No additional dependencies beyond requests library
    """

    @property
    def provider_id(self) -> str:
        """Unique identifier matching folder name: 'krokimermaid'"""
        return "krokimermaid"

    @property
    def provider_name(self) -> str:
        """Human-readable name shown in UI"""
        return "Kroki Mermaid Renderer"

    @property
    def diagram_type(self) -> str:
        """Primary diagram type: 'mermaid'"""
        return "mermaid"

    @property
    def diagram_endpoint(self) -> str:
        """Kroki API endpoint for Mermaid diagrams"""
        return "mermaid"

    def auto_fix_pattern_based(
        self, code: str, error_message: str, **options
    ) -> ValidationResult:
        """
        Attempt pattern-based auto-fix for Mermaid syntax.

        Includes Mermaid-specific fixes in addition to generic fixes.
        """
        self.logger.info("Attempting pattern-based auto-fix for Mermaid...")

        fixed_code = code
        corrections = []

        # Mermaid-specific fix 1: Add missing diagram type declaration
        if not any(
            code.startswith(prefix)
            for prefix in ['graph ', 'flowchart ', 'sequenceDiagram', 'classDiagram',
                          'stateDiagram', 'erDiagram', 'gantt', 'pie', 'journey']
        ):
            # Try to infer diagram type from content
            if '-->' in code or '->' in code:
                fixed_code = 'flowchart TD\n' + fixed_code
                corrections.append('Added missing flowchart declaration')
            elif 'sequenceDiagram' in error_message.lower():
                fixed_code = 'sequenceDiagram\n' + fixed_code
                corrections.append('Added missing sequenceDiagram declaration')

        # Mermaid-specific fix 2: Normalize arrow syntax
        if ' - >' in fixed_code:
            fixed_code = fixed_code.replace(' - >', '-->')
            corrections.append('Normalized arrow syntax (- > to -->)')

        # Generic fix: Add missing braces for subgraphs
        if '{' in fixed_code:
            open_count = fixed_code.count('{')
            close_count = fixed_code.count('}')
            if open_count > close_count:
                missing_braces = open_count - close_count
                fixed_code += '}' * missing_braces
                corrections.append(
                    f'Added {missing_braces} missing closing brace(s)'
                )

        # Validate fixed code
        validation_result = self.validate_code(fixed_code, **options)

        if validation_result.is_valid:
            validation_result.auto_fixed = True
            validation_result.fixed_code = fixed_code
            validation_result.correction_method = "pattern"
            if corrections:
                self.logger.info(
                    f"Pattern-based fixes applied: {', '.join(corrections)}"
                )
            else:
                self.logger.info("Pattern-based validation check passed")
        else:
            self.logger.debug("Pattern-based fix did not resolve errors")

        return validation_result

    def get_llm_correction_rules(self) -> Optional[str]:
        """Provide Mermaid-specific rules for LLM correction"""
        return """
MERMAID-SPECIFIC RULES:
- Start with diagram type: flowchart TD, sequenceDiagram, classDiagram, etc.
- Use proper arrow syntax: --> for connections, ->> for sequence diagrams
- Use proper node syntax: A[Text] for rectangles, (Text) for rounded
- Use quotes for labels with spaces: A["Multi word label"]
- Properly close subgraphs with "end"
- Use standard Mermaid shapes: diamonds {}, circles (()), rectangles []
- Ensure arrows connect defined nodes
- Don't use colons after node IDs
- Use LR (left-right) or TD (top-down) for flowchart direction
- Keep syntax simple and standard Mermaid format
- Use proper relationship syntax for class/ER diagrams
""".strip()
