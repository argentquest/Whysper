import pytest
from backend.tests_2026.integration.utils import skip_if_no_api_key, get_api_key, api_client

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

        response = api_client.post("/api/v1/chat", json=payload)

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
        """Test streaming chat response using AsyncClient."""
        from app.main import app
        from httpx import AsyncClient, ASGITransport

        payload = {
            "message": "Count to 3",
            "conversationId": "test_integration_chat_stream_001",
            "settings": {
                "model": "google/gemini-2.5-flash-preview-09-2025"
            }
        }

        # Use AsyncClient for proper streaming support with async endpoints
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
            async with ac.stream("POST", "/api/v1/chat/stream", json=payload) as response:
                assert response.status_code == 200
                assert "text/event-stream" in response.headers["content-type"]

                lines = []
                async for line in response.aiter_lines():
                    if line:
                        lines.append(line)

                print(f"DEBUG: Lines received: {lines}")
                assert len(lines) > 0

                # Check for at least one "event: progress" or "event: connected"
                has_event = any("event:" in line for line in lines)
                assert has_event
