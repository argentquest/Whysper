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
import logging
import uuid  # For generating unique message IDs

# Third-party imports
import markdown2  # Markdown to HTML conversion for frontend
from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse
import json
import asyncio

# Local imports
from app.core.config import load_env_defaults  # Load env defaults
from app.services.conversation_service import conversation_manager  # Conversation manager
from app.services.history_service import history_service  # History service
from app.utils import session_summary_model
from common.logger import get_logger
from common.log_broadcaster import log_broadcaster  # Log broadcasting
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

# Import validation with error handling
try:
    # Validate core service imports
    logger_temp = logging.getLogger(__name__)
    logger_temp.debug("Core service imports loaded successfully")
except Exception as e:
    logging.getLogger(__name__).error(f"Import validation failed: {e}")
    raise

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
    logger.debug(
        f"Creating conversation state response for session: {session.session_id}"
    )
    summary_model = session_summary_model(session)
    response = ConversationCreateResponse(
        conversationId=session.session_id,
        provider=session.provider,
        model=summary_model.selected_model,
        availableModels=session.available_models,
        summary=summary_model,
    )
    logger.debug(
        f"Conversation state response created: provider={response.provider}, model={response.model}"
    )
    return response


@router.post("/test")
def test_endpoint():
    """Simple test endpoint"""
    return {"status": "ok", "message": "Test endpoint working"}


@router.post("/test-new")
def test_new_endpoint():
    """New test endpoint to verify server reload"""
    return {
        "status": "ok",
        "message": "New endpoint working",
        "timestamp": "2025-09-30",
    }


@router.get("/debug-env")
def debug_env():
    """Debug environment loading"""
    from common.env_manager import env_manager

    env_data = env_manager.load_env_file()
    return {
        "api_key_found": "API_KEY" in env_data,
        "api_key_length": len(env_data.get("API_KEY", "")),
        "api_key_prefix": env_data.get("API_KEY", "")[:10],
        "keys": list(env_data.keys())[:10],  # First 10 keys
    }


@router.get("/logs/stream")
async def stream_logs(session_id: str = None):
    """
    Stream real-time INFO-level logs via Server-Sent Events (SSE)

    This endpoint broadcasts logger.info() calls to connected clients,
    filtered by session/conversation ID for privacy.

    Args:
        session_id: Optional session/conversation ID to filter logs.
                   If provided, only logs from this session are sent.
                   If omitted, all logs are sent (admin mode).

    Frontend can display these in a status bar for real-time progress updates.
    Logs are automatically truncated to 100 characters.
    """
    logger.info(f"📡 New log stream client connected (session: {session_id or 'ALL'})")

    async def log_event_generator():
        """Generator that yields log events as SSE"""
        # Create queue for this client
        client_queue = asyncio.Queue(maxsize=50)

        try:
            # Register client with broadcaster (with session filtering)
            log_broadcaster.add_client(client_queue, session_id=session_id)

            # Send initial connection event
            yield f"event: connected\ndata: {json.dumps({'message': 'Log stream connected'})}\n\n"

            # Stream logs as they arrive
            while True:
                try:
                    # Wait for next log event (with timeout to send keepalive)
                    log_event = await asyncio.wait_for(client_queue.get(), timeout=15.0)

                    # Send log event
                    yield f"event: log\ndata: {json.dumps(log_event)}\n\n"

                except asyncio.TimeoutError:
                    # Send keepalive comment to prevent connection timeout
                    yield ": keepalive\n\n"

        except asyncio.CancelledError:
            logger.info(f"📡 Log stream client disconnected (cancelled, session: {session_id or 'ALL'})")
        except Exception as e:
            logger.error(f"📡 Log stream error (session: {session_id or 'ALL'}): {str(e)}")
        finally:
            # Unregister client
            log_broadcaster.remove_client(client_queue)

    return StreamingResponse(
        log_event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        }
    )


