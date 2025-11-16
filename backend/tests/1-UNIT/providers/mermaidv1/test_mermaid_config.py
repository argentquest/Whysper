"""
Test mermaidv1 provider configuration
"""

import sys
from pathlib import Path

# Add backend to path
backend_dir = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(backend_dir))

from diagrams.provider_config import get_config_loader


def test_mermaidv1_config():
    """Test mermaidv1 provider configuration loading"""
    loader = get_config_loader()
    backend_root = Path(__file__).parent.parent.parent.parent.parent
    provider_folder = backend_root / "diagrams" / "mermaidv1"

    config = loader.load_provider_config(provider_folder)

    assert config is not None, "Config should load successfully"
    assert config.provider_id == "mermaidv1"
    assert config.diagram_type == "mermaid"
    assert "svg" in config.supported_output_formats
    assert "png" in config.supported_output_formats

    # Test overrides
    assert config.llm_correction.max_retries == 5, "Should override to 5"
    assert config.llm_correction.temperature == 0.2, "Should override to 0.2"
    assert config.validation.timeout_seconds == 180, "Should override to 180"

    # Test defaults that weren't overridden
    assert config.llm_correction.max_tokens == 4000, "Should use default"
    assert config.user_correction.session_timeout_seconds == 300, "Should use default"

    print("[OK] mermaidv1 configuration tests passed")


if __name__ == "__main__":
    test_mermaidv1_config()
