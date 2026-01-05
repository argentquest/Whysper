from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock, AsyncMock
import pytest
from app.main import app

client = TestClient(app)

class TestCodeEndpoint:
    """Tests for code extraction endpoints"""

    def test_extract_code_success(self):
        """Test successful code extraction"""
        with patch("app.api.v1.endpoints.code.extract_code_blocks_from_content") as mock_extract:
            mock_extract.return_value = [
                {"language": "python", "code": "print('hello')"}
            ]

            response = client.post(
                "/api/v1/code/extract",
                json={"content": "```python\nprint('hello')\n```", "messageId": "123"}
            )

            assert response.status_code == 200
            data = response.json()
            assert data["success"] is True
            assert len(data["data"]) == 1
            assert data["data"][0]["language"] == "python"

    def test_extract_code_empty(self):
        """Test extraction with empty content"""
        # Note: The code checks for message_id but also tries to find content if not provided
        # We provide message_id to pass validation
        response = client.post(
            "/api/v1/code/extract",
            json={"content": "", "messageId": "123"}
        )
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert len(data["data"]) == 0

    def test_extract_code_error(self):
        """Test error handling in extraction"""
        with patch("app.api.v1.endpoints.code.extract_code_blocks_from_content") as mock_extract:
            mock_extract.side_effect = Exception("Extraction failed")

            response = client.post(
                "/api/v1/code/extract",
                json={"content": "some code", "messageId": "123"}
            )

            assert response.status_code == 500
            assert "Extraction failed" in response.json()["detail"]


