"""Test to validate agent selection on first chat message."""
import os
import sys
from unittest.mock import MagicMock, patch

# Add the backend directory to the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.services.conversation_service import ConversationSession


def test_agent_prompt_on_first_message():
    """Test that agent prompt is used on the first message."""
    print("Testing agent prompt usage on first message...")
    
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
        
        # Mock the token usage to avoid TypeError
        mock_processor._last_detailed_usage = {
            "total_tokens": 10,
            "input_tokens": 5,
            "output_tokens": 5,
            "cached_tokens": 0
        }
        
        # Create a conversation session
        session = ConversationSession(
            session_id="test-session",
            ai_processor=mock_processor,
            provider="openrouter",
            available_models=["gpt-4"],
            default_model="gpt-4"
        )
        
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
        
        if system_messages:
            system_content = system_messages[0].get("content", "")
            if "Python expert" in system_content:
                print("✅ SUCCESS: Agent prompt was used in system message")
                print(f"System message: {system_content[:200]}...")
                return True
            else:
                print("❌ FAILURE: Agent prompt was NOT used in system message")
                print(f"System message: {system_content[:200]}...")
                return False
        else:
            print("❌ FAILURE: No system message found")
            return False


def test_agent_prompt_on_subsequent_message():
    """Test that agent prompt is used on subsequent messages."""
    print("\nTesting agent prompt usage on subsequent message...")
    
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
        
        # Mock the token usage to avoid TypeError
        mock_processor._last_detailed_usage = {
            "total_tokens": 10,
            "input_tokens": 5,
            "output_tokens": 5,
            "cached_tokens": 0
        }
        
        # Create a conversation session
        session = ConversationSession(
            session_id="test-session-2",
            ai_processor=mock_processor,
            provider="openrouter",
            available_models=["gpt-4"],
            default_model="gpt-4"
        )
        
        # Add a test file and simulate first message to create history
        session.add_file("test.py")
        session.app_state.conversation_history.append(
            {"role": "system", "content": "Default system message"},
            {"role": "user", "content": "First question"},
            {"role": "assistant", "content": "First response"}
        )
        
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
        
        if system_messages:
            system_content = system_messages[0].get("content", "")
            if "JavaScript expert" in system_content:
                print("✅ SUCCESS: Agent prompt updated system message")
                print(f"System message: {system_content[:200]}...")
                return True
            else:
                print("❌ FAILURE: Agent prompt was NOT used to update")
                print(f"System message: {system_content[:200]}...")
                return False
        else:
            print("❌ FAILURE: No system message found")
            return False


if __name__ == "__main__":
    print("=" * 60)
    print("AGENT SELECTION VALIDATION TEST")
    print("=" * 60)
    
    test1_passed = test_agent_prompt_on_first_message()
    test2_passed = test_agent_prompt_on_subsequent_message()
    
    print("\n" + "=" * 60)
    print("TEST RESULTS:")
    print(f"First message test: {'PASSED' if test1_passed else 'FAILED'}")
    print(f"Subsequent message test: {'PASSED' if test2_passed else 'FAILED'}")
    
    if not test1_passed:
        print("\n❌ ISSUE CONFIRMED: Agent prompt not used on first message")
        print("The system uses default system message instead of agent")
    else:
        print("\n✅ Agent selection is working correctly")
    
    print("=" * 60)