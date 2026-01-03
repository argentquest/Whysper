import pytest
import time
from backend.tests_2026.integration.utils import skip_if_no_api_key

@skip_if_no_api_key()
class TestDiagramWizardIntegration:

    def test_diagram_wizard_flow(self, api_client):
        """Test the full diagram wizard flow: Start -> Status -> (Clarify) -> Completion"""

        # 1. Start Diagram Generation
        start_payload = {
            "initial_prompt": "Create a flowchart for a user login process. Include Login Page, API, Database.",
            "diagram_type": "mermaid",
            "session_id": "test_integration_wizard_001"
        }

        response = api_client.post("/api/v1/diagram/start", json=start_payload)
        assert response.status_code == 200
        data = response.json()
        session_id = data["session_id"]
        assert session_id == "test_integration_wizard_001"

        # 2. Poll for status
        # In a real integration test, we might wait up to 30-60s.
        # Here we will poll a few times.

        max_retries = 15
        final_status = None

        for _ in range(max_retries):
            time.sleep(2) # Wait 2 seconds between polls
            status_response = api_client.get(f"/api/v1/diagram/{session_id}")
            assert status_response.status_code == 200
            status_data = status_response.json()
            status = status_data.get("status")
            print(f"Current Status: {status}")

            if status in ["diagram_code_generated", "completed", "needs_clarification", "error"]:
                final_status = status
                break

        assert final_status is not None, "Timed out waiting for diagram generation"

        # 3. Handle Clarification if needed
        if final_status == "needs_clarification":
            clarify_payload = {
                "session_id": session_id,
                "response": "Yes, include a 'Forgot Password' flow as well."
            }
            clarify_response = api_client.post("/api/v1/diagram/clarify", json=clarify_payload)
            assert clarify_response.status_code == 200

            # Poll again
            for _ in range(max_retries):
                time.sleep(2)
                status_response = api_client.get(f"/api/v1/diagram/{session_id}")
                status_data = status_response.json()
                status = status_data.get("status")
                print(f"Status after clarify: {status}")
                if status in ["diagram_code_generated", "completed", "error"]:
                    final_status = status
                    break

        # 4. Verify Success
        assert final_status in ["diagram_code_generated", "completed"]

        # 5. Check if code exists in status
        status_response = api_client.get(f"/api/v1/diagram/{session_id}")
        data = status_response.json()
        assert "current_code" in data or "code" in data

        # Optional: Render
        render_payload = {
            "session_id": session_id,
            "code": data.get("current_code", "")
        }
        if render_payload["code"]:
            render_response = api_client.post("/api/v1/diagram/render", json=render_payload)
            assert render_response.status_code == 200
