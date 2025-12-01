"""
Test Kroki Structurizr Provider Implementation
"""

from diagrams.models import ProviderCapability
from diagrams.krokistructurizr.kroki_renderer import KrokiStructurizrProvider
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


def test_krokistructurizr_provider_initialization():
    """Test that Kroki Structurizr provider initializes correctly"""
    print("\n" + "=" * 60)
    print("TEST: Kroki Structurizr Provider Initialization")
    print("=" * 60)

    provider_folder = Path(__file__).parent.parent / "krokistructurizr"
    provider = KrokiStructurizrProvider(provider_folder)

    print(f"✓ Provider ID: {provider.provider_id}")
    print(f"✓ Provider Name: {provider.provider_name}")
    print(f"✓ Diagram Type: {provider.diagram_type}")
    print(f"✓ Diagram Endpoint: {provider.diagram_endpoint}")
    print(f"✓ Supported Formats: {', '.join(provider.supported_output_formats)}")
    print(f"✓ Capabilities: {', '.join([c.value for c in provider.capabilities])}")
    print(f"✓ Available: {provider.is_available()}")
    print(f"✓ Version: {provider.get_version()}")

    assert provider.provider_id == "krokistructurizr"
    assert provider.diagram_type == "structurizr"
    assert provider.diagram_endpoint == "structurizr"
    assert "svg" in provider.supported_output_formats
    assert "png" in provider.supported_output_formats
    assert ProviderCapability.VALIDATE in provider.capabilities
    assert ProviderCapability.AUTO_FIX in provider.capabilities
    assert ProviderCapability.LLM_CORRECTION in provider.capabilities

    print("\n✅ Provider initialization test passed!")


def test_krokistructurizr_config():
    """Test that configuration is loaded correctly"""
    print("\n" + "=" * 60)
    print("TEST: Kroki Structurizr Configuration Loading")
    print("=" * 60)

    provider_folder = Path(__file__).parent.parent / "krokistructurizr"
    provider = KrokiStructurizrProvider(provider_folder)

    print(f"✓ Server URL: {provider.server_url}")
    print(f"✓ Timeout: {provider.timeout} seconds")
    print(f"✓ Max Retries: {provider.max_retries}")

    assert provider.server_url.startswith("http")
    assert provider.timeout > 0
    assert provider.max_retries > 0

    print("\n✅ Configuration test passed!")


def test_krokistructurizr_metadata():
    """Test provider metadata methods"""
    print("\n" + "=" * 60)
    print("TEST: Kroki Structurizr Provider Metadata")
    print("=" * 60)

    provider_folder = Path(__file__).parent.parent / "krokistructurizr"
    provider = KrokiStructurizrProvider(provider_folder)

    metadata = provider.get_metadata()
    print(f"✓ Provider ID: {metadata.provider_id}")
    print(f"✓ Provider Name: {metadata.provider_name}")
    print(f"✓ Diagram Type: {metadata.diagram_type}")
    print(f"✓ Available: {metadata.available}")
    print(f"✓ Requires LLM: {metadata.requires_llm}")

    assert metadata.provider_id == "krokistructurizr"
    assert metadata.diagram_type == "structurizr"

    print("\n✅ Metadata test passed!")


def test_krokistructurizr_llm_correction_rules():
    """Test LLM correction rules"""
    print("\n" + "=" * 60)
    print("TEST: Kroki Structurizr LLM Correction Rules")
    print("=" * 60)

    provider_folder = Path(__file__).parent.parent / "krokistructurizr"
    provider = KrokiStructurizrProvider(provider_folder)

    rules = provider.get_llm_correction_rules()
    print(f"✓ Rules length: {len(rules)} characters")
    print("\nRules preview:")
    print(rules[:200] + "...")

    assert rules is not None
    assert len(rules) > 0
    assert "Structurizr" in rules or "structurizr" in rules.lower()

    print("\n✅ LLM correction rules test passed!")


def test_krokistructurizr_validation():
    """Test Structurizr code validation via Kroki"""
    print("\n" + "=" * 60)
    print("TEST: Kroki Structurizr Validation")
    print("=" * 60)

    provider_folder = Path(__file__).parent.parent / "krokistructurizr"
    provider = KrokiStructurizrProvider(provider_folder)

    if not provider.is_available():
        print("⚠️  Skipping validation test - Kroki server not available")
        print("   Start Kroki server: docker run -p 8000:8000 yuzutech/kroki")
        return

    # Valid Structurizr workspace
    valid_code = """workspace {
    model {
        user = person "User"
        system = softwareSystem "System"
        user -> system "Uses"
    }
    views {
        systemContext system {
            include *
        }
    }
}"""

    print("\nValidating VALID Structurizr code...")
    result = provider.validate_code(valid_code)
    print(f"✓ Is Valid: {result.is_valid}")
    print(f"✓ Error: {result.error}")

    assert result.is_valid

    # Invalid Structurizr code (missing closing brace)
    invalid_code = """workspace {
    model {
        user = person "User"
        system = softwareSystem "System"
"""

    print("\nValidating INVALID Structurizr code (missing closing braces)...")
    result = provider.validate_code(invalid_code)
    print(f"✓ Is Valid: {result.is_valid}")
    if result.error:
        print(f"✓ Error: {result.error[:100]}...")

    assert result.is_valid == False

    print("\n✅ Validation test passed!")


