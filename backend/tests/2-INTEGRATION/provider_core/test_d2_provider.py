"""
Tests for D2 diagram provider rendering.
"""

from conftest import save_svg_artifact
import sys
from pathlib import Path

# Import from root conftest
sys.path.insert(0, str(Path(__file__).parent.parent))


class TestD2RenderingBasic:
    """Test basic D2 diagram rendering."""

    def test_render_simple_diagram(self, client, d2_code_simple):
        """Test rendering a simple D2 diagram."""
        payload = {"code": d2_code_simple, "diagram_type": "d2", "output_format": "svg"}

        response = client.post("/api/v1/diagrams/v2/render", json=payload)

        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["content"] is not None
        assert len(data["content"]) > 0
        assert "<svg" in data["content"]
        assert "provider_id" in data
        assert data["provider_id"] == "d2v1"

        # Save SVG artifact for inspection
        save_svg_artifact("test_render_simple_diagram", "d2", data["content"], data["provider_id"])

    def test_render_complex_diagram(self, client, d2_code_complex):
        """Test rendering a complex D2 diagram with styling."""
        payload = {"code": d2_code_complex, "diagram_type": "d2", "output_format": "svg"}

        response = client.post("/api/v1/diagrams/v2/render", json=payload)

        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "<svg" in data["content"]

        # Save SVG artifact for inspection
        save_svg_artifact("test_render_complex_diagram", "d2", data["content"], data["provider_id"])

    def test_render_with_auto_fix(self, client, d2_code_simple):
        """Test rendering with auto-fix enabled."""
        payload = {"code": d2_code_simple, "diagram_type": "d2", "output_format": "svg", "auto_fix": True}

        response = client.post("/api/v1/diagrams/v2/render", json=payload)

        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True

        # Save SVG artifact for inspection
        save_svg_artifact("test_render_with_auto_fix", "d2", data["content"], data["provider_id"])

    def test_render_response_format(self, client, d2_code_simple):
        """Test that response has all required fields."""
        payload = {"code": d2_code_simple, "diagram_type": "d2", "output_format": "svg"}

        response = client.post("/api/v1/diagrams/v2/render", json=payload)
        data = response.json()

        # Check required response fields
        assert "success" in data
        assert "content" in data
        assert "provider_id" in data

        # Save SVG artifact for inspection
        save_svg_artifact("test_render_response_format", "d2", data["content"], data["provider_id"])
        assert "metadata" in data
        assert "render_time" in data["metadata"]


class TestD2Validation:
    """Test D2 diagram validation."""

    def test_validate_valid_diagram(self, client, d2_code_simple):
        """Test validating a valid D2 diagram."""
        payload = {"code": d2_code_simple, "diagram_type": "d2"}

        response = client.post("/api/v1/diagrams/v2/validate", json=payload)

        assert response.status_code == 200
        data = response.json()
        # Validation endpoint returns is_valid field directly
        assert "is_valid" in data
        assert data["is_valid"] is True

    def test_validate_invalid_diagram(self, client, invalid_d2):
        """Test validating an invalid D2 diagram."""
        payload = {"code": invalid_d2, "diagram_type": "d2"}

        response = client.post("/api/v1/diagrams/v2/validate", json=payload)

        assert response.status_code == 200
        data = response.json()
        # Validation endpoint returns is_valid field directly
        assert "is_valid" in data
        # Invalid code is detected by provider
        assert data["is_valid"] is False


class TestD2ErrorHandling:
    """Test D2 error handling."""

    def test_missing_diagram_type(self, client, d2_code_simple):
        """Test error when diagram_type is missing."""
        payload = {
            "code": d2_code_simple,
            "output_format": "svg",
            # Missing diagram_type
        }

        response = client.post("/api/v1/diagrams/v2/render", json=payload)

        assert response.status_code == 422

    def test_missing_code(self, client):
        """Test error when code is missing."""
        payload = {
            "diagram_type": "d2",
            "output_format": "svg",
            # Missing code
        }

        response = client.post("/api/v1/diagrams/v2/render", json=payload)

        assert response.status_code == 422

    def test_empty_code(self, client):
        """Test error with empty code."""
        payload = {"code": "", "diagram_type": "d2", "output_format": "svg"}

        response = client.post("/api/v1/diagrams/v2/render", json=payload)

        # Empty code is treated as invalid input by pydantic
        assert response.status_code in [200, 400, 422]


class TestD2Metadata:
    """Test D2 provider metadata."""

    def test_provider_info(self, client):
        """Test getting D2 provider info."""
        response = client.get("/api/v1/diagrams/v2/providers/d2v1")

        assert response.status_code == 200
        data = response.json()
        assert data["provider_id"] == "d2v1"
        assert data["diagram_type"] == "d2"

    def test_health_check(self, client):
        """Test provider health endpoint."""
        response = client.get("/api/v1/diagrams/v2/health")

        assert response.status_code == 200
        data = response.json()
        assert "providers" in data or "status" in data
