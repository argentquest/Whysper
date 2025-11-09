"""
Integration tests for Provider Registry
"""

import sys
from pathlib import Path
from unittest.mock import Mock, patch
from typing import List, Optional

# Add backend to path
backend_dir = Path(__file__).parent.parent.parent
sys.path.insert(0, str(backend_dir))

from diagrams.provider_registry import (
    ProviderRegistry,
    get_provider_registry,
    set_provider_registry
)
from diagrams.base_diagram import BaseDiagramProvider
from diagrams.models import (
    ProviderCapability,
    ValidationResult,
    RenderResult,
    ProviderMetadata
)


# Mock Provider for Testing
class MockMermaidProvider(BaseDiagramProvider):
    """Mock Mermaid provider for testing"""

    @property
    def provider_id(self) -> str:
        return "mock_mermaid"

    @property
    def provider_name(self) -> str:
        return "Mock Mermaid Provider"

    @property
    def diagram_type(self) -> str:
        return "mermaid"

    @property
    def supported_output_formats(self) -> List[str]:
        return ["mermaid", "svg", "png"]

    @property
    def capabilities(self) -> List[ProviderCapability]:
        return [
            ProviderCapability.VALIDATE,
            ProviderCapability.RENDER_SVG,
            ProviderCapability.AUTO_FIX
        ]

    def validate_code(self, code: str, **options) -> ValidationResult:
        return ValidationResult(is_valid=True, code_length=len(code))

    def render(self, code: str, output_format: str = "svg", **options) -> RenderResult:
        return RenderResult(
            success=True,
            content="<svg>mock</svg>",
            output_format=output_format,
            validation=ValidationResult(is_valid=True, code_length=len(code))
        )

    def get_version(self) -> Optional[str]:
        return "1.0.0"

    def is_available(self) -> bool:
        return True


class MockD2Provider(BaseDiagramProvider):
    """Mock D2 provider for testing"""

    @property
    def provider_id(self) -> str:
        return "mock_d2"

    @property
    def provider_name(self) -> str:
        return "Mock D2 Provider"

    @property
    def diagram_type(self) -> str:
        return "d2"

    @property
    def supported_output_formats(self) -> List[str]:
        return ["d2", "svg"]

    @property
    def capabilities(self) -> List[ProviderCapability]:
        return [
            ProviderCapability.VALIDATE,
            ProviderCapability.RENDER_SVG,
            ProviderCapability.BATCH
        ]

    def validate_code(self, code: str, **options) -> ValidationResult:
        return ValidationResult(is_valid=True, code_length=len(code))

    def render(self, code: str, output_format: str = "svg", **options) -> RenderResult:
        return RenderResult(
            success=True,
            content="<svg>mock d2</svg>",
            output_format=output_format,
            validation=ValidationResult(is_valid=True, code_length=len(code))
        )

    def get_version(self) -> Optional[str]:
        return "0.5.0"

    def is_available(self) -> bool:
        return True


class UnavailableMockProvider(BaseDiagramProvider):
    """Mock provider that is unavailable"""

    @property
    def provider_id(self) -> str:
        return "unavailable"

    @property
    def provider_name(self) -> str:
        return "Unavailable Provider"

    @property
    def diagram_type(self) -> str:
        return "test"

    @property
    def supported_output_formats(self) -> List[str]:
        return ["svg"]

    @property
    def capabilities(self) -> List[ProviderCapability]:
        return [ProviderCapability.VALIDATE]

    def validate_code(self, code: str, **options) -> ValidationResult:
        return ValidationResult(is_valid=False, error="Not available")

    def render(self, code: str, output_format: str = "svg", **options) -> RenderResult:
        return RenderResult(
            success=False,
            content=None,
            output_format=output_format,
            validation=ValidationResult(is_valid=False, error="Not available"),
            error="Not available"
        )

    def get_version(self) -> Optional[str]:
        return None

    def is_available(self) -> bool:
        return False


def test_registry_creation():
    """Test creating a provider registry"""
    # Create registry without auto-discovery
    registry = ProviderRegistry(auto_discover=False)

    assert registry is not None
    assert registry.list_all() == []

    print("[OK] Registry creation test passed")


