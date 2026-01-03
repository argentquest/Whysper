import os
import json
import uuid
from datetime import datetime
from typing import Dict, Any, List
from common.logging_decorator import log_method_call


class FormService:
    def __init__(self):
        self.forms_directory = "forms"
        self.submissions_directory = "UserFormData"
        os.makedirs(self.forms_directory, exist_ok=True)
        os.makedirs(self.submissions_directory, exist_ok=True)

    @log_method_call
    def publish_form(self, form_data: Dict[str, Any]) -> str:
        """
        Publish a form and return the form_id
        Creates folder structure: forms/{form_id}/
        """
        # Ensure form_type is safe for filenames
        form_type = "".join(c for c in form_data['form_type'] if c.isalnum() or c in ('-', '_'))
        form_id = f"{form_type}-{uuid.uuid4().hex[:8]}"
        form_folder = os.path.join(self.forms_directory, form_id)
        os.makedirs(form_folder, exist_ok=True)

        # Save all form files
        self._save_form_files(form_folder, form_id, form_data)
        return form_id

    def _save_form_files(self, folder: str, form_id: str, data: Dict[str, Any]):
        """Save schema, ui_schema, form_data, and metadata files"""
        # Save schema.json
        with open(os.path.join(folder, "schema.json"), "w") as f:
            json.dump(data["schema"], f, indent=2)

        # Save ui_schema.json
        with open(os.path.join(folder, "ui_schema.json"), "w") as f:
            json.dump(data["ui_schema"], f, indent=2)

        # Save form_data.json (sample)
        with open(os.path.join(folder, "form_data.json"), "w") as f:
            json.dump(data["form_data"], f, indent=2)

        # Save metadata.json
        metadata = {
            "form_id": form_id,
            "form_name": data["form_name"],
            "form_description": data["form_description"],
            "form_type": data["form_type"],
            "version": data["version"],
            "created_timestamp": datetime.now().isoformat(),
            "created_by": "admin",
            "status": "published"
        }
        with open(os.path.join(folder, "metadata.json"), "w") as f:
            json.dump(metadata, f, indent=2)

    @log_method_call
    def get_published_forms(self) -> List[Dict[str, Any]]:
        """List all published forms with metadata"""
        forms = []
        if not os.path.exists(self.forms_directory):
            return []

        for form_folder_name in os.listdir(self.forms_directory):
            metadata_path = os.path.join(
                self.forms_directory,
                form_folder_name,
                "metadata.json"
            )

            if os.path.exists(metadata_path):
                try:
                    with open(metadata_path, "r") as f:
                        metadata = json.load(f)

                        # Load schema and ui_schema for preview/usage
                        schema_path = os.path.join(self.forms_directory, form_folder_name, "schema.json")
                        ui_schema_path = os.path.join(self.forms_directory, form_folder_name, "ui_schema.json")

                        if os.path.exists(schema_path):
                            with open(schema_path, "r") as sf:
                                metadata["schema"] = json.load(sf)

                        if os.path.exists(ui_schema_path):
                            with open(ui_schema_path, "r") as uf:
                                metadata["ui_schema"] = json.load(uf)

                        forms.append(metadata)
                except Exception as e:
                    print(f"Error loading form {form_folder_name}: {e}")
                    continue

        # Sort by creation timestamp (newest first)
        forms.sort(key=lambda x: x.get("created_timestamp", ""), reverse=True)
        return forms

    @log_method_call
    def submit_form(self, submission_data: Dict[str, Any]) -> str:
        """
        Submit form data and return submission_id
        Creates folder structure: UserFormData/{submission_id}/
        Stores schema and ui_schema with submission for edit resilience
        """
        submission_id = f"sub-{uuid.uuid4().hex}"
        submission_folder = os.path.join(self.submissions_directory, submission_id)
        os.makedirs(submission_folder, exist_ok=True)

        form_id = submission_data["form_id"]

        # Load schema and ui_schema from published form
        form_folder = os.path.join(self.forms_directory, form_id)
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

        # Save form_data.json
        with open(os.path.join(submission_folder, "form_data.json"), "w") as f:
            json.dump(submission_data["form_data"], f, indent=2)

        # Save schema and ui_schema with submission for edit resilience
        with open(os.path.join(submission_folder, "schema.json"), "w") as f:
            json.dump(schema, f, indent=2)

        with open(os.path.join(submission_folder, "ui_schema.json"), "w") as f:
            json.dump(ui_schema, f, indent=2)

        # Save metadata.json
        metadata = {
            "submission_id": submission_id,
            "form_id": form_id,
            "session_id": submission_data.get("session_id", ""),
            "created_timestamp": datetime.now().isoformat(),
            "is_edited": False,
            "original_submission_id": submission_id,
        }
        with open(os.path.join(submission_folder, "metadata.json"), "w") as f:
            json.dump(metadata, f, indent=2)

        return submission_id

    @log_method_call
    def get_submissions(self) -> List[Dict[str, Any]]:
        """List all form submissions with metadata"""
        submissions = []
        if not os.path.exists(self.submissions_directory):
            return []

        for submission_folder_name in os.listdir(self.submissions_directory):
            metadata_path = os.path.join(
                self.submissions_directory,
                submission_folder_name,
                "metadata.json"
            )

            if os.path.exists(metadata_path):
                try:
                    with open(metadata_path, "r") as f:
                        metadata = json.load(f)
                        submissions.append(metadata)
                except Exception as e:
                    print(f"Error loading submission {submission_folder_name}: {e}")
                    continue

        # Sort by creation timestamp (newest first)
        submissions.sort(key=lambda x: x.get("created_timestamp", ""), reverse=True)
        return submissions

    @log_method_call
    def get_submission(self, submission_id: str) -> Dict[str, Any]:
        """Get a single submission with all data"""
        submission_folder = os.path.join(self.submissions_directory, submission_id)

        if not os.path.exists(submission_folder):
            raise FileNotFoundError(f"Submission {submission_id} not found")

        result = {}

        # Load metadata
        metadata_path = os.path.join(submission_folder, "metadata.json")
        if os.path.exists(metadata_path):
            with open(metadata_path, "r") as f:
                result["metadata"] = json.load(f)

        # Load form_data
        form_data_path = os.path.join(submission_folder, "form_data.json")
        if os.path.exists(form_data_path):
            with open(form_data_path, "r") as f:
                result["form_data"] = json.load(f)

        # Load schema (stored with submission for edit resilience)
        schema_path = os.path.join(submission_folder, "schema.json")
        if os.path.exists(schema_path):
            with open(schema_path, "r") as f:
                result["schema"] = json.load(f)

        # Load ui_schema
        ui_schema_path = os.path.join(submission_folder, "ui_schema.json")
        if os.path.exists(ui_schema_path):
            with open(ui_schema_path, "r") as f:
                result["ui_schema"] = json.load(f)

        return result

    @log_method_call
    def edit_submission(self, old_submission_id: str, edit_data: Dict[str, Any]) -> str:
        """
        Edit a submission by creating a new version
        Returns the new submission_id
        Preserves version history chain
        """
        # Get original submission to find the root
        old_submission = self.get_submission(old_submission_id)
        old_metadata = old_submission["metadata"]

        # Find the original submission ID (root of version chain)
        original_submission_id = old_metadata.get("original_submission_id", old_submission_id)

        # Create new submission
        new_submission_id = f"sub-{uuid.uuid4().hex}"
        submission_folder = os.path.join(self.submissions_directory, new_submission_id)
        os.makedirs(submission_folder, exist_ok=True)

        # Save new form_data
        with open(os.path.join(submission_folder, "form_data.json"), "w") as f:
            json.dump(edit_data["form_data"], f, indent=2)

        # Copy schema and ui_schema from old submission (for edit resilience)
        if "schema" in old_submission:
            with open(os.path.join(submission_folder, "schema.json"), "w") as f:
                json.dump(old_submission["schema"], f, indent=2)

        if "ui_schema" in old_submission:
            with open(os.path.join(submission_folder, "ui_schema.json"), "w") as f:
                json.dump(old_submission["ui_schema"], f, indent=2)

        # Save metadata with edit tracking
        metadata = {
            "submission_id": new_submission_id,
            "form_id": edit_data["form_id"],
            "session_id": edit_data.get("session_id", ""),
            "created_timestamp": datetime.now().isoformat(),
            "is_edited": True,
            "original_submission_id": original_submission_id,
            "previous_submission_id": old_submission_id,
        }
        with open(os.path.join(submission_folder, "metadata.json"), "w") as f:
            json.dump(metadata, f, indent=2)

        return new_submission_id

    @log_method_call
    def get_submission_history(self, submission_id: str) -> List[Dict[str, Any]]:
        """
        Get version history for a submission
        Returns list of all versions in chronological order (oldest first)
        """
        # Find the original submission
        current_submission = self.get_submission(submission_id)
        original_id = current_submission["metadata"].get("original_submission_id", submission_id)

        # Find all submissions with this original_id
        all_submissions = self.get_submissions()
        history = []

        for sub_meta in all_submissions:
            if sub_meta.get("original_submission_id") == original_id:
                history.append(sub_meta)

        # Sort by timestamp (oldest first)
        history.sort(key=lambda x: x.get("created_timestamp", ""))

        return history
