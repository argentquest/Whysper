import pytest
from pathlib import Path
import json
import tempfile
import shutil
from diagrams.provider_config import ProviderConfigLoader, RootConfig, ProviderConfig

@pytest.fixture
def temp_diagrams_dir():
    """Create a temporary directory simulating the diagrams folder"""
    with tempfile.TemporaryDirectory() as tmpdirname:
        path = Path(tmpdirname)
        yield path

def test_load_defaults(temp_diagrams_dir):
    """Test that loader creates and loads default root config"""
    loader = ProviderConfigLoader(temp_diagrams_dir)
    config = loader.get_root_config()

    assert config is not None
    assert config.version == "1.0"
    # Verify file was created
    assert (temp_diagrams_dir / "config.json").exists()

def test_load_provider_config_merge(temp_diagrams_dir):
    """Test merging root defaults with provider overrides"""
    loader = ProviderConfigLoader(temp_diagrams_dir)

    # Create a dummy provider directory
    p_dir = temp_diagrams_dir / "my_provider"
    p_dir.mkdir()

    # Create provider config with an override
    p_config_data = {
        "provider_id": "my_provider",
        "provider_name": "My Provider",
        "diagram_type": "custom",
        "supported_output_formats": ["svg", "json"],
        "overrides": {
            "validation": {"timeout_seconds": 500},
            "llm_correction": {"enabled": False}
        }
    }

    with open(p_dir / "config.json", "w") as f:
        json.dump(p_config_data, f)

    # Load
    config = loader.load_provider_config(p_dir)

    assert config is not None
    assert config.provider_id == "my_provider"
    assert config.diagram_type == "custom"

    # Check override
    assert config.validation.timeout_seconds == 500
    assert config.llm_correction.enabled is False

    # Check default was preserved where not overridden
    # Default rendering timeout is 120
    assert config.rendering.timeout_seconds == 120

def test_minimal_config_creation(temp_diagrams_dir):
    """Test creation of minimal config when file is missing"""
    loader = ProviderConfigLoader(temp_diagrams_dir)
    p_dir = temp_diagrams_dir / "mermaid_v1" # implied type mermaid
    p_dir.mkdir()

    # No config.json exists
    config = loader.load_provider_config(p_dir)

    assert config is not None
    assert config.provider_id == "mermaid_v1"
    assert config.diagram_type == "mermaid" # Detected from name
    assert "svg" in config.supported_output_formats
