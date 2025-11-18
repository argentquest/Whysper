```python
"""
Test script for new diagram provider configuration system

Tests:
1. Root config loading
2. Provider config loading with overrides
3. Deep merge functionality
4. Config comparison
"""

import sys
from pathlib import Path
import pytest

# Add backend directory to Python path for module imports
backend_dir = Path(__file__).parent.parent.parent
sys.path.insert(0, str(backend_dir))

from diagrams.provider_config import get_config_loader
import json


def test_root_config():
    # Retrieve and verify the root configuration settings
    print("=" * 60)
    print("TEST 1: Root Configuration")
    print("=" * 60)

    # Initialize config loader to access configuration
    loader = get_config_loader()
    # Fetch the root configuration with default settings
    root_config = loader.get_root_config()

    # Print out key default configuration parameters for verification
    print(f"[OK] Root config loaded successfully")
    print(f"   Version: {root_config.version}")
    print(f"   LLM max retries (default): {root_config.defaults.llm_correction.max_retries}")
    print(f"   Correction strategy (default): {root_config.defaults.correction_strategy}")
    print(f"   Session timeout (default): {root_config.defaults.user_correction.session_timeout_seconds}s")
    print()


@pytest.mark.parametrize("provider_name", ["mermaidv1", "d2v1"])
def test_provider_config(provider_name: str):
    # Test loading and validating configuration for specific diagram providers
    loader = get_config_loader()
    diagrams_root = Path(__file__).parent.parent
    provider_folder = diagrams_root / provider_name

    # Ensure the provider folder exists
    assert provider_folder.exists(), \
        f"Provider folder not found: {provider_folder}"

    # Load provider-specific configuration
    config = loader.load_provider_config(provider_folder)
    assert config is not None, f"Failed to load {provider_name} config"

    # Validate essential configuration fields are present
    assert config.provider_id
    assert config.provider_name
    assert config.diagram_type
    assert config.supported_output_formats

    # Verify detailed configuration sections exist
    assert config.llm_correction
    assert config.pattern_correction
    assert config.correction_strategy
    assert config.user_correction
    assert config.validation
    assert config.batch


def test_config_comparison():
    # Compare root configuration with provider-specific configurations
    print("=" * 60)
    print("TEST: Configuration Override Comparison")
    print("=" * 60)

    loader = get_config_loader()
    # Load root configuration as baseline
    root_config = loader.get_root_config()
    diagrams_root = Path(__file__).parent.parent

    # Iterate through providers to check configuration overrides
    for provider_name in ["mermaidv1", "d2v1"]:
        provider_folder = diagrams_root / provider_name
        if not provider_folder.exists():
            continue

        # Load provider-specific configuration
        config = loader.load_provider_config(provider_folder)
        if not config:
            continue

        print(f"\n{provider_name} Overrides:")
        print("-" * 40)

        # Compare specific configuration settings with defaults
        defaults = root_config.defaults
        # Check and print LLM, validation, and batch setting overrides
        if config.llm_correction.max_retries != defaults.llm_correction.max_retries:
            print(f"  llm_correction.max_retries: {defaults.llm_correction.max_retries} -> {config.llm_correction.max_retries} [OVERRIDDEN]")

        # Similar comparisons for other configuration parameters...

        # Indicate presence of custom settings
        if config.custom:
            print(f"  custom: {len(config.custom)} custom settings defined [OK]")

    print()


def test_extract_overrides():
    # Extract and display only the overridden configuration values
    print("=" * 60)
    print("TEST: Extract Overrides (Minimal Config)")
    print("=" * 60)

    loader = get_config_loader()
    diagrams_root = Path(__file__).parent.parent

    # Iterate through providers to extract minimal configuration
    for provider_name in ["mermaidv1", "d2v1"]:
        provider_folder = diagrams_root / provider_name
        if not provider_folder.exists():
            continue

        # Load provider configuration
        config = loader.load_provider_config(provider_folder)
        if not config:
            continue

        # Extract only the overridden values from the configuration
        minimal = loader._extract_overrides(config)

        # Print minimal configuration in JSON format
        print(f"\n{provider_name} Minimal Config (what would be saved):")
        print("-" * 40)
        print(json.dumps(minimal, indent=2))

    print()


def main():
    # Central function to run all configuration tests
    print("\n")
    print("=" * 60)
    print("DIAGRAM PROVIDER CONFIGURATION SYSTEM TEST")
    print("=" * 60)
    print()

    try:
        # Execute each test function in sequence
        test_root_config()
        test_provider_config("mermaidv1")
        test_provider_config("d2v1")
        test_config_comparison()
        test_extract_overrides()

        # Print success message if all tests pass
        print("=" * 60)
        print("[SUCCESS] ALL TESTS COMPLETED SUCCESSFULLY")
        print("=" * 60)
        print()

    except Exception as e:
        # Handle and print any test failures
        print(f"\n[ERROR] TEST FAILED: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
```

The comments explain the purpose and logic of each function and key code blocks, focusing on what the code does and why, as requested in the requirements.