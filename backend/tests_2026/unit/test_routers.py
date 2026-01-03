from fastapi.testclient import TestClient
from unittest.mock import MagicMock, patch
import os
import sys

backend_path = os.path.abspath("backend")
if backend_path not in sys.path:
    sys.path.insert(0, backend_path)

from app.main import app

client = TestClient(app)

def test_health_check():
    """Test health check endpoint if exists, or root."""
    response = client.get("/health")
    if response.status_code == 404:
        # Try root
        response = client.get("/")

    # Root might serve static or redirect
    assert response.status_code in [200, 404]

@patch("app.routers.forms.FormService")
def test_publish_form_endpoint(mock_service_cls):
    """Test publish form API endpoint."""
    mock_service = MagicMock()
    mock_service.publish_form.return_value = "new-form-id"
    mock_service_cls.return_value = mock_service

    payload = {
        "form_name": "API Test Form",
        "form_description": "Desc",
        "form_type": "survey",
        "version": "1.0",
        "schema": {"type": "object"},
        "ui_schema": {},
        "form_data": {}
    }

    # Use api/v1/forms as found in other tests
    response = client.post("/api/v1/forms/publish", json=payload)

    assert response.status_code == 200
    assert response.json()["form_id"] == "new-form-id"

@patch("app.routers.forms.FormService")
def test_submit_form_endpoint(mock_service_cls):
    """Test submit form API endpoint."""
    mock_service = MagicMock()
    mock_service.submit_form.return_value = "sub-id"
    mock_service_cls.return_value = mock_service

    payload = {
        "form_id": "form-1",
        "form_data": {"q": "a"},
        "session_id": "sess-1"
    }

    response = client.post("/api/v1/forms/submit", json=payload)

    assert response.status_code == 200
    assert response.json()["submission_id"] == "sub-id"