@router.post("/stream")
async def send_chat_message_stream(request: dict):
    """
    Send chat message to AI and stream progress updates via Server-Sent Events (SSE)

    This endpoint provides real-time progress updates during D2 diagram rendering,
    validation, and AI processing. Frontend receives events as they happen.

    SSE Event Types:
    - progress: Progress updates (validation, rendering, etc.)
    - error: Error messages
    - complete: Final response with full content
    """
    logger.info("🚀 SSE CHAT ENDPOINT CALLED")
    logger.info(f"📨 Raw request: {request}")

    async def event_generator():
        """Generator function that yields SSE events"""
        try:
            # Extract request data
            message = request.get("message", "")
            conversation_id = request.get("conversationId", "default")
            context_files = request.get("contextFiles", [])
            settings = request.get("settings", {})

            # Send initial progress event
            yield f"event: progress\ndata: {json.dumps({'stage': 'initializing', 'message': 'Starting AI processing...'})}\n\n"
            await asyncio.sleep(0.1)  # Small delay to ensure client receives

            if not message.strip():
                yield f"event: error\ndata: {json.dumps({'error': 'Message cannot be empty'})}\n\n"
                return

            # Load configuration
            env_config = load_env_defaults()
            api_key = env_config.get("api_key", "")
            provider = env_config.get("provider", "openrouter")
            model = settings.get("model") or env_config.get("default_model", "google/gemini-2.5-flash-preview-09-2025")
            models_list = env_config.get("models", [])

            if not api_key:
                yield f"event: error\ndata: {json.dumps({'error': 'API key not configured'})}\n\n"
                return

            # Get or create session
            try:
                session = conversation_manager.get_session(conversation_id)
                yield f"event: progress\ndata: {json.dumps({'stage': 'session', 'message': 'Retrieved existing session'})}\n\n"
            except KeyError:
                yield f"event: progress\ndata: {json.dumps({'stage': 'session', 'message': 'Creating new session...'})}\n\n"
                session = conversation_manager.create_session(
                    api_key=api_key,
                    provider=provider,
                    models=models_list,
                    default_model=model,
                    session_id=conversation_id,
                )

            # Add context files
            if context_files:
                yield f"event: progress\ndata: {json.dumps({'stage': 'files', 'message': f'Adding {len(context_files)} context files...'})}\n\n"
                for file_path in context_files:
                    session.add_file(file_path)

            # Update session configuration
            if settings.get("api_key"):
                session.set_api_key(settings["api_key"])
            if settings.get("provider"):
                session.set_provider(settings["provider"])
            if settings.get("model"):
                session.set_model(settings["model"])

            # Send to AI
            yield f"event: progress\ndata: {json.dumps({'stage': 'ai_processing', 'message': 'Sending request to AI...'})}\n\n"

            agent_prompt = settings.get("systemPrompt") if settings else None

            # Create a progress callback for the session
            progress_events = []

            def progress_callback(stage: str, message: str):
                """Callback to capture progress events from conversation service"""
                progress_events.append({'stage': stage, 'message': message})

            # Attach callback to session (we'll need to modify ConversationSession to support this)
            # For now, process the question normally
            result = session.ask_question(message, agent_prompt=agent_prompt)

            # Send any D2-related progress events
            if "d2" in message.lower() or "diagram" in message.lower():
                yield f"event: progress\ndata: {json.dumps({'stage': 'd2_validation', 'message': 'Validating D2 diagram syntax...'})}\n\n"
                await asyncio.sleep(0.1)
                yield f"event: progress\ndata: {json.dumps({'stage': 'd2_rendering', 'message': 'Rendering diagram to SVG...'})}\n\n"
                await asyncio.sleep(0.1)

            # Clean response
            response_content = result.get("response", "")
            if "<system-reminder>" in response_content:
                import re
                response_content = re.sub(r"<system-reminder>.*?</system-reminder>", "", response_content, flags=re.DOTALL)

            # Extract token usage
            token_usage = result.get("token_usage", {}) or {}
            total_tokens = result.get("tokens_used") or result.get("tokensUsed") or token_usage.get("total_tokens", 0)
            input_tokens = token_usage.get("input_tokens", 0)
            output_tokens = token_usage.get("output_tokens", 0)
            cached_tokens = token_usage.get("cached_tokens", 0)

            import time
            response_message = {
                "id": f"msg_{int(time.time())}_{uuid.uuid4().hex[:8]}",
                "role": "assistant",
                "content": response_content,
                "timestamp": result.get("timestamp", time.strftime("%Y-%m-%d %H:%M:%S")),
                "metadata": {
                    "model": result.get("model_used") or result.get("modelUsed") or model,
                    "provider": provider,
                    "tokens": total_tokens,
                    "inputTokens": input_tokens,
                    "outputTokens": output_tokens,
                    "cachedTokens": cached_tokens,
                    "elapsedTime": result.get("processing_time", 0.0),
                },
            }

            response_data = {
                "message": response_message,
                "conversationId": conversation_id,
            }

            # Save history
            try:
                user_message = {
                    "id": f"msg_{int(time.time())}_{uuid.uuid4().hex[:8]}_user",
                    "role": "user",
                    "content": message,
                    "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
                }

                history_service.save_conversation(
                    conversation_id=conversation_id,
                    messages=[user_message, response_message],
                )
            except Exception as e:
                logger.error(f"Failed to save conversation history: {str(e)}")

            # Send final complete event
            yield f"event: complete\ndata: {json.dumps(response_data)}\n\n"

        except Exception as e:
            error_msg = str(e)
            logger.error(f"SSE streaming error: {error_msg}", exc_info=True)
            yield f"event: error\ndata: {json.dumps({'error': error_msg})}\n\n"

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",  # Disable nginx buffering
        }
    )


