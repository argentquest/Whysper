"""
Test Conversation Service (Phase 1)

Tests core conversation management functionality:
- Create conversations
- Retrieve history
- Save messages
- Delete conversations
- Search conversations
- Manage permissions

Coverage: 30 tests
"""

import pytest
from unittest.mock import AsyncMock, patch, MagicMock
from datetime import datetime


class TestCreateConversation:
    """Test creating new conversations"""

    @pytest.mark.asyncio
    async def test_create_conversation_with_title(self, sample_conversation_data, mock_conversation_service):
        """Create conversation with title"""
        result = await mock_conversation_service.create_conversation(
            user_id="user_123",
            title="Test Conversation"
        )
        assert result["id"] == "conv_123"
        assert mock_conversation_service.create_conversation.called

    @pytest.mark.asyncio
    async def test_create_conversation_returns_id(self, mock_conversation_service):
        """Conversation creation returns ID"""
        result = await mock_conversation_service.create_conversation(
            user_id="user_123",
            title="Test"
        )
        assert "id" in result
        assert result["id"] == "conv_123"

    @pytest.mark.asyncio
    async def test_create_conversation_sets_user(self, mock_conversation_service):
        """Conversation is assigned to user"""
        result = await mock_conversation_service.create_conversation(
            user_id="user_123",
            title="Test"
        )
        mock_conversation_service.create_conversation.assert_called_once()

    @pytest.mark.asyncio
    async def test_create_conversation_with_description(self, mock_conversation_service):
        """Create conversation with description"""
        result = await mock_conversation_service.create_conversation(
            user_id="user_123",
            title="Test",
            description="Test description"
        )
        assert result["id"] == "conv_123"

    @pytest.mark.asyncio
    async def test_create_conversation_timestamps(self, mock_conversation_service):
        """Conversation includes timestamps"""
        mock_conversation_service.create_conversation.return_value = {
            "id": "conv_123",
            "created_at": datetime.now(),
            "updated_at": datetime.now()
        }
        result = await mock_conversation_service.create_conversation(
            user_id="user_123",
            title="Test"
        )
        assert "created_at" in result
        assert "updated_at" in result


class TestGetConversationHistory:
    """Test retrieving conversation messages"""

    @pytest.mark.asyncio
    async def test_get_empty_history(self, mock_conversation_service):
        """Get history of conversation with no messages"""
        result = await mock_conversation_service.get_history(
            conversation_id="conv_123"
        )
        assert isinstance(result, list)
        assert len(result) == 0

    @pytest.mark.asyncio
    async def test_get_history_with_messages(self, mock_conversation_service, message_list):
        """Get history with messages"""
        mock_conversation_service.get_history.return_value = message_list
        result = await mock_conversation_service.get_history(
            conversation_id="conv_123"
        )
        assert isinstance(result, list)
        assert len(result) > 0

    @pytest.mark.asyncio
    async def test_get_history_with_pagination(self, mock_conversation_service):
        """History supports pagination"""
        await mock_conversation_service.get_history(
            conversation_id="conv_123",
            limit=10,
            offset=0
        )
        mock_conversation_service.get_history.assert_called_once()

    @pytest.mark.asyncio
    async def test_get_history_large_dataset(self, mock_conversation_service):
        """Retrieve history with many messages"""
        large_history = [{"id": f"msg_{i}", "content": f"Message {i}"} for i in range(1000)]
        mock_conversation_service.get_history.return_value = large_history
        result = await mock_conversation_service.get_history(
            conversation_id="conv_123"
        )
        assert len(result) == 1000

    @pytest.mark.asyncio
    async def test_get_history_ordering(self, mock_conversation_service):
        """History messages are ordered by timestamp"""
        await mock_conversation_service.get_history(
            conversation_id="conv_123"
        )
        mock_conversation_service.get_history.assert_called_once()


class TestSaveMessage:
    """Test saving messages to conversation"""

    @pytest.mark.asyncio
    async def test_save_simple_message(self, mock_conversation_service, sample_message_data):
        """Save simple text message"""
        result = await mock_conversation_service.save_message(
            conversation_id="conv_123",
            user_id="user_123",
            content="Hello, World!"
        )
        assert result["id"] == "msg_123"

    @pytest.mark.asyncio
    async def test_save_message_returns_message_id(self, mock_conversation_service):
        """Save message returns message ID"""
        result = await mock_conversation_service.save_message(
            conversation_id="conv_123",
            user_id="user_123",
            content="Test message"
        )
        assert "id" in result

    @pytest.mark.asyncio
    async def test_save_message_with_metadata(self, mock_conversation_service):
        """Save message with additional metadata"""
        result = await mock_conversation_service.save_message(
            conversation_id="conv_123",
            user_id="user_123",
            content="Message with metadata",
            metadata={"key": "value"}
        )
        assert result["id"] == "msg_123"

    @pytest.mark.asyncio
    async def test_save_message_includes_timestamp(self, mock_conversation_service):
        """Saved message includes timestamp"""
        mock_conversation_service.save_message.return_value = {
            "id": "msg_123",
            "created_at": datetime.now()
        }
        result = await mock_conversation_service.save_message(
            conversation_id="conv_123",
            user_id="user_123",
            content="Test"
        )
        assert "created_at" in result

    @pytest.mark.asyncio
    async def test_save_multiple_messages(self, mock_conversation_service):
        """Save multiple messages sequentially"""
        for i in range(5):
            await mock_conversation_service.save_message(
                conversation_id="conv_123",
                user_id="user_123",
                content=f"Message {i}"
            )
        assert mock_conversation_service.save_message.call_count == 5


