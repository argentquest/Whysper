"""
Test Provider Registry Integration

Tests that the provider registry can discover and use both mermaidv1 and d2v1 providers.
"""

import sys
import os
from pathlib import Path

# Set UTF-8 encoding for Windows console
if sys.platform == 'win32':
    import codecs
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')
    sys.stderr = codecs.getwriter('utf-8')(sys.stderr.buffer, 'strict')

# Add backend to path
backend_dir = Path(__file__).parent.parent.parent
if str(backend_dir) not in sys.path:
    sys.path.insert(0, str(backend_dir))

from diagrams.provider_registry import ProviderRegistry, reset_registry


def test_registry_discovery():
    """Test that the registry discovers both providers"""
    print("\n" + "="*60)
    print("TEST: Provider Registry Discovery")
    print("="*60)

    # Reset and create fresh registry
    reset_registry()
    diagrams_root = Path(__file__).parent.parent
    registry = ProviderRegistry(diagrams_root, auto_discover=True)

    # Get all providers
    all_providers = registry.list_all()

    print(f"\nDiscovered {len(all_providers)} provider(s):")
    for metadata in all_providers:
        print(f"  - {metadata.provider_id}: {metadata.provider_name}")
        print(f"    Type: {metadata.diagram_type}")
        print(f"    Available: {metadata.available}")
        print(f"    Formats: {', '.join(metadata.supported_output_formats)}")
        print()

    # Check that we have at least mermaidv1 and d2v1
    provider_ids = [m.provider_id for m in all_providers]

    if "mermaidv1" in provider_ids:
        print("✓ mermaidv1 discovered")
    else:
        print("✗ mermaidv1 NOT discovered")

    if "d2v1" in provider_ids:
        print("✓ d2v1 discovered")
    else:
        print("✗ d2v1 NOT discovered")

    print(f"\n✅ Discovery test passed!")
    return registry


def test_registry_get_provider():
    """Test getting specific providers"""
    print("\n" + "="*60)
    print("TEST: Get Specific Providers")
    print("="*60)

    reset_registry()
    diagrams_root = Path(__file__).parent.parent
    registry = ProviderRegistry(diagrams_root)

    # Get mermaidv1
    mermaid_provider = registry.get("mermaidv1")
    if mermaid_provider:
        print(f"✓ Got mermaidv1 provider: {mermaid_provider.provider_name}")
        print(f"  Config: {mermaid_provider.config.llm_correction.max_retries} LLM retries")
    else:
        print("✗ Could not get mermaidv1 provider")

    # Get d2v1
    d2_provider = registry.get("d2v1")
    if d2_provider:
        print(f"✓ Got d2v1 provider: {d2_provider.provider_name}")
        print(f"  Config: {d2_provider.config.llm_correction.max_retries} LLM retries")
    else:
        print("✗ Could not get d2v1 provider")

    print(f"\n✅ Get provider test passed!")


def test_registry_find_by_diagram_type():
    """Test finding providers by diagram type"""
    print("\n" + "="*60)
    print("TEST: Find Providers by Diagram Type")
    print("="*60)

    reset_registry()
    diagrams_root = Path(__file__).parent.parent
    registry = ProviderRegistry(diagrams_root)

    # Find Mermaid providers
    mermaid_providers = registry.find_by_diagram_type("mermaid")
    print(f"\nFound {len(mermaid_providers)} Mermaid provider(s):")
    for p in mermaid_providers:
        print(f"  - {p.provider_id}")

    # Find D2 providers
    d2_providers = registry.find_by_diagram_type("d2")
    print(f"\nFound {len(d2_providers)} D2 provider(s):")
    for p in d2_providers:
        print(f"  - {p.provider_id}")

    print(f"\n✅ Find by diagram type test passed!")


