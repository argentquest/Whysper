from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock
import os
import pytest
from app.main import app
from app.api.v1.endpoints.auth import VerifyAccessKeyRequest

client = TestClient(app)

class TestAuthEndpoint:
    """Tests for authentication endpoints"""

    def test_verify_access_key_valid(self):
        """Test verifying a valid access key"""
        with patch.dict(os.environ, {"ACCESS_KEY": "valid_key"}):
            response = client.post(
                "/api/v1/auth/verify",
                json={"access_key": "valid_key"}
            )
            assert response.status_code == 200
            data = response.json()
            assert data["success"] is True
            assert data["auth_disabled"] is False

    def test_verify_access_key_invalid(self):
        """Test verifying an invalid access key"""
        with patch.dict(os.environ, {"ACCESS_KEY": "valid_key"}):
            response = client.post(
                "/api/v1/auth/verify",
                json={"access_key": "wrong_key"}
            )
            assert response.status_code == 401
            assert response.json()["detail"] == "Invalid access key."

    def test_verify_access_key_disabled(self):
        """Test verification when auth is disabled (no ACCESS_KEY set)"""
        with patch.dict(os.environ, {"ACCESS_KEY": ""}):
            response = client.post(
                "/api/v1/auth/verify",
                json={"access_key": "any_key"}
            )
            assert response.status_code == 200
            data = response.json()
            assert data["success"] is True
            assert data["auth_disabled"] is True

    def test_check_auth_required(self):
        """Test checking if auth is required"""
        with patch.dict(os.environ, {"ACCESS_KEY": "valid_key"}):
            response = client.get("/api/v1/auth/check")
            assert response.status_code == 200
            data = response.json()
            assert data["auth_required"] is True
            assert data["auth_disabled"] is False

    def test_check_auth_not_required(self):
        """Test checking if auth is NOT required"""
        with patch.dict(os.environ, {"ACCESS_KEY": ""}):
            response = client.get("/api/v1/auth/check")
            assert response.status_code == 200
            data = response.json()
            assert data["auth_required"] is False
            assert data["auth_disabled"] is True


class MockSession:
    """Mock conversation session to avoid Pydantic validation issues with MagicMock"""
    def __init__(self):
        self.session_id = "test_id"
        self.provider = "openrouter"
        self.selected_directory = "/tmp"
        self.available_models = ["model1"]
        self.selected_files = []

        # Mock app_state
        self.app_state = MagicMock()
        self.app_state.selected_model = "model1"
        self.app_state.question_history = []
        self.app_state.conversation_history = []
        self.app_state.get_persistent_files.return_value = []

        # Mock methods
        self.set_model = MagicMock()
        self.set_api_key = MagicMock()
        self.set_provider = MagicMock()
        self.clear_conversation = MagicMock()
        self.add_file = MagicMock()
        self.ask_question = MagicMock()

    def get_summary(self):
        """Return self or summary mock, simpler to just return a dict compatible object"""
        # In the real code, get_summary returns a ConversationSummary object
        # which has attributes.
        summary = MagicMock()
        summary.selected_model = "model1"
        summary.conversation_id = self.session_id
        summary.provider = self.provider
        summary.selected_directory = self.selected_directory
        summary.selected_files = self.selected_files
        summary.persistent_files = []
        summary.question_history = []
        summary.conversation_history = []
        return summary


