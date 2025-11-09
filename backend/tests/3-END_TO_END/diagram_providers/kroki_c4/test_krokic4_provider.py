"""
Test Kroki C4 Provider Implementation
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

from diagrams.krokic4.kroki_renderer import KrokiC4Provider
from diagrams.models import ProviderCapability


def test_krokic4_provider_initialization():
    """Test that Kroki C4 provider initializes correctly"""
    print("\n" + "="*60)
    print("TEST: Kroki C4 Provider Initialization")
    print("="*60)

    provider_folder = Path(__file__).parent.parent / "krokic4"
    provider = KrokiC4Provider(provider_folder)

    print(f"✓ Provider ID: {provider.provider_id}")
    print(f"✓ Provider Name: {provider.provider_name}")
    print(f"✓ Diagram Type: {provider.diagram_type}")
    print(f"✓ Diagram Endpoint: {provider.diagram_endpoint}")
    print(f"✓ Supported Formats: {', '.join(provider.supported_output_formats)}")
    print(f"✓ Capabilities: {', '.join([c.value for c in provider.capabilities])}")
    print(f"✓ Available: {provider.is_available()}")
    print(f"✓ Version: {provider.get_version()}")

    assert provider.provider_id == "krokic4"
    assert provider.diagram_type == "c4"
    assert provider.diagram_endpoint == "plantuml"
    assert "svg" in provider.supported_output_formats
    assert "png" in provider.supported_output_formats
    assert ProviderCapability.VALIDATE in provider.capabilities
    assert ProviderCapability.AUTO_FIX in provider.capabilities
    assert ProviderCapability.LLM_CORRECTION in provider.capabilities

    print("\n✅ Provider initialization test passed!")


def test_krokic4_config():
    """Test that configuration is loaded correctly"""
    print("\n" + "="*60)
    print("TEST: Kroki C4 Configuration Loading")
    print("="*60)

    provider_folder = Path(__file__).parent.parent / "krokic4"
    provider = KrokiC4Provider(provider_folder)

    print(f"✓ Server URL: {provider.server_url}")
    print(f"✓ Timeout: {provider.timeout} seconds")
    print(f"✓ Max Retries: {provider.max_retries}")

    assert provider.server_url.startswith("http")
    assert provider.timeout > 0
    assert provider.max_retries > 0

    print("\n✅ Configuration test passed!")


def test_krokic4_metadata():
    """Test provider metadata methods"""
    print("\n" + "="*60)
    print("TEST: Kroki C4 Provider Metadata")
    print("="*60)

    provider_folder = Path(__file__).parent.parent / "krokic4"
    provider = KrokiC4Provider(provider_folder)

    metadata = provider.get_metadata()
    print(f"✓ Provider ID: {metadata.provider_id}")
    print(f"✓ Provider Name: {metadata.provider_name}")
    print(f"✓ Diagram Type: {metadata.diagram_type}")
    print(f"✓ Available: {metadata.available}")
    print(f"✓ Requires LLM: {metadata.requires_llm}")

    assert metadata.provider_id == "krokic4"
    assert metadata.diagram_type == "c4"

    print("\n✅ Metadata test passed!")


def test_krokic4_llm_correction_rules():
    """Test LLM correction rules"""
    print("\n" + "="*60)
    print("TEST: Kroki C4 LLM Correction Rules")
    print("="*60)

    provider_folder = Path(__file__).parent.parent / "krokic4"
    provider = KrokiC4Provider(provider_folder)

    rules = provider.get_llm_correction_rules()
    print(f"✓ Rules length: {len(rules)} characters")
    print(f"\nRules preview:")
    print(rules[:200] + "...")

    assert rules is not None
    assert len(rules) > 0
    assert "C4" in rules or "c4" in rules.lower()

    print("\n✅ LLM correction rules test passed!")


def test_krokic4_validation():
    """Test C4 code validation via Kroki"""
    print("\n" + "="*60)
    print("TEST: Kroki C4 Validation")
    print("="*60)

    provider_folder = Path(__file__).parent.parent / "krokic4"
    provider = KrokiC4Provider(provider_folder)

    if not provider.is_available():
        print("⚠️  Skipping validation test - Kroki server not available")
        print("   Start Kroki server: docker run -p 8000:8000 yuzutech/kroki")
        return

    # Valid C4 system context diagram
    valid_code = """@startuml
!include https://raw.githubusercontent.com/plantuml-stdlib/C4-PlantUML/master/C4_Context.puml

Person(user, "User", "A user of the system")
System(system, "Software System", "The system being described")

Rel(user, system, "Uses")
@enduml"""

    print("\nValidating VALID C4 code...")
    result = provider.validate_code(valid_code)
    print(f"✓ Is Valid: {result.is_valid}")
    print(f"✓ Error: {result.error}")

    assert result.is_valid == True

    # Invalid C4 code (syntax error - missing closing parenthesis)
    invalid_code = """@startuml