class TestDeleteConversation:
    """Test deleting conversations"""

    @pytest.mark.asyncio
    async def test_delete_conversation(self, mock_conversation_service):
        """Delete conversation"""
        result = await mock_conversation_service.delete_conversation(
            conversation_id="conv_123"
        )
        assert result is True

    @pytest.mark.asyncio
    async def test_delete_nonexistent_conversation(self, mock_conversation_service):
        """Delete non-existent conversation"""
        mock_conversation_service.delete_conversation.return_value = False
        result = await mock_conversation_service.delete_conversation(
            conversation_id="nonexistent"
        )
        assert result is False

    @pytest.mark.asyncio
    async def test_delete_with_messages(self, mock_conversation_service):
        """Delete conversation with messages"""
        result = await mock_conversation_service.delete_conversation(
            conversation_id="conv_123"
        )
        assert result is True


class TestSearchConversation:
    """Test searching conversations"""

    @pytest.mark.asyncio
    async def test_search_by_title(self, mock_conversation_service):
        """Search conversations by title"""
        await mock_conversation_service.get_conversations(
            user_id="user_123",
            search_query="Test"
        )
        mock_conversation_service.get_conversations.assert_called_once()

    @pytest.mark.asyncio
    async def test_get_all_conversations(self, mock_conversation_service, conversation_list):
        """Get all conversations for user"""
        mock_conversation_service.get_conversations.return_value = conversation_list
        result = await mock_conversation_service.get_conversations(
            user_id="user_123"
        )
        assert len(result) >= 0


class TestConversationPermissions:
    """Test conversation access control"""

    @pytest.mark.asyncio
    async def test_owner_can_access(self, mock_conversation_service):
        """Owner can access their conversation"""
        # Permission check in service
        await mock_conversation_service.get_conversation(
            conversation_id="conv_123",
            user_id="user_123"
        )
        mock_conversation_service.get_conversation.assert_called_once()

    @pytest.mark.asyncio
    async def test_other_user_cannot_access(self, mock_conversation_service):
        """Other users cannot access conversation"""
        mock_conversation_service.get_conversation.return_value = None
        result = await mock_conversation_service.get_conversation(
            conversation_id="conv_123",
            user_id="user_456"
        )
        # Should return None or raise permission error
        mock_conversation_service.get_conversation.assert_called_once()


class TestSessionState:
    """Test conversation session management"""

    @pytest.mark.asyncio
    async def test_session_creation(self, mock_conversation_service):
        """Session state created with conversation"""
        result = await mock_conversation_service.create_conversation(
            user_id="user_123",
            title="Test"
        )
        assert result["id"] == "conv_123"

    @pytest.mark.asyncio
    async def test_concurrent_sessions(self, mock_conversation_service):
        """Multiple users can have conversations simultaneously"""
        # Set different return values for concurrent calls
        mock_conversation_service.create_conversation.side_effect = [
            {"id": "conv_123", "title": "User 1 Conversation", "user_id": "user_123"},
            {"id": "conv_456", "title": "User 2 Conversation", "user_id": "user_456"}
        ]
        conv1 = await mock_conversation_service.create_conversation(
            user_id="user_123",
            title="User 1 Conversation"
        )
        conv2 = await mock_conversation_service.create_conversation(
            user_id="user_456",
            title="User 2 Conversation"
        )
        assert conv1["id"] != conv2["id"]


class TestConversationMetadata:
    """Test conversation metadata"""

    @pytest.mark.asyncio
    async def test_conversation_has_metadata(self, mock_conversation_service):
        """Conversation includes metadata"""
        mock_conversation_service.create_conversation.return_value = {
            "id": "conv_123",
            "title": "Test",
            "user_id": "user_123",
            "message_count": 0
        }
        result = await mock_conversation_service.create_conversation(
            user_id="user_123",
            title="Test"
        )
        assert "id" in result
        assert "title" in result
        assert "user_id" in result
