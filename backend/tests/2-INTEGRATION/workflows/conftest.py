"""
Integration Test Fixtures for Phase 3

Provides reusable fixtures for integration and end-to-end testing:
- Application fixture
- Database fixtures
- Service composition fixtures
- Complete workflow fixtures
- Performance benchmark fixtures
"""

import pytest
import asyncio
from unittest.mock import AsyncMock, MagicMock
from typing import Dict, Any, List


# ============================================================================
# APPLICATION FIXTURES
# ============================================================================


@pytest.fixture
def app():
    """Create FastAPI test application"""
    from app.main import app as main_app

    return main_app


@pytest.fixture
def async_client(app):
    """Create async HTTP client"""
    from httpx import AsyncClient

    return AsyncClient(app=app, base_url="http://test")


@pytest.fixture
def client(app):
    """Create synchronous test client"""
    from fastapi.testclient import TestClient

    return TestClient(app)


# ============================================================================
# WORKFLOW FIXTURES
# ============================================================================


@pytest.fixture
def diagram_generation_workflow() -> Dict[str, Any]:
    """Complete diagram generation workflow"""
    return {
        "user_id": "user_123",
        "prompt": "Create a flowchart for user authentication",
        "diagram_type": "mermaid",
        "expected_code": "graph TD\nA[Start] --> B[Login]\nB --> C[Authenticate]",
        "expected_format": "svg",
    }


@pytest.fixture
def conversation_workflow() -> Dict[str, Any]:
    """Complete conversation workflow"""
    return {
        "user_id": "user_123",
        "conversation_title": "Diagram Design Session",
        "messages": [
            {"content": "Create a flowchart", "role": "user"},
            {"content": "Here's a flowchart", "role": "assistant"},
            {"content": "Make it more detailed", "role": "user"},
            {"content": "Updated flowchart", "role": "assistant"},
        ],
        "expected_message_count": 4,
    }


@pytest.fixture
def file_upload_workflow() -> Dict[str, Any]:
    """File upload and processing workflow"""
    return {
        "file_name": "test_code.py",
        "file_content": "def hello():\n    print('Hello, World!')",
        "file_type": "text/plain",
        "expected_language": "python",
    }


@pytest.fixture
def multi_provider_workflow() -> Dict[str, Any]:
    """Multi-provider rendering workflow"""
    return {
        "diagram_code": "graph LR\n  A[Start] --> B[End]",
        "providers": ["mermaid", "d2"],
        "output_formats": ["svg", "png"],
        "expected_outputs": 4,
    }


# ============================================================================
# SERVICE FIXTURES
# ============================================================================


@pytest.fixture
def mock_conversation_service():
    """Mock conversation service"""
    mock = AsyncMock()
    mock.create_conversation = AsyncMock(return_value={"id": "conv_123"})
    mock.get_conversation = AsyncMock(return_value={"id": "conv_123", "title": "Test"})
    mock.save_message = AsyncMock(return_value={"id": "msg_123"})
    mock.get_history = AsyncMock(return_value=[])
    mock.delete_conversation = AsyncMock(return_value=True)
    return mock


@pytest.fixture
def mock_file_service():
    """Mock file service"""
    mock = AsyncMock()
    mock.upload_file = AsyncMock(return_value={"id": "file_123", "name": "test.py"})
    mock.get_file = AsyncMock(return_value={"id": "file_123", "content": "code"})
    mock.delete_file = AsyncMock(return_value=True)
    mock.validate_file = AsyncMock(return_value=True)
    return mock


@pytest.fixture
def mock_diagram_service():
    """Mock diagram service"""
    mock = AsyncMock()
    mock.render_diagram = AsyncMock(return_value="<svg>...</svg>")
    mock.validate_diagram = AsyncMock(return_value={"is_valid": True})
    mock.correct_diagram = AsyncMock(return_value="corrected code")
    mock.list_providers = AsyncMock(return_value=[{"id": "mermaid", "name": "Mermaid"}])
    return mock


@pytest.fixture
def mock_ai_service():
    """Mock AI service"""
    mock = AsyncMock()
    mock.generate = AsyncMock(return_value="Generated response")
    mock.process_request = AsyncMock(return_value={"success": True, "data": "result"})
    mock.validate_prompt = AsyncMock(return_value=True)
    return mock


# ============================================================================
# AUTHENTICATION FIXTURES
# ============================================================================


@pytest.fixture
def auth_token():
    """Valid authentication token"""
    return "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJ1c2VyXzEyMyIsImlhdCI6MTYwMDAwMDAwMH0.mock_signature"


@pytest.fixture
def auth_headers(auth_token):
    """Authorization headers"""
    return {"Authorization": f"Bearer {auth_token}"}


@pytest.fixture
def invalid_auth_headers():
    """Invalid authorization headers"""
    return {"Authorization": "Bearer invalid_token"}


# ============================================================================
# DATABASE FIXTURES
# ============================================================================


@pytest.fixture
def mock_db():
    """Mock database connection"""
    mock = AsyncMock()
    mock.connect = AsyncMock(return_value=True)
    mock.disconnect = AsyncMock()
    mock.execute = AsyncMock(return_value=MagicMock())
    mock.query = AsyncMock(return_value=[])
    mock.insert = AsyncMock(return_value={"id": "1"})
    mock.update = AsyncMock(return_value={"updated": 1})
    mock.delete = AsyncMock(return_value={"deleted": 1})
    return mock