@router.post("/")
def send_chat_message(request: dict):
    """Send chat message to AI and return response (legacy non-streaming endpoint)"""
    logger.info("🚀 CHAT ENDPOINT CALLED")
    logger.info(f"📨 Raw request: {request}")

    try:
        # Extract request data
        message = request.get("message", "")
        conversation_id = request.get("conversationId", "default")
        context_files = request.get("contextFiles", [])
        settings = request.get("settings", {})

        logger.info(f"💬 Message: {message}", extra={'session_id': conversation_id})
        logger.info(f"🆔 Conversation ID: {conversation_id}", extra={'session_id': conversation_id})
        logger.info(f"📁 Context Files: {context_files}", extra={'session_id': conversation_id})
        logger.info(f"⚙️ Settings: {settings}", extra={'session_id': conversation_id})

        if not message.strip():
            raise HTTPException(status_code=400, detail="Message cannot be empty")

        # Load configuration from .env file
        env_config = load_env_defaults()
        api_key = env_config.get("api_key", "")
        provider = env_config.get("provider", "openrouter")
        model = settings.get("model") or env_config.get(
            "default_model", "google/gemini-2.5-flash-preview-09-2025"
        )
        models_list = env_config.get("models", [])

        if not api_key:
            raise HTTPException(
                status_code=400, detail="API key not configured in .env file"
            )

        # Get or create conversation session
        try:
            session = conversation_manager.get_session(conversation_id)
            logger.debug(f"Retrieved existing session: {conversation_id}")
        except KeyError:
            # Create new session if it doesn't exist
            logger.info(f"Creating new conversation session: {conversation_id}", extra={'session_id': conversation_id})

            access_key = settings.get("access_key")
            if not access_key or access_key != env_config.get("access_key"):
                raise HTTPException(status_code=401, detail="Invalid access key")

            session = conversation_manager.create_session(
                api_key=api_key,
                provider=provider,
                models=models_list,
                default_model=model,
                session_id=conversation_id,
                access_key=access_key,
            )

        # Add context files IMMEDIATELY after session creation/retrieval
        if context_files:
            logger.info(
                f"📁 ADDING {len(context_files)} CONTEXT FILES TO SESSION {conversation_id}",
                extra={'session_id': conversation_id}
            )
            logger.info(f"📋 Files to add: {context_files}", extra={'session_id': conversation_id})

            for i, file_path in enumerate(context_files, 1):
                logger.info(f"📄 Adding file {i}/{len(context_files)}: {file_path}", extra={'session_id': conversation_id})
                try:
                    session.add_file(file_path)
                    logger.info(f"✅ Successfully added file: {file_path}", extra={'session_id': conversation_id})
                except Exception as e:
                    logger.error(f"❌ Failed to add file {file_path}: {str(e)}")

            logger.info(
                f"📊 SESSION SUMMARY - Total selected files: {len(session.selected_files)}",
                extra={'session_id': conversation_id}
            )
            logger.info(f"📋 Final selected files list: {session.selected_files}", extra={'session_id': conversation_id})
        else:
            logger.warning(
                "⚠️ NO CONTEXT FILES PROVIDED - proceeding without file context"
            )

        # Update session configuration if provided
        if settings.get("api_key"):
            session.set_api_key(settings["api_key"])
        if settings.get("provider"):
            session.set_provider(settings["provider"])
        if settings.get("model"):
            session.set_model(settings["model"])
        if settings.get("maxTokens"):
            session.app_state.max_tokens = settings["maxTokens"]
        if settings.get("temperature"):
            session.app_state.temperature = settings["temperature"]

        # Send message to AI and get response
        logger.info(f"Processing AI request for conversation {conversation_id}", extra={'session_id': conversation_id})

        # Extract agent prompt from settings if provided
        agent_prompt = settings.get("systemPrompt") if settings else None
        if agent_prompt:
            logger.debug(f"Using agent prompt: {agent_prompt[:100]}...")

        result = session.ask_question(message, agent_prompt=agent_prompt, context_files=context_files)

        # Convert result to frontend-compatible format
        import time

        # Clean response content by removing system reminders
        response_content = result.get("response", "")
        if "<system-reminder>" in response_content:
            # Remove system reminder blocks
            import re

            response_content = re.sub(
                r"<system-reminder>.*?</system-reminder>",
                "",
                response_content,
                flags=re.DOTALL,
            )
            logger.debug("Removed system-reminder content from AI response")

        # Extract detailed token usage information
        token_usage = result.get("token_usage", {}) or {}
        total_tokens = (
            result.get("tokens_used")
            or result.get("tokensUsed")
            or token_usage.get("total_tokens", 0)
        )
        input_tokens = token_usage.get("input_tokens", 0)
        output_tokens = token_usage.get("output_tokens", 0)
        cached_tokens = token_usage.get("cached_tokens", 0)

        response_message = {
            "id": f"msg_{int(time.time())}_{uuid.uuid4().hex[:8]}",
            "role": "assistant",
            "content": response_content,
            "timestamp": result.get("timestamp", time.strftime("%Y-%m-%d %H:%M:%S")),
            "metadata": {
                "model": result.get("model_used") or result.get("modelUsed") or model,
                "provider": provider,
                "tokens": total_tokens,
                "inputTokens": input_tokens,
                "outputTokens": output_tokens,
                "cachedTokens": cached_tokens,
                "elapsedTime": result.get("processing_time", 0.0),
            },
        }

        response = {
            "message": response_message,
            "conversationId": conversation_id,
            "debug": "FROM_MAIN_CHAT_ENDPOINT",  # Temporary debug marker
        }

        # Log conversation history to file
        try:
            # Create user message structure
            user_message = {
                "id": f"msg_{int(time.time())}_{uuid.uuid4().hex[:8]}_user",
                "role": "user",
                "content": message,
                "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
                "metadata": {"context_files": context_files, "settings": settings},
            }

            # Load existing conversation history to accumulate messages
            existing_history = history_service.load_conversation_history(
                conversation_id
            )
            if existing_history and "messages" in existing_history:
                # Append new messages to existing ones
                all_messages = existing_history["messages"] + [
                    user_message,
                    response_message,
                ]
            else:
                # First messages in conversation
                all_messages = [user_message, response_message]

            # Save complete conversation history with metadata
            history_metadata = {
                "provider": provider,
                "model": model,
                "session_id": conversation_id,
                "context_files_count": len(context_files),
                "has_agent_prompt": bool(agent_prompt),
            }

            success = history_service.save_conversation_history(
                conversation_id=conversation_id,
                messages=all_messages,
                metadata=history_metadata,
            )

            if success:
                logger.debug(
                    f"✅ Conversation history saved for {conversation_id} ({len(all_messages)} total messages)"
                )
            else:
                logger.warning(
                    f"⚠️ Failed to save conversation history for {conversation_id}"
                )

        except Exception as hist_error:
            logger.error(f"❌ Error saving conversation history: {hist_error}")

        logger.info(
            f"AI response generated successfully for conversation {conversation_id}",
            extra={'session_id': conversation_id}
        )
        return response

    except HTTPException:
        # Re-raise HTTP exceptions as-is
        raise
    except Exception as exc:
        logger.error(f"Error processing chat message: {exc}")
        raise HTTPException(
            status_code=500, detail=f"Internal server error: {str(exc)}"
        )


