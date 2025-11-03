"""
Test Kroki D2 provider configuration
"""

import sys
from pathlib import Path

# Add backend to path
backend_dir = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(backend_dir))

from diagrams.provider_config import get_config_loader


def test_krokid2_config():
    """Test Kroki D2 provider configuration loading"""
    loader = get_config_loader()
    diagrams_root = Path(__file__).parent.parent.parent
    provider_folder = diagrams_root / "krokid2"

    config = loader.load_provider_config(provider_folder)

    assert config is not None, "Config should load successfully"
    assert config.provider_id == "krokid2"
    assert config.diagram_type == "d2"
    assert "svg" in config.supported_output_formats

    print("[OK] Kroki D2 configuration tests passed")


if __name__ == "__main__":
    test_krokid2_config()