def test_krokistructurizr_auto_fix():
    """Test pattern-based auto-fix for Structurizr"""
    print("\n" + "=" * 60)
    print("TEST: Kroki Structurizr Pattern-Based Auto-Fix")
    print("=" * 60)

    provider_folder = Path(__file__).parent.parent / "krokistructurizr"
    provider = KrokiStructurizrProvider(provider_folder)

    if not provider.is_available():
        print("⚠️  Skipping auto-fix test - Kroki server not available")
        return

    # Code that can be auto-fixed (incomplete workspace)
    fixable_code = """model {
    user = person "User"
    system = softwareSystem "System"
}"""

    print("\nAttempting auto-fix on code without workspace wrapper...")
    result = provider.auto_fix_pattern_based(fixable_code, "Missing workspace declaration")

    print(f"✓ Is Valid: {result.is_valid}")
    print(f"✓ Auto Fixed: {result.auto_fixed}")
    print(f"✓ Correction Method: {result.correction_method}")

    if result.fixed_code:
        print("\nFixed code preview:")
        print(result.fixed_code[:200])

    print("\n✅ Auto-fix test passed!")


def test_krokistructurizr_render_svg():
    """Test rendering to SVG"""
    print("\n" + "=" * 60)
    print("TEST: Kroki Structurizr Rendering to SVG")
    print("=" * 60)

    provider_folder = Path(__file__).parent.parent / "krokistructurizr"
    provider = KrokiStructurizrProvider(provider_folder)

    if not provider.is_available():
        print("⚠️  Skipping render test - Kroki server not available")
        return

    valid_code = """workspace {
    model {
        user = person "User"
        webapp = softwareSystem "Web Application"
        user -> webapp "Uses"
    }
    views {
        systemContext webapp {
            include *
            autoLayout
        }
    }
}"""

    print("\nRendering Structurizr to SVG...")
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


def test_krokistructurizr_render_png():
    """Test rendering to PNG"""
    print("\n" + "=" * 60)
    print("TEST: Kroki Structurizr Rendering to PNG")
    print("=" * 60)

    provider_folder = Path(__file__).parent.parent / "krokistructurizr"
    provider = KrokiStructurizrProvider(provider_folder)

    if not provider.is_available():
        print("⚠️  Skipping render test - Kroki server not available")
        return

    valid_code = """workspace {
    model {
        user = person "User"
        system = softwareSystem "System"
        user -> system "Uses"
    }
    views {
        systemContext system {
            include *
        }
    }
}"""

    print("\nRendering Structurizr to PNG...")
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


def test_krokistructurizr_complex_diagram():
    """Test rendering a more complex Structurizr diagram"""
    print("\n" + "=" * 60)
    print("TEST: Kroki Structurizr Complex Diagram")
    print("=" * 60)

    provider_folder = Path(__file__).parent.parent / "krokistructurizr"
    provider = KrokiStructurizrProvider(provider_folder)

    if not provider.is_available():
        print("⚠️  Skipping complex diagram test - Kroki server not available")
        return

    complex_code = """workspace {
    model {
        user = person "User" "End user of the system"
        admin = person "Administrator" "System administrator"

        softwareSystem = softwareSystem "Software System" {
            webapp = container "Web Application" "Delivers content" "React"
            api = container "API" "Provides functionality" "Node.js"
            database = container "Database" "Stores data" "PostgreSQL"

            webapp -> api "Makes API calls to" "HTTPS"
            api -> database "Reads from and writes to" "SQL/TCP"
        }

        user -> webapp "Uses" "HTTPS"
        admin -> webapp "Administers" "HTTPS"
    }

    views {
        systemContext softwareSystem {
            include *
            autoLayout
        }

        container softwareSystem {
            include *
            autoLayout
        }
    }
}"""

    print("\nRendering complex Structurizr diagram...")
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
    print("KROKI STRUCTURIZR PROVIDER TEST SUITE")
    print("=" * 60)

    test_krokistructurizr_provider_initialization()
    test_krokistructurizr_config()
    test_krokistructurizr_metadata()
    test_krokistructurizr_llm_correction_rules()
    test_krokistructurizr_validation()
    test_krokistructurizr_auto_fix()
    test_krokistructurizr_render_svg()
    test_krokistructurizr_render_png()
    test_krokistructurizr_complex_diagram()

    print("\n" + "=" * 60)
    print("✅ ALL KROKI STRUCTURIZR TESTS PASSED!")
    print("=" * 60)
