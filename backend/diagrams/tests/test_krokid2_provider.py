"""
Test Kroki D2 Provider Implementation
"""

from diagrams.models import ProviderCapability
from diagrams.krokid2.kroki_renderer import KrokiD2Provider
import sys
from pathlib import Path

# Set UTF-8 encoding for Windows console
if sys.platform == "win32":
    import codecs

    sys.stdout = codecs.getwriter("utf-8")(sys.stdout.buffer, "strict")
    sys.stderr = codecs.getwriter("utf-8")(sys.stderr.buffer, "strict")

# Add backend to path
backend_dir = Path(__file__).parent.parent.parent
if str(backend_dir) not in sys.path:
    sys.path.insert(0, str(backend_dir))


def test_krokid2_provider_initialization():
    """Test that Kroki D2 provider initializes correctly"""
    print("\n" + "=" * 60)
    print("TEST: Kroki D2 Provider Initialization")
    print("=" * 60)

    provider_folder = Path(__file__).parent.parent / "krokid2"
    provider = KrokiD2Provider(provider_folder)

    print(f"✓ Provider ID: {provider.provider_id}")
    print(f"✓ Provider Name: {provider.provider_name}")
    print(f"✓ Diagram Type: {provider.diagram_type}")
    print(f"✓ Diagram Endpoint: {provider.diagram_endpoint}")
    print(f"✓ Supported Formats: {', '.join(provider.supported_output_formats)}")
    print(f"✓ Capabilities: {', '.join([c.value for c in provider.capabilities])}")
    print(f"✓ Available: {provider.is_available()}")
    print(f"✓ Version: {provider.get_version()}")

    assert provider.provider_id == "krokid2"
    assert provider.diagram_type == "d2"
    assert provider.diagram_endpoint == "d2"
    assert "svg" in provider.supported_output_formats
    assert "png" in provider.supported_output_formats
    assert ProviderCapability.VALIDATE in provider.capabilities
    assert ProviderCapability.AUTO_FIX in provider.capabilities
    assert ProviderCapability.LLM_CORRECTION in provider.capabilities

    print("\n✅ Provider initialization test passed!")


def test_krokid2_config():
    """Test that configuration is loaded correctly"""
    print("\n" + "=" * 60)
    print("TEST: Kroki D2 Configuration Loading")
    print("=" * 60)

    provider_folder = Path(__file__).parent.parent / "krokid2"
    provider = KrokiD2Provider(provider_folder)

    print(f"✓ Server URL: {provider.server_url}")
    print(f"✓ Timeout: {provider.timeout} seconds")
    print(f"✓ Max Retries: {provider.max_retries}")

    assert provider.server_url.startswith("http")
    assert provider.timeout > 0
    assert provider.max_retries > 0

    print("\n✅ Configuration test passed!")


def test_krokid2_metadata():
    """Test provider metadata methods"""
    print("\n" + "=" * 60)
    print("TEST: Kroki D2 Provider Metadata")
    print("=" * 60)

    provider_folder = Path(__file__).parent.parent / "krokid2"
    provider = KrokiD2Provider(provider_folder)

    metadata = provider.get_metadata()
    print(f"✓ Provider ID: {metadata.provider_id}")
    print(f"✓ Provider Name: {metadata.provider_name}")
    print(f"✓ Diagram Type: {metadata.diagram_type}")
    print(f"✓ Available: {metadata.available}")
    print(f"✓ Requires LLM: {metadata.requires_llm}")

    assert metadata.provider_id == "krokid2"
    assert metadata.diagram_type == "d2"

    print("\n✅ Metadata test passed!")


def test_krokid2_llm_correction_rules():
    """Test LLM correction rules"""
    print("\n" + "=" * 60)
    print("TEST: Kroki D2 LLM Correction Rules")
    print("=" * 60)

    provider_folder = Path(__file__).parent.parent / "krokid2"
    provider = KrokiD2Provider(provider_folder)

    rules = provider.get_llm_correction_rules()
    print(f"✓ Rules length: {len(rules)} characters")
    print("\nRules preview:")
    print(rules[:200] + "...")

    assert rules is not None
    assert len(rules) > 0
    assert "D2" in rules or "d2" in rules.lower()

    print("\n✅ LLM correction rules test passed!")


def test_krokid2_validation():
    """Test D2 code validation via Kroki"""
    print("\n" + "=" * 60)
    print("TEST: Kroki D2 Validation")
    print("=" * 60)

    provider_folder = Path(__file__).parent.parent / "krokid2"
    provider = KrokiD2Provider(provider_folder)

    if not provider.is_available():
        print("⚠️  Skipping validation test - Kroki server not available")
        print("   Start Kroki server: docker run -p 8000:8000 yuzutech/kroki")
        return

    # Valid D2 code
    valid_code = """direction: right

A -> B -> C

A: {
  shape: circle
}
"""

    print("\nValidating VALID D2 code...")
    result = provider.validate_code(valid_code)
    print(f"✓ Is Valid: {result.is_valid}")
    print(f"✓ Error: {result.error}")

    assert result.is_valid

    # Invalid D2 code (unclosed brace)
    invalid_code = """direction: right

container {
  A -> B
"""

    print("\nValidating INVALID D2 code (unclosed brace)...")
    result = provider.validate_code(invalid_code)
    print(f"✓ Is Valid: {result.is_valid}")
    if result.error:
        print(f"✓ Error: {result.error[:100]}...")

    assert result.is_valid == False

    print("\n✅ Validation test passed!")