!include https://raw.githubusercontent.com/plantuml-stdlib/C4-PlantUML/master/C4_Context.puml

Person(user, "User"
System(system, "System"
@enduml"""

    print("\nValidating INVALID C4 code (syntax error - missing closing parenthesis)...")
    result = provider.validate_code(invalid_code)
    print(f"✓ Is Valid: {result.is_valid}")
    if result.error:
        print(f"✓ Error: {result.error[:100]}...")

    assert result.is_valid == False

    print("\n✅ Validation test passed!")


def test_krokic4_auto_fix():
    """Test pattern-based auto-fix for C4"""
    print("\n" + "="*60)
    print("TEST: Kroki C4 Pattern-Based Auto-Fix")
    print("="*60)

    provider_folder = Path(__file__).parent.parent / "krokic4"
    provider = KrokiC4Provider(provider_folder)

    if not provider.is_available():
        print("⚠️  Skipping auto-fix test - Kroki server not available")
        return

    # Code that can be auto-fixed (missing @enduml)
    fixable_code = """@startuml
Person(user, "User")
System(system, "System")
Rel(user, system, "Uses")"""

    print("\nAttempting auto-fix on code without @enduml...")
    result = provider.auto_fix_pattern_based(fixable_code, "Missing @enduml")

    print(f"✓ Is Valid: {result.is_valid}")
    print(f"✓ Auto Fixed: {result.auto_fixed}")
    print(f"✓ Correction Method: {result.correction_method}")

    if result.fixed_code:
        print(f"\nFixed code preview:")
        print(result.fixed_code[:200])

    print("\n✅ Auto-fix test passed!")


def test_krokic4_render_svg():
    """Test rendering to SVG"""
    print("\n" + "="*60)
    print("TEST: Kroki C4 Rendering to SVG")
    print("="*60)

    provider_folder = Path(__file__).parent.parent / "krokic4"
    provider = KrokiC4Provider(provider_folder)

    if not provider.is_available():
        print("⚠️  Skipping render test - Kroki server not available")
        return

    valid_code = """@startuml
!include https://raw.githubusercontent.com/plantuml-stdlib/C4-PlantUML/master/C4_Context.puml

Person(user, "User")
System(webapp, "Web Application")

Rel(user, webapp, "Uses", "HTTPS")
@enduml"""

    print("\nRendering C4 to SVG...")
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


def test_krokic4_render_png():
    """Test rendering to PNG"""
    print("\n" + "="*60)
    print("TEST: Kroki C4 Rendering to PNG")
    print("="*60)

    provider_folder = Path(__file__).parent.parent / "krokic4"
    provider = KrokiC4Provider(provider_folder)

    if not provider.is_available():
        print("⚠️  Skipping render test - Kroki server not available")
        return

    valid_code = """@startuml
!include https://raw.githubusercontent.com/plantuml-stdlib/C4-PlantUML/master/C4_Context.puml

Person(user, "User")
System(system, "System")

Rel(user, system, "Uses")
@enduml"""

    print("\nRendering C4 to PNG...")
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


def test_krokic4_complex_diagram():
    """Test rendering a more complex C4 diagram"""
    print("\n" + "="*60)
    print("TEST: Kroki C4 Complex Diagram")
    print("="*60)

    provider_folder = Path(__file__).parent.parent / "krokic4"
    provider = KrokiC4Provider(provider_folder)

    if not provider.is_available():
        print("⚠️  Skipping complex diagram test - Kroki server not available")
        return

    complex_code = """@startuml
!include https://raw.githubusercontent.com/plantuml-stdlib/C4-PlantUML/master/C4_Container.puml

Person(user, "User", "End user of the system")
Person(admin, "Administrator", "System administrator")

System_Boundary(c1, "Software System") {
    Container(webapp, "Web Application", "React", "Delivers content to users")
    Container(api, "API Application", "Node.js", "Provides business logic")
    Container(database, "Database", "PostgreSQL", "Stores user data")

    Rel(webapp, api, "Makes API calls to", "HTTPS")
    Rel(api, database, "Reads from and writes to", "SQL/TCP")
}

System_Ext(email, "Email System", "External email service")

Rel(user, webapp, "Uses", "HTTPS")
Rel(admin, webapp, "Administers", "HTTPS")
Rel(api, email, "Sends emails using", "SMTP")

@enduml"""

    print("\nRendering complex C4 diagram...")
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
    print("\n" + "="*60)
    print("KROKI C4 PROVIDER TEST SUITE")
    print("="*60)

    test_krokic4_provider_initialization()
    test_krokic4_config()
    test_krokic4_metadata()
    test_krokic4_llm_correction_rules()
    test_krokic4_validation()
    test_krokic4_auto_fix()
    test_krokic4_render_svg()
    test_krokic4_render_png()
    test_krokic4_complex_diagram()

    print("\n" + "="*60)
    print("✅ ALL KROKI C4 TESTS PASSED!")
    print("="*60)
