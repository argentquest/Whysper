"""
Mock Test for Mermaid v1 Provider
"""

import unittest
from unittest.mock import MagicMock, patch
from pathlib import Path
import sys
import subprocess

# Add backend to path
backend_dir = Path(__file__).parent.parent.parent
if str(backend_dir) not in sys.path:
    sys.path.insert(0, str(backend_dir))

from diagrams.mermaidv1.mermaid_renderer import MermaidV1Provider


class TestMockMermaidV1Provider(unittest.TestCase):

    def setUp(self):
        self.provider_folder = Path("backend/diagrams/mermaidv1")
        with patch("diagrams.base_diagram.load_provider_config") as mock_load:
            mock_config = MagicMock()
            mock_config.provider_id = "mermaidv1"
            mock_config.provider_name = "Mermaid CLI Renderer v1"
            mock_config.custom = {"executable_path": "mmdc"}
            mock_config.pattern_correction.enabled = True
            mock_config.llm_correction.enabled = True
            mock_load.return_value = mock_config

            self.provider = MermaidV1Provider(self.provider_folder)

    @patch("subprocess.run")
    def test_is_available(self, mock_run):
        mock_run.return_value = MagicMock(returncode=0)
        self.assertTrue(self.provider.is_available())

    @patch("subprocess.run")
    def test_validate_code_success(self, mock_run):
        with patch.object(self.provider, 'is_available', return_value=True):
            mock_run.return_value = MagicMock(returncode=0)
            result = self.provider.validate_code("graph TD; A-->B;")
            self.assertTrue(result.is_valid)

    @patch("subprocess.run")
    def test_validate_code_failure(self, mock_run):
        with patch.object(self.provider, 'is_available', return_value=True):
            # Simulate CalledProcessError
            mock_run.side_effect = subprocess.CalledProcessError(
                returncode=1, cmd="mmdc", stderr="Syntax error"
            )
            result = self.provider.validate_code("invalid code")
            self.assertFalse(result.is_valid)
            self.assertIn("Syntax error", result.error)

    def test_auto_fix_pattern_based(self):
        # Test fix for missing diagram type
        with patch.object(self.provider, 'validate_code') as mock_validate:
            mock_validate.return_value = MagicMock(is_valid=True)

            code = "A --> B"
            result = self.provider.auto_fix_pattern_based(code, "Error")
            self.assertIn("flowchart TD", result.fixed_code)

if __name__ == '__main__':
    unittest.main()
