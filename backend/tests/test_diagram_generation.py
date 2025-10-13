
import pytest
from fastapi.testclient import TestClient
import sys
import os

# Add the parent directory to the Python path to import the api module
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import the FastAPI app from our API module
from app.main import app

client = TestClient(app)

class TestDiagramGenerationEndpoint:
    """Test the diagram generation endpoint."""

    def test_generate_d2_diagram(self):
        """Test generating a D2 diagram."""
        response = client.post(
            "/api/v1/diagrams/generate",
            json={
                "prompt": "Generate a D2 diagram of a simple web application architecture.",
                "diagram_type": "d2",
            },
            timeout=30  # Increase timeout to allow for diagram generation
        )
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "data:image/svg+xml;base64," in data["data"]
        assert data["format"] == "svg"

    def test_generate_mermaid_diagram(self):
        """Test generating a Mermaid diagram."""
        response = client.post(
            "/api/v1/diagrams/generate",
            json={
                "prompt": "Generate a Mermaid sequence diagram for a user login process.",
                "diagram_type": "mermaid",
            },
            timeout=30  # Increase timeout to allow for diagram generation
        )
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "data:image/svg+xml;base64," in data["data"]
        assert data["format"] == "svg"

if __name__ == "__main__":
    pytest.main([__file__, "-v"])
