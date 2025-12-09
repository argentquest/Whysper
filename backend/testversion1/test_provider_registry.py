import pytest
import logging
from unittest.mock import MagicMock
from diagrams.provider_registry import ProviderRegistry, set_provider_registry, get_registry
from diagrams.base_diagram import BaseDiagramProvider
from diagrams.models import ProviderCapability, ValidationResult, RenderResult

class MockProvider(BaseDiagramProvider):
    """Simple mock provider for registry testing"""
    def __init__(self, pid, name, dtype, formats, caps):
        self._pid = pid
        self._name = name
        self._dtype = dtype
        self._formats = formats
        self._caps = caps
        self.logger = logging.getLogger("tests.mock_provider")
        # Mock config needed by some methods that might access it
        self.config = MagicMock()
        self.config.provider_id = pid
        self.config.provider_name = name
        self.config.description = "Mock description"

    @property
    def provider_id(self): return self._pid
    @property
    def provider_name(self): return self._name
    @property
    def diagram_type(self): return self._dtype
    @property
    def supported_output_formats(self): return self._formats
    @property
    def capabilities(self): return self._caps
    def is_available(self): return True
    def get_version(self): return "1.0"
    def validate_code(self, code, **kwargs):
        return ValidationResult(is_valid=True, code_length=len(code))
    def render(self, code, output_format="svg", **kwargs):
        return RenderResult(
            success=True,
            content="<svg>mock</svg>",
            output_format=output_format,
            validation=self.validate_code(code)
        )

def test_registry_lifecycle():
    """Test creating registry, registering, and unregistering providers"""
    # Use auto_discover=False to avoid picking up real providers
    registry = ProviderRegistry(auto_discover=False)
    assert len(registry.list_all()) == 0

    p1 = MockProvider("p1", "Provider 1", "type1", ["svg"], [])
    registry.register(p1)

    assert len(registry.list_all()) == 1
    assert registry.get("p1") == p1

    registry.unregister("p1")
    assert len(registry.list_all()) == 0
    assert registry.get("p1") is None

def test_find_providers():
    """Test finding providers by type and format"""
    registry = ProviderRegistry(auto_discover=False)
    p1 = MockProvider("mermaid_v1", "Mermaid", "mermaid", ["svg", "png"], [])
    p2 = MockProvider("d2_v1", "D2", "d2", ["svg"], [])
    p3 = MockProvider("mermaid_v2", "Mermaid 2", "mermaid", ["svg"], [])

    registry.register(p1)
    registry.register(p2)
    registry.register(p3)

    # Find by type
    mermaid_providers = registry.find_by_diagram_type("mermaid")
    assert len(mermaid_providers) == 2

    d2_providers = registry.find_by_diagram_type("d2")
    assert len(d2_providers) == 1

    # Find by format
    png_providers = registry.find_by_output_format("png")
    assert len(png_providers) == 1
    assert png_providers[0] == p1

def test_capabilities():
    """Test provider capabilities"""
    registry = ProviderRegistry(auto_discover=False)
    p1 = MockProvider("p1", "P1", "d1", ["svg"], [ProviderCapability.AUTO_FIX])
    p2 = MockProvider("p2", "P2", "d1", ["svg"], [])

    registry.register(p1)
    registry.register(p2)

    assert p1.supports_capability(ProviderCapability.AUTO_FIX)
    assert not p2.supports_capability(ProviderCapability.AUTO_FIX)
    # The capability check logic calls .name on Enum, so passing string might fail if not careful
    # But BaseDiagramProvider.supports_capability arg type is ProviderCapability.
    # So we pass enum.

def test_singleton():
    """Test registry singleton pattern"""
    # Clear existing singleton
    set_provider_registry(None)

    reg1 = get_registry()
    reg2 = get_registry()

    assert reg1 is reg2
