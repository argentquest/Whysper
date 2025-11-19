"""
Test Kroki Structurizr provider configuration
"""

import sys
from pathlib import Path

# Add backend directory to Python path to enable importing backend modules
backend_dir = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(backend_dir))

# Import configuration loader function from diagrams module
from diagrams.provider_config import get_config_loader


def test_krokistructurizr_config():
    # Initialize config loader to retrieve provider configuration
    loader = get_config_loader()

    # Construct path to the root backend directory and specific provider folder
    backend_root = Path(__file__).parent.parent.parent.parent.parent
    provider_folder = backend_root / "diagrams" / "krokistructurizr"

    # Load the provider configuration for Kroki Structurizr
    config = loader.load_provider_config(provider_folder)

    # Perform validation checks on the loaded configuration
    assert config is not None, "Config should load successfully"
    assert config.provider_id == "krokistructurizr"  # Check provider identifier
    assert config.diagram_type == "structurizr"  # Confirm diagram type
    assert "svg" in config.supported_output_formats  # Verify SVG format support

    # Print success message if all tests pass
    print("[OK] Kroki Structurizr configuration tests passed")


# Run the test function if script is executed directly
if __name__ == "__main__":
    test_krokistructurizr_config()
