"""
Tests for Mermaid diagram provider rendering.
"""

import pytest
import sys
import os
from pathlib import Path

# Import from root conftest
sys.path.insert(0, str(Path(__file__).parent.parent))
from conftest import save_svg_artifact


class TestMermaidRenderingBasic:
    """Test basic Mermaid diagram rendering."""

    def test_render_simple_flowchart(self, client, mermaid_code_simple):
        """Test rendering a simple flowchart."""
        payload = {
            "code": mermaid_code_simple,
            "diagram_type": "mermaid",
            "output_format": "svg"
        }

        response = client.post("/api/v1/diagrams/v2/render", json=payload)

        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["content"] is not None
        assert len(data["content"]) > 0
        assert "<svg" in data["content"]
        assert "provider_id" in data
        assert data["provider_id"] == "mermaidv1"

        # Save SVG artifact for inspection
        save_svg_artifact("test_render_simple_flowchart", "mermaid", data["content"], data["provider_id"])

    def test_render_complex_flowchart(self, client, mermaid_code_complex):
        """Test rendering a complex flowchart."""
        payload = {
            "code": mermaid_code_complex,
            "diagram_type": "mermaid",
            "output_format": "svg"
        }

        response = client.post("/api/v1/diagrams/v2/render", json=payload)

        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "<svg" in data["content"]

        # Save SVG artifact for inspection
        save_svg_artifact("test_render_complex_flowchart", "mermaid", data["content"], data["provider_id"])

    def test_render_with_auto_fix(self, client, mermaid_code_simple):
        """Test rendering with auto-fix enabled."""
        payload = {
            "code": mermaid_code_simple,
            "diagram_type": "mermaid",
            "output_format": "svg",
            "auto_fix": True
        }

        response = client.post("/api/v1/diagrams/v2/render", json=payload)

        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True

        # Save SVG artifact for inspection
        save_svg_artifact("test_render_with_auto_fix", "mermaid", data["content"], data["provider_id"])

    def test_render_response_format(self, client, mermaid_code_simple):
        """Test that response has all required fields."""
        payload = {
            "code": mermaid_code_simple,
            "diagram_type": "mermaid",
            "output_format": "svg"
        }

        response = client.post("/api/v1/diagrams/v2/render", json=payload)
        data = response.json()

        # Check required response fields
        assert "success" in data
        assert "content" in data
        assert "provider_id" in data

        # Save SVG artifact for inspection
        save_svg_artifact("test_render_response_format", "mermaid", data["content"], data["provider_id"])
        assert "metadata" in data
        assert "render_time" in data["metadata"]


class TestMermaidValidation:
    """Test Mermaid diagram validation."""

    def test_validate_valid_diagram(self, client, mermaid_code_simple):
        """Test validating a valid diagram."""
        payload = {
            "code": mermaid_code_simple,
            "diagram_type": "mermaid"
        }

        response = client.post("/api/v1/diagrams/v2/validate", json=payload)

        assert response.status_code == 200
        data = response.json()
        # Validation endpoint returns is_valid field directly
        assert "is_valid" in data
        assert data["is_valid"] is True

    def test_validate_invalid_diagram(self, client, invalid_mermaid):
        """Test validating an invalid diagram."""
        payload = {
            "code": invalid_mermaid,
            "diagram_type": "mermaid"
        }

        response = client.post("/api/v1/diagrams/v2/validate", json=payload)

        assert response.status_code == 200
        data = response.json()
        # Validation endpoint returns is_valid field directly
        assert "is_valid" in data
        # Invalid code is detected by provider
        assert data["is_valid"] is False


class TestMermaidErrorHandling:
    """Test Mermaid error handling."""

    def test_missing_diagram_type(self, client, mermaid_code_simple):
        """Test error when diagram_type is missing."""
        payload = {
            "code": mermaid_code_simple,
            "output_format": "svg"
            # Missing diagram_type
        }

        response = client.post("/api/v1/diagrams/v2/render", json=payload)

        assert response.status_code == 422  # Unprocessable entity

    def test_missing_code(self, client):
        """Test error when code is missing."""
        payload = {
            "diagram_type": "mermaid",
            "output_format": "svg"
            # Missing code
        }

        response = client.post("/api/v1/diagrams/v2/render", json=payload)

        assert response.status_code == 422

    def test_empty_code(self, client):
        """Test error with empty code."""
        payload = {
            "code": "",
            "diagram_type": "mermaid",
            "output_format": "svg"
        }

        response = client.post("/api/v1/diagrams/v2/render", json=payload)

        # Empty code is treated as invalid input by pydantic
        assert response.status_code in [200, 400, 422]


class TestMermaidMetadata:
    """Test Mermaid provider metadata."""

    def test_provider_info(self, client):
        """Test getting Mermaid provider info."""
        response = client.get("/api/v1/diagrams/v2/providers/mermaidv1")

        assert response.status_code == 200
        data = response.json()
        assert data["provider_id"] == "mermaidv1"
        assert data["diagram_type"] == "mermaid"

    def test_health_check(self, client):
        """Test provider health endpoint."""
        response = client.get("/api/v1/diagrams/v2/health")

        assert response.status_code == 200
        data = response.json()
        assert "providers" in data or "status" in data
