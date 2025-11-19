"""
Test Kroki D2 provider configuration
"""

import sys
from pathlib import Path

# Add backend directory to Python path to enable module imports
backend_dir = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(backend_dir))

# Import configuration loader utility for provider settings
from diagrams.provider_config import get_config_loader


def test_krokid2_config():
    # Create configuration loader to handle provider settings
    loader = get_config_loader()

    # Determine the root directory for diagram providers
    diagrams_root = Path(__file__).parent.parent.parent
    
    # Specify the specific provider folder for Kroki D2
    provider_folder = diagrams_root / "krokid2"

    # Load configuration for the Kroki D2 provider
    config = loader.load_provider_config(provider_folder)

    # Validate configuration has loaded correctly
    assert config is not None, "Config should load successfully"
    
    # Check specific configuration properties
    assert config.provider_id == "krokid2"
    assert config.diagram_type == "d2"
    assert "svg" in config.supported_output_formats

    # Indicate successful test completion
    print("[OK] Kroki D2 configuration tests passed")


# Run the test if script is executed directly
if __name__ == "__main__":
    test_krokid2_config()
