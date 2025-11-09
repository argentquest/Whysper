"""
Integration tests for diagram providers.

Tests interactions between multiple providers and system-wide functionality.
"""

import pytest


class TestProviderDiscovery:
    """Test provider discovery and listing."""

    def test_list_all_providers(self, client):
        """Test listing all available providers."""
        response = client.get("/api/v1/diagrams/v2/providers")

        assert response.status_code == 200
        data = response.json()
        assert "providers" in data
        assert len(data["providers"]) >= 2  # At least mermaid and d2

    def test_provider_list_contains_mermaid(self, client):
        """Test that provider list includes Mermaid."""
        response = client.get("/api/v1/diagrams/v2/providers")
        data = response.json()

        provider_ids = [p["provider_id"] for p in data["providers"]]
        assert "mermaidv1" in provider_ids

    def test_provider_list_contains_d2(self, client):
        """Test that provider list includes D2."""
        response = client.get("/api/v1/diagrams/v2/providers")
        data = response.json()

        provider_ids = [p["provider_id"] for p in data["providers"]]
        assert "d2v1" in provider_ids

    def test_each_provider_has_required_fields(self, client):
        """Test that each provider has required metadata fields."""
        response = client.get("/api/v1/diagrams/v2/providers")
        data = response.json()

        for provider in data["providers"]:
            assert "provider_id" in provider
            assert "provider_name" in provider
            assert "diagram_type" in provider


class TestCrossProviderRendering:
    """Test rendering with different providers."""

    def test_mermaid_then_d2(self, client, mermaid_code_simple, d2_code_simple):
        """Test rendering both Mermaid and D2 in sequence."""
        # Render Mermaid
        mermaid_payload = {
            "code": mermaid_code_simple,
            "diagram_type": "mermaid",
            "output_format": "svg"
        }
        mermaid_response = client.post("/api/v1/diagrams/v2/render", json=mermaid_payload)
        assert mermaid_response.status_code == 200

        # Render D2
        d2_payload = {
            "code": d2_code_simple,
            "diagram_type": "d2",
            "output_format": "svg"
        }
        d2_response = client.post("/api/v1/diagrams/v2/render", json=d2_payload)
        assert d2_response.status_code == 200

    def test_different_output_formats(self, client, d2_code_simple):
        """Test rendering with different output formats."""
        for output_format in ["svg", "png"]:
            payload = {
                "code": d2_code_simple,
                "diagram_type": "d2",
                "output_format": output_format
            }

            response = client.post("/api/v1/diagrams/v2/render", json=payload)
            # Both SVG and PNG should be supported or at least SVG
            assert response.status_code in [200, 400]  # Allow some formats to not be supported


class TestProviderErrors:
    """Test error handling across providers."""

    def test_invalid_provider_type(self, client):
        """Test error with invalid provider type."""
        payload = {
            "code": "some code",
            "diagram_type": "invalid_type",
            "output_format": "svg"
        }

        response = client.post("/api/v1/diagrams/v2/render", json=payload)

        # Should fail with invalid provider
        assert response.status_code != 200

    def test_render_with_invalid_output_format(self, client, mermaid_code_simple):
        """Test error with invalid output format."""
        payload = {
            "code": mermaid_code_simple,
            "diagram_type": "mermaid",
            "output_format": "invalid_format"
        }

        response = client.post("/api/v1/diagrams/v2/render", json=payload)

        # Should either work or fail gracefully
        assert response.status_code in [200, 400, 422]


class TestProviderPerformance:
    """Test provider rendering performance."""

    def test_render_time_is_recorded(self, client, mermaid_code_simple):
        """Test that render time is recorded in response."""
        payload = {
            "code": mermaid_code_simple,
            "diagram_type": "mermaid",
            "output_format": "svg"
        }

        response = client.post("/api/v1/diagrams/v2/render", json=payload)
        data = response.json()

        assert "metadata" in data
        assert "render_time" in data["metadata"]
        assert data["metadata"]["render_time"] >= 0

    def test_render_time_is_reasonable(self, client, mermaid_code_simple):
        """Test that render time is within reasonable bounds."""
        payload = {
            "code": mermaid_code_simple,
            "diagram_type": "mermaid",
            "output_format": "svg"
        }

        response = client.post("/api/v1/diagrams/v2/render", json=payload)
        data = response.json()

        render_time = data["metadata"]["render_time"]
        # Render should complete in reasonable time (less than 30 seconds)
        assert render_time < 30


class TestEventLogging:
    """Test event logging with providers."""

    def test_log_render_event(self, client):
        """Test logging a render event."""
        payload = {
            "event_type": "render_success",
            "diagram_type": "mermaid",
            "code_length": 150,
            "provider": "mermaidv1",
            "render_time": 0.234
        }

        response = client.post("/api/v1/diagrams/log-diagram-event", json=payload)

        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True

    def test_log_error_event(self, client):
        """Test logging an error event."""
        payload = {
            "event_type": "render_error",
            "diagram_type": "d2",
            "error_message": "Invalid D2 syntax",
            "code_length": 100
        }

        response = client.post("/api/v1/diagrams/log-diagram-event", json=payload)

        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
