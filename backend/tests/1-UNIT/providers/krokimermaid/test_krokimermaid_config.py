"""
Test Kroki Mermaid provider configuration
"""

import sys
from pathlib import Path

# Add backend to path
backend_dir = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(backend_dir))

from diagrams.provider_config import get_config_loader


def test_krokimermaid_config():
    """Test Kroki Mermaid provider configuration loading"""
    loader = get_config_loader()
    diagrams_root = Path(__file__).parent.parent.parent
    provider_folder = diagrams_root / "krokimermaid"

    config = loader.load_provider_config(provider_folder)

    assert config is not None, "Config should load successfully"
    assert config.provider_id == "krokimermaid"
    assert config.diagram_type == "mermaid"
    assert "svg" in config.supported_output_formats

    print("[OK] Kroki Mermaid configuration tests passed")


if __name__ == "__main__":
    test_krokimermaid_config()
