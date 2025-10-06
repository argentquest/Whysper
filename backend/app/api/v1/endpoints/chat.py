"""
Chat and conversation management endpoints for Whysper Web2 Backend.

This module provides the core chat functionality of the Whysper 
application,
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

# FastAPI framework imports
from fastapi import APIRouter, HTTPException

# Common library imports for conversation management
from app.core.config import load_env_defaults              # Environment configuration
from app.services.conversation_service import conversation_manager
from app.services.history_service import history_service   # History logging service

# Pydantic schema imports for request/response validation
from schemas import (
    AskQuestionRequest,        # Chat message request schema
    AskQuestionResponse,       # Chat message response schema
    ChatRequest,               # Frontend chat request schema
    ChatResponse,              # Frontend chat response schema
    ConversationCreateRequest,  # New conversation request schema
    ConversationCreateResponse,  # Conversation state response schema
    ConversationSummaryModel,  # Conversation summary schema
    ExportConversationResponse,  # Export data response schema
    ImportConversationRequest,  # Import data request schema
    UpdateApiKeyRequest,       # API key update request schema
    UpdateModelRequest,        # Model update request schema
)

# Third-party imports
import uuid                    # For generating unique message IDs
import markdown2               # Markdown to HTML conversion for frontend

# Logging setup
from common.logger import get_logger

# Shared utilities
from app.utils import session_summary_model

# Initialize logger for this module
logger = get_logger(__name__)

# Create FastAPI router for chat endpoints
# This router will be included in the main API with /chat prefix
router = APIRouter()






def _conversation_state_response(session) -> ConversationCreateResponse:
    """
    Create a standardized conversation state response for new sessions.

    Generates the response payload that includes session metadata, available
    models, and configuration information for newly created conversations.

    Args:
        session: ConversationSession object for the new conversation

    Returns:
        ConversationCreateResponse: Structured response with session state
    """
    logger.debug(f"Creating conversation state response for session: {session.session_id}")
    summary_model = session_summary_model(session)
    response = ConversationCreateResponse(
        conversationId=session.session_id,
        provider=session.provider,
        model=summary_model.selected_model,
        availableModels=session.available_models,
        summary=summary_model,
    )
    logger.debug(f"Conversation state response created: provider={response.provider}, model={response.model}")
    return response


@router.post("/test")
def test_endpoint():
    """Simple test endpoint"""
    return {"status": "ok", "message": "Test endpoint working"}

@router.post("/test-new")
def test_new_endpoint():
    """New test endpoint to verify server reload"""
    return {"status": "ok", "message": "New endpoint working", "timestamp": "2025-09-30"}

@router.get("/debug-env")
def debug_env():
    """Debug environment loading"""
    from common.env_manager import env_manager
    env_data = env_manager.load_env_file()
    return {
        "api_key_found": "API_KEY" in env_data,
        "api_key_length": len(env_data.get('API_KEY', '')),
        "api_key_prefix": env_data.get('API_KEY', '')[:10],
        "keys": list(env_data.keys())[:10]  # First 10 keys
    }

@router.post("/")
def send_chat_message(request: dict):
    """Send chat message to AI and return response"""
    logger.info("🚀 CHAT ENDPOINT CALLED")
    logger.info(f"📨 Raw request: {request}")
    
    try:
        # Extract request data
        message = request.get('message', '')
        conversation_id = request.get('conversationId', 'default')
        context_files = request.get('contextFiles', [])
        settings = request.get('settings', {})
        
        logger.info(f"💬 Message: {message}")
        logger.info(f"🆔 Conversation ID: {conversation_id}")
        logger.info(f"📁 Context Files: {context_files}")
        logger.info(f"⚙️ Settings: {settings}")
        
        if not message.strip():
            raise HTTPException(status_code=400, detail="Message cannot be empty")

        # Load configuration from .env file
        env_config = load_env_defaults()
        api_key = env_config.get('api_key', '')
        provider = env_config.get('provider', 'openrouter')
        model = settings.get('model') or env_config.get('default_model', 'google/gemini-2.5-flash-preview-09-2025')
        models_list = env_config.get('models', [])

        if not api_key:
            raise HTTPException(status_code=400, detail="API key not configured in .env file")
        
        # Get or create conversation session
        try:
            session = conversation_manager.get_session(conversation_id)
            logger.debug(f"Retrieved existing session: {conversation_id}")
        except KeyError:
            # Create new session if it doesn't exist
            logger.info(f"Creating new conversation session: {conversation_id}")
            
            session = conversation_manager.create_session(
                api_key=api_key,
                provider=provider,
                models=models_list,
                default_model=model,
                session_id=conversation_id
            )
        
        # Add context files IMMEDIATELY after session creation/retrieval
        if context_files:
            logger.info(f"📁 ADDING {len(context_files)} CONTEXT FILES TO SESSION {conversation_id}")
            logger.info(f"📋 Files to add: {context_files}")
            
            for i, file_path in enumerate(context_files, 1):
                logger.info(f"📄 Adding file {i}/{len(context_files)}: {file_path}")
                try:
                    session.add_file(file_path)
                    logger.info(f"✅ Successfully added file: {file_path}")
                except Exception as e:
                    logger.error(f"❌ Failed to add file {file_path}: {str(e)}")
                    
            logger.info(f"📊 SESSION SUMMARY - Total selected files: {len(session.selected_files)}")
            logger.info(f"📋 Final selected files list: {session.selected_files}")
        else:
            logger.warning("⚠️ NO CONTEXT FILES PROVIDED - proceeding without file context")
        
        # Update session configuration if provided
        if settings.get('api_key'):
            session.set_api_key(settings['api_key'])
        if settings.get('provider'):
            session.set_provider(settings['provider'])
        if settings.get('model'):
            session.set_model(settings['model'])
        
        # Send message to AI and get response
        logger.info(f"Processing AI request for conversation {conversation_id}")
        
        # Extract agent prompt from settings if provided
        agent_prompt = settings.get('systemPrompt') if settings else None
        if agent_prompt:
            logger.debug(f"Using agent prompt: {agent_prompt[:100]}...")
        
        result = session.ask_question(message, agent_prompt=agent_prompt)
        
        # Convert result to frontend-compatible format
        import time
        
        # Clean response content by removing system reminders
        response_content = result.get("response", "")
        if "<system-reminder>" in response_content:
            # Remove system reminder blocks
            import re
            response_content = re.sub(r'<system-reminder>.*?</system-reminder>', '', response_content, flags=re.DOTALL)
            logger.debug("Removed system-reminder content from AI response")
        
        # Extract detailed token usage information
        token_usage = result.get("token_usage", {})
        
        response_message = {
            "id": f"msg_{int(time.time())}_{uuid.uuid4().hex[:8]}",
            "role": "assistant",
            "content": response_content,
            "timestamp": result.get("timestamp", time.strftime("%Y-%m-%d %H:%M:%S")),
            "metadata": {
                "model": result.get("modelUsed", model),
                "provider": provider,
                "tokens": result.get("tokensUsed", 0),
                "inputTokens": token_usage.get("input_tokens", 0),
                "outputTokens": token_usage.get("output_tokens", 0),
                "cachedTokens": token_usage.get("cached_tokens", 0),
                "elapsedTime": result.get("processing_time", 0.0)
            }
        }
        
        response = {
            "message": response_message,
            "conversationId": conversation_id,
            "debug": "FROM_MAIN_CHAT_ENDPOINT"  # Temporary debug marker
        }
        
        # Log conversation history to file
        try:
            # Create user message structure
            user_message = {
                "id": f"msg_{int(time.time())}_{uuid.uuid4().hex[:8]}_user",
                "role": "user", 
                "content": message,
                "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
                "metadata": {
                    "context_files": context_files,
                    "settings": settings
                }
            }
            
            # Load existing conversation history to accumulate messages
            existing_history = history_service.load_conversation_history(conversation_id)
            if existing_history and "messages" in existing_history:
                # Append new messages to existing ones
                all_messages = existing_history["messages"] + [user_message, response_message]
            else:
                # First messages in conversation
                all_messages = [user_message, response_message]
            
            # Save complete conversation history with metadata
            history_metadata = {
                "provider": provider,
                "model": model,
                "session_id": conversation_id,
                "context_files_count": len(context_files),
                "has_agent_prompt": bool(agent_prompt)
            }
            
            success = history_service.save_conversation_history(
                conversation_id=conversation_id,
                messages=all_messages,
                metadata=history_metadata
            )
            
            if success:
                logger.debug(f"✅ Conversation history saved for {conversation_id} ({len(all_messages)} total messages)")
            else:
                logger.warning(f"⚠️ Failed to save conversation history for {conversation_id}")
                
        except Exception as hist_error:
            logger.error(f"❌ Error saving conversation history: {hist_error}")
        
        logger.info(f"AI response generated successfully for conversation {conversation_id}")
        return response
        
    except HTTPException:
        # Re-raise HTTP exceptions as-is
        raise
    except Exception as exc:
        logger.error(f"Error processing chat message: {exc}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(exc)}")


@router.post("/conversations", response_model=ConversationCreateResponse)
def create_conversation(request: ConversationCreateRequest):
    logger.debug("create_conversation endpoint started")
    """Create a new conversation session."""
    logger.info("Creating new conversation")
    env_config = load_env_defaults()
    env_api_key = env_config.get('API_KEY', '')
    env_provider = env_config.get('PROVIDER', 'openrouter')
    models = env_config.get('models', [])
    env_default_model = env_config.get('DEFAULT_MODEL', '')
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

    return session_summary_model(session)


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


@router.put("/conversations/{conversation_id}/api-key", response_model=ConversationCreateResponse)
def update_api_key(conversation_id: str, request: UpdateApiKeyRequest):
    """Update the API key for a conversation."""
    logger.debug(f"update_api_key endpoint started for conversation_id: {conversation_id}")
    
    try:
        session = conversation_manager.get_session(conversation_id)
    except KeyError as exc:
        raise HTTPException(status_code=404, detail=str(exc))

    session.set_api_key(request.api_key)
    return _conversation_state_response(session)


@router.get("/conversations/{conversation_id}/export", response_model=ExportConversationResponse)
def export_conversation(conversation_id: str):
    """Export conversation data."""
    logger.debug(f"export_conversation endpoint started for conversation_id: {conversation_id}")
    
    try:
        session = conversation_manager.get_session(conversation_id)
    except KeyError as exc:
        raise HTTPException(status_code=404, detail=str(exc))

    summary_model = session_summary_model(session)
    return ExportConversationResponse(summary=summary_model)


@router.post("/conversations/import", response_model=ConversationCreateResponse)
def import_conversation(request: ImportConversationRequest):
    """Import conversation data."""
    logger.debug("import_conversation endpoint started")
    env_config = load_env_defaults()
    env_api_key = env_config.get('API_KEY', '')
    env_provider = env_config.get('PROVIDER', 'openrouter')
    models = env_config.get('models', [])
    env_default_model = env_config.get('DEFAULT_MODEL', '')
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


@router.get("/conversations/history")
def list_conversation_histories():
    """List all conversation history files."""
    logger.debug("list_conversation_histories endpoint called")
    try:
        histories = history_service.list_conversation_histories()
        return {
            "success": True,
            "data": histories,
            "count": len(histories)
        }
    except Exception as e:
        logger.error(f"Failed to list conversation histories: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to list histories: {str(e)}")


@router.get("/conversations/{conversation_id}/history")
def get_conversation_history(conversation_id: str):
    """Get conversation history for a specific conversation."""
    logger.debug(f"get_conversation_history endpoint called for: {conversation_id}")
    try:
        history = history_service.load_conversation_history(conversation_id)
        if history:
            return {
                "success": True,
                "data": history
            }
        else:
            return {
                "success": False,
                "error": "Conversation history not found"
            }
    except Exception as e:
        logger.error(f"Failed to get conversation history for {conversation_id}: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get history: {str(e)}")


@router.delete("/conversations/{conversation_id}/history")
def delete_conversation_history(conversation_id: str):
    """Delete conversation history for a specific conversation."""
    logger.debug(f"delete_conversation_history endpoint called for: {conversation_id}")
    try:
        success = history_service.delete_conversation_history(conversation_id)
        if success:
            return {
                "success": True,
                "message": "Conversation history deleted successfully"
            }
        else:
            return {
                "success": False,
                "error": "Conversation history not found"
            }
    except Exception as e:
        logger.error(f"Failed to delete conversation history for {conversation_id}: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to delete history: {str(e)}")
