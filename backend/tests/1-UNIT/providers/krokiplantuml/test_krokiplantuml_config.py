"""
Test Kroki PlantUML provider configuration
"""

import sys
from pathlib import Path

# Add backend to path
backend_dir = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(backend_dir))

from diagrams.provider_config import get_config_loader


def test_krokiplantuml_config():
    """Test Kroki PlantUML provider configuration loading"""
    loader = get_config_loader()
    backend_root = Path(__file__).parent.parent.parent.parent.parent
    provider_folder = backend_root / "diagrams" / "krokiplantuml"

    config = loader.load_provider_config(provider_folder)

    assert config is not None, "Config should load successfully"
    assert config.provider_id == "krokiplantuml"
    assert config.diagram_type == "plantuml"
    assert "svg" in config.supported_output_formats

    print("[OK] Kroki PlantUML configuration tests passed")


if __name__ == "__main__":
    test_krokiplantuml_config()
