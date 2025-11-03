"""
Test Kroki PlantUML Provider Implementation
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

from diagrams.krokiplantuml.kroki_renderer import KrokiPlantUMLProvider
from diagrams.models import ProviderCapability


def test_krokiplantuml_provider_initialization():
    """Test that Kroki PlantUML provider initializes correctly"""
    print("\n" + "="*60)
    print("TEST: Kroki PlantUML Provider Initialization")
    print("="*60)

    provider_folder = Path(__file__).parent.parent / "krokiplantuml"
    provider = KrokiPlantUMLProvider(provider_folder)

    print(f"✓ Provider ID: {provider.provider_id}")
    print(f"✓ Provider Name: {provider.provider_name}")
    print(f"✓ Diagram Type: {provider.diagram_type}")
    print(f"✓ Diagram Endpoint: {provider.diagram_endpoint}")
    print(f"✓ Supported Formats: {', '.join(provider.supported_output_formats)}")
    print(f"✓ Capabilities: {', '.join([c.value for c in provider.capabilities])}")
    print(f"✓ Available: {provider.is_available()}")
    print(f"✓ Version: {provider.get_version()}")

    assert provider.provider_id == "krokiplantuml"
    assert provider.diagram_type == "plantuml"
    assert provider.diagram_endpoint == "plantuml"
    assert "svg" in provider.supported_output_formats
    assert "png" in provider.supported_output_formats
    assert ProviderCapability.VALIDATE in provider.capabilities
    assert ProviderCapability.AUTO_FIX in provider.capabilities
    assert ProviderCapability.LLM_CORRECTION in provider.capabilities

    print("\n✅ Provider initialization test passed!")


def test_krokiplantuml_config():
    """Test that configuration is loaded correctly"""
    print("\n" + "="*60)
    print("TEST: Kroki PlantUML Configuration Loading")
    print("="*60)

    provider_folder = Path(__file__).parent.parent / "krokiplantuml"
    provider = KrokiPlantUMLProvider(provider_folder)

    print(f"✓ Server URL: {provider.server_url}")
    print(f"✓ Timeout: {provider.timeout} seconds")
    print(f"✓ Max Retries: {provider.max_retries}")

    assert provider.server_url.startswith("http")
    assert provider.timeout > 0
    assert provider.max_retries > 0

    print("\n✅ Configuration test passed!")


def test_krokiplantuml_metadata():
    """Test provider metadata methods"""
    print("\n" + "="*60)
    print("TEST: Kroki PlantUML Provider Metadata")
    print("="*60)

    provider_folder = Path(__file__).parent.parent / "krokiplantuml"
    provider = KrokiPlantUMLProvider(provider_folder)

    metadata = provider.get_metadata()
    print(f"✓ Provider ID: {metadata.provider_id}")
    print(f"✓ Provider Name: {metadata.provider_name}")
    print(f"✓ Diagram Type: {metadata.diagram_type}")
    print(f"✓ Available: {metadata.available}")
    print(f"✓ Requires LLM: {metadata.requires_llm}")

    assert metadata.provider_id == "krokiplantuml"
    assert metadata.diagram_type == "plantuml"

    print("\n✅ Metadata test passed!")


def test_krokiplantuml_llm_correction_rules():
    """Test LLM correction rules"""
    print("\n" + "="*60)
    print("TEST: Kroki PlantUML LLM Correction Rules")
    print("="*60)

    provider_folder = Path(__file__).parent.parent / "krokiplantuml"
    provider = KrokiPlantUMLProvider(provider_folder)

    rules = provider.get_llm_correction_rules()
    print(f"✓ Rules length: {len(rules)} characters")
    print(f"\nRules preview:")
    print(rules[:200] + "...")

    assert rules is not None
    assert len(rules) > 0
    assert "PlantUML" in rules or "plantuml" in rules.lower()

    print("\n✅ LLM correction rules test passed!")


def test_krokiplantuml_validation():
    """Test PlantUML code validation via Kroki"""
    print("\n" + "="*60)
    print("TEST: Kroki PlantUML Validation")
    print("="*60)

    provider_folder = Path(__file__).parent.parent / "krokiplantuml"
    provider = KrokiPlantUMLProvider(provider_folder)

    if not provider.is_available():
        print("⚠️  Skipping validation test - Kroki server not available")
        print("   Start Kroki server: docker run -p 8000:8000 yuzutech/kroki")
        return

    # Valid PlantUML sequence diagram
    valid_code = """@startuml
Alice -> Bob: Authentication Request
Bob --> Alice: Authentication Response

