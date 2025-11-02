"""
Test Mermaid v1 Provider Implementation
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

from diagrams.mermaidv1.mermaid_renderer import MermaidV1Provider
from diagrams.models import ProviderCapability


def test_mermaidv1_provider_initialization():
    """Test that mermaidv1 provider initializes correctly"""
    print("\n" + "="*60)
    print("TEST: Mermaid v1 Provider Initialization")
    print("="*60)

    provider_folder = Path(__file__).parent.parent / "mermaidv1"
    provider = MermaidV1Provider(provider_folder)

    print(f"✓ Provider ID: {provider.provider_id}")
    print(f"✓ Provider Name: {provider.provider_name}")
    print(f"✓ Diagram Type: {provider.diagram_type}")
    print(f"✓ Supported Formats: {', '.join(provider.supported_output_formats)}")
    print(f"✓ Capabilities: {', '.join([c.value for c in provider.capabilities])}")
    print(f"✓ Available: {provider.is_available()}")
    print(f"✓ Version: {provider.get_version()}")

    assert provider.provider_id == "mermaidv1"
    assert provider.diagram_type == "mermaid"
    assert "svg" in provider.supported_output_formats
    assert ProviderCapability.VALIDATE in provider.capabilities
    assert ProviderCapability.AUTO_FIX in provider.capabilities

    print("\n✅ Provider initialization test passed!")
    return provider


def test_mermaidv1_validation():
    """Test Mermaid code validation"""
    print("\n" + "="*60)
    print("TEST: Mermaid v1 Validation")
    print("="*60)

    provider_folder = Path(__file__).parent.parent / "mermaidv1"
    provider = MermaidV1Provider(provider_folder)

    if not provider.is_available():
        print("⚠️  Skipping validation test - Mermaid CLI not available")
        return

    # Valid Mermaid code
    valid_code = """flowchart TD
    A[Start] --> B[Process]
    B --> C[End]
"""

    print("\nValidating VALID Mermaid code...")
    result = provider.validate_code(valid_code)
    print(f"✓ Is Valid: {result.is_valid}")
    print(f"✓ Error: {result.error}")

    assert result.is_valid == True
    assert result.error is None

    # Invalid Mermaid code
    invalid_code = """flowchart TD
    A[Start] -> B[Process]
    B -> C[End]
"""

    print("\nValidating INVALID Mermaid code...")
    result = provider.validate_code(invalid_code)
    print(f"✓ Is Valid: {result.is_valid}")
    print(f"✓ Error: {result.error[:100] if result.error else None}...")

    assert result.is_valid == False
    assert result.error is not None

    print("\n✅ Validation test passed!")


def test_mermaidv1_auto_fix():
    """Test pattern-based auto-fix"""
    print("\n" + "="*60)
    print("TEST: Mermaid v1 Pattern-Based Auto-Fix")
    print("="*60)

    provider_folder = Path(__file__).parent.parent / "mermaidv1"
    provider = MermaidV1Provider(provider_folder)

    if not provider.is_available():
        print("⚠️  Skipping auto-fix test - Mermaid CLI not available")
        return

    # Code that can be auto-fixed (missing diagram type)
    fixable_code = """A[Start] --> B[Process]
    B --> C[End]
"""

    print("\nAttempting auto-fix on code without diagram type...")
    result = provider.auto_fix_pattern_based(fixable_code, "Missing diagram type")

    print(f"✓ Is Valid: {result.is_valid}")
    print(f"✓ Auto Fixed: {result.auto_fixed}")
    print(f"✓ Correction Method: {result.correction_method}")

    if result.fixed_code:
        print(f"\nFixed code preview:")
        print(result.fixed_code[:200])

    print("\n✅ Auto-fix test passed!")


def test_mermaidv1_render():
    """Test rendering to SVG"""
    print("\n" + "="*60)
    print("TEST: Mermaid v1 Rendering")
    print("="*60)

    provider_folder = Path(__file__).parent.parent / "mermaidv1"
    provider = MermaidV1Provider(provider_folder)

    if not provider.is_available():
        print("⚠️  Skipping render test - Mermaid CLI not available")
        return

    valid_code = """flowchart TD
    A[Start] --> B[Process]
    B --> C[End]
"""

    print("\nRendering to SVG...")
    result = provider.render(valid_code, output_format="svg")

    print(f"✓ Success: {result.success}")
    print(f"✓ Output Format: {result.output_format}")
    print(f"✓ Content Length: {len(result.content) if result.content else 0} bytes")
    print(f"✓ Error: {result.error}")

    assert result.success == True
    assert result.content is not None
    assert "<svg" in result.content

    print("\n✅ Render test passed!")


def test_mermaidv1_config():
    """Test configuration loading"""
    print("\n" + "="*60)
    print("TEST: Mermaid v1 Configuration")
    print("="*60)

    provider_folder = Path(__file__).parent.parent / "mermaidv1"
    provider = MermaidV1Provider(provider_folder)

    config = provider.get_config()

    print(f"✓ Provider ID: {config.provider_id}")
    print(f"✓ Provider Name: {config.provider_name}")
    print(f"✓ LLM Max Retries: {config.llm_correction.max_retries}")
    print(f"✓ LLM Temperature: {config.llm_correction.temperature}")
    print(f"✓ Validation Timeout: {config.validation.timeout_seconds}s")
    print(f"✓ Correction Strategy: {config.correction_strategy}")

    assert config.provider_id == "mermaidv1"
    assert config.llm_correction.max_retries == 5  # From mermaidv1/config.json override

    print("\n✅ Configuration test passed!")


def test_mermaidv1_metadata():
    """Test provider metadata"""
    print("\n" + "="*60)
    print("TEST: Mermaid v1 Metadata")
    print("="*60)

    provider_folder = Path(__file__).parent.parent / "mermaidv1"
    provider = MermaidV1Provider(provider_folder)

    metadata = provider.get_metadata()

    print(f"✓ Provider ID: {metadata.provider_id}")
    print(f"✓ Provider Name: {metadata.provider_name}")
    print(f"✓ Diagram Type: {metadata.diagram_type}")
    print(f"✓ Supported Formats: {', '.join(metadata.supported_output_formats)}")
    print(f"✓ Capabilities: {', '.join([c.value for c in metadata.capabilities])}")
    print(f"✓ Version: {metadata.version}")
    print(f"✓ Available: {metadata.available}")
    print(f"✓ Requires LLM: {metadata.requires_llm}")

    assert metadata.provider_id == "mermaidv1"
    assert metadata.diagram_type == "mermaid"
    assert metadata.requires_llm == True  # Has LLM_CORRECTION capability

    print("\n✅ Metadata test passed!")


if __name__ == "__main__":
    print("\n" + "="*60)
    print("MERMAID V1 PROVIDER TEST SUITE")
    print("="*60)

    try:
        provider = test_mermaidv1_provider_initialization()
        test_mermaidv1_config()
        test_mermaidv1_metadata()
        test_mermaidv1_validation()
        test_mermaidv1_auto_fix()
        test_mermaidv1_render()

        print("\n" + "="*60)
        print("✅ ALL TESTS PASSED!")
        print("="*60)

    except Exception as e:
        print(f"\n❌ TEST FAILED: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
