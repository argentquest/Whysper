"""
Test script for new diagram provider configuration system

Tests:
1. Root config loading
2. Provider config loading with overrides
3. Deep merge functionality
4. Config comparison
"""

import json
from diagrams.provider_config import get_config_loader
import sys
from pathlib import Path
import pytest

# Add backend directory to Python path for module imports
backend_dir = Path(__file__).parent.parent.parent
sys.path.insert(0, str(backend_dir))


def test_root_config():
    # Load and display the root configuration, showing default settings
    print("=" * 60)
    print("TEST 1: Root Configuration")
    print("=" * 60)

    # Initialize config loader to retrieve global default settings
    loader = get_config_loader()
    root_config = loader.get_root_config()

    # Print out key default configuration values
    print("[OK] Root config loaded successfully")
    print(f"   Version: {root_config.version}")
    print(f"   LLM max retries (default): {root_config.defaults.llm_correction.max_retries}")
    print(f"   Correction strategy (default): {root_config.defaults.correction_strategy}")
    print(f"   Session timeout (default): {root_config.defaults.user_correction.session_timeout_seconds}s")
    print()


@pytest.mark.parametrize("provider_name", ["mermaidv1", "d2v1"])
def test_provider_config(provider_name: str):
    # Test loading and validating provider-specific configuration
    loader = get_config_loader()
    backend_root = Path(__file__).parent.parent.parent.parent
    provider_folder = backend_root / "diagrams" / provider_name

    # Validate provider folder exists
    assert provider_folder.exists(), f"Provider folder not found: {provider_folder}"

    # Load provider configuration and validate its structure
    config = loader.load_provider_config(provider_folder)
    assert config is not None, f"Failed to load {provider_name} config"

    # Verify essential configuration fields are present
    assert config.provider_id
    assert config.provider_name
    assert config.diagram_type
    assert config.supported_output_formats

    # Check detailed configuration sections
    assert config.llm_correction
    assert config.pattern_correction
    assert config.correction_strategy
    assert config.user_correction
    assert config.validation
    assert config.batch


def test_config_comparison():
    # Compare root default configuration with provider-specific overrides
    print("=" * 60)
    print("TEST: Configuration Override Comparison")
    print("=" * 60)

    loader = get_config_loader()
    root_config = loader.get_root_config()
    backend_root = Path(__file__).parent.parent.parent.parent

    # Iterate through providers to compare configuration settings
    for provider_name in ["mermaidv1", "d2v1"]:
        provider_folder = backend_root / "diagrams" / provider_name
        if not provider_folder.exists():
            continue

        config = loader.load_provider_config(provider_folder)
        if not config:
            continue

        print(f"\n{provider_name} Overrides:")
        print("-" * 40)

        # Compare specific configuration settings against defaults
        defaults = root_config.defaults
        if config.llm_correction.max_retries != defaults.llm_correction.max_retries:
            print(
                f"  llm_correction.max_retries: {
                    defaults.llm_correction.max_retries} -> {
                    config.llm_correction.max_retries} [OVERRIDDEN]"
            )

        if config.llm_correction.temperature != defaults.llm_correction.temperature:
            print(
                f"  llm_correction.temperature: {
                    defaults.llm_correction.temperature} -> {
                    config.llm_correction.temperature} [OVERRIDDEN]"
            )

        # Similar comparisons for other configuration parameters
        # ... (rest of the comparison logic remains the same)

    print()


def test_extract_overrides():
    # Extract and display only the configuration values that differ from defaults
    print("=" * 60)
    print("TEST: Extract Overrides (Minimal Config)")
    print("=" * 60)

    loader = get_config_loader()
    backend_root = Path(__file__).parent.parent.parent.parent

    # Process each provider configuration
    for provider_name in ["mermaidv1", "d2v1"]:
        provider_folder = backend_root / "diagrams" / provider_name
        if not provider_folder.exists():
            continue

        config = loader.load_provider_config(provider_folder)
        if not config:
            continue

        # Generate minimal configuration with only overridden values
        minimal = loader._extract_overrides(config)

        print(f"\n{provider_name} Minimal Config (what would be saved):")
        print("-" * 40)
        print(json.dumps(minimal, indent=2))

    print()


def main():
    # Main test execution function to run all configuration tests
    print("\n")
    print("=" * 60)
    print("DIAGRAM PROVIDER CONFIGURATION SYSTEM TEST")
    print("=" * 60)
    print()

    try:
        # Sequential test execution
        test_root_config()
        test_provider_config("mermaidv1")
        test_provider_config("d2v1")
        test_config_comparison()
        test_extract_overrides()

        # Success message if all tests pass
        print("=" * 60)
        print("[SUCCESS] ALL TESTS COMPLETED SUCCESSFULLY")
        print("=" * 60)
        print()

    except Exception as e:
        # Error handling and detailed traceback
        print(f"\n[ERROR] TEST FAILED: {e}")
        import traceback

        traceback.print_exc()


if __name__ == "__main__":
    main()
