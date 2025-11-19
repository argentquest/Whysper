from typing import Any
from schemas import ConversationSummaryModel
from common.logger import get_logger

# Initialize logger for tracking and debugging session-related operations
logger = get_logger(__name__)


def session_summary_model(session) -> ConversationSummaryModel:
    # Log the start of session summary conversion for debugging purposes
    logger.debug(f"Converting session summary for session: {session.session_id}")

    # Retrieve the summary data from the session object 
    # This extracts key metadata and conversation details
    summary = session.get_summary()

    # Log details about retrieved summary to track conversation depth
    logger.debug(f"Session summary retrieved: {len(summary.question_history)} questions, {len(summary.conversation_history)} messages")

    # Create and return a standardized summary model with all session metadata
    # This transforms internal session state into a consistent API response format
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
