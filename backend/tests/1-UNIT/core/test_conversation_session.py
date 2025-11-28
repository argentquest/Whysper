"""Test to verify agent selection fix in ConversationSession."""
import pytest
from app.services.conversation_service import ConversationSession

def test_agent_fix():
    """Test that agent prompt is preserved in system message."""
    
    # Create a mock AI processor
    class MockAIProcessor:
        def __init__(self):
            self.api_key = "test-key"
            self.provider_name = "test"
            self._last_detailed_usage = {
                "total_tokens": 10,
                "input_tokens": 5,
                "output_tokens": 5,
                "cached_tokens": 0
            }
        
        def validate_api_key(self):
            return True
        
        def set_api_key(self, key):
            self.api_key = key
        
        def process_question(self, question, conversation_history, codebase_content, model, max_tokens, temperature, update_callback=None):
            # Check if the system message contains the agent prompt
            if conversation_history and conversation_history[0].get("role") == "system":
                content = conversation_history[0].get("content", "")
                if "Python expert" in content:
                    return "SUCCESS: Agent prompt found"
                else:
                    return f"FAILURE: Agent prompt NOT found in: {content[:100]}..."
            else:
                return "FAILURE: No system message found"
    
    # Create a conversation session with mock processor
    session = ConversationSession(
        session_id="test-session",
        ai_processor=MockAIProcessor(),
        provider="test",
        available_models=["test-model"],
        default_model="test-model"
    )
    
    # Add a file to simulate context
    session.selected_files = ["test.py"]
    
    # Ask a question with an agent prompt
    agent_prompt = "You are a Python expert. {codebase_content}"
    result = session.ask_question(
        question="What is this code about?",
        agent_prompt=agent_prompt
    )
    
    # The return value from ask_question is a dict with 'response', 'rawMarkdown', etc.
    # We returned "SUCCESS: Agent prompt found" from the mock AI processor.
    # So we should check if that string is in result['response'] or result['rawMarkdown']
    
    assert "SUCCESS: Agent prompt found" in result["rawMarkdown"]
