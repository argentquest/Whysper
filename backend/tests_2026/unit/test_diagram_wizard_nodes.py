import unittest
from unittest.mock import MagicMock, patch, AsyncMock
import os
import sys
import json

backend_path = os.path.abspath("backend")
if backend_path not in sys.path:
    sys.path.insert(0, backend_path)

# Import helper functions
# LLM helper functions are async, so we need to test them properly
try:
    from app.utils.diagram_wizard.nodes.llm_helpers import call_llm, extract_json_from_response
except ImportError:
    pass

class TestDiagramWizardNodes(unittest.IsolatedAsyncioTestCase):

    @patch('app.utils.diagram_wizard.nodes.llm_helpers.create_ai_processor')
    @patch('app.utils.diagram_wizard.nodes.llm_helpers.settings')
    async def test_call_llm(self, mock_settings, mock_create_processor):
        """Test call_llm helper (Async)."""

        # Setup settings
        mock_settings.api_key = "test_key"
        mock_settings.provider = "openrouter"
        mock_settings.default_model = "test-model"
        mock_settings.max_tokens = 100
        mock_settings.temperature = 0.5
        mock_settings.ai_connect_timeout = 10
        mock_settings.ai_read_timeout = 10

        # Setup processor mock
        mock_processor = MagicMock()
        # process_question is synchronous in the real code, called via asyncio.to_thread
        mock_processor.process_question.return_value = "Mock AI Response"
        mock_create_processor.return_value = mock_processor

        response = await call_llm(
            prompt="System Prompt",
            user_content="User Content",
            session_id="sess-1"
        )

        self.assertEqual(response, "Mock AI Response")
        mock_create_processor.assert_called_with(api_key="test_key", provider="openrouter")

    def test_extract_json_from_response(self):
        """Test JSON parsing helper."""
        # Standard JSON
        self.assertEqual(extract_json_from_response('{"key": "value"}'), {"key": "value"})

        # Markdown wrapped (json)
        self.assertEqual(extract_json_from_response('```json\n{"key": "value"}\n```'), {"key": "value"})

        # Markdown wrapped (no lang)
        self.assertEqual(extract_json_from_response('```\n{"key": "value"}\n```'), {"key": "value"})

        # Text with embedded JSON
        self.assertEqual(extract_json_from_response('Here is the json: {"key": "value"} thanks.'), {"key": "value"})
