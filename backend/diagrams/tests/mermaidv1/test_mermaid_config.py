```python
"""
Test mermaidv1 provider configuration
"""

import sys
from pathlib import Path

# Add backend directory to Python path to ensure module imports work correctly
backend_dir = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(backend_dir))

# Import configuration loader for diagram providers
from diagrams.provider_config import get_config_loader


def test_mermaidv1_config():
    # Initialize config loader to handle provider-specific configurations
    loader = get_config_loader()
    
    # Construct paths to the mermaidv1 provider configuration folder
    diagrams_root = Path(__file__).parent.parent.parent
    provider_folder = diagrams_root / "mermaidv1"

    # Load the configuration for the mermaidv1 provider
    config = loader.load_provider_config(provider_folder)

    # Validate basic configuration properties
    assert config is not None, "Config should load successfully"
    assert config.provider_id == "mermaidv1"
    assert config.diagram_type == "mermaid"
    
    # Ensure supported output formats include SVG and PNG
    assert "svg" in config.supported_output_formats
    assert "png" in config.supported_output_formats

    # Verify configuration overrides for specific parameters
    assert config.llm_correction.max_retries == 5, "Should override to 5"
    assert config.llm_correction.temperature == 0.2, "Should override to 0.2"
    assert config.validation.timeout_seconds == 180, "Should override to 180"

    # Check that default values are used when not explicitly overridden
    assert config.llm_correction.max_tokens == 4000, "Should use default"
    assert config.user_correction.session_timeout_seconds == 300, "Should use default"

    # Print success message if all assertions pass
    print("[OK] mermaidv1 configuration tests passed")


# Run the test function if script is executed directly
if __name__ == "__main__":
    test_mermaidv1_config()