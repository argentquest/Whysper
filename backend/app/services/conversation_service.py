"""Conversation management service for the web backend.

This module adapts the Tkinter conversation orchestration from the legacy Whysper CLI
for use in a REST environment.  It keeps the business logic (AI processing,
code aggregation, persistent file context, system prompt execution) while
removing UI dependencies so the same functionality can serve the web client.
"""
from __future__ import annotations

import os
import time
import uuid
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Tuple
from common.ai import create_ai_processor
from common.lazy_file_scanner import LazyCodebaseScanner
from common.logger import get_logger
from common.models import AppState, ConversationMessage
from pattern_matcher import pattern_matcher
# from common.system_message_manager import system_message_manager  # Legacy - now using agent prompts
from common.env_manager import env_manager
from security_utils import SecurityUtils
import markdown2

logger = get_logger(__name__)


@dataclass
class ConversationSummary:
    """
    Serializable snapshot of a conversation session.

    Contains all the essential state information needed to persist
    and restore a conversation session between requests.

    Attributes:
        conversation_id: Unique identifier for the conversation session
        selected_model: Currently selected AI model name
        provider: AI provider (openrouter, custom)
        selected_directory: Current working directory path
        selected_files: List of currently selected file paths
        persistent_files: Files that remain loaded across all questions
        question_history: List of all Q&A interactions with metadata
        conversation_history: Full chat history with role/content pairs
    """

    conversation_id: str
    selected_model: str
    provider: str
    selected_directory: str
    selected_files: List[str]
    persistent_files: List[str]
    question_history: List[Dict[str, Any]]
    conversation_history: List[Dict[str, Any]]


