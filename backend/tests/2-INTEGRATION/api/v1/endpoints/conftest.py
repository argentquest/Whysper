"""
API Test Fixtures for Phase 1

Provides reusable fixtures for testing API endpoints:
- test_client: FastAPI TestClient
- auth_headers: JWT authorization headers
- sample diagram code and files
- Mock database and services
"""

import pytest
from fastapi.testclient import TestClient
from unittest.mock import MagicMock
from typing import Dict, Any


@pytest.fixture
def test_client():
    """Create FastAPI test client for making test requests"""
    from app.main import app

    return TestClient(app)


@pytest.fixture
def sample_mermaid_code() -> str:
    """Valid Mermaid diagram code"""
    return """graph TD
    A[Start] --> B[Process]
    B --> C[Decision]
    C -->|Yes| D[End]
    C -->|No| B"""


@pytest.fixture
def sample_d2_code() -> str:
    """Valid D2 diagram code"""
    return """User -> Browser -> Server
Server -> Database
Database -> Server
Server -> Browser -> User"""


@pytest.fixture
def simple_mermaid_code() -> str:
    """Simple valid Mermaid code"""
    return "graph LR\n  A[Start] --> B[End]"


@pytest.fixture
def simple_d2_code() -> str:
    """Simple valid D2 code"""
    return "A -> B"


@pytest.fixture
def invalid_diagram_code() -> str:
    """Invalid diagram code that will fail validation"""
    return "this is not valid @#$%^&*() diagram code"


@pytest.fixture
def empty_code() -> str:
    """Empty code string"""
    return ""


@pytest.fixture
def large_code() -> str:
    """Code larger than typical size"""
    lines = ["graph TD"]
    for i in range(100):
        lines.append(f"  Node{i}[Node {i}]")
        if i > 0:
            lines.append(f"  Node{i - 1} --> Node{i}")
    return "\n".join(lines)


@pytest.fixture
def code_with_special_chars() -> str:
    """Mermaid code with special characters"""
    return """graph TD
    A["Start & Process"] --> B["Decision?"]
    B -->|"Yes (100%)"| C["Success!"]
    B -->|"No (0%)"| D["Failed..."]"""


@pytest.fixture
def mermaid_code_with_error() -> str:
    """Mermaid code with a fixable error"""
    return """graph TD
    A[Start]
    B[Process
    C[End]
    A --> B --> C"""


@pytest.fixture
def auth_headers() -> Dict[str, str]:
    """Valid authorization headers with JWT token"""
    # Mock token for testing - in real scenario would come from auth
    mock_token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJ0ZXN0X3VzZXIiLCJpYXQiOjE2MDAwMDAwMDB9.mock_signature"
    return {"Authorization": f"Bearer {mock_token}"}


@pytest.fixture
def invalid_auth_headers() -> Dict[str, str]:
    """Invalid authorization headers"""
    return {"Authorization": "Bearer invalid_token_12345"}


@pytest.fixture
def no_auth_headers() -> Dict[str, str]:
    """Empty headers (no auth)"""
    return {}


@pytest.fixture
def sample_user() -> Dict[str, Any]:
    """Sample user object for testing"""
    return {"id": "user_123", "username": "testuser", "email": "test@example.com", "is_active": True, "roles": ["user"]}


@pytest.fixture
def sample_admin_user() -> Dict[str, Any]:
    """Sample admin user object"""
    return {
        "id": "admin_123",
        "username": "adminuser",
        "email": "admin@example.com",
        "is_active": True,
        "roles": ["admin", "user"],
    }


@pytest.fixture
def sample_conversation() -> Dict[str, Any]:
    """Sample conversation object"""
    return {
        "id": "conv_123",
        "title": "Test Conversation",
        "user_id": "user_123",
        "messages": [],
        "created_at": "2024-01-01T00:00:00Z",
        "updated_at": "2024-01-01T00:00:00Z",
        "is_active": True,
    }


@pytest.fixture
def sample_message() -> Dict[str, Any]:
    """Sample chat message"""
    return {
        "id": "msg_123",
        "conversation_id": "conv_123",
        "user_id": "user_123",
        "content": "Hello, can you help me?",
        "created_at": "2024-01-01T00:00:00Z",
        "is_system": False,
    }


@pytest.fixture
def sample_file_content() -> bytes:
    """Sample file content for upload testing"""
    return b"This is a sample file content for testing file uploads"


