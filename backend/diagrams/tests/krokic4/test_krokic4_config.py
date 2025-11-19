"""
Test Kroki C4 provider configuration
"""

import sys
from pathlib import Path

# Add backend directory to Python path for importing modules
backend_dir = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(backend_dir))

from diagrams.provider_config import get_config_loader


def test_krokic4_config():
    # Initialize config loader to handle provider configuration
    loader = get_config_loader()

    # Locate the directory containing the Kroki C4 provider configuration
    diagrams_root = Path(__file__).parent.parent.parent
    provider_folder = diagrams_root / "krokic4"

    # Load the provider configuration from the specified folder
    config = loader.load_provider_config(provider_folder)

    # Perform validation checks on the loaded configuration
    assert config is not None, "Config should load successfully"
    assert config.provider_id == "krokic4"  # Verify correct provider ID
    assert config.diagram_type == "c4"  # Check diagram type is C4
    assert "svg" in config.supported_output_formats  # Ensure SVG is a supported format

    # Indicate successful configuration test
    print("[OK] Kroki C4 configuration tests passed")


if __name__ == "__main__":
    # Run the configuration test when script is executed directly
    test_krokic4_config()
