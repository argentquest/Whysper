"""
LLM Correction Service

Handles LLM-based diagram code correction using existing AI processor.
Sends error messages to LLM and gets corrected diagram code.
"""

from typing import Optional, Tuple
import logging
import re

from common.logging_decorator import log_method_call

logger = logging.getLogger(__name__)


class LLMCorrectionService:
    """
    Service for LLM-based diagram code correction.

    Integrates with existing common.ai.AIProcessor to send error feedback
    to LLM and get corrected code back.
    """

    @log_method_call
    def __init__(self, ai_processor=None):
        """
        Initialize LLM correction service.

        Args:
            ai_processor: Optional AI processor instance. If None, will be set later.
        """
        self.ai_processor = ai_processor
        self._initialized = ai_processor is not None  # Initialize if processor provided
        logger.info(
            "LLM correction service created (not yet initialized)"
            if ai_processor is None
            else "LLM correction service created with AI processor"
        )

    @log_method_call
    def initialize(self, api_key: str = None, provider: str = "openrouter"):
        """
        Initialize AI processor with credentials.

        Args:
            api_key: API key for LLM provider (optional if already set in env)
            provider: LLM provider name (default: "openrouter")
        """
        if self.ai_processor is None:
            try:
                from common.ai import create_ai_processor

                self.ai_processor = create_ai_processor(api_key=api_key or "", provider=provider)
                self._initialized = True
                logger.info(f"LLM correction service initialized with provider: {provider}")
            except Exception as e:
                logger.info(f"Failed to initialize LLM correction service: {e}")
                self._initialized = False
        else:
            self._initialized = True
            logger.info("LLM correction service using existing AI processor")

    @log_method_call
    def is_available(self) -> bool:
        """Check if LLM correction service is available"""
        return self._initialized and self.ai_processor is not None

    @log_method_call
    def correct_diagram_code(
        self,
        diagram_type: str,
        invalid_code: str,
        error_message: str,
        provider_specific_rules: Optional[str] = None,
        max_tokens: int = 4000,
        temperature: float = 0.3,
        model: Optional[str] = None,
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
            logger.info("LLM correction service not available")
            return False, invalid_code, "LLM correction service not initialized"

        # Build correction prompt
        correction_prompt = self._build_correction_prompt(
            diagram_type=diagram_type,
            invalid_code=invalid_code,
            error_message=error_message,
            provider_specific_rules=provider_specific_rules,
        )

        # Provide a focused system message so we don't fall back to the default codebase prompt
        type_rules = self._get_type_specific_rules(diagram_type)
        rules_sections = []
        rules_sections.append("\n".join(f"- {rule}" for rule in type_rules))
        if provider_specific_rules:
            # Include provider-specific rules verbatim (from correction_rules.md)
            rules_sections.append(provider_specific_rules.strip())

        system_prompt = (
            f"You are an expert at fixing {diagram_type} diagram syntax. "
            "Return only the corrected diagram code block with no commentary. "
            "Follow these rules strictly:\n"
            f"{'\n'.join(rules_sections)}"
        )
        system_message = {"role": "system", "content": system_prompt}

        logger.info(f"[LLM CORRECTION] Requesting correction for {diagram_type} diagram...")
        logger.debug(f"[LLM CORRECTION] Error: {error_message[:200]}")

        try:
            # Call LLM
            corrected_response = self.ai_processor.process_question(
                question=correction_prompt,
                # Pre-seed with our own system message to avoid default system prompt
                conversation_history=[system_message],
                codebase_content="",
                model=model,
                max_tokens=max_tokens,
                temperature=temperature,
            )

            logger.info(f"[LLM CORRECTION] Received response ({len(corrected_response)} chars)")

            # Extract corrected code from response
            corrected_code = self._extract_code_from_response(corrected_response, diagram_type)

            if corrected_code:
                logger.info("[LLM CORRECTION] ✅ Successfully extracted corrected code")
                return True, corrected_code, "LLM correction applied"
            else:
                logger.info("[LLM CORRECTION] ❌ Could not extract code from response")
                return False, invalid_code, "Could not extract corrected code from LLM response"

        except Exception as e:
            logger.info(f"[LLM CORRECTION] ❌ Error during correction: {e}", exc_info=True)
            return False, invalid_code, f"LLM correction failed: {str(e)}"

    @log_method_call
    def _build_correction_prompt(
        self, diagram_type: str, invalid_code: str, error_message: str, provider_specific_rules: Optional[str]
    ) -> str:
        """Build correction prompt for LLM"""

        # Generic rules for all diagram types
        generic_rules = [
            "Fix ALL syntax errors completely",
            "Maintain original intent and structure",
            "Keep diagram simple and readable",
            "Use proper syntax according to specification",
            "Do NOT add explanations - return ONLY corrected code block",
        ]

        # Diagram-type-specific rules
        type_specific_rules = self._get_type_specific_rules(diagram_type)

        # Combine all rules
        all_rules = generic_rules + type_specific_rules
        if provider_specific_rules:
            all_rules.append(provider_specific_rules)

        # Build prompt
        prompt = f"""FIX THIS {diagram_type.upper()} DIAGRAM SYNTAX ERROR:

**ERROR MESSAGE:**{error_message}
**INVALID CODE:**{diagram_type}
{invalid_code}
**CORRECTION RULES:**
{chr(10).join(f"- {rule}" for rule in all_rules)}

**INSTRUCTIONS:**
Return ONLY corrected ```{diagram_type} code block with ALL errors fixed.
Do not include explanations, comments, or any text outside the code block.
The code must be complete and valid."""

        return prompt

    @log_method_call
    def _get_type_specific_rules(self, diagram_type: str) -> list:
        """Get diagram-type-specific correction rules"""

        # Provider-specific markdown rules should be the source of truth.
        # Keep this empty to avoid mixing baked-in rules with the provider files.
        logger.debug(
            "Type-specific rules are sourced from provider markdown; returning empty list",
            extra={"diagram_type": diagram_type},
        )
        return []

    @log_method_call
    def _extract_code_from_response(self, response: str, diagram_type: str) -> Optional[str]:
        """Extract diagram code from LLM response"""

        # Try to extract code block with specific type
        pattern = rf"```{diagram_type}\s*\n?(.*?)```"
        matches = re.findall(pattern, response, re.DOTALL | re.IGNORECASE)

        if matches:
            extracted = matches[0].strip()
            logger.debug(f"[LLM CORRECTION] Extracted code with {diagram_type} fence")
            return extracted

        # Try generic code block
        pattern = r"```\s*\n?(.*?)```"
        matches = re.findall(pattern, response, re.DOTALL)

        if matches:
            # Return first code block
            extracted = matches[0].strip()
            logger.debug("[LLM CORRECTION] Extracted code with generic fence")
            return extracted

        # If no code blocks found, try to find diagram-type-specific keywords
        # and extract portion that looks like code
        if diagram_type.lower() == "mermaid":
            # Look for mermaid diagram keywords
            keywords = [
                "flowchart",
                "graph",
                "sequenceDiagram",
                "classDiagram",
                "stateDiagram",
                "erDiagram",
                "gantt",
                "pie",
            ]
            for keyword in keywords:
                if keyword in response:
                    # Try to extract from keyword to end
                    start_idx = response.find(keyword)
                    # Find next triple backticks or end
                    end_idx = response.find("```", start_idx)
                    if end_idx == -1:
                        extracted = response[start_idx:].strip()
                    else:
                        extracted = response[start_idx:end_idx].strip()
                    logger.debug("[LLM CORRECTION] Extracted mermaid code by keyword detection")
                    return extracted

        # Last resort: return entire response stripped
        logger.info("[LLM CORRECTION] No code blocks found, using full response")
        return response.strip()


# Global singleton instance
_llm_correction_service = None


@log_method_call
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


@log_method_call
def set_llm_correction_service(service: LLMCorrectionService):
    """Set the global LLM correction service instance (for testing)"""
    global _llm_correction_service
    _llm_correction_service = service
