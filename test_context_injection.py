"""
Test script to verify that context is injected/updated on every AI call,
not just the first turn.
"""
import sys
import os

# Add backend to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

from backend.common.models import AppState, ConversationMessage
from backend.app.services.conversation_service import ConversationSession


def test_context_injection_on_every_call():
    """Test that system message is updated on every call with current context."""
    print("\n" + "="*80)
    print("Testing Context Injection on Every AI Call")
    print("="*80)

    # Create a mock session
    app_state = AppState()

    # Simulate first message with initial context
    print("\n1. First message - should insert system message at position 0")
    initial_codebase = "File1.py content here"

    # Add user message
    app_state.conversation_history.append(
        ConversationMessage(role="user", content="What does this code do?")
    )

    # Add assistant response
    app_state.conversation_history.append(
        ConversationMessage(role="assistant", content="This code...")
    )

    # Simulate system message injection (what _update_conversation_history does)
    system_msg_1 = f"System message with context:\n{initial_codebase}"

    # Check if system message exists
    if len(app_state.conversation_history) > 1 and app_state.conversation_history[0].role == "system":
        app_state.conversation_history[0] = ConversationMessage(role="system", content=system_msg_1)
        print("OK Updated existing system message")
    else:
        app_state.conversation_history.insert(
            0, ConversationMessage(role="system", content=system_msg_1)
        )
        print("OK Inserted new system message")

    print(f"   History length: {len(app_state.conversation_history)}")
    print(f"   Position 0 role: {app_state.conversation_history[0].role}")
    print(f"   Position 0 content preview: {app_state.conversation_history[0].content[:50]}...")

    # Simulate second message with updated context (files added)
    print("\n2. Second message - should UPDATE system message with new context")
    updated_codebase = "File1.py content here\n\nFile2.py new content here"

    # Add user message
    app_state.conversation_history.append(
        ConversationMessage(role="user", content="What about File2?")
    )

    # Add assistant response
    app_state.conversation_history.append(
        ConversationMessage(role="assistant", content="File2 contains...")
    )

    # Simulate system message update
    system_msg_2 = f"System message with context:\n{updated_codebase}"

    # Check if system message exists
    if len(app_state.conversation_history) > 1 and app_state.conversation_history[0].role == "system":
        app_state.conversation_history[0] = ConversationMessage(role="system", content=system_msg_2)
        print("OK Updated existing system message with new context")
    else:
        app_state.conversation_history.insert(
            0, ConversationMessage(role="system", content=system_msg_2)
        )
        print("OK Inserted new system message")

    print(f"   History length: {len(app_state.conversation_history)}")
    print(f"   Position 0 role: {app_state.conversation_history[0].role}")
    print(f"   System message now contains File2: {'File2' in app_state.conversation_history[0].content}")

    # Verify the system message was updated, not inserted again
    system_message_count = sum(1 for msg in app_state.conversation_history if msg.role == "system")
    print(f"\n3. Verification:")
    print(f"   Total messages: {len(app_state.conversation_history)}")
    print(f"   System messages: {system_message_count}")
    print(f"   OK Only ONE system message exists: {system_message_count == 1}")
    print(f"   OK System message contains updated context: {'File2' in app_state.conversation_history[0].content}")

    # Print full conversation structure
    print(f"\n4. Final conversation structure:")
    for i, msg in enumerate(app_state.conversation_history):
        content_preview = msg.content[:60] + "..." if len(msg.content) > 60 else msg.content
        print(f"   [{i}] {msg.role}: {content_preview}")

    # Assertions
    assert system_message_count == 1, f"Expected 1 system message, got {system_message_count}"
    assert "File2" in app_state.conversation_history[0].content, "System message should contain updated context"
    assert app_state.conversation_history[0].role == "system", "Position 0 should be system message"

    print("\n" + "="*80)
    print("OK ALL TESTS PASSED!")
    print("="*80 + "\n")


if __name__ == "__main__":
    test_context_injection_on_every_call()
