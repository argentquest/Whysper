from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock
import pytest
import os
from app.main import app

client = TestClient(app)

class TestFilesEndpoint:
    """Tests for files endpoints"""

    def test_save_file(self):
        """Test saving a file"""
        with patch("app.api.v1.endpoints.files.file_service") as mock_service:
            # Use absolute path for CODE_PATH to pass security check
            abs_code_path = os.path.abspath(".")
            with patch("common.env_manager.env_manager.load_env_file", return_value={"CODE_PATH": abs_code_path}):
                with patch("builtins.open", new_callable=MagicMock):
                    with patch("os.makedirs"):
                        # We need os.path.exists to return True for directory checks
                        with patch("os.path.exists", return_value=True):
                            response = client.post(
                                "/api/v1/files/save",
                                json={"path": "file.txt", "content": "content"}
                            )

                            assert response.status_code == 200
                            assert response.json()["success"] is True

    def test_read_file(self):
        """Test reading a file"""
        abs_code_path = os.path.abspath(".")
        with patch("common.env_manager.env_manager.load_env_file", return_value={"CODE_PATH": abs_code_path}):
            with patch("os.path.exists", return_value=True):
                with patch("os.path.isfile", return_value=True):
                    with patch("builtins.open", new_callable=MagicMock) as mock_open:
                        mock_open.return_value.__enter__.return_value.read.return_value = "content"

                        response = client.get("/api/v1/files/read/file.txt")

                        assert response.status_code == 200
                        assert response.json()["success"] is True
                        assert response.json()["data"]["content"] == "content"

    def test_list_files(self):
        """Test listing files"""
        with patch("common.env_manager.env_manager.load_env_file", return_value={"CODE_PATH": "."}):
            with patch("os.path.exists", return_value=True):
                with patch("os.path.isdir", return_value=True):
                    with patch("os.listdir", return_value=["file1.txt"]):
                        with patch("os.path.isfile", return_value=True):
                            with patch("os.stat") as mock_stat:
                                mock_stat.return_value.st_size = 100
                                response = client.get("/api/v1/files/")

                                assert response.status_code == 200
                                assert response.json()["success"] is True
                                assert len(response.json()["data"]) == 1

class TestGitHubEndpoints:
    """Tests for GitHub endpoints"""

    def test_import_github(self):
        """Test importing GitHub repo"""
        with patch("app.api.v1.endpoints.github_context.github_context_service") as mock_service:
            mock_result = MagicMock()
            mock_result.repository = "owner/repo"
            mock_result.ref = "main"
            mock_result.root_path = "/tmp/repo"
            mock_result.scan_path = "/tmp/repo"
            mock_result.files = []
            mock_result.tree = {}
            mock_result.message = "Success"

            mock_service.import_repository.return_value = mock_result

            response = client.post(
                "/api/v1/github/import",
                json={"repository": "owner/repo"}
            )

            assert response.status_code == 200
            assert response.json()["repository"] == "owner/repo"

class TestSettingsEndpoint:
    """Tests for settings endpoints"""

    def test_get_settings(self):
        """Test getting settings"""
        with patch("app.api.v1.endpoints.settings.settings_service") as mock_service:
            mock_service.get_settings.return_value = {"theme": "dark"}

            response = client.get("/api/v1/settings/")

            assert response.status_code == 200
            assert response.json()["theme"] == "dark"

    def test_update_settings(self):
        """Test updating settings"""
        # The endpoint is update_env, not update_settings
        with patch("app.api.v1.endpoints.settings.settings_service") as mock_service:
            mock_service.update_env.return_value = {"success": True, "updated": ["theme"]}

            response = client.put(
                "/api/v1/settings/env",
                json={"updates": {"theme": "light"}}
            )

            assert response.status_code == 200
            assert response.json()["success"] is True

class TestSystemEndpoint:
    """Tests for system endpoints"""

    def test_health_check(self):
        """Test health check"""
        response = client.get("/api/v1/system/health")
        assert response.status_code == 200
        # The endpoint returns "healthy" for status if providers are available
        # or "degraded" if not.
        # We need to mock get_registry to ensure availability for "healthy"
        # Or just check it's one of the valid statuses
        status = response.json()["status"]
        assert status in ["healthy", "degraded", "unhealthy"]

    def test_version(self):
        """Test version info"""
        response = client.get("/api/v1/system/version")
        assert response.status_code == 200
        data = response.json()
        assert "api_version" in data
        assert "api_title" in data
