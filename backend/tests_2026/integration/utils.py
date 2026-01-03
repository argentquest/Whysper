import os
import pytest
from fastapi.testclient import TestClient
from dotenv import load_dotenv

# Try to load from backend directory
env_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), ".env")
load_dotenv(env_path)

def get_api_key():
    """Get API key from environment"""
    return os.getenv("API_KEY")

def skip_if_no_api_key():
    """Skip test if API key is not present"""
    if not get_api_key():
        return pytest.mark.skip(reason="API_KEY not found in environment")
    return pytest.mark.integration

def get_base_url():
    """Get base URL for API"""
    return "http://localhost:8003" # Default, but we use TestClient usually

@pytest.fixture
def api_client():
    """
    Fixture that returns a TestClient for the application.
    This assumes app.main:app is the entry point.
    """
    from app.main import app
    return TestClient(app)

@pytest.fixture
def auth_headers():
    """Return headers with API Key if needed"""
    api_key = get_api_key()
    if api_key:
        return {"Authorization": f"Bearer {api_key}", "X-API-Key": api_key}
    return {}
