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

# Add backend to path
backend_dir = Path(__file__).parent.parent.parent
sys.path.insert(0, str(backend_dir))

from diagrams.provider_config import get_config_loader
import json


def test_root_config():
    """Test loading root configuration"""
    print("=" * 60)
    print("TEST 1: Root Configuration")
    print("=" * 60)

    loader = get_config_loader()
    root_config = loader.get_root_config()

    print(f"[OK] Root config loaded successfully")
    print(f"   Version: {root_config.version}")
    print(f"   LLM max retries (default): {root_config.defaults.llm_correction.max_retries}")
    print(f"   Correction strategy (default): {root_config.defaults.correction_strategy}")
    print(f"   Session timeout (default): {root_config.defaults.user_correction.session_timeout_seconds}s")
    print()


@pytest.mark.parametrize("provider_name", ["mermaidv1", "d2v1"])
def test_provider_config(provider_name: str):
    """Test loading provider configuration"""
    loader = get_config_loader()
    backend_root = Path(__file__).parent.parent.parent.parent
    provider_folder = backend_root / "diagrams" / provider_name

    # Provider folder should exist
    assert provider_folder.exists(), \
        f"Provider folder not found: {provider_folder}"

    # Config should load successfully
    config = loader.load_provider_config(provider_folder)
    assert config is not None, f"Failed to load {provider_name} config"

    # Basic provider info
    assert config.provider_id
    assert config.provider_name
    assert config.diagram_type
    assert config.supported_output_formats

    # Config should have all expected fields
    assert config.llm_correction
    assert config.pattern_correction
    assert config.correction_strategy
    assert config.user_correction
    assert config.validation
    assert config.batch


def test_config_comparison():
    """Test config comparison to see what's overridden"""
    print("=" * 60)
    print("TEST: Configuration Override Comparison")
    print("=" * 60)

    loader = get_config_loader()
    root_config = loader.get_root_config()
    backend_root = Path(__file__).parent.parent.parent.parent

    for provider_name in ["mermaidv1", "d2v1"]:
        provider_folder = backend_root / "diagrams" / provider_name
        if not provider_folder.exists():
            continue

        config = loader.load_provider_config(provider_folder)
        if not config:
            continue

        print(f"\n{provider_name} Overrides:")
        print("-" * 40)

        # Compare LLM settings
        defaults = root_config.defaults
        if config.llm_correction.max_retries != defaults.llm_correction.max_retries:
            print(f"  llm_correction.max_retries: {defaults.llm_correction.max_retries} -> {config.llm_correction.max_retries} [OVERRIDDEN]")

        if config.llm_correction.temperature != defaults.llm_correction.temperature:
            print(f"  llm_correction.temperature: {defaults.llm_correction.temperature} -> {config.llm_correction.temperature} [OVERRIDDEN]")

        if config.llm_correction.max_tokens != defaults.llm_correction.max_tokens:
            print(f"  llm_correction.max_tokens: {defaults.llm_correction.max_tokens} -> {config.llm_correction.max_tokens} [OVERRIDDEN]")

        # Compare validation settings
        if config.validation.timeout_seconds != defaults.validation.timeout_seconds:
            print(f"  validation.timeout_seconds: {defaults.validation.timeout_seconds} -> {config.validation.timeout_seconds} [OVERRIDDEN]")

        # Compare batch settings
        if config.batch.enabled != defaults.batch.enabled:
            print(f"  batch.enabled: {defaults.batch.enabled} -> {config.batch.enabled} [OVERRIDDEN]")

        if config.batch.max_items != defaults.batch.max_items:
            print(f"  batch.max_items: {defaults.batch.max_items} -> {config.batch.max_items} [OVERRIDDEN]")

        # Show custom settings
        if config.custom:
            print(f"  custom: {len(config.custom)} custom settings defined [OK]")

    print()


def test_extract_overrides():
    """Test extracting only overridden values"""
    print("=" * 60)
    print("TEST: Extract Overrides (Minimal Config)")
    print("=" * 60)

    loader = get_config_loader()
    backend_root = Path(__file__).parent.parent.parent.parent

    for provider_name in ["mermaidv1", "d2v1"]:
        provider_folder = backend_root / "diagrams" / provider_name
        if not provider_folder.exists():
            continue

        config = loader.load_provider_config(provider_folder)
        if not config:
            continue

        # Extract minimal config (only overrides)
        minimal = loader._extract_overrides(config)

        print(f"\n{provider_name} Minimal Config (what would be saved):")
        print("-" * 40)
        print(json.dumps(minimal, indent=2))

    print()


def main():
    """Run all tests"""
    print("\n")
    print("=" * 60)
    print("DIAGRAM PROVIDER CONFIGURATION SYSTEM TEST")
    print("=" * 60)
    print()

    try:
        # Test 1: Root config
        test_root_config()

        # Test 2: Provider configs
        test_provider_config("mermaidv1")
        test_provider_config("d2v1")

        # Test 3: Config comparison
        test_config_comparison()

        # Test 4: Extract overrides
        test_extract_overrides()

        print("=" * 60)
        print("[SUCCESS] ALL TESTS COMPLETED SUCCESSFULLY")
        print("=" * 60)
        print()

    except Exception as e:
        print(f"\n[ERROR] TEST FAILED: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
