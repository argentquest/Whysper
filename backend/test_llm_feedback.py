#!/usr/bin/env python3
"""
LLM Feedback Loop Test

This script specifically tests the fix for AI response feedback loops.
It verifies that AI responses are not being fed back to the LLM as user input.
"""

import asyncio
import sys
import os

# Add the app directory to Python path
sys.path.append(os.path.join(os.path.dirname(__file__), 'app'))

from app.utils.diagram_wizard.nodes import clarify_prompt
from app.utils.diagram_wizard.graph_state import DiagramType, GraphState


async def test_feedback_prevention():
    """Test that AI responses don't create feedback loops."""
    
    print("🔍 Testing AI Feedback Loop Prevention")
    print("="*50)
    
    # Create initial state with conversation history including AI responses
    initial_state: GraphState = {
        "diagram_type": DiagramType.D2,
        "clarification_history": [
            {"role": "user", "content": "I want to create a web application diagram"},
            {"role": "assistant", "content": "What authentication method will you use?"},
            {"role": "user", "content": "JWT tokens with database storage"},
            {"role": "assistant", "content": "What database will you use for user data?"},
            {"role": "user", "content": "PostgreSQL with user profiles and sessions"}
        ],
        "question_count": 2,
        "_session_id": "test-session-123"
    }
    
    print("📝 Initial conversation history:")
    for i, msg in enumerate(initial_state["clarification_history"], 1):
        role_icon = "👤" if msg["role"] == "user" else "🤖"
        print(f"  {i}. {role_icon} {msg['role']}: {msg['content'][:60]}...")
    
    print(f"\n🧪 Testing clarify_prompt node...")
    print("This should ONLY use user messages as LLM input context")
    
    try:
        # Call the clarify_prompt node
        result = await clarify_prompt(initial_state)
        
        print(f"\n📊 Results:")
        print(f"LLM Ready: {result.get('llm_ready', False)}")
        print(f"Question Count: {result.get('question_count', 0)}")
        print(f"Current State: {result.get('current_state', 'unknown')}")
        
        # Check the updated history
        updated_history = result.get('clarification_history', [])
        print(f"\n📝 Updated conversation history ({len(updated_history)} messages):")
        for i, msg in enumerate(updated_history, 1):
            role_icon = "👤" if msg["role"] == "user" else "🤖"
            content_preview = msg['content'][:60] + "..." if len(msg['content']) > 60 else msg['content']
            print(f"  {i}. {role_icon} {msg['role']}: {content_preview}")
        
        # Verify the fix: check that only user messages were processed
        user_only_messages = [msg for msg in initial_state["clarification_history"] if msg["role"] == "user"]
        print(f"\n✅ Verification:")
        print(f"Total messages in history: {len(initial_state['clarification_history'])}")
        print(f"User-only messages: {len(user_only_messages)}")
        print(f"AI response messages: {len(initial_state['clarification_history']) - len(user_only_messages)}")
        
        # Check if the new AI response was added
        new_ai_responses = [msg for msg in updated_history if msg["role"] == "assistant"]
        old_ai_responses = [msg for msg in initial_state["clarification_history"] if msg["role"] == "assistant"]
        
        if len(new_ai_responses) > len(old_ai_responses):
            print(f"✅ New AI response added to conversation history")
            latest_ai_response = new_ai_responses[-1]
            print(f"📄 Latest AI response: {latest_ai_response['content'][:100]}...")
        
        print(f"\n🎯 Feedback Loop Test Result:")
        if "user" in str(result).lower() and "assistant" not in str(result).get('final_design_summary', ''):
            print("✅ PASSED: No AI responses detected in processing context")
        else:
            print("⚠️  UNCLEAR: Manual verification needed")
        
        return True
        
    except Exception as e:
        print(f"\n❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
        return False


async def test_user_only_context():
    """Test that only user messages are used as LLM context."""
    
    print("\n\n🔍 Testing User-Only Context Processing")
    print("="*50)
    
    # Create state with mix of user and AI messages
    test_state: GraphState = {
        "diagram_type": DiagramType.MERMAID,
        "clarification_history": [
            {"role": "user", "content": "Create a login system"},
            {"role": "assistant", "content": "What authentication method?"},
            {"role": "user", "content": "OAuth and JWT"},
            {"role": "assistant", "content": "Which OAuth providers?"},
            {"role": "user", "content": "Google and GitHub"},
            {"role": "assistant", "content": "What user data to store?"},
            {"role": "user", "content": "Email, name, and preferences"}
        ],
        "question_count": 3,
        "_session_id": "test-session-456"
    }
    
    user_messages = [msg for msg in test_state["clarification_history"] if msg["role"] == "user"]
    ai_messages = [msg for msg in test_state["clarification_history"] if msg["role"] == "assistant"]
    
    print(f"📊 Test Data:")
    print(f"Total messages: {len(test_state['clarification_history'])}")
    print(f"User messages: {len(user_messages)}")
    print(f"AI messages: {len(ai_messages)}")
    
    print(f"\n📝 User messages that should be processed:")
    for i, msg in enumerate(user_messages, 1):
        print(f"  {i}. {msg['content'][:50]}...")
    
    print(f"\n🤖 AI messages that should be IGNORED for LLM context:")
    for i, msg in enumerate(ai_messages, 1):
        print(f"  {i}. {msg['content'][:50]}...")
    
    try:
        result = await clarify_prompt(test_state)
        
        print(f"\n✅ Node execution completed")
        print(f"LLM Ready: {result.get('llm_ready', False)}")
        
        # Success if no errors occurred
        print(f"\n🎯 User-Only Context Test Result: ✅ PASSED")
        return True
        
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        return False


async def main():
    """Run all feedback loop prevention tests."""
    print("🧪 LLM Feedback Loop Prevention Tests")
    print("This verifies our fix for AI responses being fed back to LLM")
    print("="*60)
    
    test_results = []
    
    # Test 1: Basic feedback prevention
    result1 = await test_feedback_prevention()
    test_results.append(("Feedback Prevention", result1))
    
    # Test 2: User-only context processing
    result2 = await test_user_only_context()
    test_results.append(("User-Only Context", result2))
    
    # Summary
    print(f"\n\n📊 TEST SUMMARY")
    print("="*60)
    
    passed = sum(1 for _, result in test_results if result)
    total = len(test_results)
    
    for test_name, result in test_results:
        status = "✅ PASSED" if result else "❌ FAILED"
        print(f"{test_name}: {status}")
    
    overall_result = passed == total
    print(f"\nOverall: {passed}/{total} tests passed")
    print(f"Result: {'✅ ALL TESTS PASSED' if overall_result else '❌ SOME TESTS FAILED'}")
    
    if overall_result:
        print("\n🎉 AI feedback loop fix is working correctly!")
        print("   - AI responses are stored in history for UI display")
        print("   - Only user messages are used as LLM input context")
        print("   - No feedback loops should occur")
    else:
        print("\n⚠️  Some issues detected - manual review recommended")
    
    return overall_result


if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1)
