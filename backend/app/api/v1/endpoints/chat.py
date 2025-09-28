"""
Chat and conversation management endpoints for WhysperCode Web2 Backend.

This module provides the core chat functionality of the WhysperCode application,
handling real AI integration, conversation management, and session persistence.

Key Features:
- Multi-provider chat integration
- Conversation session management and persistence
- Model and API key runtime configuration
- Markdown to HTML conversion for frontend display
- Context file attachment support
- Conversation import/export functionality

Endpoints:
- POST /chat: Send chat messages to AI providers
- POST /conversations: Create new conversation sessions
- GET /conversations/{id}/summary: Retrieve conversation summaries
- PUT /conversations/{id}/model: Update AI model for conversation
- PUT /conversations/{id}/api-key: Update API key for conversation
- GET /conversations/{id}/export: Export conversation data
- POST /conversations/import: Import conversation data
"""
# Standard library imports
from typing import List, Optional
from datetime import datetime

# FastAPI framework imports
from fastapi import APIRouter, HTTPException

# Common library imports for conversation management
from app.core.config import load_env_defaults              # Environment configuration
from app.services.conversation_service import conversation_manager

# Pydantic schema imports for request/response validation
from schemas import (
    AskQuestionRequest,        # Chat message request schema
    AskQuestionResponse,       # Chat message response schema
    ConversationCreateRequest, # New conversation request schema
    ConversationCreateResponse,# Conversation state response schema
    ConversationSummaryModel,  # Conversation summary schema
    ExportConversationResponse,# Export data response schema
    ImportConversationRequest, # Import data request schema
    UpdateApiKeyRequest,       # API key update request schema
    UpdateModelRequest,        # Model update request schema
)

# Third-party imports
import markdown2               # Markdown to HTML conversion for frontend

# Logging setup
from common.logger import get_logger

# Initialize logger for this module
logger = get_logger(__name__)

# Create FastAPI router for chat endpoints
# This router will be included in the main API with /chat prefix
router = APIRouter()


@router.post("/")
@router.post("")  # Handle both /api/v1/chat/ and /api/v1/chat
def send_message_root(request: dict):
    logger.debug("send_message_root endpoint started")
    logger.debug("send_message_root endpoint started")
    """Primary chat endpoint used by the frontend."""

    if not isinstance(request, dict):
        raise HTTPException(status_code=400, detail="Invalid request payload")

    message = request.get("message") or request.get("question")
    if not message or not str(message).strip():
        raise HTTPException(status_code=400, detail="message is required")

    conversation_id = request.get("conversationId") or None
    settings = request.get("settings") or {}
    context_files = request.get("contextFiles") or []

    config = load_env_defaults()

    api_key = settings.get("apiKey") or config["api_key"]
    provider = settings.get("provider") or config["provider"]
    model = settings.get("model") or config["default_model"] or (config["models"][0] if config["models"] else None)

    if not api_key:
        raise HTTPException(status_code=400, detail="API key is required")

    
    try:
        session = None
        if conversation_id:
            
    try:
                session = conversation_manager.get_session(conversation_id)
            except KeyError:
                session = None

        if session is None:
            session = conversation_manager.create_session(
                api_key=api_key,
                provider=provider,
                models=models,
                default_model=model,
                session_id=conversation_id,
            )

        session.set_api_key(api_key)
        session.set_provider(provider)
        if model:
            session.set_model(model)
        if models:
            session.update_available_models(models)

        if context_files:
            session.update_selected_files(context_files, make_persistent=True)

        result = session.ask_question(str(message))

        assistant_message = {
            "id": f"msg-{session.session_id}-{datetime.utcnow().timestamp():.6f}",
            "role": "assistant",
            "content": result["response"],
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "metadata": {
                "rawMarkdown": result.get("rawMarkdown", ""),
                "tokens": result.get("tokens_used", 0),
                "processing_time": result.get("processing_time", 0.0),
                "question_index": result.get("question_index", 0),
            },
        }

        logger.debug("send_message_root endpoint ready to return content")
        return {
            "success": True,
            "data": {
                "message": assistant_message,
                "usage": {
                    "completionTokens": result.get("tokens_used", 0),
                    "promptTokens": 0,
                    "totalTokens": result.get("tokens_used", 0),
                },
                "conversationId": session.session_id,
            },
        }
        logger.debug("send_message_root endpoint ready to return content")
        return response

    except HTTPException:
        raise
    except Exception as exc:  # pragma: no cover - defensive fallback
        logger.exception("Error processing chat message", exc_info=exc)
        raise HTTPException(status_code=500, detail="Failed to process chat request")



def _session_summary_model(session) -> ConversationSummaryModel:
    """Convert session summary to response model."""
    summary = session.get_summary()
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


def _conversation_state_response(session) -> ConversationCreateResponse:
    """Create conversation state response."""
    summary_model = _session_summary_model(session)
    return ConversationCreateResponse(
        conversationId=session.session_id,
        provider=session.provider,
        model=summary_model.selected_model,
        availableModels=session.available_models,
        summary=summary_model,
    )


@router.post("/chat", response_model=AskQuestionResponse)
    
