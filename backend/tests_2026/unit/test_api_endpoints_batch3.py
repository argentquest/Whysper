from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock
import pytest
from app.main import app

client = TestClient(app)

class TestDiagramProvider:
    """Tests for diagram provider endpoints"""

    def test_list_providers(self):
        """Test listing diagram providers"""
        with patch("app.api.v1.endpoints.diagram_provider.get_registry") as mock_registry:
            mock_registry.return_value.list_all.return_value = []
            mock_registry.return_value.get_statistics.return_value = {
                "total_providers": 0,
                "available_providers": 0,
                "unavailable_providers": 0,
            }

            # Correct path with v2
            response = client.get("/api/v1/diagrams/v2/providers")

            assert response.status_code == 200
            data = response.json()
            assert "providers" in data

    def test_render_diagram(self):
        """Test rendering diagram via provider API"""
        with patch("app.api.v1.endpoints.diagram_provider.get_registry") as mock_registry:
            with patch("app.api.v1.endpoints.diagram_provider.get_provider_for_request") as mock_get_provider:
                mock_provider = MagicMock()
                mock_provider.provider_id = "test_provider"
                mock_provider.provider_name = "Test Provider"

                mock_result = MagicMock()
                mock_result.success = True
                mock_result.content = "svg_content"
                mock_result.output_format = "svg"
                mock_result.validation.is_valid = True
                mock_result.validation.error = None
                mock_result.validation.auto_fixed = False
                mock_result.validation.llm_corrected = False
                mock_result.validation.correction_method = None
                mock_result.metadata = {}
                mock_result.error = None

                mock_provider.render.return_value = mock_result
                mock_get_provider.return_value = mock_provider

                # Correct path with v2
                response = client.post(
                    "/api/v1/diagrams/v2/render",
                    json={
                        "code": "graph TD; A-->B;",
                        "diagram_type": "mermaid",
                        "output_format": "svg"
                    }
                )

                assert response.status_code == 200
                data = response.json()
                assert data["success"] is True
                assert data["content"] == "svg_content"

    def test_validate_diagram(self):
        """Test validating diagram"""
        with patch("app.api.v1.endpoints.diagram_provider.get_registry") as mock_registry:
            with patch("app.api.v1.endpoints.diagram_provider.get_provider_for_request") as mock_get_provider:
                mock_provider = MagicMock()
                mock_provider.provider_id = "test_provider"

                mock_result = MagicMock()
                mock_result.is_valid = True
                mock_result.error = None
                mock_result.auto_fixed = False
                mock_result.llm_corrected = False
                mock_result.fixed_code = None
                mock_result.correction_method = None

                mock_provider.validate_code.return_value = mock_result
                mock_get_provider.return_value = mock_provider

                # Correct path with v2
                response = client.post(
                    "/api/v1/diagrams/v2/validate",
                    json={
                        "code": "graph TD; A-->B;",
                        "diagram_type": "mermaid"
                    }
                )

                assert response.status_code == 200
                data = response.json()
                assert data["is_valid"] is True

class TestDocumentation:
    """Tests for documentation endpoints"""

    def test_generate_documentation(self):
        """Test generating documentation"""
        with patch("app.api.v1.endpoints.documentation.documentation_service") as mock_service:
            mock_result = MagicMock()
            mock_result.id = "doc_id"
            mock_result.content = "Documentation content"
            mock_result.metadata = {"session_guid": "guid_123"}

            mock_service.generate_documentation_with_guid.return_value = mock_result

            response = client.post(
                "/api/v1/documentation/generate",
                json={
                    "file_paths": ["file1.py"]
                }
            )

            assert response.status_code == 200
            data = response.json()
            assert data["session_guid"] == "guid_123"

    def test_download_documentation(self):
        """Test downloading documentation"""
        with patch("app.api.v1.endpoints.documentation.documentation_service") as mock_service:
            # Setup cache
            mock_service.cache = {"guid_123": ({"doc": "data"}, ["file1.py"])}
            mock_service.create_documentation_zip.return_value = b"zip_content"

            response = client.get("/api/v1/documentation/download/guid_123")

            assert response.status_code == 200
            assert response.headers["content-type"] == "application/zip"

    def test_download_documentation_not_found(self):
        """Test downloading documentation not found"""
        with patch("app.api.v1.endpoints.documentation.documentation_service") as mock_service:
            mock_service.cache = {}

            response = client.get("/api/v1/documentation/download/non_existent")

            assert response.status_code == 404
            assert "not found" in response.json()["detail"].lower()