@router.post("/conversations", response_model=ConversationCreateResponse)
def create_conversation(request: ConversationCreateRequest):
    logger.debug("create_conversation endpoint started")
    """Create a new conversation session."""
    logger.info("Creating new conversation")
    env_config = load_env_defaults()
    env_api_key = env_config.get("API_KEY", "")
    env_provider = env_config.get("PROVIDER", "openrouter")
    models = env_config.get("models", [])
    env_default_model = env_config.get("DEFAULT_MODEL", "")
    api_key = request.api_key or env_api_key
    provider = request.provider or env_provider
    default_model = request.model or env_default_model or (models[0] if models else "")

    access_key = request.access_key

    if not access_key or access_key != env_config.get("access_key"):
        raise HTTPException(status_code=401, detail="Invalid access key")

    if not api_key:
        raise HTTPException(status_code=400, detail="API key is required")

    session = conversation_manager.create_session(
        provider=provider, api_key=api_key, models=models, access_key=access_key
    )

    if default_model:
        session.set_model(default_model)

    logger.info(f"Created conversation: {session.session_id}")
    return _conversation_state_response(session)


@router.get(
    "/conversations/{conversation_id}/summary", response_model=ConversationSummaryModel
)
def get_conversation_summary(conversation_id: str):
    """Get conversation summary."""
    logger.debug(
        f"get_conversation_summary endpoint started for conversation_id: {conversation_id}"
    )

    try:
        session = conversation_manager.get_session(conversation_id)
    except KeyError as exc:
        raise HTTPException(status_code=404, detail=str(exc))

    return session_summary_model(session)


