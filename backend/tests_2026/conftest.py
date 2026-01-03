import os
import pytest
from dotenv import load_dotenv

# Load environment variables from .env.test if it exists
env_test_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "backend", ".env.test")
# Fallback to just .env.test if in backend
if not os.path.exists(env_test_path):
    env_test_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), ".env.test")

if os.path.exists(env_test_path):
    print(f"Loading test env from {env_test_path}")
    load_dotenv(env_test_path)
else:
    print(f"Test env file not found at {env_test_path}. Integration tests needing API keys may be skipped.")

def pytest_configure(config):
    config.addinivalue_line(
        "markers", "integration: mark test as an integration test (slow, external calls)"
    )

@pytest.fixture(scope="session")
def test_env_config():
    """Returns the loaded environment configuration for verification."""
    return {
        "api_key": os.getenv("API_KEY"),
        "default_model": os.getenv("DEFAULT_MODEL")
    }
