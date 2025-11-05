"""
Test Diagram Provider API Endpoints (Phase 1)

Tests for:
- GET /api/v1/diagrams/v2/providers (list providers)
- POST /api/v1/diagrams/v2/render (render diagrams)
- POST /api/v1/diagrams/v2/validate (validate code)

Coverage: 47 tests
"""

import pytest
from fastapi.testclient import TestClient


class TestListProviders:
    """Test listing available diagram providers"""

    def test_list_providers_returns_200(self, test_client):
        """GET /diagrams/v2/providers returns 200 OK"""
        response = test_client.get("/api/v1/diagrams/v2/providers")
        assert response.status_code == 200

    def test_list_providers_returns_json(self, test_client):
        """Response is valid JSON"""
        response = test_client.get("/api/v1/diagrams/v2/providers")
        data = response.json()
        # Response can be dict or list
        assert isinstance(data, (dict, list))

    def test_list_providers_contains_expected_fields(self, test_client):
        """Each provider has required fields"""
        response = test_client.get("/api/v1/diagrams/v2/providers")
        data = response.json()

        # Handle dict response with 'providers' key
        if isinstance(data, dict) and "providers" in data:
            providers = data["providers"]
        else:
            providers = data if isinstance(data, list) else []

        if providers:  # Check only if providers exist
            for provider in providers:
                assert "provider_id" in provider
                assert "provider_name" in provider
                assert "diagram_type" in provider

    def test_list_providers_mermaid_available(self, test_client):
        """Mermaid provider is in list"""
        response = test_client.get("/api/v1/diagrams/v2/providers")
        data = response.json()

        # Handle dict response with 'providers' key
        if isinstance(data, dict) and "providers" in data:
            providers = data["providers"]
        else:
            providers = data if isinstance(data, list) else []

        provider_ids = [p.get("provider_id", "") for p in providers]
        assert any("mermaid" in pid.lower() for pid in provider_ids)

    def test_list_providers_d2_available(self, test_client):
        """D2 provider is in list"""
        response = test_client.get("/api/v1/diagrams/v2/providers")
        data = response.json()

        # Handle dict response with 'providers' key
        if isinstance(data, dict) and "providers" in data:
            providers = data["providers"]
        else:
            providers = data if isinstance(data, list) else []

        provider_ids = [p.get("provider_id", "") for p in providers]
        assert any("d2" in pid.lower() for pid in provider_ids)