@router.put(
    "/conversations/{conversation_id}/model", response_model=ConversationCreateResponse
)
def update_model(conversation_id: str, request: UpdateModelRequest):
    logger.debug(
        f"update_model endpoint started for conversation_id: {conversation_id}"
    )
    """Update the AI model for a conversation."""

    try:
        session = conversation_manager.get_session(conversation_id)
    except KeyError as exc:
        raise HTTPException(status_code=404, detail=str(exc))

    session.set_model(request.model)
    return _conversation_state_response(session)


@router.put(
    "/conversations/{conversation_id}/api-key",
    response_model=ConversationCreateResponse,
)
def update_api_key(conversation_id: str, request: UpdateApiKeyRequest):
    """Update the API key for a conversation."""
    logger.debug(
        f"update_api_key endpoint started for conversation_id: {conversation_id}"
    )

    try:
        session = conversation_manager.get_session(conversation_id)
    except KeyError as exc:
        raise HTTPException(status_code=404, detail=str(exc))

    session.set_api_key(request.api_key)
    return _conversation_state_response(session)


@router.get(
    "/conversations/{conversation_id}/export", response_model=ExportConversationResponse
)
def export_conversation(conversation_id: str):
    """Export conversation data."""
    logger.debug(
        f"export_conversation endpoint started for conversation_id: {conversation_id}"
    )

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
    env_api_key = env_config.get("API_KEY", "")
    env_provider = env_config.get("PROVIDER", "openrouter")
    models = env_config.get("models", [])
    env_default_model = env_config.get("DEFAULT_MODEL", "")
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
        return {"success": True, "data": histories, "count": len(histories)}
    except Exception as e:
        logger.error(f"Failed to list conversation histories: {e}")
        raise HTTPException(
            status_code=500, detail=f"Failed to list histories: {str(e)}"
        )


