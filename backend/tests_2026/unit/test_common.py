import unittest
from unittest.mock import MagicMock, patch
import logging
from typing import Dict, Any, Tuple, List

# Import classes to test
# We need to mock the abstract class to test concrete implementations or common logic
from common.base_ai import BaseAIProvider, AIProviderConfig
from common.logger import get_logger, CodeChatLogger

# Concrete implementation for testing BaseAIProvider
class TestProvider(BaseAIProvider):
    def _get_provider_config(self) -> AIProviderConfig:
        return AIProviderConfig(name="test_provider", api_url="http://test.url")

    def _prepare_headers(self) -> Dict[str, str]:
        return {"Test-Header": "test_value"}

    def _prepare_request_data(self, messages, model, max_tokens, temperature) -> Dict[str, Any]:
        return {"messages": messages}

    def _extract_response_content(self, response_data) -> str:
        return response_data.get("content", "")

    def _extract_token_usage(self, response_data) -> Tuple[int, int, int]:
        return 10, 20, 30

    def _handle_api_error(self, status_code, response_text) -> str:
        return f"Error {status_code}"

class TestBaseAIProvider(unittest.TestCase):
    def setUp(self):
        self.provider = TestProvider(api_key="test_key")

    def test_initialization(self):
        self.assertEqual(self.provider.api_key, "test_key")
        self.assertEqual(self.provider.get_provider_name(), "test_provider")
        self.assertTrue(self.provider.validate_api_key())

    def test_provider_info(self):
        info = self.provider.get_provider_info()
        self.assertEqual(info["name"], "test_provider")
        self.assertTrue(info["has_api_key"])

    def test_secure_debug_info(self):
        debug_info = self.provider.get_secure_debug_info()
        self.assertNotEqual(debug_info["api_key"], "test_key")
        # Checking if it masks it, usually implies it contains asterisks or is different
        # If mask_api_key returns 'tes...key', it won't be equal to 'test_key'
        # Let's just check it is not the original key
        self.assertNotEqual(debug_info["api_key"], "test_key")

    @patch("requests.post")
    def test_process_question_success(self, mock_post):
        # Setup mock response
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"content": "Test response", "usage": {}}
        mock_post.return_value = mock_response

        response = self.provider.process_question(
            question="Hello",
            conversation_history=[],
            codebase_content="",
            model="test-model",
            max_tokens=100,
            temperature=0.7
        )

        self.assertEqual(response, "Test response")
        mock_post.assert_called_once()

    @patch("requests.post")
    def test_process_question_api_error(self, mock_post):
        # Setup mock error response
        mock_response = MagicMock()
        mock_response.status_code = 500
        mock_response.text = "Internal Server Error"
        mock_post.return_value = mock_response

        with self.assertRaises(Exception) as context:
            self.provider.process_question(
                question="Hello",
                conversation_history=[],
                codebase_content="",
                model="test-model",
                max_tokens=100,
                temperature=0.7
            )

        self.assertTrue("Error 500" in str(context.exception))

class TestLogger(unittest.TestCase):
    def test_get_logger(self):
        logger = get_logger("test_module")
        # The custom logger wrapper returns CodeChatLogger, not logging.Logger
        self.assertIsInstance(logger, CodeChatLogger)
        # Check name if exposed, or check underlying logger
        self.assertTrue(logger.name.endswith("test_module"))
