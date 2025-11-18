```python
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


# Create output directory for test artifacts - ensures a consistent location for saving test results
ARTIFACTS_DIR = Path(__file__).parent.parent / "providers_test_artifacts"
ARTIFACTS_DIR.mkdir(parents=True, exist_ok=True)


@pytest.fixture
def client():
    # Create and return a test client for making API requests without running actual server
    return TestClient(app)


@pytest.fixture
def svg_output_dir():
    # Provide a consistent directory for storing generated SVG files during testing
    return ARTIFACTS_DIR


def save_svg_artifact(test_name: str, diagram_type: str, content: str, provider_id: str):
    # Save SVG content to a file for later inspection and debugging
    # Only save if content exists and contains SVG markup
    if not content or "<svg" not in content:
        return None

    # Generate a unique filename based on test parameters
    filename = f"{test_name}_{diagram_type}_{provider_id}.svg"
    filepath = ARTIFACTS_DIR / filename

    try:
        # Attempt to write SVG content to file
        filepath.write_text(content)
        return str(filepath)
    except Exception as e:
        # Log warning if file saving fails, but don't interrupt test execution
        print(f"Warning: Could not save SVG artifact: {e}")
        return None


@pytest.fixture
def mermaid_code_simple():
    # Provide a simple Mermaid flowchart for testing basic rendering
    return """flowchart TD
    A[Start] --> B[Process]
    B --> C{Decision}
    C -->|Yes| D[End]
    C -->|No| B"""


@pytest.fixture
def mermaid_code_complex():
    # Provide a more complex Mermaid diagram with multiple components and interactions
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
    # Provide a simple D2 diagram for basic rendering tests
    return """A -> B -> C
    B -> D
    D -> E"""


@pytest.fixture
def d2_code_complex():
    # Provide a complex D2 diagram with shapes, labels, and multiple connections
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
    # Provide a simple C4 diagram for testing system relationship rendering
    return """
    Person(user, "User", "A user of the system")
    System(sys, "Software System", "The software system")

    Rel(user, sys, "Uses")
    """


@pytest.fixture
def invalid_mermaid():
    # Provide an intentionally invalid Mermaid code to test error handling
    return """flowchart TD
    A --> B
    B --> C
    D --> E
    missing connection"""


@pytest.fixture
def invalid_d2():
    # Provide an intentionally invalid D2 code to test error handling
    return """
    A -> B -> C
    D -> -> E
    F: shape invalid_shape
    """
```

The comments focus on explaining the purpose of each fixture, the logic behind key functions, and provide context for the test setup. They describe WHAT the code does and WHY it's structured this way.