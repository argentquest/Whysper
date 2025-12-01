"""
Test d2v1 provider configuration
"""

from diagrams.provider_config import get_config_loader
import sys
from pathlib import Path

# Add backend directory to Python path to enable module imports
backend_dir = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(backend_dir))


def test_d2v1_config():
    # Initialize config loader for provider configuration
    loader = get_config_loader()

    # Construct path to the d2v1 provider configuration folder
    diagrams_root = Path(__file__).parent.parent.parent
    provider_folder = diagrams_root / "d2v1"

    # Load the provider configuration from the specified folder
    config = loader.load_provider_config(provider_folder)

    # Verify basic configuration properties are loaded correctly
    assert config is not None, "Config should load successfully"
    assert config.provider_id == "d2v1"
    assert config.diagram_type == "d2"

    # Check supported output formats
    assert "svg" in config.supported_output_formats
    assert "d2" in config.supported_output_formats

    # Test configuration overrides for LLM correction settings
    assert config.llm_correction.max_retries == 8, "Should override to 8"
    assert config.llm_correction.max_tokens == 6000, "Should override to 6000"

    # Verify batch processing configuration overrides
    assert config.batch.enabled, "Should override to True"
    assert config.batch.max_items == 100, "Should override to 100"

    # Confirm default settings that were not explicitly overridden
    assert config.llm_correction.temperature == 0.3, "Should use default"
    assert config.validation.timeout_seconds == 120, "Should use default"

    # Check custom provider-specific settings
    assert config.custom.get("layout_engine") == "dagre"
    assert config.custom.get("theme") == "default"

    # Print success message if all assertions pass
    print("[OK] d2v1 configuration tests passed")


if __name__ == "__main__":
    test_d2v1_config()
