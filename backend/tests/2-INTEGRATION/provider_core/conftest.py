import pytest
from unittest.mock import patch, MagicMock
from fastapi.testclient import TestClient
from app.main import app

@pytest.fixture(scope="session")
def client():
    with TestClient(app) as c:
        yield c

@pytest.fixture(scope="session", autouse=True)
def mock_provider_availability():
    """Mock provider availability checks to simulate installed CLIs."""

    # We use a context manager stack to apply multiple patches
    with patch("diagrams.d2v1.d2_renderer.D2V1Provider.is_available", return_value=True), \
         patch("diagrams.mermaidv1.mermaid_renderer.MermaidV1Provider.is_available", return_value=True), \
         patch("diagrams.d2v1.d2_renderer.validate_d2_with_cli", return_value=(True, "Mocked D2 Valid")), \
         patch("diagrams.d2v1.d2_renderer.validate_d2_and_render", return_value=(True, "Mocked D2 Rendered", "<svg>Mocked D2</svg>")), \
         patch("diagrams.mermaidv1.mermaid_renderer.validate_mermaid_with_cli", return_value=(True, "Mocked Mermaid Valid")), \
         patch("diagrams.mermaidv1.mermaid_renderer.validate_mermaid_and_render", return_value=(True, "Mocked Mermaid Rendered", "<svg>Mocked Mermaid</svg>")):
        yield