@pytest.fixture
def sample_python_code() -> str:
    """Sample Python code"""
    return """def hello_world():
    print("Hello, World!")
    return True

if __name__ == "__main__":
    hello_world()"""


@pytest.fixture
def sample_javascript_code() -> str:
    """Sample JavaScript code"""
    return """function helloWorld() {
    console.log("Hello, World!");
    return true;
}

helloWorld();"""


@pytest.fixture
def mock_db():
    """Mock database connection"""
    mock = MagicMock()
    mock.query = MagicMock(return_value=MagicMock())
    mock.add = MagicMock()
    mock.commit = MagicMock()
    mock.rollback = MagicMock()
    return mock


@pytest.fixture
def mock_file_service():
    """Mock file service"""
    mock = MagicMock()
    mock.upload_file = MagicMock(return_value={"id": "file_123", "name": "test.txt"})
    mock.download_file = MagicMock(return_value=b"file content")
    mock.validate_file = MagicMock(return_value=True)
    mock.delete_file = MagicMock(return_value=True)
    return mock


@pytest.fixture
def mock_conversation_service():
    """Mock conversation service"""
    mock = MagicMock()
    mock.create_conversation = MagicMock(return_value={"id": "conv_123", "title": "Test"})
    mock.get_conversation = MagicMock(return_value={"id": "conv_123", "title": "Test"})
    mock.get_history = MagicMock(return_value=[])
    mock.save_message = MagicMock(return_value={"id": "msg_123"})
    return mock


@pytest.fixture
def mock_ai_service():
    """Mock AI service for diagram generation"""
    mock = MagicMock()
    mock.generate_diagram_code = MagicMock(return_value="graph TD\n  A[Generated] --> B[Diagram]")
    mock.correct_diagram_code = MagicMock(return_value="graph TD\n  A[Corrected] --> B[Code]")
    return mock


@pytest.fixture
def mock_provider_registry():
    """Mock provider registry"""
    mock = MagicMock()
    mock.list_providers = MagicMock(
        return_value=[
            {
                "provider_id": "mermaidv1",
                "provider_name": "Mermaid v1",
                "diagram_type": "mermaid",
                "supported_output_formats": ["svg", "png"],
            },
            {
                "provider_id": "d2v1",
                "provider_name": "D2 v1",
                "diagram_type": "d2",
                "supported_output_formats": ["svg", "png"],
            },
        ]
    )
    mock.get_provider = MagicMock(return_value=MagicMock())
    return mock


@pytest.fixture
def render_request_valid() -> Dict[str, Any]:
    """Valid diagram render request"""
    return {"code": "graph TD\n  A[Start] --> B[End]", "diagram_type": "mermaid", "output_format": "svg"}


@pytest.fixture
def render_request_invalid_missing_code() -> Dict[str, Any]:
    """Render request with missing code"""
    return {"diagram_type": "mermaid", "output_format": "svg"}


@pytest.fixture
def render_request_invalid_missing_type() -> Dict[str, Any]:
    """Render request with missing diagram type"""
    return {"code": "graph TD\n  A --> B", "output_format": "svg"}


@pytest.fixture
def validation_request_valid() -> Dict[str, Any]:
    """Valid diagram validation request"""
    return {"code": "graph TD\n  A[Start] --> B[End]", "diagram_type": "mermaid", "auto_fix": True}


@pytest.fixture
def chat_request_valid() -> Dict[str, Any]:
    """Valid chat message request"""
    return {"conversation_id": "conv_123", "content": "Hello, can you help me create a diagram?", "include_code": True}


@pytest.fixture
def file_upload_request() -> Dict[str, Any]:
    """File upload request data"""
    return {"filename": "test_file.txt", "file_type": "text/plain", "size": 100}


@pytest.fixture
def settings_update_request() -> Dict[str, Any]:
    """Settings update request"""
    return {"theme": "dark", "language": "en", "notifications_enabled": True, "auto_save": True}


# Markers and parametrization data for tests
@pytest.fixture
def provider_types():
    """List of supported provider/diagram types"""
    return ["mermaid", "d2", "structurizr", "c4", "plantuml"]


@pytest.fixture
def output_formats():
    """List of supported output formats"""
    return ["svg", "png", "pdf"]


@pytest.fixture
def http_status_codes():
    """Common HTTP status codes"""
    return {
        "ok": 200,
        "created": 201,
        "bad_request": 400,
        "unauthorized": 401,
        "forbidden": 403,
        "not_found": 404,
        "conflict": 409,
        "server_error": 500,
        "service_unavailable": 503,
    }
