"""
LLM Correction Service

Handles LLM-based diagram code correction using the existing AI processor.
Sends error messages to LLM and gets corrected diagram code.
"""

from typing import Optional, Tuple
import logging
import re

logger = logging.getLogger(__name__)


class LLMCorrectionService:
    """
    Service for LLM-based diagram code correction.

    Integrates with existing common.ai.AIProcessor to send error feedback
    to LLM and get corrected code back.
    """

    def __init__(self, ai_processor=None):
        """
        Initialize the LLM correction service.

        Args:
            ai_processor: Optional AI processor instance. If None, will be set later.
        """
        self.ai_processor = ai_processor
        self._initialized = ai_processor is not None  # Initialize if processor provided
        logger.info("LLM correction service created (not yet initialized)" if ai_processor is None else "LLM correction service created with AI processor")

    def initialize(self, api_key: str = None, provider: str = "openrouter"):
        """
        Initialize the AI processor with credentials.

        Args:
            api_key: API key for the LLM provider (optional if already set in env)
            provider: LLM provider name (default: "openrouter")
        """
        if self.ai_processor is None:
            try:
                from common.ai import create_ai_processor
                self.ai_processor = create_ai_processor(api_key=api_key or "", provider=provider)
                self._initialized = True
                logger.info(f"LLM correction service initialized with provider: {provider}")
            except Exception as e:
                logger.error(f"Failed to initialize LLM correction service: {e}")
                self._initialized = False
        else:
            self._initialized = True
            logger.info("LLM correction service using existing AI processor")

    def is_available(self) -> bool:
        """Check if LLM correction service is available"""
        return self._initialized and self.ai_processor is not None

    def correct_diagram_code(
        self,
        diagram_type: str,
        invalid_code: str,
        error_message: str,
        provider_specific_rules: Optional[str] = None,
        max_tokens: int = 4000,
        temperature: float = 0.3,
        model: Optional[str] = None
    ) -> Tuple[bool, str, str]:
        """
        Use LLM to correct diagram code based on error feedback.

        Args:
            diagram_type: Type of diagram (mermaid, d2, plantuml, etc.)
            invalid_code: The invalid diagram code
            error_message: The error message from validation
            provider_specific_rules: Optional provider-specific syntax rules
            max_tokens: Maximum tokens for LLM response
            temperature: Temperature for LLM generation (lower = more deterministic)
            model: Optional specific model to use

        Returns:
            Tuple of (success, corrected_code, correction_message)
        """
        if not self.is_available():
            logger.warning("LLM correction service not available")
            return False, invalid_code, "LLM correction service not initialized"

        # Build correction prompt
        correction_prompt = self._build_correction_prompt(
            diagram_type=diagram_type,
            invalid_code=invalid_code,
            error_message=error_message,
            provider_specific_rules=provider_specific_rules
        )

        logger.info(f"[LLM CORRECTION] Requesting correction for {diagram_type} diagram...")
        logger.debug(f"[LLM CORRECTION] Error: {error_message[:200]}")

        try:
            # Call LLM
            corrected_response = self.ai_processor.process_question(
                question=correction_prompt,
                conversation_history=[],  # No context needed for correction
                codebase_content="",
                model=model,
                max_tokens=max_tokens,
                temperature=temperature
            )

            logger.info(f"[LLM CORRECTION] Received response ({len(corrected_response)} chars)")

            # Extract corrected code from response
            corrected_code = self._extract_code_from_response(
                corrected_response, diagram_type
            )

            if corrected_code:
                logger.info(f"[LLM CORRECTION] ✅ Successfully extracted corrected code")
                return True, corrected_code, "LLM correction applied"
            else:
                logger.warning(f"[LLM CORRECTION] ❌ Could not extract code from response")
                return False, invalid_code, "Could not extract corrected code from LLM response"

        except Exception as e:
            logger.error(f"[LLM CORRECTION] ❌ Error during correction: {e}", exc_info=True)
            return False, invalid_code, f"LLM correction failed: {str(e)}"

    def _build_correction_prompt(
        self,
        diagram_type: str,
        invalid_code: str,
        error_message: str,
        provider_specific_rules: Optional[str]
    ) -> str:
        """Build the correction prompt for the LLM"""

        # Generic rules for all diagram types
        generic_rules = [
            "Fix ALL syntax errors completely",
            "Maintain the original intent and structure",
            "Keep the diagram simple and readable",
            "Use proper syntax according to the specification",
            "Do NOT add explanations - return ONLY the corrected code block"
        ]

        # Diagram-type-specific rules
        type_specific_rules = self._get_type_specific_rules(diagram_type)

        # Combine all rules
        all_rules = generic_rules + type_specific_rules
        if provider_specific_rules:
            all_rules.append(provider_specific_rules)

        # Build prompt
        prompt = f"""FIX THIS {diagram_type.upper()} DIAGRAM SYNTAX ERROR:

**ERROR MESSAGE:**
```
{error_message}
```

**INVALID CODE:**
```{diagram_type}
{invalid_code}
```

**CORRECTION RULES:**
{chr(10).join(f"- {rule}" for rule in all_rules)}

**INSTRUCTIONS:**
Return ONLY the corrected ```{diagram_type} code block with ALL errors fixed.
Do not include explanations, comments, or any text outside the code block.
The code must be complete and valid."""

        return prompt

    def _get_type_specific_rules(self, diagram_type: str) -> list:
        """Get diagram-type-specific correction rules"""

        rules_map = {
            "mermaid": [
                "Always start with diagram type (flowchart TD, sequenceDiagram, etc.)",
                "Use proper arrow syntax with spaces: A --> B (not A-->B)",
                "Quote labels with special characters: A[\"My Node\"]",
                "Do NOT use reserved keywords as node IDs (end, start, subgraph, etc.)",
                "Close all subgraphs with 'end'",
                "For sequence diagrams, use: participant, -->>, -->"
            ],
            "d2": [
                "Use proper shape syntax: shape_name: text",
                "Use proper connection syntax: A -> B or A -- B",
                "Use proper style syntax: shape.style.fill: \"#color\"",
                "Properly indent nested structures",
                "Use quotes for labels with spaces or special characters"
            ],
            "plantuml": [
                "Use @startuml and @enduml tags",
                "Use proper component syntax",
                "Use proper relationship syntax (-->, ..>, etc.)",
                "Follow PlantUML keyword conventions"
            ]
        }

        return rules_map.get(diagram_type.lower(), [])

    def _extract_code_from_response(self, response: str, diagram_type: str) -> Optional[str]:
        """Extract diagram code from LLM response"""

        # Try to extract code block with specific type
        pattern = rf'```{diagram_type}\s*\n?(.*?)```'
        matches = re.findall(pattern, response, re.DOTALL | re.IGNORECASE)

        if matches:
            extracted = matches[0].strip()
            logger.debug(f"[LLM CORRECTION] Extracted code with {diagram_type} fence")
            return extracted

        # Try generic code block
        pattern = r'```\s*\n?(.*?)```'
        matches = re.findall(pattern, response, re.DOTALL)

        if matches:
            # Return the first code block
            extracted = matches[0].strip()
            logger.debug(f"[LLM CORRECTION] Extracted code with generic fence")
            return extracted

        # If no code blocks found, try to find diagram-type-specific keywords
        # and extract the portion that looks like code
        if diagram_type.lower() == "mermaid":
            # Look for mermaid diagram keywords
            keywords = ['flowchart', 'graph', 'sequenceDiagram', 'classDiagram',
                       'stateDiagram', 'erDiagram', 'gantt', 'pie']
            for keyword in keywords:
                if keyword in response:
                    # Try to extract from keyword to end
                    start_idx = response.find(keyword)
                    # Find next triple backticks or end
                    end_idx = response.find('```', start_idx)
                    if end_idx == -1:
                        extracted = response[start_idx:].strip()
                    else:
                        extracted = response[start_idx:end_idx].strip()
                    logger.debug(f"[LLM CORRECTION] Extracted mermaid code by keyword detection")
                    return extracted

        # Last resort: return the entire response stripped
        logger.warning("[LLM CORRECTION] No code blocks found, using full response")
        return response.strip()


# Global singleton instance
_llm_correction_service = None


def get_llm_correction_service() -> LLMCorrectionService:
    """Get the global LLM correction service instance"""
    global _llm_correction_service
    if _llm_correction_service is None:
        _llm_correction_service = LLMCorrectionService()

        # Try to initialize with existing settings if available
        try:
            from common.env_manager import env_manager
            env_vars = env_manager.load_env_file()
            api_key = env_vars.get("API_KEY", "")
            provider = env_vars.get("AI_PROVIDER", "openrouter")

            if api_key:
                _llm_correction_service.initialize(api_key=api_key, provider=provider)
                logger.info("LLM correction service auto-initialized from env")
        except Exception as e:
            logger.debug(f"Could not auto-initialize LLM correction service: {e}")

    return _llm_correction_service


def set_llm_correction_service(service: LLMCorrectionService):
    """Set the global LLM correction service instance (for testing)"""
    global _llm_correction_service
    _llm_correction_service = service