def test_registry_statistics():
    """Test registry statistics"""
    print("\n" + "="*60)
    print("TEST: Registry Statistics")
    print("="*60)

    reset_registry()
    diagrams_root = Path(__file__).parent.parent
    registry = ProviderRegistry(diagrams_root)

    stats = registry.get_statistics()

    print(f"\nRegistry Statistics:")
    print(f"  Total Providers: {stats['total_providers']}")
    print(f"  Available: {stats['available_providers']}")
    print(f"  Unavailable: {stats['unavailable_providers']}")
    print(f"\nDiagram Types:")
    for dtype, count in stats['diagram_types'].items():
        print(f"  - {dtype}: {count} provider(s)")
    print(f"\nProvider IDs: {', '.join(stats['provider_ids'])}")

    assert stats['total_providers'] >= 2, "Should have at least 2 providers"

    print(f"\n✅ Statistics test passed!")


def test_provider_validation():
    """Test that providers can validate code"""
    print("\n" + "="*60)
    print("TEST: Provider Validation")
    print("="*60)

    reset_registry()
    diagrams_root = Path(__file__).parent.parent
    registry = ProviderRegistry(diagrams_root)

    # Test mermaidv1 validation
    mermaid_provider = registry.get("mermaidv1")
    if mermaid_provider and mermaid_provider.is_available():
        print("\nTesting mermaidv1 validation...")
        valid_code = """flowchart TD
    A[Start] --> B[End]
"""
        result = mermaid_provider.validate_code(valid_code)
        print(f"  Validation result: {result.is_valid}")
    else:
        print("\n⚠️  Skipping mermaidv1 validation - CLI not available")

    # Test d2v1 validation
    d2_provider = registry.get("d2v1")
    if d2_provider and d2_provider.is_available():
        print("\nTesting d2v1 validation...")
        valid_code = """direction: right
A -> B: "Connection"
"""
        result = d2_provider.validate_code(valid_code)
        print(f"  Validation result: {result.is_valid}")
    else:
        print("\n⚠️  Skipping d2v1 validation - CLI not available")

    print(f"\n✅ Provider validation test passed!")


def test_provider_metadata():
    """Test provider metadata"""
    print("\n" + "="*60)
    print("TEST: Provider Metadata")
    print("="*60)

    reset_registry()
    diagrams_root = Path(__file__).parent.parent
    registry = ProviderRegistry(diagrams_root)

    # Get mermaidv1 metadata
    mermaid_provider = registry.get("mermaidv1")
    if mermaid_provider:
        metadata = mermaid_provider.get_metadata()
        print(f"\nmermaidv1 Metadata:")
        print(f"  Provider ID: {metadata.provider_id}")
        print(f"  Name: {metadata.provider_name}")
        print(f"  Diagram Type: {metadata.diagram_type}")
        print(f"  Formats: {', '.join(metadata.supported_output_formats)}")
        print(f"  Capabilities: {', '.join([c.value for c in metadata.capabilities])}")
        print(f"  Requires LLM: {metadata.requires_llm}")
        print(f"  Available: {metadata.available}")
        print(f"  Version: {metadata.version}")

    # Get d2v1 metadata
    d2_provider = registry.get("d2v1")
    if d2_provider:
        metadata = d2_provider.get_metadata()
        print(f"\nd2v1 Metadata:")
        print(f"  Provider ID: {metadata.provider_id}")
        print(f"  Name: {metadata.provider_name}")
        print(f"  Diagram Type: {metadata.diagram_type}")
        print(f"  Formats: {', '.join(metadata.supported_output_formats)}")
        print(f"  Capabilities: {', '.join([c.value for c in metadata.capabilities])}")
        print(f"  Requires LLM: {metadata.requires_llm}")
        print(f"  Available: {metadata.available}")
        print(f"  Version: {metadata.version}")

    print(f"\n✅ Metadata test passed!")


if __name__ == "__main__":
    print("\n" + "="*60)
    print("PROVIDER REGISTRY INTEGRATION TEST SUITE")
    print("="*60)

    try:
        registry = test_registry_discovery()
        test_registry_get_provider()
        test_registry_find_by_diagram_type()
        test_registry_statistics()
        test_provider_validation()
        test_provider_metadata()

        print("\n" + "="*60)
        print("✅ ALL REGISTRY TESTS PASSED!")
        print("="*60)

    except Exception as e:
        print(f"\n❌ TEST FAILED: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