class TestChatEndpoint:
    """Tests for chat endpoints"""

    @pytest.fixture
    def mock_conversation_manager(self):
        with patch("app.api.v1.endpoints.chat.conversation_manager") as mock:
            yield mock

    @pytest.fixture
    def mock_env_config(self):
        with patch("app.api.v1.endpoints.chat.load_env_defaults") as mock:
            mock.return_value = {
                "api_key": "test_api_key",
                "provider": "openrouter",
                "models": ["model1", "model2"],
                "default_model": "model1",
                "access_key": "secret"
            }
            yield mock

    def test_test_endpoint(self):
        """Test simple test endpoint"""
        response = client.post("/api/v1/chat/test")
        assert response.status_code == 200
        assert response.json() == {"status": "ok", "message": "Test endpoint working"}

    def test_debug_env(self):
        """Test debug env endpoint"""
        with patch("common.env_manager.env_manager.load_env_file", return_value={"API_KEY": "abc"}):
            response = client.get("/api/v1/chat/debug-env")
            assert response.status_code == 200
            data = response.json()
            assert data["api_key_found"] is True
            assert data["api_key_prefix"] == "abc"

    def test_create_conversation_success(self, mock_conversation_manager, mock_env_config):
        """Test creating a new conversation"""
        mock_session = MockSession()
        mock_session.session_id = "test_session_id"
        mock_conversation_manager.create_session.return_value = mock_session

        response = client.post(
            "/api/v1/chat/conversations",
            json={
                "api_key": "test_key",
                "provider": "openrouter",
                "access_key": "secret"
            }
        )

        assert response.status_code == 200
        data = response.json()
        assert data["conversationId"] == "test_session_id"
        assert data["model"] == "model1"

    def test_create_conversation_invalid_access_key(self, mock_env_config):
        """Test creating conversation with invalid access key"""
        response = client.post(
            "/api/v1/chat/conversations",
            json={
                "api_key": "test_key",
                "access_key": "wrong_secret"
            }
        )
        assert response.status_code == 401

    def test_send_chat_message(self, mock_conversation_manager, mock_env_config):
        """Test sending a chat message"""
        mock_session = MockSession()

        # Mock ask_question return value
        mock_result = {
            "response": "<p>AI response</p>",
            "rawMarkdown": "AI response",
            "processing_time": 1.0,
            "tokens_used": 10,
            "token_usage": {"total_tokens": 10},
            "question_index": 0,
            "model_used": "model1",
            "timestamp": "2023-01-01 12:00:00"
        }
        mock_session.ask_question.return_value = mock_result

        mock_conversation_manager.get_or_create_session.return_value = (mock_session, False)

        with patch("app.api.v1.endpoints.chat.history_service") as mock_history:
            mock_history.save_conversation_history.return_value = True

            response = client.post(
                "/api/v1/chat",
                json={
                    "message": "Hello",
                    "conversationId": "test_id"
                }
            )

            assert response.status_code == 200
            data = response.json()
            assert data["message"]["content"] == "<p>AI response</p>"
            assert data["conversationId"] == "test_id"

    def test_send_chat_message_empty(self):
        """Test sending empty chat message"""
        response = client.post(
            "/api/v1/chat",
            json={"message": "   "}
        )
        assert response.status_code == 400

    def test_get_conversation_summary(self, mock_conversation_manager):
        """Test getting conversation summary"""
        mock_session = MockSession()
        mock_conversation_manager.get_session.return_value = mock_session

        response = client.get("/api/v1/chat/conversations/test_id/summary")
        assert response.status_code == 200

    def test_update_model(self, mock_conversation_manager):
        """Test updating conversation model"""
        mock_session = MockSession()
        mock_session.app_state.selected_model = "new_model"

        mock_conversation_manager.get_session.return_value = mock_session

        response = client.put(
            "/api/v1/chat/conversations/test_id/model",
            json={"model": "new_model"}
        )

        assert response.status_code == 200
        mock_session.set_model.assert_called_with("new_model")

    def test_update_api_key(self, mock_conversation_manager):
        """Test updating conversation API key"""
        mock_session = MockSession()
        mock_conversation_manager.get_session.return_value = mock_session

        response = client.put(
            "/api/v1/chat/conversations/test_id/api-key",
            json={"api_key": "new_key"}
        )

        assert response.status_code == 200
        mock_session.set_api_key.assert_called_with("new_key")

    def test_clear_conversation(self, mock_conversation_manager):
        """Test clearing conversation"""
        mock_session = MockSession()
        mock_conversation_manager.get_session.return_value = mock_session

        response = client.post("/api/v1/chat/conversations/test_id/clear")

        assert response.status_code == 200
        assert response.json()["success"] is True
        mock_session.clear_conversation.assert_called_once()

    def test_get_conversation_files(self, mock_conversation_manager):
        """Test getting conversation files"""
        mock_session = MockSession()
        mock_session.selected_files = ["file1.py", "file2.py"]
        mock_conversation_manager.get_session.return_value = mock_session

        response = client.get("/api/v1/chat/conversations/test_id/files")

        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert len(data["files"]) == 2
        assert "file1.py" in data["files"]

    def test_list_conversation_histories(self):
        """Test listing conversation histories"""
        with patch("app.api.v1.endpoints.chat.history_service") as mock_history:
            mock_history.list_conversation_histories.return_value = [{"id": "1"}, {"id": "2"}]

            response = client.get("/api/v1/chat/conversations/history")

            assert response.status_code == 200
            data = response.json()
            assert data["success"] is True
            assert data["count"] == 2

    def test_delete_conversation_history(self):
        """Test deleting conversation history"""
        with patch("app.api.v1.endpoints.chat.history_service") as mock_history:
            mock_history.delete_conversation_history.return_value = True

            response = client.delete("/api/v1/chat/conversations/test_id/history")

            assert response.status_code == 200
            assert response.json()["success"] is True
