import pytest
from backend.tests_2026.integration.utils import skip_if_no_api_key, get_api_key

@skip_if_no_api_key()
class TestChatIntegration:

    def test_chat_simple_message(self, api_client):
        """Test sending a simple message to the chat endpoint."""
        payload = {
            "message": "Say exactly 'Hello World'",
            "conversationId": "test_integration_chat_001",
            "settings": {
                "model": "google/gemini-2.5-flash-preview-09-2025", # Use a fast/cheap model
                "temperature": 0.1
            }
        }

        response = api_client.post("/api/v1/chat/", json=payload)

        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert "content" in data["message"]
        content = data["message"]["content"]
        assert len(content) > 0
        # Semantic check
        assert "Hello World" in content or "Hello" in content

    @pytest.mark.asyncio
    async def test_chat_streaming(self):
        """Test streaming chat response (requires running server or async client)."""
        # Note: TestClient doesn't support streaming well for SSE usually,
        # so we might skip strict SSE validation here or use httpx against a live server if configured.
        # For integration tests within the app, we can use TestClient but checking streaming is tricky.
        # We will do a basic check that it returns 200 and correct media type.

        # We need to import the app to use TestClient
        from app.main import app
        from fastapi.testclient import TestClient

        client = TestClient(app)

        payload = {
            "message": "Count to 3",
            "conversationId": "test_integration_chat_stream_001",
            "settings": {
                "model": "google/gemini-2.5-flash-preview-09-2025"
            }
        }

        # We use stream=True
        with client.stream("POST", "/api/v1/chat/stream", json=payload) as response:
            assert response.status_code == 200
            # Check for SSE headers
            assert "text/event-stream" in response.headers["content-type"]

            # Read a few lines to verify data format
            lines = list(response.iter_lines())
            assert len(lines) > 0

            # Check for at least one "event: progress" or "event: connected"
            has_event = any(b"event:" in line for line in lines)
            assert has_event