@dataclass
class ConversationSession:
    """
    In-memory representation of a user conversation session.

    This class encapsulates all the state and functionality needed to manage
    a single user conversation, including AI processing, file context,
    conversation history, and session configuration.

    Attributes:
        session_id: Unique identifier for this conversation session
        ai_processor: AI provider instance for handling requests
        provider: AI service provider name (openrouter, custom)
        available_models: List of models available for this provider
        default_model: Default model to use for this session
        app_state: Application state containing configuration and data
        codebase_scanner: Lazy scanner for efficient file operations
        selected_directory: Currently selected working directory
        selected_files: Files currently selected for context
        logger: Session-specific logger with context

    The session maintains conversation state between API calls and handles
    all the complex orchestration of AI processing, file context management,
    and conversation persistence.
    """

    session_id: str
    ai_processor: Any
    provider: str
    available_models: List[str]
    default_model: str
    app_state: AppState = field(default_factory=AppState)
    codebase_scanner: LazyCodebaseScanner = field(default_factory=LazyCodebaseScanner)
    selected_directory: str = ""
    selected_files: List[str] = field(default_factory=list)
    logger = get_logger("conversation")

    def __post_init__(self) -> None:
        """
        Initialize conversation session after dataclass creation.

        Sets up the session's logging context, initializes the AI processor
        with the default model, and logs the session creation.

        Args:
            None

        Returns:
            None
        """
        logger.debug(f"Initializing conversation session: {self.session_id}")

        # Set default model in app state
        self.app_state.selected_model = self.default_model
        logger.debug(f"Set default model: {self.default_model}")

        # Set up session-specific logger
        self.logger = get_logger(f"conversation.{self.session_id}")
        self.logger.set_context(component="conversation", operation="init")
        logger.debug(f"Initialized session logger for: {self.session_id}")

        # Log session creation with metadata
        self.logger.info(
            "Created new conversation session",
            extra={
                "session_id": self.session_id,
                "provider": self.provider,
                "model": self.default_model,
            },
        )
        logger.info(f"Conversation session {self.session_id} initialized successfully")

    # ---------------------------------------------------------------------
    # Session setup helpers
    # ---------------------------------------------------------------------

    def set_api_key(self, api_key: str) -> None:
        """
        Update the API key for this conversation session.

        Stores the API key in the session state and propagates it to the
        AI processor for authentication with the provider.

        Args:
            api_key: API key string for the AI provider. Can be empty string
                    to clear the key.

        Returns:
            None
        """
        logger.debug(f"Setting API key for session {self.session_id}")
        self.app_state.api_key = api_key or ""
        self.ai_processor.set_api_key(self.app_state.api_key)
        logger.debug(f"API key updated for session {self.session_id}")

    def set_model(self, model: str) -> None:
        """
        Update the AI model for this conversation session.

        Changes the selected model and adds it to available models if not
        already present. Updates both session state and logging context.

        Args:
            model: Name of the AI model to use (e.g., 'gpt-4', 'claude-3')

        Returns:
            None

        Note:
            If model is empty or None, the method returns without changes.
        """
        if not model:
            logger.debug("Model update skipped - empty model name")
            return

        logger.debug(f"Updating model to '{model}' for session {self.session_id}")

        # Add to available models if not present
        if model not in self.available_models:
            self.available_models.append(model)
            logger.debug(f"Added '{model}' to available models list")

        # Update selected model
        self.app_state.selected_model = model

        # Log the change
        self.logger.info(
            "Model updated",
            extra={"session_id": self.session_id, "model": model},
        )
        logger.info(f"Model changed to '{model}' for session {self.session_id}")

    def set_provider(self, provider: str) -> None:
        """
        Update the AI provider for this conversation session.

        Changes the provider and notifies the AI processor of the change.
        Only updates if the provider is different from the current one.

        Args:
            provider: Name of the AI provider (e.g., 'openrouter', 'custom')

        Returns:
            None
        """
        if provider and provider != self.provider:
            logger.debug(f"Changing provider from '{self.provider}' to '{provider}' for session {self.session_id}")

            self.provider = provider
            self.ai_processor.set_provider(provider)

            self.logger.info(
                "Provider updated",
                extra={"session_id": self.session_id, "provider": provider},
            )
            logger.info(f"Provider changed to '{provider}' for session {self.session_id}")
        else:
            logger.debug(f"Provider update skipped - same or empty provider: '{provider}'")

    def update_available_models(self, models: List[str]) -> None:
        """
        Update the list of available AI models for this session.

        Replaces the current available models list with the provided list.
        Models are used for validation and UI display.

        Args:
            models: List of model names available for the current provider

        Returns:
            None

        Note:
            If models list is empty, the method returns without changes.
        """
        if not models:
            logger.debug("Available models update skipped - empty list")
            return

        logger.debug(f"Updating available models list for session {self.session_id}: {len(models)} models")
        self.available_models = models.copy()
        logger.info(f"Available models updated for session {self.session_id} ({len(models)} models)")
        if self.app_state.selected_model not in models:
            self.app_state.selected_model = models[0]

    # ------------------------------------------------------------------
    # Directory and file handling
    # ------------------------------------------------------------------
    def set_directory(self, directory: str) -> Tuple[bool, str, List[str]]:
        """
        Validate and scan a directory for this conversation session.

        Performs directory validation, scans for files, and updates the session
        state with the new working directory. Resets file selections when
        directory changes.

        Args:
            directory: Path to the directory to validate and scan

        Returns:
            Tuple[bool, str, List[str]]: A tuple containing:
                - success: True if directory was set successfully
                - message: Status message or error description
                - files: List of file paths found in the directory

        Note:
            On success, this method resets selected_files and persistent_files
            since they belong to the previous directory.
        """
        logger.debug(f"Attempting to set directory to: {directory} for session {self.session_id}")

        # Validate the directory using the codebase scanner
        is_valid, error_message = self.codebase_scanner.validate_directory(directory)
        if not is_valid:
            logger.warning(f"Directory validation failed for {directory}: {error_message}")
            return False, error_message, []

        logger.debug(f"Directory validated successfully: {directory}")

        # Update session state
        self.selected_directory = directory
        self.app_state.selected_directory = directory

        # Scan for files
        logger.debug("Scanning directory for files...")
        files = self.codebase_scanner.scan_directory(directory)
        logger.debug(f"Found {len(files)} files in directory")

        # Update codebase files
        self.app_state.codebase_files = files

        # Reset file selections for new directory
        self.selected_files = []
        self.app_state.persistent_selected_files = []

        # Log the successful operation
        self.logger.info(
            "Directory scanned",
            extra={
                "session_id": self.session_id,
                "directory": directory,
                "file_count": len(files),
            },
        )
        logger.info(f"Directory set to '{directory}' with {len(files)} files for session {self.session_id}")

        return True, "Directory scanned successfully", files

    def update_selected_files(
        self,
        selected_files: Optional[List[str]] = None,
        make_persistent: bool = False,
    ) -> None:
        """
        Update the list of selected files for this conversation session.

        Replaces the current file selection with the provided list.
        Optionally marks the files as persistent for inclusion in all
        subsequent questions.

        Args:
            selected_files: List of file paths to select. Defaults to empty list.
            make_persistent: If True, marks these files as persistent for
                           all future questions in this session.

        Returns:
            None
        """
        selected_files = selected_files or []
        logger.debug(f"Updating selected files for session {self.session_id}: {len(selected_files)} files")

        # Preserve order while removing duplicates using dict.fromkeys
        unique_files = list(dict.fromkeys(selected_files))
        logger.debug(f"After deduplication: {len(unique_files)} unique files")

        # Update session selection
        self.selected_files = unique_files

        # Make persistent if requested
        if make_persistent:
            logger.debug("Setting files as persistent")
            self.app_state.set_persistent_files(unique_files)

        # Log the update with metrics
        self.logger.debug(
            "Updated file selection",
            extra={
                "session_id": self.session_id,
                "selected": len(unique_files),
                "persistent": len(self.app_state.get_persistent_files()) if make_persistent else 0,
                "total_persistent": len(self.app_state.get_persistent_files()),
            },
        )
        logger.info(f"Updated file selection for session {self.session_id}: {len(unique_files)} selected files")

    def add_file(self, file_path: str, make_persistent: bool = False) -> None:
        """
        Add a single file to the current selection.

        Performs a security check to ensure the file_path does not traverse
        outside the application's current working directory.

        Adds the specified file to the existing selection. If the file is
        already selected, this method does nothing.

        Args:
            file_path: Path to the file to add to selection
            make_persistent: If True, also adds the file to persistent files

        Returns:
            None
        """
        logger.info(f"🔍 ADDING FILE TO SESSION {self.session_id}: {file_path}")
        
        # Security Check: Prevent Path Traversal
        # Use CODE_PATH as base directory instead of current working directory
        env_vars = env_manager.load_env_file()
        code_path = env_vars.get("CODE_PATH", os.getcwd())
        logger.info(f"📂 Using CODE_PATH: {code_path}")
        logger.info(f"📄 Resolving file path: {file_path}")
        
        safe_path = SecurityUtils.safe_path_resolve(code_path, file_path)
        logger.info(f"🔐 Resolved safe_path: {safe_path}")
        
        if not safe_path:
            logger.error(
                f"❌ PATH RESOLUTION FAILED for {file_path} - file not found or path traversal attempted",
                extra={"session_id": self.session_id, "code_path": code_path, "file_path": file_path}
            )
            return

        if safe_path not in self.selected_files:
            self.selected_files.append(safe_path)
            logger.info(f"✅ FILE ADDED SUCCESSFULLY! Total files: {len(self.selected_files)}")
            logger.info(f"📋 Current selected files: {self.selected_files}")
        else:
            logger.warning(f"⚠️ File already in selection: {safe_path}")

        if make_persistent:
            self.app_state.set_persistent_files(self.selected_files)

        self.logger.debug(
            "File added to selection",
            extra={
                "session_id": self.session_id,
                "file_path": safe_path,
                "selected": len(self.selected_files),
            },
        )

    def clear_files(self) -> None:
        """
        Clear all selected and persistent files for this conversation session.

        Resets the file selection state, removing all currently selected files
        and persistent files. This allows starting fresh with a new file context.

        Args:
            None

        Returns:
            None

        Note:
            This operation is irreversible and affects the conversation's
            file context immediately.
        """
        logger.debug(f"Clearing all files for session {self.session_id}")
        logger.debug(f"Before clear: {len(self.selected_files)} selected, {len(self.app_state.get_persistent_files())} persistent files")

        # Clear selections
        self.selected_files = []
        self.app_state.set_persistent_files([])

        # Log the operation
        self.logger.debug(
            "Cleared selected files",
            extra={"session_id": self.session_id},
        )
        logger.info(f"Cleared all file selections for session {self.session_id}")

    # ------------------------------------------------------------------
    # Conversation operations
    # ------------------------------------------------------------------
    def ask_question(self, question: str, agent_prompt: str = None) -> Dict[str, Any]:
        """
        Process a user question and generate an AI response.

        This is the main method for handling user questions in a conversation.
        It validates input, determines whether codebase context is needed,
        processes the question through the AI provider, and returns formatted
        response data with metadata.

        Args:
            question: The user's question text to process
            agent_prompt: Agent prompt content to use as system message (optional)

        Returns:
            Dict[str, Any]: Response dictionary containing:
                - response: HTML-formatted response for frontend display
                - rawMarkdown: Original markdown response from AI
                - processing_time: Time taken to process the question (seconds)
                - tokens_used: Number of tokens consumed by the AI request
                - question_index: Index of this question in the conversation

        Raises:
            ValueError: If question is empty, API key is invalid, or no files
                       are selected for the first message

        Note:
            First message requires at least one selected file for context.
            Subsequent messages may use persistent file context.
        """
        logger.debug(f"Processing question for session {self.session_id}")

        # Input validation
        if not question.strip():
            logger.error(f"Empty question received for session {self.session_id}")
            raise ValueError("Question cannot be empty")

        if not self.ai_processor.validate_api_key():
            logger.error(f"API key validation failed for session {self.session_id}")
            raise ValueError("API key is not configured")

        # Check if this is the first message in conversation
        is_first_message = len(self.app_state.conversation_history) == 0
        logger.debug(f"Question is {'first' if is_first_message else 'follow-up'} message")

        # First message validation - warn if no file context but allow to proceed
        if is_first_message and not self.selected_files:
            logger.info(f"First question has no file context in session {self.session_id} - proceeding without code context")

        # Track question in session state
        question_status = self.app_state.add_question(question)
        question_index = len(self.app_state.question_history) - 1
        logger.debug(f"Question tracked with index {question_index}")

        # Set logging context and log the operation
        self.logger.set_context(component="conversation", operation="ask_question")
        self.logger.info(
            "Processing question",
            extra={
                "session_id": self.session_id,
                "question_preview": question[:80] + "..." if len(question) > 80 else question,
                "first_message": is_first_message,
                "question_length": len(question),
                "selected_files": len(self.selected_files),
                "persistent_files": len(self.app_state.get_persistent_files()),
            },
        )
        logger.info(f"Started processing question for session {self.session_id}")

        # Start timing the operation
        start_time = time.time()
        logger.debug(".3f")

        # Determine if codebase context is needed
        needs_codebase_context = is_first_message or self._is_tool_command(question)
        logger.info(f"Codebase context needed: {needs_codebase_context} (first_message={is_first_message})")
        # Auto-detect diagram requests and use appropriate agent prompt
        if not agent_prompt:
            agent_prompt = self._detect_diagram_request(question)
            if agent_prompt:
                logger.info(f"🎨 [DIAGRAM DEBUG] Auto-detected diagram request, using agent prompt: {agent_prompt[:50]}...")

        # Track user message in conversation history
        logger.info("Adding user message to conversation history")
        self.app_state.conversation_history.append(
            ConversationMessage(role="user", content=question)
        )

        # Gather codebase content
        logger.info("Gathering codebase content for AI processing")
        codebase_content = self._get_codebase_content(is_first_message, needs_codebase_context)
        logger.debug(f"Codebase content length: {len(codebase_content)} characters")

        # Process question with AI (with automatic D2 validation and retry)
        logger.info("Sending question to AI processor")
        response_text = self._process_with_ai(question, codebase_content)
        logger.info(f"Received AI response: {len(response_text)} characters")

        # Auto-validate and fix D2 diagrams if present
        response_text = self._validate_and_fix_d2_diagrams(response_text, question)
        logger.info(f"After D2 validation/fix: {len(response_text)} characters")

        # DEBUG: Log agent prompt usage
        if agent_prompt:
            logger.info(SecurityUtils.safe_debug_info(f"🎨 [DIAGRAM DEBUG] Using agent prompt for question: {question[:100]}..."))
            logger.info(SecurityUtils.safe_debug_info(f"🎨 [DIAGRAM DEBUG] Agent prompt length: {len(agent_prompt)} characters"))
            logger.info(SecurityUtils.safe_debug_info(f"🎨 [DIAGRAM DEBUG] Agent prompt preview: {agent_prompt[:200]}..."))
        else:
            logger.info(SecurityUtils.safe_debug_info(f"🎨 [DIAGRAM DEBUG] No agent prompt provided for question: {question[:100]}..."))

        # DEBUG: Log AI response for diagram generation
        if "mermaid" in question.lower() or "diagram" in question.lower():
            logger.info(SecurityUtils.safe_debug_info(f"🎨 [DIAGRAM DEBUG] Question contains diagram keywords"))
            logger.info(SecurityUtils.safe_debug_info(f"🎨 [DIAGRAM DEBUG] AI response preview: {response_text[:500]}..."))
            if "```mermaid" in response_text:
                logger.info(SecurityUtils.safe_debug_info(f"🎨 [DIAGRAM DEBUG] AI response contains Mermaid code block"))
            else:
                logger.warning(SecurityUtils.safe_debug_info(f"🎨 [DIAGRAM DEBUG] AI response does NOT contain Mermaid code block"))

        # Calculate timing and resources
        processing_time = time.time() - start_time
        token_usage = self._get_last_token_usage()
        tokens_used = token_usage.get("total_tokens", 0)
        logger.debug(f"Processing completed in {processing_time:.3f}s")

        # Update conversation state
        logger.debug("Updating conversation history and status")
        self._update_conversation_history(response_text, is_first_message, codebase_content, agent_prompt)
        self.app_state.update_question_status(
            question_index,
            "completed",
            response=response_text,
            tokens_used=tokens_used,
            processing_time=processing_time,
            model_used=self.app_state.selected_model,
        )

        # Convert markdown to HTML for frontend
        logger.debug("Converting markdown response to HTML")
        html_response = markdown2.markdown(response_text, extras=['fenced-code-blocks', 'tables', 'codehilite'])

        # Prepare and return response data
        response_data = {
            "response": html_response,
            "rawMarkdown": response_text,
            "processing_time": processing_time,
            "tokens_used": tokens_used,
            "token_usage": token_usage,  # Detailed token information
            "question_index": question_index,
            "model_used": self.app_state.selected_model,
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
        }

        logger.info(f"Question processing completed for session {self.session_id} in {processing_time:.2f}s using {tokens_used} tokens")
        self.logger.info(
            "Question completed",
            extra={
                "session_id": self.session_id,
                "processing_time": processing_time,
                "tokens_used": tokens_used,
                "response_length": len(response_text),
            },
        )

        return response_data

    def run_system_prompt(self, agent_prompt: str = None) -> Dict[str, Any]:
        """
        Execute the active system prompt for initial codebase analysis.

        This method runs the configured system prompt to perform initial
        analysis of the selected codebase files. It's typically called
        before asking the first question to provide context about the
        codebase structure and functionality.

        Returns:
            Dict[str, Any]: Response dictionary containing:
                - response: HTML-formatted system prompt response
                - rawMarkdown: Original markdown response
                - processing_time: Time taken to process (seconds)
                - tokens_used: Number of tokens consumed

        Raises:
            ValueError: If API key is invalid or no files are selected

        Note:
            This is typically the first operation performed in a new
            conversation to establish codebase understanding.
        """
        logger.debug(f"Running system prompt for session {self.session_id}")

        # Validate API key
        if not self.ai_processor.validate_api_key():
            logger.error(f"API key validation failed for system prompt in session {self.session_id}")
            raise ValueError("API key is not configured")

        # System prompt validation - warn if no file context but allow to proceed
        is_first_message = len(self.app_state.conversation_history) == 0
        if is_first_message and not self.selected_files:
            logger.info(f"System prompt has no file context in session {self.session_id} - proceeding without code context")

        # Gather codebase content for analysis
        logger.debug("Gathering codebase content for system prompt analysis")
        codebase_content = self._get_codebase_content(is_first_message=True, needs_codebase_context=True)
        logger.debug(f"System prompt codebase content: {len(codebase_content)} characters")

        # Generate system message with codebase context
        logger.debug("Generating system message with codebase context")
        if agent_prompt:
            system_message = self._format_agent_prompt(agent_prompt, codebase_content)
        else:
            # Default system message for backwards compatibility
            system_message = (
                "🚨 CRITICAL FORMATTING REQUIREMENT: You MUST respond EXCLUSIVELY in pure markdown format. 🚨\n\n"
                "You are a helpful AI assistant that helps with code analysis and development.\n\n"
                "ABSOLUTELY REQUIRED:\n"
                "- Use ONLY markdown syntax for ALL formatting\n"
                "- For headers: Use # ## ### (NOT <h1> <h2> <h3>)\n"
                "- For code blocks: Use ```language syntax (NOT <pre><code>)\n"
                "- For lists: Use - or 1. syntax (NOT <ul><li>)\n"
                "- For emphasis: Use **bold** and *italic* (NOT <strong><em>)\n"
                "- For links: Use [text](url) syntax (NOT <a href>)\n\n"
                "STRICTLY FORBIDDEN:\n"
                "- NO HTML tags whatsoever: no <p>, <div>, <span>, <pre>, <code>, <h1-6>, <ul>, <li>, <strong>, <em>, <a>, etc.\n"
                "- NO HTML entities: no &lt; &gt; &nbsp; etc.\n"
                "- NO HTML attributes or styling\n\n"
                "If you include mermaid diagrams, use this EXACT format:\n"
                "```mermaid\n"
                "graph TD\n"
                "    A --> B\n"
                "```\n\n"
                "VIOLATION OF THIS RULE WILL BREAK THE APPLICATION. Respond in pure markdown only.\n\n"
                f"The user has provided the following codebase:\n\n{codebase_content}"
            )
        logger.debug(f"Generated system message: {len(system_message)} characters")

        # Execute system prompt through AI processor
        logger.debug("Executing system prompt through AI processor")
        start_time = time.time()
        response_text = self.ai_processor.process_question(
            question=system_message,
            conversation_history=[],  # Fresh context for system analysis
            codebase_content="",      # System prompt carries its own context
            model=self.app_state.selected_model,
        )
        processing_time = time.time() - start_time
        token_usage = self._get_last_token_usage()
        tokens_used = token_usage.get("total_tokens", 0)
        logger.debug(f"System prompt completed in {processing_time:.3f}s")

        # Update conversation history with system response
        logger.debug("Updating system prompt conversation history")
        self._update_system_prompt_history(response_text)

        # Convert to HTML and prepare response
        logger.debug("Converting system prompt response to HTML")
        html_response = markdown2.markdown(response_text, extras=['fenced-code-blocks', 'tables', 'codehilite'])

        response_data = {
            "response": html_response,
            "rawMarkdown": response_text,
            "processing_time": processing_time,
            "tokens_used": tokens_used,
            "token_usage": token_usage,
            "model_used": self.app_state.selected_model,
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
        }

        logger.info(f"System prompt completed for session {self.session_id} in {processing_time:.2f}s using {tokens_used} tokens")
        self.logger.info(
            "System prompt executed",
            extra={
                "session_id": self.session_id,
                "processing_time": processing_time,
                "tokens_used": tokens_used,
                "response_length": len(response_text),
            },
        )

        return response_data

    def clear_conversation(self) -> None:
        """
        Clear all conversation history and start fresh.

        This completely resets the conversation state, removing all messages,
        question history, and conversation data. The session configuration
        (model, provider, files) is preserved.

        Args:
            None

        Returns:
            None

        Note:
            This operation is irreversible and affects the entire conversation.
        """
        logger.debug(f"Clearing conversation for session {self.session_id}")
        self.app_state.clear_conversation()
        self.logger.info("Conversation cleared", extra={"session_id": self.session_id})
        logger.info(f"Conversation cleared for session {self.session_id}")

    # ------------------------------------------------------------------
    # Introspection helpers
    # ------------------------------------------------------------------
    def get_summary(self) -> ConversationSummary:
        history = [message.to_dict() for message in self.app_state.conversation_history]
        question_history = [
            {
                "question": q.question,
                "status": q.status,
                "response": q.response,
                "timestamp": q.timestamp,
                "tokens_used": q.tokens_used,
                "processing_time": q.processing_time,
                "model_used": q.model_used,
            }
            for q in self.app_state.question_history
        ]
        return ConversationSummary(
            conversation_id=self.session_id,
            selected_model=self.app_state.selected_model,
            provider=self.provider,
            selected_directory=self.selected_directory,
            selected_files=self.selected_files,
            persistent_files=self.app_state.get_persistent_files(),
            conversation_history=history,
            question_history=question_history,
        )

    # ------------------------------------------------------------------
    # Internal helpers mirroring Tkinter implementation
    # ------------------------------------------------------------------
    def _is_tool_command(self, question: str) -> bool:
        try:
            env_vars = env_manager.load_env_file()
            tool_vars = {key: value for key, value in env_vars.items() if key.startswith("TOOL")}
            return pattern_matcher.is_tool_command(question, tool_vars, threshold=0.5)
        except Exception:
            return False

    def _get_codebase_content(self, is_first_message: bool, needs_codebase_context: bool) -> str:
        logger.info(f"🔄 GETTING CODEBASE CONTENT - first_message: {is_first_message}, needs_context: {needs_codebase_context}")
        logger.info(f"📊 Current selected files count: {len(self.selected_files)}")
        logger.info(f"📋 Selected files: {self.selected_files}")
        
        if not needs_codebase_context:
            logger.info("❌ No codebase context needed, returning empty")
            return ""

        if is_first_message:
            if self.selected_files:
                logger.info(f"🚀 FIRST MESSAGE - Loading {len(self.selected_files)} files")
                self.app_state.set_persistent_files(self.selected_files)
                
                logger.info(f"📖 Calling _load_files with: {self.selected_files}")
                content = self._load_files(self.selected_files)
                logger.info(f"📄 LOADED CONTENT - {len(content)} characters")
                
                if content:
                    logger.info(f"✅ SUCCESS - Content loaded, preview: {content[:200]}...")
                else:
                    logger.error(f"❌ FAILED - No content loaded from files!")
                
                return content
            else:
                logger.warning("⚠️ First message but NO SELECTED FILES")
            return ""

        persistent_files = self.app_state.get_persistent_files()
        if persistent_files:
            return self._load_files(persistent_files)

        if self.selected_files:
            return self._load_files(self.selected_files)

        return ""

    def _load_files(self, files: List[str]) -> str:
        logger.info(f"📚 LOADING FILES - {len(files)} files")
        logger.info(f"📋 Files to load: {files}")
        
        try:
            if len(files) > 50:
                logger.info("🔄 Using lazy loading (>50 files)")
                content = self.codebase_scanner.get_codebase_content_lazy(files)
            else:
                logger.info("🔄 Using regular loading (≤50 files)")
                content = self.codebase_scanner.get_codebase_content(files)
            
            logger.info(f"📄 LOADING RESULT - {len(content)} characters")
            if content:
                logger.info(f"📖 Content preview: {content[:200]}...")
            else:
                logger.error("❌ NO CONTENT RETURNED from codebase scanner!")
            
            return content
        except Exception as e:
            logger.error(f"❌ EXCEPTION in _load_files: {str(e)}")
            raise

    def _process_with_ai(self, question: str, codebase_content: str) -> str:
        conversation_for_api = []
        for message in self.app_state.conversation_history[:-1]:
            if message.role != "system":
                conversation_for_api.append(message.to_dict())

        return self.ai_processor.process_question(
            question=question,
            conversation_history=conversation_for_api,
            codebase_content=codebase_content,
            model=self.app_state.selected_model,
        )

    def _validate_and_fix_d2_diagrams(self, response_text: str, original_question: str, max_retries: int = 2) -> str:
        """
        Automatically validate D2 diagrams in the response and retry with error feedback if invalid.

        Args:
            response_text: The AI's response containing potential D2 diagrams
            original_question: The original user question
            max_retries: Maximum number of retry attempts (default: 2)

        Returns:
            Corrected response text with valid D2 diagrams
        """
        import re
        from app.services.d2_render_service import get_d2_service

        # Check if response contains D2 code blocks
        # Match ```d2 with optional whitespace before newline or content
        d2_pattern = r'```d2\s*\n?(.*?)```'
        d2_matches = re.findall(d2_pattern, response_text, re.DOTALL)

        if not d2_matches:
            logger.debug("No D2 diagrams found in response, skipping validation")
            return response_text

        logger.info(f"🔍 [D2 PROGRESS] Found {len(d2_matches)} D2 diagram(s) - validating syntax...")

        try:
            d2_service = get_d2_service()
            retry_count = 0
            current_response = response_text

            while retry_count < max_retries:
                all_valid = True
                validation_errors = []

                logger.debug(f"Validation attempt {retry_count + 1}/{max_retries}")

                # Validate each D2 diagram
                for i, d2_code in enumerate(re.findall(d2_pattern, current_response, re.DOTALL)):
                    is_valid, error_msg = d2_service.validate_d2_code(d2_code)

                    if not is_valid:
                        all_valid = False
                        validation_errors.append(f"D2 Diagram #{i+1} Error:\n{error_msg}")
                        logger.warning(f"D2 diagram #{i+1} validation failed: {error_msg[:200]}")

                if all_valid:
                    logger.info("✅ [D2 PROGRESS] All D2 diagrams validated successfully!")
                    logger.info("🎨 [D2 PROGRESS] Rendering diagrams to SVG...")

                    # Pre-render all D2 diagrams to SVG to avoid frontend re-extraction corruption
                    current_response = self._pre_render_d2_diagrams(current_response)

                    logger.info("✅ [D2 PROGRESS] D2 diagrams rendered and ready for display!")
                    return current_response

                # If validation failed, send errors back to AI for correction
                retry_count += 1
                logger.info(f"🔧 [D2 PROGRESS] Validation errors found - requesting AI auto-fix (attempt {retry_count}/{max_retries})...")

                error_summary = "\n\n".join(validation_errors)
                correction_prompt = (
                    f"FIX THESE D2 SYNTAX ERRORS:\n\n{error_summary}\n\n"
                    f"RULES:\n"
                    f"- Databases: shape: cylinder\n"
                    f"- Web/Apps: shape: rectangle\n"
                    f"- Users: shape: person\n"
                    f"- Cloud: shape: cloud\n"
                    f"- Strings: Always close quotes\n\n"
                    f"Return ONLY the corrected ```d2 code block. Keep it SIMPLE and COMPLETE."
                )

                # Send correction request to AI
                conversation_for_api = []
                for message in self.app_state.conversation_history[:-1]:
                    if message.role != "system":
                        conversation_for_api.append(message.to_dict())

                corrected_response = self.ai_processor.process_question(
                    question=correction_prompt,
                    conversation_history=conversation_for_api,
                    codebase_content="",
                    model=self.app_state.selected_model,
                )

                logger.info(f"✅ [D2 PROGRESS] Received corrected D2 code ({len(corrected_response)} chars) - re-validating...")

                # Check if response looks truncated (ends abruptly without closing backticks)
                if corrected_response.count('```d2') > corrected_response.count('```\n') and corrected_response.count('```d2') > corrected_response.count('```'):
                    logger.warning(f"⚠️  Corrected response may be TRUNCATED! Model: {self.app_state.selected_model}")
                    logger.warning(f"⚠️  Try switching to a model that doesn't truncate (e.g., qwen/qwen3-coder-30b-a3b-instruct or anthropic/claude-4.5-sonnet)")

                current_response = corrected_response

            # If we exhausted retries, include validation errors in the response
            logger.warning(f"D2 validation failed after {max_retries} retries")

            # Create error report section
            error_report = "\n\n---\n\n"
            error_report += "## ⚠️ D2 Diagram Validation Failed\n\n"
            error_report += f"The D2 diagram could not be validated after {max_retries} auto-fix attempts.\n\n"
            error_report += "**Validation Errors:**\n\n"

            for error in validation_errors:
                error_report += f"```\n{error}\n```\n\n"

            error_report += "**Common fixes:**\n"
            error_report += "- Use `shape: cylinder` for databases\n"
            error_report += "- Use `shape: rectangle` for web/app components\n"
            error_report += "- Use `shape: person` for users\n"
            error_report += "- Use `shape: cloud` for cloud services\n"
            error_report += "- Ensure all strings are properly quoted\n"
            error_report += "- Check for syntax errors in relationships (use `->` or `--`)\n\n"

            error_report += "**D2 Code (Failed Validation):**\n\n"

            # Extract the D2 code that failed
            failed_d2_matches = re.findall(d2_pattern, current_response, re.DOTALL)
            if failed_d2_matches:
                for i, d2_code in enumerate(failed_d2_matches):
                    error_report += f"```d2\n{d2_code}\n```\n\n"

            # Try to pre-render anyway (might partially work)
            logger.warning(f"Attempting pre-render despite validation errors...")
            try:
                current_response = self._pre_render_d2_diagrams(current_response)
                error_report += "*Note: Pre-rendering was attempted but may have failed. Check the output above.*\n\n"
            except Exception as e:
                logger.error(f"Pre-render also failed: {str(e)}")
                error_report += f"*Pre-rendering failed: {str(e)}*\n\n"

            # Append error report to response
            current_response += error_report

            return current_response

        except Exception as e:
            logger.error(f"Error during D2 validation/fix: {str(e)}")
            # Return original response if validation fails
            return response_text

    def _pre_render_d2_diagrams(self, response_text: str) -> str:
        """
        Pre-render validated D2 diagrams to SVG and embed them in the response.
        This prevents frontend re-extraction corruption.

        Args:
            response_text: Response containing validated D2 diagrams

        Returns:
            Response with D2 diagrams replaced by rendered SVG
        """
        import re
        import os
        import hashlib
        from datetime import datetime
        from app.services.d2_render_service import get_d2_service

        # Match ```d2 with optional whitespace before newline or content
        d2_pattern = r'```d2\s*\n?(.*?)```'

        try:
            d2_service = get_d2_service()

            # Create directory for saved SVG files
            svg_dir = os.path.join("backend", "static", "d2_diagrams")
            os.makedirs(svg_dir, exist_ok=True)

            diagram_count = 0

            def render_d2_block(match):
                nonlocal diagram_count
                diagram_count += 1

                d2_code = match.group(1)
                logger.info(f"Pre-rendering D2 diagram #{diagram_count} ({len(d2_code)} chars)")

                # Render to SVG
                success, error_msg, svg_content = d2_service.render_d2_to_svg(d2_code)

                if success and svg_content:
                    # Generate unique filename based on content hash and timestamp
                    content_hash = hashlib.md5(d2_code.encode()).hexdigest()[:8]
                    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                    filename = f"d2_diagram_{timestamp}_{content_hash}.svg"
                    filepath = os.path.join(svg_dir, filename)

                    # Save SVG to file
                    try:
                        with open(filepath, 'w', encoding='utf-8') as f:
                            f.write(svg_content)
                        logger.info(f"Saved D2 diagram to: {filepath}")

                        # Create download URL
                        download_url = f"/api/v1/d2/download/{filename}"
                    except Exception as e:
                        logger.error(f"Failed to save SVG file: {str(e)}")
                        download_url = None

                    # Replace D2 code block with rendered SVG
                    # Keep the original D2 code in a collapsed HTML details section
                    download_link = f'<p style="margin-top: 8px; margin-bottom: 8px;"><a href="{download_url}" download="{filename}" style="display: inline-block; padding: 8px 16px; background-color: #667eea; color: white; text-decoration: none; border-radius: 6px; font-size: 13px; font-weight: 500;">⬇️ Download SVG</a></p>\n' if download_url else ''

                    # Add status badge showing rendering was successful
                    status_badge = (
                        f'<div style="display: inline-flex; align-items: center; gap: 6px; padding: 6px 12px; '
                        f'background: linear-gradient(135deg, #10b981 0%, #059669 100%); '
                        f'border-radius: 6px; margin-bottom: 12px; font-size: 12px; font-weight: 500; color: white;">\n'
                        f'  <span style="font-size: 14px;">✅</span>\n'
                        f'  <span>D2 Diagram Rendered Successfully</span>\n'
                        f'</div>\n'
                    )

                    return (
                        f'<div class="d2-diagram-container" style="margin: 16px 0;">\n'
                        f'{status_badge}'
                        f'  <div class="d2-rendered-diagram">\n'
                        f'    {svg_content}\n'
                        f'  </div>\n'
                        f'{download_link}'
                        f'  <details style="margin-top: 8px;">\n'
                        f'    <summary style="cursor: pointer; padding: 8px 12px; background-color: #f1f5f9; '
                        f'border: 1px solid #cbd5e1; border-radius: 6px; font-size: 13px; font-weight: 500; '
                        f'color: #475569; user-select: none;">📝 View D2 Source Code (click to expand/copy)</summary>\n'
                        f'    <pre style="background-color: #1e293b; color: #e2e8f0; padding: 16px; '
                        f'border-radius: 0 0 6px 6px; border: 1px solid #cbd5e1; border-top: none; '
                        f'overflow-x: auto; font-size: 13px; line-height: 1.2; margin-top: 0;"><code>{d2_code}</code></pre>\n'
                        f'  </details>\n'
                        f'</div>\n'
                    )
                else:
                    logger.warning(f"Failed to pre-render D2: {error_msg}")
                    # Keep original D2 code block
                    return match.group(0)

            # Replace all D2 blocks with rendered versions
            rendered_response = re.sub(d2_pattern, render_d2_block, response_text, flags=re.DOTALL)

            logger.info("D2 diagrams pre-rendered successfully")
            return rendered_response

        except Exception as e:
            logger.error(f"Error pre-rendering D2 diagrams: {str(e)}")
            return response_text

    def _update_conversation_history(
        self, response_text: str, is_first_message: bool, codebase_content: str, agent_prompt: str = None
    ) -> None:
        self.app_state.conversation_history.append(
            ConversationMessage(role="assistant", content=response_text)
        )
        if is_first_message:
            # Use agent prompt if provided, otherwise fall back to default
            if agent_prompt:
                system_msg = self._format_agent_prompt(agent_prompt, codebase_content)
            else:
                # Default system message for backwards compatibility
                system_msg = (
                    "🚨 CRITICAL FORMATTING REQUIREMENT: You MUST respond EXCLUSIVELY in pure markdown format. 🚨\n\n"
                    "You are a helpful AI assistant that helps with code analysis and development.\n\n"
                    "ABSOLUTELY REQUIRED:\n"
                    "- Use ONLY markdown syntax for ALL formatting\n"
                    "- For headers: Use # ## ### (NOT <h1> <h2> <h3>)\n"
                    "- For code blocks: Use ```language syntax (NOT <pre><code>)\n"
                    "- For lists: Use - or 1. syntax (NOT <ul><li>)\n"
                    "- For emphasis: Use **bold** and *italic* (NOT <strong><em>)\n"
                    "- For links: Use [text](url) syntax (NOT <a href>)\n\n"
                    "STRICTLY FORBIDDEN:\n"
                    "- NO HTML tags whatsoever: no <p>, <div>, <span>, <pre>, <code>, <h1-6>, <ul>, <li>, <strong>, <em>, <a>, etc.\n"
                    "- NO HTML entities: no &lt; &gt; &nbsp; etc.\n"
                    "- NO HTML attributes or styling\n\n"
                    "If you include mermaid diagrams, use this EXACT format:\n"
                    "```mermaid\n"
                    "graph TD\n"
                    "    A --> B\n"
                    "```\n\n"
                    "VIOLATION OF THIS RULE WILL BREAK THE APPLICATION. Respond in pure markdown only.\n\n"
                    f"The user has provided the following codebase:\n\n{codebase_content}"
                )
            self.app_state.conversation_history.insert(
                0, ConversationMessage(role="system", content=system_msg)
            )

    def _format_agent_prompt(self, agent_prompt: str, codebase_content: str) -> str:
        """
        Format agent prompt with codebase content.
        
        Args:
            agent_prompt: The agent prompt content
            codebase_content: The codebase content to include
            
        Returns:
            Formatted system message
        """
        # Add strong markdown-only format instruction to agent prompt
        markdown_instruction = (
            "🚨 CRITICAL FORMATTING REQUIREMENT: You MUST respond EXCLUSIVELY in pure markdown format. 🚨\n\n"
            "ABSOLUTELY REQUIRED:\n"
            "- Use ONLY markdown syntax for ALL formatting\n"
            "- For headers: Use # ## ### (NOT <h1> <h2> <h3>)\n"
            "- For code blocks: Use ```language syntax (NOT <pre><code>)\n"
            "- For lists: Use - or 1. syntax (NOT <ul><li>)\n"
            "- For emphasis: Use **bold** and *italic* (NOT <strong><em>)\n"
            "- For links: Use [text](url) syntax (NOT <a href>)\n\n"
            "STRICTLY FORBIDDEN:\n"
            "- NO HTML tags whatsoever: no <p>, <div>, <span>, <pre>, <code>, <h1-6>, <ul>, <li>, <strong>, <em>, <a>, etc.\n"
            "- NO HTML entities: no &lt; &gt; &nbsp; etc.\n"
            "- NO HTML attributes or styling\n\n"
            "If you include mermaid diagrams, use this EXACT format:\n"
            "```mermaid\n"
            "graph TD\n"
            "    A --> B\n"
            "```\n\n"
            "VIOLATION OF THIS RULE WILL BREAK THE APPLICATION. Respond in pure markdown only.\n\n"
        )
        
        # Check if agent prompt has a placeholder for codebase content
        if "{codebase_content}" in agent_prompt:
            formatted_prompt = agent_prompt.replace("{codebase_content}", codebase_content)
        else:
            # If no placeholder, append codebase content
            formatted_prompt = f"{agent_prompt}\n\nThe user has provided the following codebase:\n\n{codebase_content}"
            
        return markdown_instruction + formatted_prompt

    def _update_system_prompt_history(self, response_text: str) -> None:
        self.app_state.conversation_history.append(
            ConversationMessage(role="user", content="[System Prompt Executed]")
        )
        self.app_state.conversation_history.append(
            ConversationMessage(role="assistant", content=response_text)
        )

    def _get_last_token_usage(self) -> dict:
        """
        Retrieves detailed token usage information from the last AI request.

        This method introspects the underlying AI provider object to safely
        extract detailed token information from the most recent operation.

        Returns:
            dict: Token usage information containing:
                - total_tokens: Total tokens used
                - input_tokens: Input/prompt tokens
                - output_tokens: Output/completion tokens
                - cached_tokens: Cached tokens (if available)
        """
        try:
            provider = getattr(self.ai_processor, "_provider", None)
            if provider and hasattr(provider, "_last_detailed_usage"):
                return provider._last_detailed_usage
            elif provider and hasattr(provider, "_last_token_usage"):
                # Fallback to simple token count
                total = int(provider._last_token_usage)
                return {
                    "total_tokens": total,
                    "input_tokens": 0,
                    "output_tokens": 0,
                    "cached_tokens": 0
                }
        except Exception:
            pass
        return {
            "total_tokens": 0,
            "input_tokens": 0,
            "output_tokens": 0,
            "cached_tokens": 0
        }

    def _detect_diagram_request(self, question: str) -> Optional[str]:
        """
        Detect if the user is requesting a diagram and return the appropriate agent prompt.

        Args:
            question: The user's question

        Returns:
            Agent prompt content if diagram detected, None otherwise
        """
        question_lower = question.lower()

        # Check for Mermaid diagram requests
        if ("mermaid" in question_lower and
            ("diagram" in question_lower or "generate" in question_lower or "create" in question_lower)):
            try:
                from .settings_service import settings_service
                mermaid_prompt = settings_service.get_agent_prompt_content("mermaid-architecture.md")
                if mermaid_prompt:
                    logger.info("🎨 [DIAGRAM DEBUG] Detected Mermaid diagram request, loading mermaid-architecture.md prompt")
                    return mermaid_prompt
            except Exception as e:
                logger.error(f"Failed to load mermaid prompt: {e}")

        # Check for D2 diagram requests
        if ("d2" in question_lower and
            ("diagram" in question_lower or "generate" in question_lower or "create" in question_lower)):
            try:
                from .settings_service import settings_service
                d2_prompt = settings_service.get_agent_prompt_content("d2-architecture.md")
                if d2_prompt:
                    logger.info("🎨 [DIAGRAM DEBUG] Detected D2 diagram request, loading d2-architecture.md prompt")
                    return d2_prompt
            except Exception as e:
                logger.error(f"Failed to load D2 prompt: {e}")

        return None


