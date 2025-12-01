"""
Test mermaidv1 provider configuration
"""

from diagrams.provider_config import get_config_loader
import sys
from pathlib import Path

# Add backend to Python path to enable importing from parent directories
backend_dir = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(backend_dir))

# Import configuration loader to test provider configuration


def test_mermaidv1_config():
    # Initialize config loader to retrieve provider configurations
    loader = get_config_loader()

    # Construct path to mermaidv1 provider configuration folder
    backend_root = Path(__file__).parent.parent.parent.parent.parent
    provider_folder = backend_root / "diagrams" / "mermaidv1"

    # Load the provider configuration for mermaidv1
    config = loader.load_provider_config(provider_folder)

    # Validate basic configuration properties
    assert config is not None, "Config should load successfully"
    assert config.provider_id == "mermaidv1"
    assert config.diagram_type == "mermaid"

    # Check supported output formats
    assert "svg" in config.supported_output_formats
    assert "png" in config.supported_output_formats

    # Verify configuration overrides for specific settings
    assert config.llm_correction.max_retries == 5, "Should override to 5"
    assert config.llm_correction.temperature == 0.2, "Should override to 0.2"
    assert config.validation.timeout_seconds == 180, "Should override to 180"

    # Confirm default values remain unchanged
    assert config.llm_correction.max_tokens == 4000, "Should use default"
    assert config.user_correction.session_timeout_seconds == 300, "Should use default"

    # Indicate successful test completion
    print("[OK] mermaidv1 configuration tests passed")


# Run the test if script is executed directly
if __name__ == "__main__":
    test_mermaidv1_config()
