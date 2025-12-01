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
    Kroki Structurizr Provider - Structurizr diagrams via Kroki service

    This provider uses Kroki (https://kroki.io) to render Structurizr diagrams
    via HTTP API calls to a local Kroki server.

    Attributes:
        provider_id (str): Unique identifier for this provider.
        provider_name (str): Human-readable name for this provider.
        diagram_type (str): Primary diagram type this provider handles.
        diagram_endpoint (str): Specific Kroki API endpoint for Structurizr.
    """

    @property
    def provider_id(self) -> str:
        """
        Unique identifier for this provider (same as folder name).

        Returns:
            str: "krokistructurizr"
        """
        return "krokistructurizr"

    @property
    def provider_name(self) -> str:
        """
        Human-readable name for this provider.

        Returns:
            str: "Kroki Structurizr Renderer"
        """
        return "Kroki Structurizr Renderer"

    @property
    def diagram_type(self) -> str:
        """
        Primary diagram type this provider handles.

        Returns:
            str: "structurizr"
        """
        return "structurizr"

    @property
    def diagram_endpoint(self) -> str:
        """
        Define the specific Kroki API endpoint for Structurizr diagrams.

        Returns:
            str: "structurizr"
        """
        return "structurizr"

    def auto_fix_pattern_based(self, code: str, error_message: str, **options) -> ValidationResult:
        """
        Implement automated syntax correction for Structurizr diagrams.

        Args:
            code (str): The invalid diagram code.
            error_message (str): The error message from the previous validation attempt.
            **options: Additional provider-specific options.

        Returns:
            ValidationResult: The result of the auto-fix attempt, including the fixed code if successful.
        """
        # Log the start of auto-fix process
        self.logger.info("Attempting pattern-based auto-fix for Structurizr...")

        # Initialize variables for code fixing
        fixed_code = code
        corrections = []

        # Check and add missing workspace declaration if not present
        if not code.strip().startswith("workspace"):
            self.logger.info("Detected missing 'workspace' declaration. Adding it.")
            fixed_code = "workspace {\n" + fixed_code + "\n}"
            corrections.append("Added missing workspace declaration")

        # Add model block if missing but required elements are present
        if "model {" in fixed_code:
            # Already has model block, no action needed
            pass
        elif "->" in fixed_code or "person " in fixed_code:
            # Likely missing model block, so insert it
            self.logger.info("Detected missing 'model' block. Injecting it into workspace.")
            fixed_code = fixed_code.replace("workspace {", "workspace {\n  model {")
            fixed_code = fixed_code.rstrip("}") + "\n  }\n}"
            corrections.append("Added missing model block")

        # Ensure balanced braces by adding missing closing braces
        if "{" in fixed_code:
            open_count = fixed_code.count("{")
            close_count = fixed_code.count("}")
            if open_count > close_count:
                missing_braces = open_count - close_count
                self.logger.info(f"Detected {missing_braces} missing closing brace(s). Appending them.")
                fixed_code += "}" * missing_braces
                corrections.append(f"Added {missing_braces} missing closing brace(s)")

        # Validate the corrected code
        self.logger.info("Validating fixed Structurizr code...")
        validation_result = self.validate_code(fixed_code, **options)

        # Process and log validation results
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
        Provide structured rules for AI-based diagram correction.

        Returns:
            str: A string containing specific rules and hints for the LLM to generate valid Structurizr DSL.
        """
        self.logger.info("Retrieving Structurizr-specific LLM correction rules.")
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
