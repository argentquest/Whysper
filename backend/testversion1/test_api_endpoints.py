import pytest
from unittest.mock import MagicMock
from diagrams.models import RenderResult, ValidationResult, ProviderMetadata, ProviderCapability

def test_list_providers(client, mock_registry):
    """Test listing providers"""
    # Setup mock metadata
    p_meta = ProviderMetadata(
        provider_id="test_p",
        provider_name="Test Provider",
        diagram_type="d2",
        supported_output_formats=["svg"],
        capabilities=[ProviderCapability.VALIDATE],
        version="1.0",
        available=True,
        requires_llm=False,
        description="Test description"
    )

    mock_registry.list_all.return_value = [p_meta]
    mock_registry.get_statistics.return_value = {
        "total_providers": 1,
        "available_providers": 1,
        "unavailable_providers": 0
    }

    res = client.get("/api/v1/diagrams/v2/providers")
    assert res.status_code == 200
    data = res.json()
    assert data["total_providers"] == 1
    assert data["providers"][0]["provider_id"] == "test_p"

def test_render_success(client, mock_registry):
    """Test successful rendering"""
    # Mock provider
    mock_provider = MagicMock()
    mock_provider.provider_id = "d2v1"
    mock_provider.provider_name = "D2"
    mock_provider.is_available.return_value = True

    mock_result = RenderResult(
        success=True,
        content="<svg>mock</svg>",
        output_format="svg",
        validation=ValidationResult(is_valid=True, code_length=10),
        metadata={}
    )
    mock_provider.render.return_value = mock_result

    # Configure registry to return mock provider
    mock_registry.get_default_provider.return_value = mock_provider
    mock_registry.get.return_value = mock_provider

    payload = {
        "code": "x -> y",
        "diagram_type": "d2",
        "output_format": "svg"
    }

    res = client.post("/api/v1/diagrams/v2/render", json=payload)
    assert res.status_code == 200
    data = res.json()
    assert data["success"] is True
    assert data["content"] == "<svg>mock</svg>"

    # Verify provider was called
    mock_provider.render.assert_called_once()

def test_render_provider_not_found(client, mock_registry):
    """Test rendering when provider is missing"""
    mock_registry.get_default_provider.return_value = None
    mock_registry.get.return_value = None

    payload = {
        "code": "x -> y",
        "diagram_type": "unknown"
    }

    res = client.post("/api/v1/diagrams/v2/render", json=payload)
    assert res.status_code == 404

def test_render_provider_unavailable(client, mock_registry):
    """Test rendering when provider is unavailable"""
    mock_provider = MagicMock()
    mock_provider.is_available.return_value = False
    mock_registry.get_default_provider.return_value = mock_provider
    mock_registry.get.return_value = mock_provider

    payload = {
        "code": "x -> y",
        "diagram_type": "d2"
    }

    res = client.post("/api/v1/diagrams/v2/render", json=payload)
    assert res.status_code == 503

def test_validate_endpoint(client, mock_registry):
    """Test validation endpoint"""
    mock_provider = MagicMock()
    mock_provider.provider_id = "d2v1"
    mock_provider.is_available.return_value = True

    mock_val_result = ValidationResult(is_valid=False, error="Syntax Error", code_length=10)
    mock_provider.validate_code.return_value = mock_val_result

    # Auto fix mock
    mock_fix_result = ValidationResult(is_valid=True, auto_fixed=True, fixed_code="fixed", code_length=10)
    mock_provider.auto_fix_pattern_based.return_value = mock_fix_result

    mock_registry.get_default_provider.return_value = mock_provider

    payload = {
        "code": "bad code",
        "diagram_type": "d2",
        "auto_fix": True
    }

    res = client.post("/api/v1/diagrams/v2/validate", json=payload)
    assert res.status_code == 200
    data = res.json()
    assert data["is_valid"] is True # Because it was auto-fixed
    assert data["auto_fixed"] is True
    assert data["fixed_code"] == "fixed"
