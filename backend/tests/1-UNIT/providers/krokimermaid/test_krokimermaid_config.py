"""
Test Kroki Mermaid provider configuration
"""

import sys
from pathlib import Path

# Add backend directory to Python path to enable module imports
backend_dir = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(backend_dir))

# Import config loader utility for diagram providers
from diagrams.provider_config import get_config_loader


def test_krokimermaid_config():
    # Initialize config loader to handle provider configurations
    loader = get_config_loader()

    # Navigate to the root backend directory and provider-specific folder
    backend_root = Path(__file__).parent.parent.parent.parent.parent
    provider_folder = backend_root / "diagrams" / "krokimermaid"

    # Load configuration for the Kroki Mermaid provider
    config = loader.load_provider_config(provider_folder)

    # Perform validation checks on the loaded configuration
    assert config is not None, "Config should load successfully"  # Ensure config is loaded
    assert config.provider_id == "krokimermaid"  # Verify correct provider identifier
    assert config.diagram_type == "mermaid"  # Confirm diagram type
    assert "svg" in config.supported_output_formats  # Check supported output format

    # Print success message if all tests pass
    print("[OK] Kroki Mermaid configuration tests passed")


# Run the test function if script is executed directly
if __name__ == "__main__":
    test_krokimermaid_config()