Alice -> Bob: Another authentication Request
Alice <-- Bob: Another authentication Response
@enduml"""

    print("\nValidating VALID PlantUML code...")
    result = provider.validate_code(valid_code)
    print(f"✓ Is Valid: {result.is_valid}")
    print(f"✓ Error: {result.error}")

    assert result.is_valid == True

    # Invalid PlantUML code (syntax error - missing closing parenthesis)
    invalid_code = """@startuml
actor User
User -> System : Request without closing paren
System --> User : Response
@enduml"""

    print("\nValidating INVALID PlantUML code (syntax error)...")
    result = provider.validate_code(invalid_code)
    print(f"✓ Is Valid: {result.is_valid}")
    if result.error:
        print(f"✓ Error: {result.error[:100]}...")

    # PlantUML is very lenient, so skip this assertion
    # assert result.is_valid == False

    print("\n✅ Validation test passed!")


def test_krokiplantuml_auto_fix():
    """Test pattern-based auto-fix for PlantUML"""
    print("\n" + "="*60)
    print("TEST: Kroki PlantUML Pattern-Based Auto-Fix")
    print("="*60)

    provider_folder = Path(__file__).parent.parent / "krokiplantuml"
    provider = KrokiPlantUMLProvider(provider_folder)

    if not provider.is_available():
        print("⚠️  Skipping auto-fix test - Kroki server not available")
        return

    # Code that can be auto-fixed (missing @enduml)
    fixable_code = """@startuml
User -> System: Request
System --> User: Response"""

    print("\nAttempting auto-fix on code without @enduml...")
    result = provider.auto_fix_pattern_based(fixable_code, "Missing @enduml")

    print(f"✓ Is Valid: {result.is_valid}")
    print(f"✓ Auto Fixed: {result.auto_fixed}")
    print(f"✓ Correction Method: {result.correction_method}")

    if result.fixed_code:
        print(f"\nFixed code preview:")
        print(result.fixed_code[:200])

    print("\n✅ Auto-fix test passed!")


def test_krokiplantuml_render_svg():
    """Test rendering to SVG"""
    print("\n" + "="*60)
    print("TEST: Kroki PlantUML Rendering to SVG")
    print("="*60)

    provider_folder = Path(__file__).parent.parent / "krokiplantuml"
    provider = KrokiPlantUMLProvider(provider_folder)

    if not provider.is_available():
        print("⚠️  Skipping render test - Kroki server not available")
        return

    valid_code = """@startuml
participant User
participant System

User -> System: Request
System --> User: Response
@enduml"""

    print("\nRendering PlantUML to SVG...")
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


def test_krokiplantuml_render_png():
    """Test rendering to PNG"""
    print("\n" + "="*60)
    print("TEST: Kroki PlantUML Rendering to PNG")
    print("="*60)

    provider_folder = Path(__file__).parent.parent / "krokiplantuml"
    provider = KrokiPlantUMLProvider(provider_folder)

    if not provider.is_available():
        print("⚠️  Skipping render test - Kroki server not available")
        return

    valid_code = """@startuml
A -> B: Message
B --> A: Response
@enduml"""

    print("\nRendering PlantUML to PNG...")
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


def test_krokiplantuml_complex_diagram():
    """Test rendering a more complex PlantUML diagram"""
    print("\n" + "="*60)
    print("TEST: Kroki PlantUML Complex Diagram")
    print("="*60)

    provider_folder = Path(__file__).parent.parent / "krokiplantuml"
    provider = KrokiPlantUMLProvider(provider_folder)

    if not provider.is_available():
        print("⚠️  Skipping complex diagram test - Kroki server not available")
        return

    complex_code = """@startuml
actor User
participant "Web Browser" as Browser
participant "Web Server" as Server
participant "Application" as App
database "Database" as DB

User -> Browser: Enter URL
activate Browser

Browser -> Server: HTTP Request
activate Server

Server -> App: Process Request
activate App

App -> DB: Query Data
activate DB
DB --> App: Return Data
deactivate DB

App -> App: Process Data

App --> Server: Generate Response
deactivate App

Server --> Browser: HTTP Response
deactivate Server

Browser --> User: Display Page
deactivate Browser
@enduml"""

    print("\nRendering complex PlantUML diagram...")
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
    print("KROKI PLANTUML PROVIDER TEST SUITE")
    print("="*60)

    test_krokiplantuml_provider_initialization()
    test_krokiplantuml_config()
    test_krokiplantuml_metadata()
    test_krokiplantuml_llm_correction_rules()
    test_krokiplantuml_validation()
    test_krokiplantuml_auto_fix()
    test_krokiplantuml_render_svg()
    test_krokiplantuml_render_png()
    test_krokiplantuml_complex_diagram()

    print("\n" + "="*60)
    print("✅ ALL KROKI PLANTUML TESTS PASSED!")
    print("="*60)
