import os
import json
import uuid
from datetime import datetime
from typing import Dict, Any, List

class FormService:
    def __init__(self):
        self.forms_directory = "forms"
        os.makedirs(self.forms_directory, exist_ok=True)

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