def test_registry_register_provider():
    """Test registering providers"""
    registry = ProviderRegistry(auto_discover=False)

    # Create mock provider folder
    mock_folder = Path(__file__).parent.parent / "mermaidv1"

    provider = MockMermaidProvider(mock_folder)
    registry.register(provider)

    assert len(registry.list_all()) == 1
    assert registry.get("mock_mermaid") == provider

    print("[OK] Registry register provider test passed")


def test_registry_get_provider():
    """Test retrieving provider by ID"""
    registry = ProviderRegistry(auto_discover=False)
    mock_folder = Path(__file__).parent.parent / "mermaidv1"

    provider = MockMermaidProvider(mock_folder)
    registry.register(provider)

    # Get existing provider
    retrieved = registry.get("mock_mermaid")
    assert retrieved is not None
    assert retrieved.provider_id == "mock_mermaid"

    # Get non-existent provider
    none_provider = registry.get("nonexistent")
    assert none_provider is None

    print("[OK] Registry get provider test passed")


def test_registry_find_by_diagram_type():
    """Test finding providers by diagram type"""
    registry = ProviderRegistry(auto_discover=False)
    mock_folder = Path(__file__).parent.parent / "mermaidv1"

    # Register multiple providers
    mermaid = MockMermaidProvider(mock_folder)
    d2 = MockD2Provider(mock_folder)

    registry.register(mermaid)
    registry.register(d2)

    # Find by diagram type
    mermaid_providers = registry.find_by_diagram_type("mermaid")
    assert len(mermaid_providers) == 1
    assert mermaid_providers[0].diagram_type == "mermaid"

    d2_providers = registry.find_by_diagram_type("d2")
    assert len(d2_providers) == 1
    assert d2_providers[0].diagram_type == "d2"

    # Non-existent type
    none_providers = registry.find_by_diagram_type("plantuml")
    assert len(none_providers) == 0

    print("[OK] Registry find by diagram type test passed")


def test_registry_find_by_output_format():
    """Test finding providers by output format"""
    registry = ProviderRegistry(auto_discover=False)
    mock_folder = Path(__file__).parent.parent / "mermaidv1"

    mermaid = MockMermaidProvider(mock_folder)
    d2 = MockD2Provider(mock_folder)

    registry.register(mermaid)
    registry.register(d2)

    # Find providers that support SVG
    svg_providers = registry.find_by_output_format("svg")
    assert len(svg_providers) == 2, "Both providers support SVG"

    # Find providers that support PNG
    png_providers = registry.find_by_output_format("png")
    assert len(png_providers) == 1, "Only mermaid supports PNG"
    assert png_providers[0].provider_id == "mock_mermaid"

    # Non-existent format
    pdf_providers = registry.find_by_output_format("pdf")
    assert len(pdf_providers) == 0

    print("[OK] Registry find by output format test passed")


def test_registry_get_best_provider():
    """Test getting default provider for diagram type"""
    registry = ProviderRegistry(auto_discover=False)
    mock_folder = Path(__file__).parent.parent / "mermaidv1"

    mermaid = MockMermaidProvider(mock_folder)
    unavailable = UnavailableMockProvider(mock_folder)

    registry.register(mermaid)
    registry.register(unavailable)

    # Get default available provider
    best_mermaid = registry.get_default_provider("mermaid")
    assert best_mermaid is not None
    assert best_mermaid.provider_id == "mock_mermaid"

    # Get default for unavailable type
    best_test = registry.get_default_provider("test")
    assert best_test is None, "Should not return unavailable provider"

    # Get default for non-existent type
    best_none = registry.get_default_provider("nonexistent")
    assert best_none is None

    print("[OK] Registry get default provider test passed")


def test_registry_list_providers():
    """Test listing providers with filters"""
    registry = ProviderRegistry(auto_discover=False)
    mock_folder = Path(__file__).parent.parent / "mermaidv1"

    mermaid = MockMermaidProvider(mock_folder)
    d2 = MockD2Provider(mock_folder)
    unavailable = UnavailableMockProvider(mock_folder)

    registry.register(mermaid)
    registry.register(d2)
    registry.register(unavailable)

    # List all providers
    all_providers = registry.list_all()
    assert len(all_providers) == 3

    # List only available providers
    available = registry.list_available()
    assert len(available) == 2

    # List by diagram type
    mermaid_only = registry.find_by_diagram_type("mermaid")
    assert len(mermaid_only) == 1
    assert mermaid_only[0].diagram_type == "mermaid"

    # List by output format
    png_support = registry.find_by_output_format("png")
    assert len(png_support) == 1
    assert "png" in png_support[0].supported_output_formats

    print("[OK] Registry list providers test passed")


