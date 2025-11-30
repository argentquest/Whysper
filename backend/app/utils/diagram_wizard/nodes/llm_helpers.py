"""
LLM helper functions and utilities for diagram wizard nodes.

Provides centralized AI/LLM call handling, model ID mapping,
and shared helper functions used across multiple nodes.
"""

import asyncio
import httpx
import json
import re
from typing import Dict, Any, Union
from ..graph_state import DiagramType
from common.ai import create_ai_processor
from common.logger import get_logger
from app.core.config import settings

logger = get_logger(__name__)


def extract_json_from_response(response_text: str) -> Dict[str, Any]:
    """
    Extract and parse JSON from an LLM response that may be wrapped in markdown code blocks.
    
    Args:
        response_text (str): The raw response text from the LLM.
        
    Returns:
        Dict[str, Any]: Parsed JSON dictionary.
        
    Raises:
        json.JSONDecodeError: If the response cannot be parsed as JSON.
    """
    try:
        # First try direct JSON parsing
        return json.loads(response_text)
    except json.JSONDecodeError:
        # Try to extract JSON from markdown code blocks
        # Pattern matches ```json ... ``` or ``` ... ```
        # Use greedy match (.*) to capture nested JSON objects like {"a": {"b": "c"}}
        json_pattern = r'```(?:json)?\s*(\{.*\})\s*```'
        match = re.search(json_pattern, response_text, re.DOTALL)
        
        if match:
            json_str = match.group(1)
            return json.loads(json_str)
        
        # If no code blocks found, try to find JSON object in the text
        # Look for content between curly braces
        brace_pattern = r'\{.*\}'
        match = re.search(brace_pattern, response_text, re.DOTALL)
        
        if match:
            return json.loads(match.group(0))
        
        # If all else fails, raise the original error
        raise


def get_diagram_type_str(diagram_type: Union[DiagramType, str]) -> str:
    """
    Helper function to convert DiagramType enum to string.

    Handles both enum values and string fallbacks.

    Args:
        diagram_type (Union[DiagramType, str]): The diagram type enum or value.

    Returns:
        str: The string representation of the diagram type.
    """
    return diagram_type.value if hasattr(diagram_type, 'value') else str(diagram_type)


def _get_model_for_id(model_id: str = None) -> str:
    """
    Get the actual AI model to use for API calls.

    NOTE: The model_id parameter is used to select which system PROMPT to use
    (different prompt styles for gpt5, grok, claude, gemini), but the ACTUAL
    model used for API calls always comes from DEFAULT_MODEL in .env file.

    Args:
        model_id (str, optional): Used for prompt selection only (gpt5, grok, claude, gemini).
                                  Does NOT affect which actual AI model is called.

    Returns:
        str: Actual model identifier from .env DEFAULT_MODEL for API calls.
    """
    default_model = settings.default_model or "google/gemini-2.5-flash-preview-09-2025"

    logger.info(f"Using actual AI model from .env: {default_model} (prompt style: {model_id or 'default'})")
    return default_model


async def call_llm(prompt: str, user_content: str, session_id: str = None, model_id: str = None) -> str:
    """
    Helper function to call AI/LLM with proper error handling and SSE logging.

    Args:
        prompt (str): System prompt template.
        user_content (str): User message content.
        session_id (str, optional): Session ID for SSE filtering.
        model_id (str, optional): Selected AI model ID (gpt5, grok, claude, gemini).

    Returns:
        str: AI response string.

    Raises:
        Exception: When AI call fails with descriptive error message.
    """
    try:
        # Load configuration via settings (.env + environment)
        api_key = settings.api_key
        provider = settings.provider or "openrouter"
        model = _get_model_for_id(model_id)

        if not api_key:
            logger.error("No API key configured for diagram wizard AI calls",
                        extra={'session_id': session_id} if session_id else {})
            raise Exception("No API key configured. Please configure your AI provider API key in settings.")

        # Log AI call initiation (visible via SSE)
        logger.info("🤖 Starting AI call for diagram generation",
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

        # Pull token and temperature configuration from settings
        try:
            max_tokens = int(settings.max_tokens)
        except (TypeError, ValueError):
            max_tokens = 2000

        try:
            temperature = float(settings.temperature)
        except (TypeError, ValueError):
            temperature = 0.7

        # Compute a hard timeout so a stuck provider call doesn't hang the workflow
        try:
            connect_timeout = int(settings.ai_connect_timeout)
            read_timeout = int(settings.ai_read_timeout)
        except (TypeError, ValueError):
            connect_timeout = 30
            read_timeout = 120
        total_timeout = connect_timeout + read_timeout + 15
  
        # Make the AI call in a worker thread with an overall timeout
        try:
            result = await asyncio.wait_for(
                asyncio.to_thread(
                    processor.process_question,
                    user_content,
                    conversation_history,
                    "",  # codebase_content not used for diagram wizard
                    model,
                    max_tokens,
                    temperature,
                ),
                timeout=total_timeout,
            )
        except asyncio.TimeoutError as timeout_err:
            logger.error(
                f"AI call exceeded timeout ({total_timeout}s)",
                extra={'session_id': session_id} if session_id else {},
            )
            raise Exception(
                f"AI call timed out after {total_timeout}s. Please try again or simplify the request."
            ) from timeout_err

        # Handle both string and dict return types
        if isinstance(result, str):
            response = result
            tokens_used = 0
            processing_time = 0.0
        else:
            response = result.get("response")
            if not response:
                raise ValueError("AI processor returned dict without 'response' key or empty response")
            tokens_used = result.get("tokens_used", 0)
            processing_time = result.get("processing_time", 0.0)

        # Log successful AI response (visible via SSE)
        logger.info(f"✅ LLM RESPONSE RECEIVED: {len(response)} chars | {tokens_used} tokens | {processing_time:.1f}s",
                   extra={'session_id': session_id} if session_id else {})

        # Log the FULL raw AI response for debugging
        logger.debug(f"📄 FULL USER HISTORY :\n{conversation_history}",
                   extra={'session_id': session_id} if session_id else {})

        logger.debug(f"📄 FULL HISTORY :\n{user_content}",
                   extra={'session_id': session_id} if session_id else {})

        # Log the FULL raw AI response for debugging
        logger.debug(f"📄 FULL LLM RAW RESPONSE:\n{response}",
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
        raise Exception(error_msg) from e
