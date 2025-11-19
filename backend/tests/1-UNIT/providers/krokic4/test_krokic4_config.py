"""
Test Kroki C4 provider configuration
"""

import sys
from pathlib import Path

# Add backend directory to Python path for import resolution
backend_dir = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(backend_dir))

from diagrams.provider_config import get_config_loader


def test_krokic4_config():
    # Initialize configuration loader for retrieving provider settings
    loader = get_config_loader()

    # Construct path to backend root and specific provider configuration folder
    backend_root = Path(__file__).parent.parent.parent.parent.parent
    provider_folder = backend_root / "diagrams" / "krokic4"

    # Load provider configuration from specified folder
    config = loader.load_provider_config(provider_folder)

    # Validate configuration attributes and ensure critical settings are present
    assert config is not None, "Config should load successfully"
    assert config.provider_id == "krokic4"
    assert config.diagram_type == "c4"
    assert "svg" in config.supported_output_formats

    # Print success message if all assertions pass
    print("[OK] Kroki C4 configuration tests passed")


if __name__ == "__main__":
    # Run configuration test when script is executed directly
    test_krokic4_config()
