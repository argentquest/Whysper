import os
import json
import uuid
from datetime import datetime
from typing import Dict, Any, List
from fastapi import HTTPException

class FormSubmissionService:
    def __init__(self):
        self.submissions_directory = "UserFormData"
        self.forms_directory = "forms"
        os.makedirs(self.submissions_directory, exist_ok=True)

    def submit_form(self, submission_data: Dict[str, Any]) -> str:
        """Submit a new form and return submission_id"""
        submission_id = f"submission-{uuid.uuid4().hex[:8]}"
        submission_folder = os.path.join(self.submissions_directory, submission_id)
        os.makedirs(submission_folder, exist_ok=True)

        # Get form metadata
        try:
            form_metadata = self._get_form_metadata(submission_data["form_id"])
        except HTTPException:
             # Fallback if form def not found (e.g. deleted), but try to proceed with minimal data
             form_metadata = {
                 "form_name": "Unknown Form",
                 "form_type": "unknown",
                 "version": "1.0"
             }

        # Save form data
        with open(os.path.join(submission_folder, "form_data.json"), "w") as f:
            json.dump(submission_data["form_data"], f, indent=2)

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

    def edit_form_submission(self, original_submission_id: str, submission_data: Dict[str, Any]) -> str:
        """Edit existing form submission, creates new version"""
        # Create new submission
        new_submission_id = f"submission-{uuid.uuid4().hex[:8]}"
        submission_folder = os.path.join(self.submissions_directory, new_submission_id)
        os.makedirs(submission_folder, exist_ok=True)

        # Get form metadata
        try:
            form_metadata = self._get_form_metadata(submission_data["form_id"])
        except HTTPException:
             form_metadata = {
                 "form_name": "Unknown Form",
                 "form_type": "unknown",
                 "version": "1.0"
             }

        # Save form data
        with open(os.path.join(submission_folder, "form_data.json"), "w") as f:
            json.dump(submission_data["form_data"], f, indent=2)

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

        return {
            "metadata": metadata,
            "form_data": form_data
        }

    def _get_form_metadata(self, form_id: str) -> Dict[str, Any]:
        """Get metadata for a published form"""
        # Search for folder that matches form_id
        # The form_id is "contact-form-12ab34cd" (matches folder name)
        metadata_path = os.path.join(self.forms_directory, form_id, "metadata.json")

        if not os.path.exists(metadata_path):
            raise HTTPException(status_code=404, detail=f"Form {form_id} not found")

        with open(metadata_path, "r") as f:
            return json.load(f)