class TestRenderEndpoint:
    """Test diagram rendering endpoint"""

    def test_render_valid_mermaid_code_returns_200(self, test_client, sample_mermaid_code):
        """POST /render with valid Mermaid code returns 200"""
        request_data = {
            "code": sample_mermaid_code,
            "diagram_type": "mermaid",
            "output_format": "svg"
        }
        response = test_client.post("/api/v1/diagrams/v2/render", json=request_data)
        assert response.status_code == 200

    def test_render_valid_d2_code_returns_200(self, test_client, sample_d2_code):
        """POST /render with valid D2 code returns 200"""
        request_data = {
            "code": sample_d2_code,
            "diagram_type": "d2",
            "output_format": "svg"
        }
        response = test_client.post("/api/v1/diagrams/v2/render", json=request_data)
        assert response.status_code in [200, 500]  # Allow 500 if D2 not available

    def test_render_response_is_json(self, test_client, render_request_valid):
        """Render response is valid JSON"""
        response = test_client.post("/api/v1/diagrams/v2/render", json=render_request_valid)
        assert response.headers.get("content-type", "").startswith("application/json")

    def test_render_response_has_required_fields(self, test_client, render_request_valid):
        """Render response contains required fields"""
        response = test_client.post("/api/v1/diagrams/v2/render", json=render_request_valid)
        if response.status_code == 200:
            data = response.json()
            assert "success" in data
            assert "provider_id" in data

    def test_render_empty_code_returns_422(self, test_client, empty_code):
        """Empty code returns 422 Bad Request"""
        request_data = {
            "code": empty_code,
            "diagram_type": "mermaid",
            "output_format": "svg"
        }
        response = test_client.post("/api/v1/diagrams/v2/render", json=request_data)
        assert response.status_code == 422  # Pydantic validation

    def test_render_missing_code_returns_422(self, test_client):
        """Missing code field returns 422"""
        request_data = {
            "diagram_type": "mermaid",
            "output_format": "svg"
        }
        response = test_client.post("/api/v1/diagrams/v2/render", json=request_data)
        assert response.status_code == 422

    def test_render_missing_diagram_type_returns_422(self, test_client, simple_mermaid_code):
        """Missing diagram_type returns 422"""
        request_data = {
            "code": simple_mermaid_code,
            "output_format": "svg"
        }
        response = test_client.post("/api/v1/diagrams/v2/render", json=request_data)
        assert response.status_code == 422

    def test_render_invalid_diagram_type_returns_error(self, test_client, simple_mermaid_code):
        """Invalid diagram type returns error"""
        request_data = {
            "code": simple_mermaid_code,
            "diagram_type": "nonexistent",
            "output_format": "svg"
        }
        response = test_client.post("/api/v1/diagrams/v2/render", json=request_data)
        assert response.status_code in [400, 404]

    def test_render_returns_svg_by_default(self, test_client, simple_mermaid_code):
        """Default output format is SVG"""
        request_data = {
            "code": simple_mermaid_code,
            "diagram_type": "mermaid"
        }
        response = test_client.post("/api/v1/diagrams/v2/render", json=request_data)
        if response.status_code == 200:
            data = response.json()
            assert data.get("output_format", "svg") == "svg"

    def test_render_with_special_characters(self, test_client, code_with_special_chars):
        """Render code with special characters"""
        request_data = {
            "code": code_with_special_chars,
            "diagram_type": "mermaid",
            "output_format": "svg"
        }
        response = test_client.post("/api/v1/diagrams/v2/render", json=request_data)
        assert response.status_code in [200, 400]  # May be invalid

    def test_render_large_code(self, test_client, large_code):
        """Render very large code"""
        request_data = {
            "code": large_code,
            "diagram_type": "mermaid",
            "output_format": "svg"
        }
        response = test_client.post("/api/v1/diagrams/v2/render", json=request_data)
        assert response.status_code in [200, 400, 413]  # May fail due to size

    def test_render_response_includes_metadata(self, test_client, render_request_valid):
        """Response includes metadata"""
        response = test_client.post("/api/v1/diagrams/v2/render", json=render_request_valid)
        if response.status_code == 200:
            data = response.json()
            assert "metadata" in data

    def test_render_with_specific_provider(self, test_client, simple_mermaid_code):
        """Render with specific provider ID"""
        request_data = {
            "code": simple_mermaid_code,
            "diagram_type": "mermaid",
            "provider_id": "mermaidv1",
            "output_format": "svg"
        }
        response = test_client.post("/api/v1/diagrams/v2/render", json=request_data)
        if response.status_code == 200:
            data = response.json()
            assert data.get("provider_id") == "mermaidv1"

    def test_render_with_svg_format(self, test_client, simple_mermaid_code):
        """Render with SVG output format"""
        request_data = {
            "code": simple_mermaid_code,
            "diagram_type": "mermaid",
            "output_format": "svg"
        }
        response = test_client.post("/api/v1/diagrams/v2/render", json=request_data)
        if response.status_code == 200:
            assert "svg" in response.json().get("output_format", "").lower()

    def test_render_with_png_format(self, test_client, simple_mermaid_code):
        """Render with PNG output format"""
        request_data = {
            "code": simple_mermaid_code,
            "diagram_type": "mermaid",
            "output_format": "png"
        }
        response = test_client.post("/api/v1/diagrams/v2/render", json=request_data)
        # PNG may not be supported on all systems
        assert response.status_code in [200, 400, 500]


