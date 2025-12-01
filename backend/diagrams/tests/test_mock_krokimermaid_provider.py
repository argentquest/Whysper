"""
Mock Test for Kroki Mermaid Provider
"""

from diagrams.krokimermaid.kroki_renderer import KrokiMermaidProvider
import unittest
from unittest.mock import MagicMock, patch
from pathlib import Path
import sys

# Add backend to path
backend_dir = Path(__file__).parent.parent.parent
if str(backend_dir) not in sys.path:
    sys.path.insert(0, str(backend_dir))


class TestMockKrokiMermaidProvider(unittest.TestCase):

    def setUp(self):
        self.provider_folder = Path("backend/diagrams/krokimermaid")
        with patch("diagrams.base_diagram.load_provider_config") as mock_load:
            mock_config = MagicMock()
            mock_config.provider_id = "krokimermaid"
            mock_config.provider_name = "Kroki Mermaid Renderer"
            mock_config.custom = {"server_url": "http://mock-kroki:8000"}
            mock_config.pattern_correction.enabled = True
            mock_config.llm_correction.enabled = True
            mock_load.return_value = mock_config

            self.provider = KrokiMermaidProvider(self.provider_folder)

    @patch("requests.get")
    def test_is_available(self, mock_get):
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_get.return_value = mock_response
        self.assertTrue(self.provider.is_available())

    def test_auto_fix_pattern_based(self):
        """Test mermaid specific pattern fixes."""
        with patch.object(self.provider, "validate_code") as mock_validate:
            mock_validate.return_value = MagicMock(is_valid=True)

            # Case: Missing diagram type, but has arrows
            code = "A --> B"
            result = self.provider.auto_fix_pattern_based(code, "Error")

            self.assertTrue(result.auto_fixed)
            self.assertIn("flowchart TD", result.fixed_code)

            # Case: Invalid arrow syntax
            code = "flowchart TD\nA - > B"
            result = self.provider.auto_fix_pattern_based(code, "Error")
            self.assertIn("A-->B", result.fixed_code.replace(" ", ""))


if __name__ == "__main__":
    unittest.main()