class ConversationManager:
    """Registry for active conversation sessions."""

    def __init__(self) -> None:
        self._sessions: Dict[str, ConversationSession] = {}
        self._logger = get_logger("conversation_manager")

    def create_session(
        self,
        api_key: str,
        provider: str,
        models: List[str],
        default_model: Optional[str] = None,
        session_id: Optional[str] = None,
    ) -> ConversationSession:
        logger.info(
            "Creating conversation session",
            extra={"provider": provider, "requested_id": session_id},
        )
        session_id = session_id or str(uuid.uuid4())
        if session_id in self._sessions:
            self._logger.info(
                "Replacing existing session",
                extra={"session_id": session_id},
            )
            self._sessions.pop(session_id, None)
        ai_processor = create_ai_processor(api_key=api_key, provider=provider)
        default_model = default_model or (models[0] if models else "")
        session = ConversationSession(
            session_id=session_id,
            ai_processor=ai_processor,
            provider=provider,
            available_models=models,
            default_model=default_model,
        )
        session.set_api_key(api_key)
        self._sessions[session_id] = session
        logger.info("Session created", extra={"session_id": session_id})
        return session

    def get_session(self, session_id: str) -> ConversationSession:
        if session_id not in self._sessions:
            raise KeyError(f"Conversation {session_id} not found")
        return self._sessions[session_id]

    def list_sessions(self) -> List[ConversationSession]:
        """Return all active conversation sessions."""
        return list(self._sessions.values())

    def drop_session(self, session_id: str) -> None:
        if session_id in self._sessions:
            self._logger.info("Conversation session removed", extra={"session_id": session_id})
            del self._sessions[session_id]

conversation_manager = ConversationManager()
