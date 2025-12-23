import pytest
from fastapi.testclient import TestClient
from app.main import app
import os
import shutil
import json

client = TestClient(app)

# Test Data
SAMPLE_FORM = {
    "form_name": "Test Contact Form",
    "form_description": "A test form for unit testing",
    "form_type": "test-contact",
    "version": "1.0",
    "schema": {
        "type": "object",
        "properties": {
            "name": {"type": "string"},
            "email": {"type": "string"}
        }
    },
    "ui_schema": {
        "email": {"ui:widget": "email"}
    },
    "form_data": {
        "name": "John Doe",
        "email": "john@example.com"
    }
}

@pytest.fixture(autouse=True)
def setup_teardown():
    # Setup: Ensure clean state
    if os.path.exists("forms"):
        # We don't delete the whole forms dir as it might contain other stuff,
        # but for this test environment it's likely safe or we should be specific.
        # Let's clean up specific test artifacts.
        pass

    yield

    # Teardown: Clean up created files
    # Note: In a real env we might use a temp dir override for settings.
    pass

def test_publish_form():
    response = client.post("/api/v1/forms/publish", json=SAMPLE_FORM)
    assert response.status_code == 200
    data = response.json()
    assert "form_id" in data
    assert "message" in data

    form_id = data["form_id"]
    assert os.path.exists(f"forms/{form_id}/metadata.json")
    assert os.path.exists(f"forms/{form_id}/schema.json")

    return form_id

def test_get_published_forms():
    # Ensure at least one form exists
    test_publish_form()

    response = client.get("/api/v1/forms/published")
    assert response.status_code == 200
    forms = response.json()
    assert isinstance(forms, list)
    assert len(forms) > 0

    # Check structure
    form = forms[0]
    assert "form_id" in form
    assert "form_name" in form

def test_submit_form():
    form_id = test_publish_form()

    submission_payload = {
        "form_id": form_id,
        "form_data": {
            "name": "Jane Doe",
            "email": "jane@example.com"
        },
        "session_id": "test-session-123"
    }

    response = client.post("/api/v1/forms/submit", json=submission_payload)
    assert response.status_code == 200
    data = response.json()
    assert "submission_id" in data

    submission_id = data["submission_id"]
    assert os.path.exists(f"UserFormData/{submission_id}/form_data.json")

    return submission_id

def test_get_submissions():
    test_submit_form()

    response = client.get("/api/v1/forms/submissions")
    assert response.status_code == 200
    submissions = response.json()
    assert isinstance(submissions, list)
    assert len(submissions) > 0

def test_get_single_submission():
    submission_id = test_submit_form()

    response = client.get(f"/api/v1/forms/submissions/{submission_id}")
    assert response.status_code == 200
    data = response.json()
    assert "metadata" in data
    assert "form_data" in data
    assert data["form_data"]["name"] == "Jane Doe"

def test_edit_submission():
    submission_id = test_submit_form()

    # Need to know the form_id from the submission to edit it properly
    # (though our API currently requires passing it back in payload)
    # Get the submission first to get form_id
    get_res = client.get(f"/api/v1/forms/submissions/{submission_id}")
    form_id = get_res.json()["metadata"]["form_id"]

    edit_payload = {
        "form_id": form_id,
        "form_data": {
            "name": "Jane Doe Edited",
            "email": "jane.edited@example.com"
        },
        "session_id": "test-session-123"
    }

    response = client.put(f"/api/v1/forms/edit/{submission_id}", json=edit_payload)
    assert response.status_code == 200
    data = response.json()
    new_submission_id = data["submission_id"]

    assert new_submission_id != submission_id

    # Verify new submission has reference to old one
    new_sub_res = client.get(f"/api/v1/forms/submissions/{new_submission_id}")
    metadata = new_sub_res.json()["metadata"]
    assert metadata["is_edited"] == True
    assert metadata["original_submission_id"] == submission_id
