"""
Mock Test for Kroki D2 Provider
"""

import unittest
from unittest.mock import MagicMock, patch
from pathlib import Path
import sys

# Add backend to path
backend_dir = Path(__file__).parent.parent.parent
if str(backend_dir) not in sys.path:
    sys.path.insert(0, str(backend_dir))

from diagrams.krokid2.kroki_renderer import KrokiD2Provider


class TestMockKrokiD2Provider(unittest.TestCase):

    def setUp(self):
        self.provider_folder = Path("backend/diagrams/krokid2")
        with patch("diagrams.base_diagram.load_provider_config") as mock_load:
            mock_config = MagicMock()
            mock_config.provider_id = "krokid2"
            mock_config.provider_name = "Kroki D2 Renderer"
            mock_config.custom = {"server_url": "http://mock-kroki:8000"}
            mock_config.pattern_correction.enabled = True
            mock_config.llm_correction.enabled = True
            mock_load.return_value = mock_config

            self.provider = KrokiD2Provider(self.provider_folder)

    @patch("requests.get")
    def test_is_available(self, mock_get):
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_get.return_value = mock_response
        self.assertTrue(self.provider.is_available())

    def test_provider_properties(self):
        self.assertEqual(self.provider.provider_id, "krokid2")
        self.assertEqual(self.provider.diagram_type, "d2")
        self.assertEqual(self.provider.diagram_endpoint, "d2")

if __name__ == '__main__':
    unittest.main()