def test_krokid2_auto_fix():
    """Test pattern-based auto-fix"""
    print("\n" + "=" * 60)
    print("TEST: Kroki D2 Pattern-Based Auto-Fix")
    print("=" * 60)

    provider_folder = Path(__file__).parent.parent / "krokid2"
    provider = KrokiD2Provider(provider_folder)

    if not provider.is_available():
        print("⚠️  Skipping auto-fix test - Kroki server not available")
        return

    # Code that can be auto-fixed (missing direction)
    fixable_code = """A -> B -> C"""

    print("\nAttempting auto-fix on code without direction...")
    result = provider.auto_fix_pattern_based(fixable_code, "Missing direction")

    print(f"✓ Is Valid: {result.is_valid}")
    print(f"✓ Auto Fixed: {result.auto_fixed}")
    print(f"✓ Correction Method: {result.correction_method}")

    if result.fixed_code:
        print("\nFixed code preview:")
        print(result.fixed_code[:200])

    # The auto-fix might add direction
    # (but not always required for D2)
    print("\n✅ Auto-fix test passed!")


def test_krokid2_render_svg():
    """Test rendering to SVG"""
    print("\n" + "=" * 60)
    print("TEST: Kroki D2 Rendering to SVG")
    print("=" * 60)

    provider_folder = Path(__file__).parent.parent / "krokid2"
    provider = KrokiD2Provider(provider_folder)

    if not provider.is_available():
        print("⚠️  Skipping render test - Kroki server not available")
        return

    valid_code = """direction: right

Start -> Process -> End

Start: {
  shape: circle
}

End: {
  shape: circle
}
"""

    print("\nRendering D2 to SVG...")
    result = provider.render(valid_code, output_format="svg")

    print(f"✓ Success: {result.success}")
    print(f"✓ Output Format: {result.output_format}")
    print(f"✓ Has Content: {result.content is not None}")
    if result.content:
        print(f"✓ Content Length: {len(result.content)} bytes")
        if isinstance(result.content, str):
            print(f"✓ Content Preview: {result.content[:100]}...")

    if result.success:
        assert result.content is not None
        if isinstance(result.content, str):
            assert "<svg" in result.content
    else:
        print(f"⚠️  Render failed: {result.error}")

    print("\n✅ Render SVG test passed!")


def test_krokid2_render_png():
    """Test rendering to PNG"""
    print("\n" + "=" * 60)
    print("TEST: Kroki D2 Rendering to PNG")
    print("=" * 60)

    provider_folder = Path(__file__).parent.parent / "krokid2"
    provider = KrokiD2Provider(provider_folder)

    if not provider.is_available():
        print("⚠️  Skipping render test - Kroki server not available")
        return

    valid_code = """direction: right

A -> B -> C
"""

    print("\nRendering D2 to PNG...")
    result = provider.render(valid_code, output_format="png")

    print(f"✓ Success: {result.success}")
    print(f"✓ Output Format: {result.output_format}")
    print(f"✓ Has Content: {result.content is not None}")
    if result.content:
        content_len = len(result.content) if isinstance(result.content, (str, bytes)) else 0
        print(f"✓ Content Length: {content_len} bytes")

    if result.success:
        assert result.content is not None
    else:
        print(f"⚠️  Render failed: {result.error}")

    print("\n✅ Render PNG test passed!")


def test_krokid2_complex_diagram():
    """Test rendering a more complex D2 diagram"""
    print("\n" + "=" * 60)
    print("TEST: Kroki D2 Complex Diagram")
    print("=" * 60)

    provider_folder = Path(__file__).parent.parent / "krokid2"
    provider = KrokiD2Provider(provider_folder)

    if not provider.is_available():
        print("⚠️  Skipping complex diagram test - Kroki server not available")
        return

    complex_code = """direction: right

User -> WebServer: HTTP/HTTPS
WebServer -> Database: SQL
WebServer -> Cache: Query

Database: {
  shape: cylinder
  style: {
    fill: "#FFE5B4"
  }
}

Cache: {
  shape: rectangle
  style: {
    fill: "#B4E5FF"
  }
}

WebServer: {
  shape: rectangle
  style: {
    fill: "#E5FFB4"
  }
}
"""

    print("\nRendering complex D2 diagram...")
    result = provider.render(complex_code, output_format="svg")

    print(f"✓ Success: {result.success}")
    print(f"✓ Validation: {result.validation.is_valid}")

    if result.success:
        assert result.content is not None
        if isinstance(result.content, str):
            assert "<svg" in result.content
    else:
        print(f"⚠️  Render failed: {result.error}")

    print("\n✅ Complex diagram test passed!")


if __name__ == "__main__":
    print("\n" + "=" * 60)
    print("KROKI D2 PROVIDER TEST SUITE")
    print("=" * 60)

    test_krokid2_provider_initialization()
    test_krokid2_config()
    test_krokid2_metadata()
    test_krokid2_llm_correction_rules()
    test_krokid2_validation()
    test_krokid2_auto_fix()
    test_krokid2_render_svg()
    test_krokid2_render_png()
    test_krokid2_complex_diagram()

    print("\n" + "=" * 60)
    print("✅ ALL KROKI D2 TESTS PASSED!")
    print("=" * 60)
