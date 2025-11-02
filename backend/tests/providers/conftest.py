"""
Pytest fixtures for provider rendering tests.
"""

import sys
import os
import pytest
from fastapi.testclient import TestClient
from pathlib import Path

# Import app - paths are already set up by root conftest.py
from app.main import app


# Create output directory for test artifacts
ARTIFACTS_DIR = Path(__file__).parent.parent / "providers_test_artifacts"
ARTIFACTS_DIR.mkdir(parents=True, exist_ok=True)


@pytest.fixture
def client():
    """FastAPI test client."""
    return TestClient(app)


@pytest.fixture
def svg_output_dir():
    """Directory for storing generated SVG files during tests."""
    return ARTIFACTS_DIR


def save_svg_artifact(test_name: str, diagram_type: str, content: str, provider_id: str):
    """Save SVG content to file for inspection."""
    if not content or "<svg" not in content:
        return None

    filename = f"{test_name}_{diagram_type}_{provider_id}.svg"
    filepath = ARTIFACTS_DIR / filename

    try:
        filepath.write_text(content)
        return str(filepath)
    except Exception as e:
        print(f"Warning: Could not save SVG artifact: {e}")
        return None


@pytest.fixture
def mermaid_code_simple():
    """Simple Mermaid flowchart."""
    return """flowchart TD
    A[Start] --> B[Process]
    B --> C{Decision}
    C -->|Yes| D[End]
    C -->|No| B"""


@pytest.fixture
def mermaid_code_complex():
    """Complex Mermaid diagram with multiple features."""
    return """flowchart LR
    A[User] --> B[API]
    B --> C[Database]
    B --> D[Cache]
    C --> E[Storage]
    D --> E
    E --> F[Response]
    F --> A"""


@pytest.fixture
def d2_code_simple():
    """Simple D2 diagram."""
    return """A -> B -> C
    B -> D
    D -> E"""


@pytest.fixture
def d2_code_complex():
    """Complex D2 diagram with styling and attributes."""
    return """
    Web Server: {
      shape: rectangle
      label: Web Server
    }

    Database: {
      shape: cylinder
      label: PostgreSQL DB
    }

    Cache: {
      shape: rectangle
      label: Redis Cache
    }

    Web Server -> Database: query
    Web Server -> Cache: get/set
    Database -> Cache: invalidate
    """


@pytest.fixture
def c4_code_simple():
    """Simple C4 diagram."""
    return """
    Person(user, "User", "A user of the system")
    System(sys, "Software System", "The software system")

    Rel(user, sys, "Uses")
    """


@pytest.fixture
def invalid_mermaid():
    """Invalid Mermaid code."""
    return """flowchart TD
    A --> B
    B --> C
    D --> E
    missing connection"""


@pytest.fixture
def invalid_d2():
    """Invalid D2 code."""
    return """
    A -> B -> C
    D -> -> E
    F: shape invalid_shape
    """
