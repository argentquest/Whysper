"""
Test Kroki D2 provider configuration
"""

import sys
from pathlib import Path

# Add backend directory to Python path for importing modules from parent directories
backend_dir = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(backend_dir))

from diagrams.provider_config import get_config_loader


def test_krokid2_config():
    # Initialize config loader to handle provider configuration
    loader = get_config_loader()
    
    # Navigate to the backend root and provider-specific folder
    backend_root = Path(__file__).parent.parent.parent.parent.parent
    provider_folder = backend_root / "diagrams" / "krokid2"

    # Load configuration for the Kroki D2 provider
    config = loader.load_provider_config(provider_folder)

    # Validate configuration settings and ensure critical attributes are present
    assert config is not None, "Config should load successfully"
    assert config.provider_id == "krokid2"  # Verify correct provider identifier
    assert config.diagram_type == "d2"  # Confirm diagram type is D2
    assert "svg" in config.supported_output_formats  # Check SVG is a supported output format

    # Indicate successful test completion
    print("[OK] Kroki D2 configuration tests passed")


if __name__ == "__main__":
    # Run configuration test when script is executed directly
    test_krokid2_config()