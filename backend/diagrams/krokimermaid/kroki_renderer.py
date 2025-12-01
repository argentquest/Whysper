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

    Attributes:
        provider_id (str): Unique identifier for this provider.
        provider_name (str): Human-readable name for this provider.
        diagram_type (str): Primary diagram type this provider handles.
        diagram_endpoint (str): Specific Kroki API endpoint for Mermaid.
    """

    @property
    def provider_id(self) -> str:
        """
        Unique identifier for this provider (same as folder name).

        Returns:
            str: "krokimermaid"
        """
        return "krokimermaid"

    @property
    def provider_name(self) -> str:
        """
        Human-readable name for this provider.

        Returns:
            str: "Kroki Mermaid Renderer"
        """
        return "Kroki Mermaid Renderer"

    @property
    def diagram_type(self) -> str:
        """
        Primary diagram type this provider handles.

        Returns:
            str: "mermaid"
        """
        return "mermaid"

    @property
    def diagram_endpoint(self) -> str:
        """
        Kroki API endpoint for Mermaid diagrams.

        Returns:
            str: "mermaid"
        """
        return "mermaid"

    def auto_fix_pattern_based(self, code: str, error_message: str, **options) -> ValidationResult:
        """
        Attempt pattern-based auto-fix for Mermaid syntax.

        Includes Mermaid-specific fixes in addition to generic fixes.

        Args:
            code (str): The invalid diagram code.
            error_message (str): The error message from the previous validation attempt.
            **options: Additional provider-specific options.

        Returns:
            ValidationResult: The result of the auto-fix attempt, including the fixed code if successful.
        """
        self.logger.info("Attempting pattern-based auto-fix for Mermaid...")

        fixed_code = code
        corrections = []

        # Mermaid-specific fix 1: Add missing diagram type declaration
        # Checks if known Mermaid keywords are present at the start of the code
        if not any(
            code.strip().startswith(prefix)
            for prefix in [
                "graph ",
                "flowchart ",
                "sequenceDiagram",
                "classDiagram",
                "stateDiagram",
                "erDiagram",
                "gantt",
                "pie",
                "journey",
            ]
        ):
            self.logger.info("Missing diagram type declaration detected.")
            # Try to infer diagram type from content
            if "-->" in code or "->" in code:
                self.logger.info("Inferring 'flowchart TD' from arrow syntax.")
                fixed_code = "flowchart TD\n" + fixed_code
                corrections.append("Added missing flowchart declaration")
            elif "sequenceDiagram" in error_message.lower():
                self.logger.info("Error message suggests 'sequenceDiagram'. Adding it.")
                fixed_code = "sequenceDiagram\n" + fixed_code
                corrections.append("Added missing sequenceDiagram declaration")

        # Mermaid-specific fix 2: Normalize arrow syntax
        # " - >" is a common typo for "-->"
        if " - >" in fixed_code:
            self.logger.info("Detected invalid arrow syntax ' - >'. Normalizing to '-->'.")
            fixed_code = fixed_code.replace(" - >", "-->")
            corrections.append("Normalized arrow syntax (- > to -->)")

        # Generic fix: Add missing braces for subgraphs
        if "{" in fixed_code:
            open_count = fixed_code.count("{")
            close_count = fixed_code.count("}")
            if open_count > close_count:
                missing_braces = open_count - close_count
                self.logger.info(f"Detected {missing_braces} missing closing brace(s). Appending them.")
                fixed_code += "}" * missing_braces
                corrections.append(f"Added {missing_braces} missing closing brace(s)")

        # Validate fixed code
        self.logger.info("Validating fixed Mermaid code...")
        validation_result = self.validate_code(fixed_code, **options)

        if validation_result.is_valid:
            validation_result.auto_fixed = True
            validation_result.fixed_code = fixed_code
            validation_result.correction_method = "pattern"
            if corrections:
                self.logger.info(f"Pattern-based fixes applied successfully: {', '.join(corrections)}")
            else:
                self.logger.info("Pattern-based validation check passed (no changes needed)")
        else:
            self.logger.info("Pattern-based fix did not resolve errors. Code remains invalid.")
            self.logger.debug(f"Failed validation error: {validation_result.error}")

        return validation_result

    def get_llm_correction_rules(self) -> Optional[str]:
        """
        Provide Mermaid-specific rules for LLM correction.

        Returns:
            str: A string containing specific rules and hints for the LLM to generate valid Mermaid syntax.
        """
        self.logger.info("Retrieving Mermaid-specific LLM correction rules.")
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
