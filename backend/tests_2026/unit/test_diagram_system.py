import unittest
from unittest.mock import MagicMock, patch, ANY
import os
import sys

# Ensure 'backend' directory is in sys.path so we can import 'diagrams' directly
# matching how the application code does it (e.g. inside the container/backend dir)
backend_path = os.path.abspath("backend")
if backend_path not in sys.path:
    sys.path.insert(0, backend_path)

# Import using 'diagrams' package directly, avoiding 'backend.' prefix to match internal imports
from diagrams.provider_registry import ProviderRegistry
from diagrams.d2v1.d2_renderer import D2V1Provider
from diagrams.base_diagram import BaseDiagramProvider

class TestDiagramSystem(unittest.TestCase):

    def test_provider_registry_discovery(self):
        """Test that the registry can discover providers."""

        mock_path = MagicMock()
        mock_folder = MagicMock()
        mock_folder.is_dir.return_value = True
        mock_folder.name = "test_provider_folder"

        # Need config.json to exist
        mock_config_file = MagicMock()
        mock_config_file.exists.return_value = True
        mock_folder.__truediv__.return_value = mock_config_file

        mock_path.iterdir.return_value = [mock_folder]

        with patch('diagrams.provider_registry.importlib.import_module') as mock_import:
            # Mock the module returned by import
            mock_module = MagicMock()

            # Mock the provider class in the module
            mock_provider_class = MagicMock()
            mock_provider_class.provider_id = "test_provider_id"
            mock_provider_class.__name__ = "TestProvider"

            # The instance returned by class()
            mock_instance = MagicMock()
            mock_instance.provider_id = "test_provider_id"
            mock_provider_class.return_value = mock_instance

            # The registry's _find_provider_class needs to find a class
            with patch.object(ProviderRegistry, '_find_provider_class', return_value=mock_provider_class):
                with patch('diagrams.provider_registry.get_llm_correction_service'):
                    with patch('diagrams.provider_registry.get_config_loader'):

                        # Initialize without auto-discover to control state
                        registry = ProviderRegistry(diagrams_root=mock_path, auto_discover=False)

                        # Override enabled_providers to allow our test provider
                        registry.enabled_providers = None

                        # Manually trigger discovery
                        registry._discover_providers()

                        # Verify register was called
                        # Since mock_provider_class is called to create instance, and then registered
                        # We should check if the ID is in the registry
                        self.assertIn("test_provider_id", registry._providers)

    @patch('diagrams.d2v1.d2_renderer.validate_d2_and_render')
    def test_d2_renderer(self, mock_val_render):
        """Test D2 Renderer logic without calling actual D2 CLI."""

        # Patch _load_config on the BaseDiagramProvider that D2V1Provider inherits from
        # Using the imported class reference
        with patch.object(BaseDiagramProvider, '_load_config'):
             # Patch _setup_logging to avoid logger setup issues
             with patch.object(D2V1Provider, '_setup_logging'):

                # Create instance
                provider = D2V1Provider(provider_folder=MagicMock())

                # Mock checks
                provider._cli_available = True

                # Mock successful D2 execution
                mock_val_render.return_value = (True, "Success", "<svg>diagram</svg>")

                result = provider.render("x -> y", output_format="svg")

                self.assertTrue(result.success)
                self.assertEqual(result.content, "<svg>diagram</svg>")
