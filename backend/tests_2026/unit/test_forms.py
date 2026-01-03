import unittest
from unittest.mock import MagicMock, patch, mock_open
import os
import sys
import json

backend_path = os.path.abspath("backend")
if backend_path not in sys.path:
    sys.path.insert(0, backend_path)

# Correct import based on findings: app.services.form_service.FormService
from app.services.form_service import FormService

class TestFormProcessor(unittest.TestCase):

    def test_publish_form(self):
        """Test publishing a form."""
        service = FormService()

        mock_data = {
            "form_name": "Test Form",
            "form_description": "Desc",
            "form_type": "type",
            "version": "1.0",
            "schema": {},
            "ui_schema": {},
            "form_data": {}
        }

        with patch("builtins.open", mock_open()) as mock_file:
            with patch("os.makedirs"):
                with patch("os.path.exists", return_value=False):

                    form_id = service.publish_form(mock_data)
                    self.assertIsNotNone(form_id)
                    mock_file.assert_called()

    def test_submit_form(self):
        """Test submitting a form."""
        service = FormService()

        mock_submission = {
            "form_id": "test-form-id",
            "form_data": {"key": "val"},
            "session_id": "sess-1"
        }

        with patch("builtins.open", mock_open()) as mock_file:
            with patch("os.makedirs"):
                 # submit_form likely reads the form definition first, then saves submission
                 # We need to ensure it can 'read' the form def if it validates

                 # If submit_form just writes, this is enough.
                 # If it validates, we might need to mock open read behavior too.

                 # Let's try to mock writing only for now.
                 submission_id = service.submit_form(mock_submission)
                 self.assertIsNotNone(submission_id)
