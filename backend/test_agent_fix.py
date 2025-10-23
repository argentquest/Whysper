"""Simple test to verify agent selection fix."""
import sys
import os

# Add the backend directory to the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.services.conversation_service import ConversationSession
from common.models import ConversationMessage

def test_agent_fix():
    """Test that agent prompt is preserved in system message."""
    print("Testing agent prompt preservation...")
    
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
                    print("✅ SUCCESS: Agent prompt found in system message")
                    return "Test response"
                else:
                    print("❌ FAILURE: Agent prompt NOT found in system message")
                    print(f"System message: {content[:200]}...")
                    return "Test response"
            else:
                print("❌ FAILURE: No system message found")
                return "Test response"
    
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
    
    return result

if __name__ == "__main__":
    print("=" * 60)
    print("AGENT SELECTION FIX TEST")
    print("=" * 60)
    
    test_agent_fix()
    
    print("=" * 60)
    print("Test completed")
    print("=" * 60)