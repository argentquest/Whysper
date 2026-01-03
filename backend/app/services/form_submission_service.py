import os
import json
import uuid
from datetime import datetime
from typing import Dict, Any, List
from fastapi import HTTPException
from common.logging_decorator import log_method_call


class FormSubmissionService:
    def __init__(self):
        self.submissions_directory = "UserFormData"
        self.forms_directory = "forms"
        os.makedirs(self.submissions_directory, exist_ok=True)

    @log_method_call
    def submit_form(self, submission_data: Dict[str, Any]) -> str:
        """Submit a new form and return submission_id"""
        submission_id = f"submission-{uuid.uuid4().hex[:8]}"
        submission_folder = os.path.join(self.submissions_directory, submission_id)
        os.makedirs(submission_folder, exist_ok=True)

        # Get form metadata and definition
        try:
            form_metadata = self._get_form_metadata(submission_data["form_id"])
            form_definition = self._get_form_definition(submission_data["form_id"])
        except HTTPException:
            # Fallback if form def not found (e.g. deleted), but try to proceed with minimal data
            form_metadata = {
                "form_name": "Unknown Form",
                "form_type": "unknown",
                "version": "1.0"
            }
            form_definition = None

        # Save form data
        with open(os.path.join(submission_folder, "form_data.json"), "w") as f:
            json.dump(submission_data["form_data"], f, indent=2)

        # Save form schema and ui_schema for edit resilience
        if form_definition:
            with open(os.path.join(submission_folder, "schema.json"), "w") as f:
                json.dump(form_definition.get("schema", {}), f, indent=2)
            with open(os.path.join(submission_folder, "ui_schema.json"), "w") as f:
                json.dump(form_definition.get("ui_schema", {}), f, indent=2)

        # Save submission metadata
        metadata = {
            "submission_id": submission_id,
            "form_id": submission_data["form_id"],
            "form_name": form_metadata.get("form_name", "Unknown"),
            "form_type": form_metadata.get("form_type", "unknown"),
            "version": form_metadata.get("version", "1.0"),
            "session_id": submission_data.get("session_id", "unknown"),
            "submission_timestamp": datetime.now().isoformat(),
            "submission_date": datetime.now().date().isoformat(),
            "is_edited": False,
            "original_submission_id": None
        }

        with open(os.path.join(submission_folder, "metadata.json"), "w") as f:
            json.dump(metadata, f, indent=2)

        return submission_id

    @log_method_call
    def edit_form_submission(self, original_submission_id: str, submission_data: Dict[str, Any]) -> str:
        """Edit existing form submission, creates new version"""
        # Create new submission
        new_submission_id = f"submission-{uuid.uuid4().hex[:8]}"
        submission_folder = os.path.join(self.submissions_directory, new_submission_id)
        os.makedirs(submission_folder, exist_ok=True)

        # Get form metadata and definition (or copy from original submission)
        try:
            form_metadata = self._get_form_metadata(submission_data["form_id"])
            form_definition = self._get_form_definition(submission_data["form_id"])
        except HTTPException:
            # Try to copy schema from original submission
            form_metadata = {
                "form_name": "Unknown Form",
                "form_type": "unknown",
                "version": "1.0"
            }
            form_definition = self._get_submission_schema(original_submission_id)

        # Save form data
        with open(os.path.join(submission_folder, "form_data.json"), "w") as f:
            json.dump(submission_data["form_data"], f, indent=2)

        # Save form schema and ui_schema for edit resilience
        if form_definition:
            with open(os.path.join(submission_folder, "schema.json"), "w") as f:
                json.dump(form_definition.get("schema", {}), f, indent=2)
            with open(os.path.join(submission_folder, "ui_schema.json"), "w") as f:
                json.dump(form_definition.get("ui_schema", {}), f, indent=2)

        # Save submission metadata with edit reference
        metadata = {
            "submission_id": new_submission_id,
            "form_id": submission_data["form_id"],
            "form_name": form_metadata.get("form_name", "Unknown"),
            "form_type": form_metadata.get("form_type", "unknown"),
            "version": form_metadata.get("version", "1.0"),
            "session_id": submission_data.get("session_id", "unknown"),
            "submission_timestamp": datetime.now().isoformat(),
            "submission_date": datetime.now().date().isoformat(),
            "is_edited": True,
            "original_submission_id": original_submission_id
        }

        with open(os.path.join(submission_folder, "metadata.json"), "w") as f:
            json.dump(metadata, f, indent=2)

        return new_submission_id

    @log_method_call
    def get_all_submissions(self) -> List[Dict[str, Any]]:
        """Get all form submissions with metadata"""
        submissions = []
        if not os.path.exists(self.submissions_directory):
            return []

        for submission_folder in os.listdir(self.submissions_directory):
            metadata_path = os.path.join(
                self.submissions_directory,
                submission_folder,
                "metadata.json"
            )

            if os.path.exists(metadata_path):
                try:
                    with open(metadata_path, "r") as f:
                        metadata = json.load(f)
                        submissions.append(metadata)
                except Exception:
                    continue

        # Sort by submission timestamp (newest first)
        submissions.sort(key=lambda x: x.get("submission_timestamp", ""), reverse=True)
        return submissions

    @log_method_call
    def get_submission(self, submission_id: str) -> Dict[str, Any]:
        """Get specific form submission with data and metadata"""
        submission_folder = os.path.join(self.submissions_directory, submission_id)

        if not os.path.exists(submission_folder):
            raise HTTPException(status_code=404, detail="Submission not found")

        # Load metadata
        with open(os.path.join(submission_folder, "metadata.json"), "r") as f:
            metadata = json.load(f)

        # Load form data
        with open(os.path.join(submission_folder, "form_data.json"), "r") as f:
            form_data = json.load(f)

        # Load schema if available (for edit resilience)
        schema = None
        ui_schema = None
        schema_path = os.path.join(submission_folder, "schema.json")
        ui_schema_path = os.path.join(submission_folder, "ui_schema.json")

        if os.path.exists(schema_path):
            with open(schema_path, "r") as f:
                schema = json.load(f)

        if os.path.exists(ui_schema_path):
            with open(ui_schema_path, "r") as f:
                ui_schema = json.load(f)

        result = {
            "metadata": metadata,
            "form_data": form_data
        }

        if schema:
            result["schema"] = schema
        if ui_schema:
            result["ui_schema"] = ui_schema

        return result

    @log_method_call
    def get_version_history(self, root_submission_id: str) -> List[Dict[str, Any]]:
        """Get all versions of a submission (original and all edits)"""
        versions = []

        # Get all submissions
        all_submissions = self.get_all_submissions()

        # Find the root submission and all its edits
        for submission in all_submissions:
            # Check if this is the root submission or one of its edits
            if (submission.get("submission_id") == root_submission_id or
                submission.get("original_submission_id") == root_submission_id):
                versions.append(submission)

        # Sort by timestamp (oldest first)
        versions.sort(key=lambda x: x.get("submission_timestamp", ""))
        return versions

    def _get_form_metadata(self, form_id: str) -> Dict[str, Any]:
        """Get metadata for a published form"""
        # Search for folder that matches form_id
        # The form_id is "contact-form-12ab34cd" (matches folder name)
        metadata_path = os.path.join(self.forms_directory, form_id, "metadata.json")

        if not os.path.exists(metadata_path):
            raise HTTPException(status_code=404, detail=f"Form {form_id} not found")

        with open(metadata_path, "r") as f:
            return json.load(f)

    def _get_form_definition(self, form_id: str) -> Dict[str, Any]:
        """Get schema and ui_schema for a published form"""
        form_folder = os.path.join(self.forms_directory, form_id)

        if not os.path.exists(form_folder):
            raise HTTPException(status_code=404, detail=f"Form {form_id} not found")

        schema_path = os.path.join(form_folder, "schema.json")
        ui_schema_path = os.path.join(form_folder, "ui_schema.json")

        schema = {}
        ui_schema = {}

        if os.path.exists(schema_path):
            with open(schema_path, "r") as f:
                schema = json.load(f)

        if os.path.exists(ui_schema_path):
            with open(ui_schema_path, "r") as f:
                ui_schema = json.load(f)

        return {
            "schema": schema,
            "ui_schema": ui_schema
        }

    def _get_submission_schema(self, submission_id: str) -> Dict[str, Any] | None:
        """Get schema from an existing submission for reuse"""
        submission_folder = os.path.join(self.submissions_directory, submission_id)

        if not os.path.exists(submission_folder):
            return None

        schema_path = os.path.join(submission_folder, "schema.json")
        ui_schema_path = os.path.join(submission_folder, "ui_schema.json")

        if not os.path.exists(schema_path):
            return None

        schema = {}
        ui_schema = {}

        if os.path.exists(schema_path):
            with open(schema_path, "r") as f:
                schema = json.load(f)

        if os.path.exists(ui_schema_path):
            with open(ui_schema_path, "r") as f:
                ui_schema = json.load(f)

        return {
            "schema": schema,
            "ui_schema": ui_schema
        }
