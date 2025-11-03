"""
Kroki Structurizr Provider Implementation

Renders Structurizr diagrams using Kroki service at http://localhost:8000

This provider delegates all HTTP-based operations to KrokiBaseProvider.
Includes Structurizr-specific pattern-based fixes.
"""

from typing import Optional

from diagrams.kroki_base import KrokiBaseProvider
from diagrams.models import ValidationResult


class KrokiStructurizrProvider(KrokiBaseProvider):
    """
    Kroki Structurizr Provider - Structurizr/C4 diagrams via Kroki

    This provider uses Kroki (https://kroki.io) to render Structurizr diagrams
    via HTTP API calls to a local Kroki server.

    Architecture:
    - HTTP-based: Sends diagram code to Kroki server via POST
    - No local dependencies: All rendering happens on Kroki server
    - Fast response: Direct API calls without CLI overhead
    - Error handling: Parses Kroki error responses

    Supported Diagrams:
    - C4 System Context diagrams
    - C4 Container diagrams
    - C4 Component diagrams
    - C4 Code diagrams
    - Structurizr DSL diagrams

    Capabilities:
    - VALIDATE: Check Structurizr syntax via Kroki
    - RENDER_SVG: Generate SVG output
    - RENDER_PNG: Generate PNG output
    - AUTO_FIX: Pattern-based syntax correction
    - LLM_CORRECTION: AI-powered diagram correction

    Configuration:
    - server_url: Kroki server URL (default: http://localhost:8000)
    - timeout_seconds: Request timeout (default: 30)
    - diagram_endpoint: API endpoint for Structurizr (structurizr)

    Installation:
    - Requires local Kroki server running at configured URL
    - No additional dependencies beyond requests library
    """

    @property
    def provider_id(self) -> str:
        """Unique identifier matching folder name: 'krokistructurizr'"""
        return "krokistructurizr"

    @property
    def provider_name(self) -> str:
        """Human-readable name shown in UI"""
        return "Kroki Structurizr Renderer"

    @property
    def diagram_type(self) -> str:
        """Primary diagram type: 'structurizr'"""
        return "structurizr"

    @property
    def diagram_endpoint(self) -> str:
        """Kroki API endpoint for Structurizr diagrams"""
        return "structurizr"

    def auto_fix_pattern_based(
        self, code: str, error_message: str, **options
    ) -> ValidationResult:
        """
        Attempt pattern-based auto-fix for Structurizr syntax.

        Includes Structurizr-specific fixes in addition to generic fixes.
        """
        self.logger.info("Attempting pattern-based auto-fix for Structurizr...")

        fixed_code = code
        corrections = []

        # Structurizr-specific fix 1: Add missing workspace declaration
        if not code.strip().startswith('workspace'):
            fixed_code = 'workspace {\n' + fixed_code + '\n}'
            corrections.append('Added missing workspace declaration')

        # Structurizr-specific fix 2: Fix model syntax
        if 'model {' in fixed_code:
            # Already has model block
            pass
        elif '->' in fixed_code or 'person ' in fixed_code:
            # Likely missing model block
            fixed_code = fixed_code.replace(
                'workspace {',
                'workspace {\n  model {'
            )
            fixed_code = fixed_code.rstrip('}') + '\n  }\n}'
            corrections.append('Added missing model block')

        # Generic fix: Add missing braces
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
        """Provide Structurizr-specific rules for LLM correction"""
        return """
STRUCTURIZR-SPECIFIC RULES:
- Start with: workspace { ... }
- Include model { ... } block for elements
- Define people: person "Name"
- Define systems: softwareSystem "Name"
- Define containers: container "Name"
- Define relationships: source -> destination "description"
- Use proper element syntax: element = object "label"
- Properly indent nested structures (2-4 spaces)
- Use quotes for labels with spaces or special characters
- Ensure all opening braces have corresponding closing braces
- Include views { ... } block for diagrams
- Use systemContext, container, component for view types
- Keep syntax simple and standard Structurizr format
""".strip()
