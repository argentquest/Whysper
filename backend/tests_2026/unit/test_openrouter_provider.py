import unittest
from unittest.mock import MagicMock, patch
from backend.providers.openrouter_provider import OpenRouterProvider
from app.core.config import settings

class TestOpenRouterProvider(unittest.TestCase):
    def setUp(self):
        # Patch settings to avoid missing env var errors if config tries to load them
        self.settings_patcher = patch('backend.providers.openrouter_provider.settings')
        self.mock_settings = self.settings_patcher.start()
        self.mock_settings.openrouter_api_url = "https://openrouter.ai/api/v1/chat/completions"
        self.mock_settings.openrouter_http_referer = "http://test.com"
        self.mock_settings.openrouter_title = "Test App"

        self.provider = OpenRouterProvider(api_key="test_openrouter_key")

    def tearDown(self):
        self.settings_patcher.stop()

    def test_config(self):
        config = self.provider._get_provider_config()
        self.assertEqual(config.name, "openrouter")
        self.assertEqual(config.api_url, "https://openrouter.ai/api/v1/chat/completions")
        self.assertTrue(config.supports_tokens)

    def test_headers(self):
        headers = self.provider._prepare_headers()
        self.assertEqual(headers["Authorization"], "Bearer test_openrouter_key")
        self.assertEqual(headers["HTTP-Referer"], "http://test.com")
        self.assertEqual(headers["X-Title"], "Test App")

    def test_request_data(self):
        messages = [{"role": "user", "content": "hello"}]
        data = self.provider._prepare_request_data(messages, "gpt-4", 100, 0.5)
        self.assertEqual(data["model"], "gpt-4")
        self.assertEqual(data["messages"], messages)
        self.assertEqual(data["max_tokens"], 100)
        self.assertEqual(data["temperature"], 0.5)
        self.assertFalse(data["stream"])

    def test_extract_response_content(self):
        # Standard response
        response_data = {
            "choices": [
                {"message": {"content": "Hello world"}}
            ]
        }
        content = self.provider._extract_response_content(response_data)
        self.assertEqual(content, "Hello world")

        # Grok reasoning case
        grok_response = {
            "choices": [
                {"message": {"content": "", "reasoning": "Thinking..."}}
            ]
        }
        content = self.provider._extract_response_content(grok_response)
        self.assertEqual(content, "Thinking...")

    def test_extract_token_usage(self):
        usage_data = {
            "usage": {
                "prompt_tokens": 10,
                "completion_tokens": 20,
                "total_tokens": 30
            }
        }
        p, c, t = self.provider._extract_token_usage(usage_data)
        self.assertEqual(p, 10)
        self.assertEqual(c, 20)
        self.assertEqual(t, 30)

        # Missing usage
        p, c, t = self.provider._extract_token_usage({})
        self.assertEqual(p, 0)

    def test_handle_api_error(self):
        self.assertTrue("invalid" in self.provider._handle_api_error(401, ""))
        self.assertTrue("rate limit" in self.provider._handle_api_error(429, ""))
        self.assertTrue("unavailable" in self.provider._handle_api_error(502, ""))
        self.assertTrue("failed" in self.provider._handle_api_error(500, "Error"))
