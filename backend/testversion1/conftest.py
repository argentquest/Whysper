import sys
import os
from pathlib import Path
import pytest
from unittest.mock import MagicMock, patch
from fastapi.testclient import TestClient

# Add backend root to Python path
# Current file: backend/testversion1/conftest.py
# Backend root: backend/
backend_root = Path(__file__).parent.parent
if str(backend_root) not in sys.path:
    sys.path.insert(0, str(backend_root))

# Import app after path setup
from app.main import app

@pytest.fixture
def client():
    return TestClient(app)

@pytest.fixture
def mock_registry():
    """
    Mock the global registry used in API endpoints.
    Patches 'app.api.v1.endpoints.diagram_provider.get_registry'
    """
    with patch("app.api.v1.endpoints.diagram_provider.get_registry") as mock:
        registry = MagicMock()
        mock.return_value = registry
        yield registry

@pytest.fixture
def mock_settings():
    """Mock application settings"""
    with patch("app.core.config.settings") as mock:
        mock.api_key = "test-key"
        mock.default_model = "test-model"
        yield mock
