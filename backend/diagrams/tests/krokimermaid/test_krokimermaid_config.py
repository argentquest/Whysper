"""
Test Kroki Mermaid provider configuration
"""

from diagrams.provider_config import get_config_loader
import sys
from pathlib import Path

# Dynamically calculate the backend directory path to ensure correct module importing
backend_dir = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(backend_dir))

# Import the configuration loader function from the diagrams module


def test_krokimermaid_config():
    # Initialize the config loader to read provider configurations
    loader = get_config_loader()

    # Determine the root directory for diagrams and the specific provider folder
    diagrams_root = Path(__file__).parent.parent.parent
    provider_folder = diagrams_root / "krokimermaid"

    # Load the provider configuration for Kroki Mermaid
    config = loader.load_provider_config(provider_folder)

    # Perform assertions to validate the configuration
    assert config is not None, "Config should load successfully"  # Ensure config is not None
    assert config.provider_id == "krokimermaid"  # Verify correct provider ID
    assert config.diagram_type == "mermaid"  # Check diagram type is mermaid
    assert "svg" in config.supported_output_formats  # Confirm SVG is a supported output format

    # Print success message if all tests pass
    print("[OK] Kroki Mermaid configuration tests passed")


# Run the test function if script is executed directly
if __name__ == "__main__":
    test_krokimermaid_config()
