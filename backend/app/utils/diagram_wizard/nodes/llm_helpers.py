"""
LLM helper functions and utilities for diagram wizard nodes.

Provides centralized AI/LLM call handling, model ID mapping,
and shared helper functions used across multiple nodes.
"""

import logging
import httpx
from typing import Dict
from ..graph_state import DiagramType
from common.ai import create_ai_processor
from common.env_manager import env_manager

logger = logging.getLogger(__name__)

# Provider mapping constant to avoid duplication
PROVIDER_MAP = {
    "Mermaid": "mermaidv1",
    "D2": "d2v1",
    "PlantUML": "krokiplantuml"
}


def get_diagram_type_str(diagram_type: DiagramType) -> str:
    """
    Helper function to convert DiagramType enum to string.

    Handles both enum values and string fallbacks.
    """
    return diagram_type.value if hasattr(diagram_type, 'value') else str(diagram_type)


def _get_model_for_id(model_id: str = None) -> str:
    """Get the actual AI model to use for API calls.

    NOTE: The model_id parameter is used to select which system PROMPT to use
    (different prompt styles for gpt5, grok, claude, gemini), but the ACTUAL
    model used for API calls always comes from DEFAULT_MODEL in .env file.

    Args:
        model_id: Used for prompt selection only (gpt5, grok, claude, gemini)
                  Does NOT affect which actual AI model is called

    Returns:
        Actual model identifier from .env DEFAULT_MODEL for API calls
    """
    # Always use the actual model from .env file for API calls
    # The model_id is only used to select prompt style via get_prompt()
    env_vars = env_manager.load_env_file()
    default_model = env_vars.get("DEFAULT_MODEL", "google/gemini-2.5-flash-preview-09-2025")

    logger.info(f"Using actual AI model from .env: {default_model} (prompt style: {model_id or 'default'})")
    return default_model


async def call_llm(prompt: str, user_content: str, session_id: str = None, model_id: str = None) -> str:
    """Helper function to call AI/LLM with proper error handling and SSE logging.

    Args:
        prompt: System prompt template
        user_content: User message content
        session_id: Session ID for SSE filtering (optional)
        model_id: Selected AI model ID (gpt5, grok, claude, gemini)

    Returns:
        AI response string

    Raises:
        Exception: When AI call fails with descriptive error message
    """
    try:
        # Load environment configuration
        env_vars = env_manager.load_env_file()
        api_key = env_vars.get("API_KEY", "")
        provider = env_vars.get("PROVIDER", "openrouter")
        # Use selected model or fall back to environment/default
        model = _get_model_for_id(model_id) if model_id else env_vars.get("DEFAULT_MODEL", "google/gemini-2.5-flash-preview-09-2025")

        if not api_key:
            logger.error("No API key configured for diagram wizard AI calls",
                        extra={'session_id': session_id} if session_id else {})
            raise Exception("No API key configured. Please configure your AI provider API key in settings.")

        # Log AI call initiation (visible via SSE)
        logger.info(f"🤖 Starting AI call for diagram generation",
                   extra={'session_id': session_id} if session_id else {})
        logger.info(f"📋 Model: {model} | Provider: {provider}",
                   extra={'session_id': session_id} if session_id else {})

        # Create AI processor
        processor = create_ai_processor(api_key=api_key, provider=provider)

        # Format conversation for AI call
        conversation_history = [
            {"role": "system", "content": prompt},
            {"role": "user", "content": user_content}
        ]

        logger.info(f"🚀 ACTUAL LLM CALL - Sending request to AI (prompt: {len(prompt)} chars, content: {len(user_content)} chars)",
                   extra={'session_id': session_id} if session_id else {})

        # Make the AI call
        result = processor.process_question(
            question=user_content,
            conversation_history=conversation_history,
            model=model,
            codebase_content="",  # No codebase context needed for diagrams
            max_tokens=2000,      # Reasonable token limit for diagram generation
            temperature=0.7       # Balance creativity and consistency
        )

        # Handle both string and dict return types
        if isinstance(result, str):
            response = result
            tokens_used = 0
            processing_time = 0.0
        else:
            response = result.get("response", "")
            tokens_used = result.get("tokens_used", 0)
            processing_time = result.get("processing_time", 0.0)

        # Log successful AI response (visible via SSE)
        logger.info(f"✅ LLM RESPONSE RECEIVED: {len(response)} chars | {tokens_used} tokens | {processing_time:.1f}s",
                   extra={'session_id': session_id} if session_id else {})

        # Log the FULL raw AI response for debugging
        logger.info(f"📄 FULL LLM RAW RESPONSE:\n{response}",
                   extra={'session_id': session_id} if session_id else {})

        return response
    except httpx.RequestError as e:
        error_msg = f"Network error during AI call: {str(e)}. Please check your internet connection and try again."
        logger.error(f"❌ AI call failed due to a network error: {e}",
                    extra={'session_id': session_id} if session_id else {})
        raise Exception(error_msg)
    except Exception as e:
        # Check if it's an API key error from the error message
        error_str = str(e).lower()
        if "api key" in error_str or "invalid" in error_str or "expired" in error_str or "unauthorized" in error_str:
            error_msg = f"API key error: {str(e)}. Please check your AI provider API key in settings."
        else:
            error_msg = f"AI call failed: {str(e)}"

        logger.error(f"❌ An error occurred during the AI call: {e}",
                    extra={'session_id': session_id} if session_id else {})
        raise Exception(error_msg)