class TestDiagramEndpoint:
    """Tests for diagram endpoints"""

    def test_generate_diagram_status_success(self):
        """Test getting diagram status success"""
        with patch("app.api.v1.endpoints.diagram.DiagramSessionStore") as mock_store:
            with patch("app.api.v1.endpoints.diagram.DiagramFactoryService") as mock_service_cls:
                mock_session = MagicMock()
                mock_store.get_session.return_value = mock_session

                mock_service = MagicMock()
                mock_service.get_status.return_value = {
                    "session_id": "test_id",
                    "status": "complete",
                    "diagram_code": "graph TD; A-->B;",
                    "diagram_type": "mermaid"
                }
                mock_service_cls.return_value = mock_service

                response = client.get("/api/v1/diagram/test_id")

                assert response.status_code == 200
                data = response.json()
                assert data["session_id"] == "test_id"
                assert data["status"] == "complete"

    def test_generate_diagram_status_not_found(self):
        """Test getting diagram status not found"""
        with patch("app.api.v1.endpoints.diagram.DiagramSessionStore") as mock_store:
            mock_store.get_session.return_value = None

            response = client.get("/api/v1/diagram/non_existent_id")

            assert response.status_code == 404

    def test_generate_diagram_start(self):
        """Test starting diagram generation"""
        with patch("app.api.v1.endpoints.diagram.DiagramSessionStore") as mock_store:
            with patch("app.api.v1.endpoints.diagram.DiagramFactoryService") as mock_service_cls:
                mock_session = MagicMock()
                mock_session.session_id = "new_session_id"
                mock_store.create_session.return_value = mock_session

                mock_service = MagicMock()
                mock_service.start_generation = AsyncMock()
                # Use a dictionary for status, as required by the schema
                mock_service.get_status.return_value = {"status": "started"}
                mock_service_cls.return_value = mock_service

                response = client.post(
                    "/api/v1/diagram/start",
                    json={
                        "initial_prompt": "Create a flow diagram",
                        "diagram_type": "mermaid"
                    }
                )

                assert response.status_code == 200
                data = response.json()
                assert data["session_id"] == "new_session_id"
                assert data["status"]["status"] == "started"

    def test_generate_diagram_start_error(self):
        """Test starting diagram generation error"""
        with patch("app.api.v1.endpoints.diagram.DiagramSessionStore") as mock_store:
            mock_store.create_session.side_effect = Exception("Generation failed")

            response = client.post(
                "/api/v1/diagram/start",
                json={
                    "initial_prompt": "Create a flow diagram",
                    "diagram_type": "mermaid"
                }
            )

            assert response.status_code == 500
            assert "Generation failed" in response.json()["detail"]

    def test_validate_session(self):
        """Test validate_session endpoint"""
        with patch("app.api.v1.endpoints.diagram.DiagramSessionStore") as mock_store:
            mock_store.get_session.return_value = MagicMock()

            response = client.get("/api/v1/diagram/validate/test_id")

            assert response.status_code == 200
            assert response.json() == {"exists": True, "session_id": "test_id"}

    def test_delete_session(self):
        """Test delete_session endpoint"""
        with patch("app.api.v1.endpoints.diagram.DiagramSessionStore") as mock_store:
            mock_store.get_session.return_value = MagicMock()
            mock_store.delete_session.return_value = True

            response = client.delete("/api/v1/diagram/test_id")

            assert response.status_code == 200
            assert response.json()["message"] == "Session test_id deleted"

    def test_submit_clarification(self):
        """Test submitting clarification"""
        with patch("app.api.v1.endpoints.diagram.DiagramSessionStore") as mock_store:
            with patch("app.api.v1.endpoints.diagram.DiagramFactoryService") as mock_service_cls:
                mock_store.get_session.return_value = MagicMock()

                mock_service = MagicMock()
                mock_service.handle_clarification = AsyncMock()
                mock_service.get_status.return_value = {"status": "clarified"}
                mock_service_cls.return_value = mock_service

                response = client.post(
                    "/api/v1/diagram/clarify",
                    json={"session_id": "test_id", "response": "Yes, please"}
                )

                assert response.status_code == 200
                assert response.json() == {"status": "clarified"}

    def test_confirm_ready(self):
        """Test confirm ready"""
        with patch("app.api.v1.endpoints.diagram.DiagramSessionStore") as mock_store:
            with patch("app.api.v1.endpoints.diagram.DiagramFactoryService") as mock_service_cls:
                mock_store.get_session.return_value = MagicMock()

                mock_service = MagicMock()
                mock_service.confirm_ready = AsyncMock()
                mock_service.get_status.return_value = {"status": "confirmed"}
                mock_service_cls.return_value = mock_service

                response = client.post(
                    "/api/v1/diagram/confirm_ready",
                    json={"session_id": "test_id"}
                )

                assert response.status_code == 200
                assert response.json() == {"status": "confirmed"}

    def test_select_diagram_type(self):
        """Test select diagram type"""
        with patch("app.api.v1.endpoints.diagram.DiagramSessionStore") as mock_store:
            with patch("app.api.v1.endpoints.diagram.DiagramFactoryService") as mock_service_cls:
                mock_store.get_session.return_value = MagicMock()

                mock_service = MagicMock()
                mock_service.select_diagram_type = AsyncMock()
                mock_service.get_status.return_value = {"status": "selected"}
                mock_service_cls.return_value = mock_service

                response = client.post(
                    "/api/v1/diagram/select_diagram_type",
                    json={"session_id": "test_id", "diagram_type": "d2"}
                )

                assert response.status_code == 200
                assert response.json() == {"status": "selected"}

    def test_approve_render(self):
        """Test approve render"""
        with patch("app.api.v1.endpoints.diagram.DiagramSessionStore") as mock_store:
            with patch("app.api.v1.endpoints.diagram.DiagramFactoryService") as mock_service_cls:
                mock_store.get_session.return_value = MagicMock()

                mock_service = MagicMock()
                mock_service.approve_render = AsyncMock()
                mock_service.get_status.return_value = {"status": "approved"}
                mock_service_cls.return_value = mock_service

                response = client.post(
                    "/api/v1/diagram/approve_render",
                    json={"session_id": "test_id"}
                )

                assert response.status_code == 200
                assert response.json() == {"status": "approved"}

    def test_render_diagram(self):
        """Test render diagram"""
        with patch("app.api.v1.endpoints.diagram.DiagramSessionStore") as mock_store:
            with patch("app.api.v1.endpoints.diagram.DiagramFactoryService") as mock_service_cls:
                mock_store.get_session.return_value = MagicMock()

                mock_service = MagicMock()
                mock_service.render_diagram = AsyncMock(return_value={"image": "base64..."})
                mock_service_cls.return_value = mock_service

                response = client.post(
                    "/api/v1/diagram/render",
                    json={"session_id": "test_id", "code": "graph TD; A-->B;"}
                )

                assert response.status_code == 200
                assert response.json() == {"image": "base64..."}

    def test_add_form_data_to_session(self):
        """Test adding form data to session"""
        with patch("app.api.v1.endpoints.diagram.DiagramSessionStore") as mock_store:
            with patch("app.api.v1.endpoints.diagram.DiagramFactoryService") as mock_service_cls:
                with patch("os.path.exists", return_value=True):
                    with patch("builtins.open", new_callable=MagicMock) as mock_open:
                        # Mock file reads
                        mock_file = MagicMock()
                        mock_file.__enter__.return_value.read.return_value = "{}"
                        mock_open.return_value = mock_file

                        mock_session = MagicMock()
                        mock_session.FormsData = []
                        mock_store.get_session.return_value = mock_session

                        mock_service = MagicMock()
                        mock_service.get_status.return_value = {"status": "updated"}
                        mock_service_cls.return_value = mock_service

                        response = client.post(
                            "/api/v1/diagram/add_form_data",
                            json={"session_id": "test_id", "submission_id": "sub_123"}
                        )

                        assert response.status_code == 200
                        assert response.json() == {"status": "updated"}
                        assert len(mock_session.FormsData) == 1
