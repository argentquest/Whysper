"""
Test Kroki PlantUML provider configuration
"""

import sys
from pathlib import Path

# Add backend directory to Python path to enable importing modules from parent directories
backend_dir = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(backend_dir))

# Import configuration loader for diagram providers
from diagrams.provider_config import get_config_loader


def test_krokiplantuml_config():
    # Initialize config loader to handle provider configurations
    loader = get_config_loader()

    # Determine the backend root and specific provider folder path
    backend_root = Path(__file__).parent.parent.parent.parent.parent
    provider_folder = backend_root / "diagrams" / "krokiplantuml"

    # Load the configuration for the Kroki PlantUML provider
    config = loader.load_provider_config(provider_folder)

    # Validate the loaded configuration meets expected criteria
    assert config is not None, "Config should load successfully"
    assert config.provider_id == "krokiplantuml"
    assert config.diagram_type == "plantuml"
    assert "svg" in config.supported_output_formats

    # Print success message if all assertions pass
    print("[OK] Kroki PlantUML configuration tests passed")


# Run the test configuration function if script is executed directly
if __name__ == "__main__":
    test_krokiplantuml_config()