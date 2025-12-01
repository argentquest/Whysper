"""Test to verify Kroki Structurizr provider registration."""

from unittest.mock import patch
from diagrams.provider_registry import get_registry


def test_structurizr_registration():
    """Test that Kroki Structurizr provider is properly registered"""

    # Mock is_available to avoid network calls and ensure it appears available
    with patch("diagrams.krokistructurizr.kroki_renderer.KrokiStructurizrProvider.is_available", return_value=True):
        # Get the provider registry
        registry = get_registry()

        # Get all providers
        all_providers = registry.list_all()

        # Check for Structurizr provider
        structurizr_providers = [p for p in all_providers if p.diagram_type == "structurizr"]

        assert structurizr_providers, "No Structurizr providers found!"

        for provider in structurizr_providers:
            # Verify it's the krokistructurizr provider
            if provider.provider_id == "krokistructurizr":
                assert provider.diagram_type == "structurizr"

        # Test getting the provider directly
        provider = registry.get("krokistructurizr")
        assert provider, "Could not retrieve krokistructurizr provider directly!"

        # Test finding by diagram type
        structurizr_providers = registry.find_by_diagram_type("structurizr")
        assert structurizr_providers, "No providers found for 'structurizr' diagram type!"

        # Test getting default provider
        default_provider = registry.get_default_provider("structurizr")
        assert default_provider, "No default provider for 'structurizr' diagram type!"

        # Get registry statistics
        stats = registry.get_statistics()
        assert stats["total_providers"] > 0
