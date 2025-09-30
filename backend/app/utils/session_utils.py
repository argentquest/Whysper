"""
Shared utilities for working with conversation sessions.

This module provides common helper functions used across multiple endpoints
for session management, response formatting, and data conversion.
"""

from typing import Any
from schemas import ConversationSummaryModel
from common.logger import get_logger

logger = get_logger(__name__)


def session_summary_model(session) -> ConversationSummaryModel:
    """
    Convert conversation session to standardized response model.

    Helper function to transform internal session state into the
    standardized Pydantic response model used by API endpoints.

    Args:
        session: ConversationSession object containing session state

    Returns:
        ConversationSummaryModel: Standardized summary response model
    """
    logger.debug(f"Converting session summary for session: {session.session_id}")
    summary = session.get_summary()
    logger.debug(f"Session summary retrieved: {len(summary.question_history)} questions, {len(summary.conversation_history)} messages")

    return ConversationSummaryModel(
        conversation_id=summary.conversation_id,
        provider=summary.provider,
        selected_model=summary.selected_model,
        selected_directory=summary.selected_directory,
        selected_files=summary.selected_files,
        persistent_files=summary.persistent_files,
        question_history=summary.question_history,
        conversation_history=summary.conversation_history,
    )