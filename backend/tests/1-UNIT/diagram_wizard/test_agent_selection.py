"""Test to validate agent selection on first chat message."""
import pytest
from unittest.mock import MagicMock, patch
from app.services.conversation_service import ConversationSession
from common.models import ConversationMessage

def test_agent_prompt_on_first_message():
    """Test that agent prompt is used on the first message."""
    
    # Create a mock AI processor
    with patch('common.ai.create_ai_processor') as mock_create:
        mock_processor = MagicMock()
        mock_create.return_value = mock_processor
        
        # Mock the process_question method to capture the system message
        captured_messages = []

        def capture_process_question(
            question, conversation_history, codebase_content, model,
            max_tokens, temperature, update_callback=None
        ):
            # conversation_history is a list of dicts here because _process_with_ai converts objects to dicts
            captured_messages.extend(conversation_history)
            return "Test response"
        
        mock_processor.process_question.side_effect = capture_process_question
        
        # Properly mock the token usage
        # The code likely accesses processor._provider._last_detailed_usage.get()
        # So we need to ensure the chain exists and returns an int

        mock_provider = MagicMock()
        mock_processor._provider = mock_provider
        mock_provider._last_detailed_usage.get.return_value = 10

        # Explicitly mock _last_token_usage as property returning int
        type(mock_processor)._last_token_usage = 10
        
        # Create a conversation session
        session = ConversationSession(
            session_id="test-session",
            ai_processor=mock_processor,
            provider="openrouter",
            available_models=["gpt-4"],
            default_model="gpt-4"
        )
        
        # Mock add_file to avoid filesystem issues
        with patch.object(session, 'add_file') as mock_add_file:
            # Add a test file
            session.add_file("test.py")

            # Define a test agent prompt
            test_agent_prompt = "You are a Python expert. {codebase_content}"

            # Ask a question with the agent prompt (simulating first message)
            session.ask_question(
                question="What is this code about?",
                agent_prompt=test_agent_prompt
            )
        
        # Check if the agent prompt was used in the system message
        system_messages = [
            msg for msg in captured_messages if msg.get("role") == "system"
        ]
        
        assert system_messages, "No system message found"
        system_content = system_messages[0].get("content", "")
        assert "Python expert" in system_content, f"Agent prompt NOT found in system message: {system_content[:200]}..."

def test_agent_prompt_on_subsequent_message():
    """Test that agent prompt is used on subsequent messages."""
    
    # Create a mock AI processor
    with patch('common.ai.create_ai_processor') as mock_create:
        mock_processor = MagicMock()
        mock_create.return_value = mock_processor
        
        # Mock the process_question method to capture the system message
        captured_messages = []

        def capture_process_question(
            question, conversation_history, codebase_content, model,
            max_tokens, temperature, update_callback=None
        ):
            captured_messages.extend(conversation_history)
            return "Test response"
        
        mock_processor.process_question.side_effect = capture_process_question
        
        # Properly mock the token usage
        mock_provider = MagicMock()
        mock_processor._provider = mock_provider
        mock_provider._last_detailed_usage.get.return_value = 10

        type(mock_processor)._last_token_usage = 10
        
        # Create a conversation session
        session = ConversationSession(
            session_id="test-session-2",
            ai_processor=mock_processor,
            provider="openrouter",
            available_models=["gpt-4"],
            default_model="gpt-4"
        )
        
        # Mock add_file
        with patch.object(session, 'add_file'):
            session.add_file("test.py")

            # Initialize with history using objects!
            session.app_state.conversation_history = [
                ConversationMessage(role="system", content="Default system message"),
                ConversationMessage(role="user", content="First question"),
                ConversationMessage(role="assistant", content="First response")
            ]

            # Define a test agent prompt
            test_agent_prompt = "You are a JavaScript expert. {codebase_content}"

            # Ask a question with the agent prompt (subsequent message)
            session.ask_question(
                question="What about this code?",
                agent_prompt=test_agent_prompt
            )
        
        # Check if the agent prompt was used to update the system message
        system_messages = [
            msg for msg in captured_messages if msg.get("role") == "system"
        ]
        
        assert system_messages, "No system message found"
        system_content = system_messages[0].get("content", "")
        assert "JavaScript expert" in system_content, f"Agent prompt NOT found in updated system message: {system_content[:200]}..."
