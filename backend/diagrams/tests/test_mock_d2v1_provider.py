"""
Mock Test for D2 v1 Provider
"""

from diagrams.d2v1.d2_renderer import D2V1Provider
import unittest
from unittest.mock import MagicMock, patch
from pathlib import Path
import sys
import subprocess

# Add backend to path
backend_dir = Path(__file__).parent.parent.parent
if str(backend_dir) not in sys.path:
    sys.path.insert(0, str(backend_dir))


class TestMockD2V1Provider(unittest.TestCase):

    def setUp(self):
        self.provider_folder = Path("backend/diagrams/d2v1")
        with patch("diagrams.base_diagram.load_provider_config") as mock_load:
            mock_config = MagicMock()
            mock_config.provider_id = "d2v1"
            mock_config.provider_name = "D2 CLI Renderer v1"
            mock_config.custom = {"executable_path": "d2"}
            mock_config.pattern_correction.enabled = True
            mock_config.llm_correction.enabled = True
            mock_load.return_value = mock_config

            self.provider = D2V1Provider(self.provider_folder)

    @patch("subprocess.run")
    def test_is_available(self, mock_run):
        mock_run.return_value = MagicMock(returncode=0)
        self.assertTrue(self.provider.is_available())

    @patch("subprocess.run")
    def test_validate_code_success(self, mock_run):
        with patch.object(self.provider, "is_available", return_value=True):
            mock_run.return_value = MagicMock(returncode=0)
            result = self.provider.validate_code("x -> y")
            self.assertTrue(result.is_valid)

    @patch("subprocess.run")
    def test_validate_code_failure(self, mock_run):
        with patch.object(self.provider, "is_available", return_value=True):
            mock_run.side_effect = subprocess.CalledProcessError(returncode=1, cmd="d2", stderr="Syntax error")
            result = self.provider.validate_code("invalid")
            self.assertFalse(result.is_valid)

    def test_auto_fix_pattern_based(self):
        with patch.object(self.provider, "validate_code") as mock_validate:
            mock_validate.return_value = MagicMock(is_valid=True)

            # Case: Missing closing brace
            code = "x: {"
            result = self.provider.auto_fix_pattern_based(code, "Error")
            self.assertTrue(result.auto_fixed)
            self.assertIn("}", result.fixed_code)


if __name__ == "__main__":
    unittest.main()
