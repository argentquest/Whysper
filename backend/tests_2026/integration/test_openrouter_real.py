import pytest
import os
from backend.providers.openrouter_provider import OpenRouterProvider
from app.core.config import settings

@pytest.mark.integration
class TestOpenRouterIntegration:

    @pytest.fixture
    def provider(self):
        """Fixture to initialize provider with real API key from .env.test"""
        api_key = os.getenv("API_KEY")
        if not api_key:
            pytest.skip("API_KEY not found in environment, skipping integration test")

        # Ensure we don't accidentally mock things here, though we might need to
        # ensure settings are correct if they are pulled from global config
        return OpenRouterProvider(api_key=api_key)

    def test_real_api_call(self, provider):
        """Makes a real call to OpenRouter."""
        model = os.getenv("DEFAULT_MODEL", "x-ai/grok-code-fast-1")

        print(f"\nUsing Model: {model}")

        response = provider.process_question(
            question="Reply with exactly the word 'Pong'.",
            conversation_history=[],
            codebase_content="",
            model=model,
            max_tokens=10,
            temperature=0.1
        )

        print(f"Response: {response}")
        assert response is not None
        assert len(response) > 0
        # AI might be chatty, but should contain Pong
        assert "Pong" in response or "pong" in response.lower()