@pytest.fixture
def sample_db_data() -> Dict[str, List[Dict]]:
    """Sample database records"""
    return {
        "users": [
            {"id": "user_123", "email": "user@example.com", "created_at": "2024-01-01"},
            {"id": "user_456", "email": "user2@example.com", "created_at": "2024-01-02"},
        ],
        "conversations": [
            {"id": "conv_123", "user_id": "user_123", "title": "Test", "created_at": "2024-01-01"},
            {"id": "conv_456", "user_id": "user_456", "title": "Test2", "created_at": "2024-01-02"},
        ],
        "messages": [
            {"id": "msg_123", "conversation_id": "conv_123", "content": "Hello"},
            {"id": "msg_456", "conversation_id": "conv_123", "content": "Hi"},
        ],
    }


# ============================================================================
# REQUEST/RESPONSE FIXTURES
# ============================================================================


@pytest.fixture
def complete_diagram_request() -> Dict[str, Any]:
    """Complete diagram rendering request"""
    return {
        "code": "graph TD\n  A[Start] --> B[End]",
        "diagram_type": "mermaid",
        "output_format": "svg",
        "provider_id": "mermaid_v1",
    }


@pytest.fixture
def complete_conversation_request() -> Dict[str, Any]:
    """Complete conversation request"""
    return {"conversation_id": "conv_123", "content": "Can you help with diagrams?", "include_code": True}


@pytest.fixture
def complete_generation_request() -> Dict[str, Any]:
    """Complete generation request"""
    return {
        "prompt": "Create a flowchart for authentication",
        "diagram_type": "mermaid",
        "user_context": {"user_id": "user_123"},
    }


# ============================================================================
# SCENARIO FIXTURES
# ============================================================================


@pytest.fixture
def success_scenario() -> Dict[str, Any]:
    """Successful workflow scenario"""
    return {
        "name": "successful_workflow",
        "steps": [
            {"action": "create_conversation", "expected": "success"},
            {"action": "send_message", "expected": "success"},
            {"action": "render_diagram", "expected": "success"},
            {"action": "save_result", "expected": "success"},
        ],
        "expected_outcome": "all_successful",
    }


@pytest.fixture
def error_recovery_scenario() -> Dict[str, Any]:
    """Error recovery scenario"""
    return {
        "name": "error_recovery",
        "steps": [
            {"action": "invalid_request", "expected": "error"},
            {"action": "retry_request", "expected": "success"},
            {"action": "verify_state", "expected": "consistent"},
        ],
        "expected_outcome": "recovered",
    }


@pytest.fixture
def concurrent_scenario() -> Dict[str, Any]:
    """Concurrent operations scenario"""
    return {
        "name": "concurrent_operations",
        "concurrent_users": 5,
        "operations_per_user": 10,
        "expected_total_operations": 50,
        "expected_success_rate": 0.95,
    }


# ============================================================================
# PERFORMANCE FIXTURES
# ============================================================================


@pytest.fixture
def performance_baseline() -> Dict[str, float]:
    """Performance baseline thresholds"""
    return {
        "api_endpoint_latency": 0.5,  # seconds
        "diagram_rendering": 2.0,
        "file_upload": 1.0,
        "conversation_creation": 0.2,
        "database_query": 0.1,
        "concurrent_request": 1.0,
    }


@pytest.fixture
def load_test_config() -> Dict[str, Any]:
    """Load test configuration"""
    return {
        "concurrent_users": 10,
        "requests_per_user": 20,
        "total_requests": 200,
        "ramp_up_time": 5,
        "hold_time": 10,
        "ramp_down_time": 5,
        "expected_success_rate": 0.99,
    }


# ============================================================================
# STATE FIXTURES
# ============================================================================


@pytest.fixture
def application_state() -> Dict[str, Any]:
    """Application state tracker"""
    return {"conversations": {}, "messages": {}, "files": {}, "users": {}, "diagrams": {}}


@pytest.fixture
def user_session() -> Dict[str, Any]:
    """User session fixture"""
    return {
        "user_id": "user_123",
        "session_id": "sess_abc123",
        "created_at": "2024-01-01T00:00:00Z",
        "last_activity": "2024-01-01T00:00:00Z",
        "authenticated": True,
        "permissions": ["read", "write", "delete"],
    }


# ============================================================================
# MONITORING FIXTURES
# ============================================================================


@pytest.fixture
def metrics_tracker():
    """Track test metrics"""
    return {"requests": [], "responses": [], "errors": [], "latencies": [], "memory_usage": [], "cpu_usage": []}


@pytest.fixture
def event_log():
    """Event log for workflow tracking"""
    return []


# ============================================================================
# UTILITY FIXTURES
# ============================================================================


@pytest.fixture
def async_event_loop():
    """Async event loop for tests"""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture
def mock_external_api():
    """Mock external API calls"""
    mock = AsyncMock()
    mock.call = AsyncMock(return_value={"status": "success", "data": {}})
    mock.validate_response = AsyncMock(return_value=True)
    return mock