def send_chat_message(request: AskQuestionRequest):
    """
    Send a chat message and get AI response.
    
    This endpoint handles real AI chat integration using the AIProviderFactory
    to communicate with various AI providers (OpenRouter, Anthropic, OpenAI, etc.).
    
    """
    
    try:
        # Load environment defaults for AI configuration
        env_api_key, env_provider, models, env_default_model = load_env_defaults()
        
        # Use provided API key or fall back to environment default
        api_key = request.api_key or env_api_key
        if not api_key:
            raise HTTPException(
                status_code=400, 
                detail="API key is required. Please provide it in the request or set it in environment."
            )
        
        # Determine provider and model
        provider = request.provider or env_provider
        model = request.model or env_default_model
        
        if not model:
            raise HTTPException(
                status_code=400,
                detail="Model is required. Please specify a model or set a default."
            )
        
        # Get or create conversation session
        conversation_id = request.conversation_id or "default"
        
        
    try:
            session = conversation_manager.get_session(conversation_id)
        except KeyError:
            # Create new session if it doesn't exist
            logger.info(f"Creating new conversation session: {conversation_id}")
            session = conversation_manager.create_session(
                conversation_id, 
                provider=provider,
                api_key=api_key,
                models=models
            )
            session.set_model(model)
        
        # Update session configuration if provided
        if request.api_key:
            session.set_api_key(request.api_key)
        if request.provider:
            session.set_provider(request.provider)
        if request.model:
            session.set_model(request.model)
        
        # Add context files if provided
        if hasattr(request, 'context_files') and request.context_files:
            for file_path in request.context_files:
                session.add_file(file_path)
        
        # Send the question and get AI response
        logger.info(f"Processing chat message in conversation {conversation_id}")
        result = session.ask_question(request.question)
        
        # Convert markdown to HTML for frontend
        raw_response = result["response"]
        html_response = markdown2.markdown(raw_response)
        result["rawResponse"] = raw_response
        result["response"] = html_response
        
        logger.info(f"Chat message processed successfully for conversation {conversation_id}")
        return result
        
    except ValueError as exc:
        logger.error(f"Validation error in chat: {exc}")
        raise HTTPException(status_code=400, detail=str(exc))
    except Exception as exc:
        logger.error(f"Error processing chat message: {exc}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.post("/conversations", response_model=ConversationCreateResponse)
def create_conversation(request: ConversationCreateRequest):
    logger.debug("create_conversation endpoint started")
    """Create a new conversation session."""
    logger.info("Creating new conversation")
    env_api_key, env_provider, models, env_default_model = load_env_defaults()
    api_key = request.api_key or env_api_key
    provider = request.provider or env_provider
    default_model = request.model or env_default_model or (models[0] if models else "")

    if not api_key:
        raise HTTPException(status_code=400, detail="API key is required")

    session = conversation_manager.create_session(
        provider=provider, api_key=api_key, models=models
    )
    
    if default_model:
        session.set_model(default_model)

    logger.info(f"Created conversation: {session.session_id}")
    return _conversation_state_response(session)


@router.get("/conversations/{conversation_id}/summary", response_model=ConversationSummaryModel)
def get_conversation_summary(conversation_id: str):
    """Get conversation summary."""
    logger.debug(f"get_conversation_summary endpoint started for conversation_id: {conversation_id}")
    
    try:
        session = conversation_manager.get_session(conversation_id)
    except KeyError as exc:
        raise HTTPException(status_code=404, detail=str(exc))

    return _session_summary_model(session)


@router.put("/conversations/{conversation_id}/model", response_model=ConversationCreateResponse)
def update_model(conversation_id: str, request: UpdateModelRequest):
    logger.debug(f"update_model endpoint started for conversation_id: {conversation_id}")
    """Update the AI model for a conversation."""
    
    try:
        session = conversation_manager.get_session(conversation_id)
    except KeyError as exc:
        raise HTTPException(status_code=404, detail=str(exc))

    session.set_model(request.model)
    return _conversation_state_response(session)


    logger.debug(f"update_api_key endpoint started for conversation_id: {conversation_id}")
@router.put("/conversations/{conversation_id}/api-key", response_model=ConversationCreateResponse)
def update_api_key(conversation_id: str, request: UpdateApiKeyRequest):
    """Update the API key for a conversation."""
    
    try:
        session = conversation_manager.get_session(conversation_id)
    except KeyError as exc:
        raise HTTPException(status_code=404, detail=str(exc))

    session.set_api_key(request.api_key)
    return _conversation_state_response(session)
    logger.debug(f"export_conversation endpoint started for conversation_id: {conversation_id}")


@router.get("/conversations/{conversation_id}/export", response_model=ExportConversationResponse)
def export_conversation(conversation_id: str):
    """Export conversation data."""
    
    try:
        session = conversation_manager.get_session(conversation_id)
    except KeyError as exc:
        raise HTTPException(status_code=404, detail=str(exc))

    summary_model = _session_summary_model(session)
    return ExportConversationResponse(summary=summary_model)
    logger.debug("import_conversation endpoint started")


@router.post("/conversations/import", response_model=ConversationCreateResponse)
def import_conversation(request: ImportConversationRequest):
    """Import conversation data."""
    env_api_key, env_provider, models, env_default_model = load_env_defaults()
    api_key = request.api_key or env_api_key
    provider = request.provider or env_provider
    default_model = request.model or env_default_model or (models[0] if models else "")

    if not api_key:
        raise HTTPException(status_code=400, detail="API key is required")

    # Create session and restore data
    session = conversation_manager.create_session(
        provider=provider, api_key=api_key, models=models
    )
    
    if default_model:
        session.set_model(default_model)

    # TODO: Implement actual import logic here
    # This would restore conversation history, files, etc.
    
    logger.info(f"Imported conversation: {session.session_id}")
    return _conversation_state_response(session)
