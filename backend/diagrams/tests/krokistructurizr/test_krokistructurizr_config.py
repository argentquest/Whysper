"""
Test Kroki Structurizr provider configuration
"""

from diagrams.provider_config import get_config_loader
import sys
from pathlib import Path

# Add backend directory to Python path to enable module imports
backend_dir = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(backend_dir))

# Import configuration loader for diagram providers


def test_krokistructurizr_config():
    # Create config loader for accessing provider configuration
    loader = get_config_loader()

    # Determine the root directory for diagrams and specific provider folder
    diagrams_root = Path(__file__).parent.parent.parent
    provider_folder = diagrams_root / "krokistructurizr"

    # Load configuration for Kroki Structurizr provider
    config = loader.load_provider_config(provider_folder)

    # Verify configuration is loaded correctly with expected properties
    assert config is not None, "Config should load successfully"
    assert config.provider_id == "krokistructurizr"
    assert config.diagram_type == "structurizr"
    assert "svg" in config.supported_output_formats

    # Indicate successful test completion
    print("[OK] Kroki Structurizr configuration tests passed")


# Run test if script is executed directly
if __name__ == "__main__":
    test_krokistructurizr_config()
