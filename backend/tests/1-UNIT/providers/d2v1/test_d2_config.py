"""
Test d2v1 provider configuration
"""

import sys
from pathlib import Path

# Add backend to Python path to enable module imports from parent directories
backend_dir = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(backend_dir))

from diagrams.provider_config import get_config_loader


def test_d2v1_config():
    """Test d2v1 provider configuration loading"""
    # Initialize config loader to handle provider configuration
    loader = get_config_loader()

    # Construct path to the provider's configuration directory
    backend_root = Path(__file__).parent.parent.parent.parent.parent
    provider_folder = backend_root / "diagrams" / "d2v1"

    # Load the provider configuration from specified folder
    config = loader.load_provider_config(provider_folder)

    # Verify basic configuration properties are correctly loaded
    assert config is not None, "Config should load successfully"
    assert config.provider_id == "d2v1"
    assert config.diagram_type == "d2"
    assert "svg" in config.supported_output_formats
    assert "d2" in config.supported_output_formats

    # Validate configuration overrides for specific settings
    # Check that custom retry and token settings are applied
    assert config.llm_correction.max_retries == 8, "Should override to 8"
    assert config.llm_correction.max_tokens == 6000, "Should override to 6000"

    # Verify batch processing configuration overrides
    assert config.batch.enabled == True, "Should override to True"
    assert config.batch.max_items == 100, "Should override to 100"

    # Confirm default values are preserved for unmodified settings
    assert config.llm_correction.temperature == 0.3, "Should use default"
    assert config.validation.timeout_seconds == 120, "Should use default"

    # Check custom provider-specific configuration settings
    assert config.custom.get("layout_engine") == "dagre"
    assert config.custom.get("theme") == "default"

    # Print success message if all assertions pass
    print("[OK] d2v1 configuration tests passed")


if __name__ == "__main__":
    test_d2v1_config()