@router.get("/conversations/{conversation_id}/history")
def get_conversation_history(conversation_id: str):
    """Get conversation history for a specific conversation."""
    logger.debug(f"get_conversation_history endpoint called for: {conversation_id}")
    try:
        history = history_service.load_conversation_history(conversation_id)
        if history:
            return {"success": True, "data": history}
        else:
            return {"success": False, "error": "Conversation history not found"}
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
                "message": "Conversation history deleted successfully",
            }
        else:
            return {"success": False, "error": "Conversation history not found"}
    except Exception as e:
        logger.error(
            f"Failed to delete conversation history for {conversation_id}: {e}"
        )
        raise HTTPException(
            status_code=500, detail=f"Failed to delete history: {str(e)}"
        )


@router.post("/conversations/{conversation_id}/clear")
def clear_conversation(conversation_id: str):
    """Clear conversation history for a specific conversation."""
    logger.debug(f"clear_conversation endpoint called for: {conversation_id}")
    try:
        session = conversation_manager.get_session(conversation_id)
        if session:
            # Clear the conversation history in the session
            session.clear_conversation()
            logger.info(f"Conversation cleared for session: {conversation_id}")
            return {
                "success": True,
                "message": "Conversation cleared successfully",
                "conversationId": conversation_id
            }
        else:
            logger.warning(f"Conversation session not found: {conversation_id}")
            return {"success": False, "error": "Conversation not found"}
    except KeyError:
        logger.warning(f"Conversation session not found: {conversation_id}")
        return {"success": False, "error": "Conversation not found"}
    except Exception as e:
        logger.error(
            f"Failed to clear conversation for {conversation_id}: {e}"
        )
        raise HTTPException(
            status_code=500, detail=f"Failed to clear conversation: {str(e)}"
        )


@router.get("/conversations/{conversation_id}/files")
def get_conversation_files(conversation_id: str):
    """Get the list of context files selected for a conversation session."""
    logger.debug(f"get_conversation_files endpoint called for: {conversation_id}")
    try:
        session = conversation_manager.get_session(conversation_id)
        if session:
            files = session.selected_files
            logger.info(f"Retrieved {len(files)} context files for session: {conversation_id}")
            return {
                "success": True,
                "conversationId": conversation_id,
                "files": files,
                "count": len(files)
            }
        else:
            logger.warning(f"Conversation session not found: {conversation_id}")
            return {"success": False, "error": "Conversation not found", "files": [], "count": 0}
    except KeyError:
        logger.warning(f"Conversation session not found: {conversation_id}")
        return {"success": False, "error": "Conversation not found", "files": [], "count": 0}
    except Exception as e:
        logger.error(
            f"Failed to get conversation files for {conversation_id}: {e}"
        )
        raise HTTPException(
            status_code=500, detail=f"Failed to get conversation files: {str(e)}"
        )