def test_registry_get_metadata():
    """Test getting provider metadata"""
    registry = ProviderRegistry(auto_discover=False)
    mock_folder = Path(__file__).parent.parent / "mermaidv1"

    provider = MockMermaidProvider(mock_folder)
    registry.register(provider)

    # Get metadata through provider
    retrieved_provider = registry.get("mock_mermaid")
    metadata = retrieved_provider.get_metadata()

    assert metadata is not None
    assert metadata.provider_id == "mock_mermaid"
    assert metadata.diagram_type == "mermaid"
    assert "svg" in metadata.supported_output_formats
    assert ProviderCapability.VALIDATE in metadata.capabilities
    assert metadata.version == "1.0.0"
    assert metadata.available == True

    print("[OK] Registry get metadata test passed")


def test_registry_get_all_metadata():
    """Test getting all provider metadata"""
    registry = ProviderRegistry(auto_discover=False)
    mock_folder = Path(__file__).parent.parent / "mermaidv1"

    mermaid = MockMermaidProvider(mock_folder)
    d2 = MockD2Provider(mock_folder)

    registry.register(mermaid)
    registry.register(d2)

    all_metadata = registry.list_all()

    assert len(all_metadata) == 2
    assert all(isinstance(m, ProviderMetadata) for m in all_metadata)

    provider_ids = [m.provider_id for m in all_metadata]
    assert "mock_mermaid" in provider_ids
    assert "mock_d2" in provider_ids

    print("[OK] Registry get all metadata test passed")


def test_registry_singleton():
    """Test registry singleton"""
    # Reset singleton for test
    set_provider_registry(None)

    registry1 = get_provider_registry()
    registry2 = get_provider_registry()

    assert registry1 is registry2, "Should return same instance"

    print("[OK] Registry singleton test passed")


def test_registry_unregister():
    """Test unregistering providers"""
    registry = ProviderRegistry(auto_discover=False)
    mock_folder = Path(__file__).parent.parent / "mermaidv1"

    provider = MockMermaidProvider(mock_folder)
    registry.register(provider)

    assert registry.get("mock_mermaid") is not None

    # Unregister (returns None in actual implementation)
    registry.unregister("mock_mermaid")
    assert registry.get("mock_mermaid") is None

    # Try to unregister non-existent (should not raise error)
    registry.unregister("nonexistent")

    print("[OK] Registry unregister test passed")


def test_registry_supports_capability():
    """Test finding providers by capability"""
    registry = ProviderRegistry(auto_discover=False)
    mock_folder = Path(__file__).parent.parent / "mermaidv1"

    mermaid = MockMermaidProvider(mock_folder)
    d2 = MockD2Provider(mock_folder)

    registry.register(mermaid)
    registry.register(d2)

    # Find providers with AUTO_FIX
    auto_fix_providers = [
        p for p in registry._providers.values()
        if p.supports_capability(ProviderCapability.AUTO_FIX)
    ]
    assert len(auto_fix_providers) == 1
    assert auto_fix_providers[0].provider_id == "mock_mermaid"

    # Find providers with BATCH
    batch_providers = [
        p for p in registry._providers.values()
        if p.supports_capability(ProviderCapability.BATCH)
    ]
    assert len(batch_providers) == 1
    assert batch_providers[0].provider_id == "mock_d2"

    # Find providers with VALIDATE (both should have it)
    validate_providers = [
        p for p in registry._providers.values()
        if p.supports_capability(ProviderCapability.VALIDATE)
    ]
    assert len(validate_providers) == 2

    print("[OK] Registry supports capability test passed")


def run_all_tests():
    """Run all provider registry tests"""
    print("\n" + "="*60)
    print("Testing Provider Registry")
    print("="*60 + "\n")

    test_registry_creation()
    test_registry_register_provider()
    test_registry_get_provider()
    test_registry_find_by_diagram_type()
    test_registry_find_by_output_format()
    test_registry_get_best_provider()
    test_registry_list_providers()
    test_registry_get_metadata()
    test_registry_get_all_metadata()
    test_registry_singleton()
    test_registry_unregister()
    test_registry_supports_capability()

    print("\n" + "="*60)
    print("[OK] All provider registry tests passed!")
    print("="*60 + "\n")


if __name__ == "__main__":
    run_all_tests()
