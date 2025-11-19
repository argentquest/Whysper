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
    # Define provider-specific metadata for identification and configuration

    @property
    def provider_id(self) -> str:
        # Return unique identifier matching folder name for internal tracking
        return "krokistructurizr"

    @property
    def provider_name(self) -> str:
        # Return human-readable name for user-facing displays
        return "Kroki Structurizr Renderer"

    @property
    def diagram_type(self) -> str:
        # Specify the primary diagram type for routing and processing
        return "structurizr"

    @property
    def diagram_endpoint(self) -> str:
        # Define the specific Kroki API endpoint for Structurizr diagrams
        return "structurizr"

    def auto_fix_pattern_based(
        self, code: str, error_message: str, **options
    ) -> ValidationResult:
        # Implement automated syntax correction for Structurizr diagrams
        
        # Log the start of auto-fix process
        self.logger.info("Attempting pattern-based auto-fix for Structurizr...")

        # Initialize variables for code fixing
        fixed_code = code
        corrections = []

        # Check and add missing workspace declaration if not present
        if not code.strip().startswith('workspace'):
            fixed_code = 'workspace {\n' + fixed_code + '\n}'
            corrections.append('Added missing workspace declaration')

        # Add model block if missing but required elements are present
        if 'model {' in fixed_code:
            # Already has model block, no action needed
            pass
        elif '->' in fixed_code or 'person ' in fixed_code:
            # Likely missing model block, so insert it
            fixed_code = fixed_code.replace(
                'workspace {',
                'workspace {\n  model {'
            )
            fixed_code = fixed_code.rstrip('}') + '\n  }\n}'
            corrections.append('Added missing model block')

        # Ensure balanced braces by adding missing closing braces
        if '{' in fixed_code:
            open_count = fixed_code.count('{')
            close_count = fixed_code.count('}')
            if open_count > close_count:
                missing_braces = open_count - close_count
                fixed_code += '}' * missing_braces
                corrections.append(
                    f'Added {missing_braces} missing closing brace(s)'
                )

        # Validate the corrected code
        validation_result = self.validate_code(fixed_code, **options)

        # Process and log validation results
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
        # Provide structured rules for AI-based diagram correction
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