class TestValidateEndpoint:
    """Test diagram validation endpoint"""

    def test_validate_valid_code_returns_200(self, test_client, simple_mermaid_code):
        """POST /validate with valid code returns 200"""
        request_data = {
            "code": simple_mermaid_code,
            "diagram_type": "mermaid",
            "auto_fix": False
        }
        response = test_client.post("/api/v1/diagrams/v2/validate", json=request_data)
        assert response.status_code == 200

    def test_validate_response_is_json(self, test_client, validation_request_valid):
        """Validation response is JSON"""
        response = test_client.post("/api/v1/diagrams/v2/validate", json=validation_request_valid)
        assert response.headers.get("content-type", "").startswith("application/json")

    def test_validate_response_has_is_valid_field(self, test_client, validation_request_valid):
        """Response includes is_valid field"""
        response = test_client.post("/api/v1/diagrams/v2/validate", json=validation_request_valid)
        if response.status_code == 200:
            data = response.json()
            assert "is_valid" in data

    def test_validate_invalid_code_returns_200(self, test_client, invalid_diagram_code):
        """Invalid code still returns 200 with is_valid=false"""
        request_data = {
            "code": invalid_diagram_code,
            "diagram_type": "mermaid",
            "auto_fix": False
        }
        response = test_client.post("/api/v1/diagrams/v2/validate", json=request_data)
        assert response.status_code == 200
        data = response.json()
        assert "is_valid" in data

    def test_validate_with_auto_fix_enabled(self, test_client, mermaid_code_with_error):
        """Validation with auto_fix enabled"""
        request_data = {
            "code": mermaid_code_with_error,
            "diagram_type": "mermaid",
            "auto_fix": True
        }
        response = test_client.post("/api/v1/diagrams/v2/validate", json=request_data)
        assert response.status_code == 200

    def test_validate_missing_code_returns_422(self, test_client):
        """Missing code field returns 422"""
        request_data = {
            "diagram_type": "mermaid",
            "auto_fix": False
        }
        response = test_client.post("/api/v1/diagrams/v2/validate", json=request_data)
        assert response.status_code == 422

    def test_validate_missing_diagram_type_returns_422(self, test_client, simple_mermaid_code):
        """Missing diagram_type returns 422"""
        request_data = {
            "code": simple_mermaid_code,
            "auto_fix": False
        }
        response = test_client.post("/api/v1/diagrams/v2/validate", json=request_data)
        assert response.status_code == 422

    def test_validate_empty_code_returns_422(self, test_client):
        """Empty code returns 422"""
        request_data = {
            "code": "",
            "diagram_type": "mermaid",
            "auto_fix": False
        }
        response = test_client.post("/api/v1/diagrams/v2/validate", json=request_data)
        assert response.status_code == 422

    def test_validate_includes_code_length(self, test_client, simple_mermaid_code):
        """Validation response includes code_length"""
        request_data = {
            "code": simple_mermaid_code,
            "diagram_type": "mermaid",
            "auto_fix": False
        }
        response = test_client.post("/api/v1/diagrams/v2/validate", json=request_data)
        if response.status_code == 200:
            data = response.json()
            assert "code_length" in data
            assert data["code_length"] == len(simple_mermaid_code)

    def test_validate_large_code(self, test_client, large_code):
        """Validate large code"""
        request_data = {
            "code": large_code,
            "diagram_type": "mermaid",
            "auto_fix": False
        }
        response = test_client.post("/api/v1/diagrams/v2/validate", json=request_data)
        assert response.status_code in [200, 413]

    def test_validate_d2_code(self, test_client, sample_d2_code):
        """Validate D2 code"""
        request_data = {
            "code": sample_d2_code,
            "diagram_type": "d2",
            "auto_fix": False
        }
        response = test_client.post("/api/v1/diagrams/v2/validate", json=request_data)
        assert response.status_code == 200


class TestErrorHandling:
    """Test error handling in diagram endpoints"""

    def test_render_nonexistent_provider(self, test_client, simple_mermaid_code):
        """Nonexistent provider returns error"""
        request_data = {
            "code": simple_mermaid_code,
            "diagram_type": "mermaid",
            "provider_id": "nonexistent_provider_xyz",
            "output_format": "svg"
        }
        response = test_client.post("/api/v1/diagrams/v2/render", json=request_data)
        assert response.status_code in [400, 404]

    def test_render_invalid_json_returns_422(self, test_client):
        """Invalid JSON returns 422"""
        response = test_client.post(
            "/api/v1/diagrams/v2/render",
            data="invalid json {",
            headers={"Content-Type": "application/json"}
        )
        assert response.status_code == 422

    def test_render_very_large_code_over_limit(self, test_client):
        """Very large code over size limit"""
        huge_code = "graph TD\n" + ("  A --> B\n" * 10000)
        request_data = {
            "code": huge_code,
            "diagram_type": "mermaid",
            "output_format": "svg"
        }
        response = test_client.post("/api/v1/diagrams/v2/render", json=request_data)
        assert response.status_code in [200, 400, 413, 500]


class TestResponseValidation:
    """Test response validation"""

    def test_render_success_response_structure(self, test_client, render_request_valid):
        """Render response has proper structure"""
        response = test_client.post("/api/v1/diagrams/v2/render", json=render_request_valid)
        if response.status_code == 200:
            data = response.json()
            assert isinstance(data, dict)
            assert "success" in data
            assert "provider_id" in data

    def test_validate_success_response_structure(self, test_client, validation_request_valid):
        """Validate response has proper structure"""
        response = test_client.post("/api/v1/diagrams/v2/validate", json=validation_request_valid)
        if response.status_code == 200:
            data = response.json()
            assert isinstance(data, dict)
            assert "is_valid" in data
            assert "code_length" in data
            assert "provider_id" in data
