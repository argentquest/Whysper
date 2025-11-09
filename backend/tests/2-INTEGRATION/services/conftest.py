"""
Service Layer Test Fixtures

Provides reusable fixtures for testing backend services:
- Mock database
- Sample data objects
- Mock external services
"""

import pytest
from unittest.mock import Mock, MagicMock, AsyncMock
from datetime import datetime
from typing import Dict, Any, List


@pytest.fixture
def mock_db():
    """Mock database session"""
    mock = MagicMock()
    mock.query = MagicMock(return_value=MagicMock())
    mock.add = MagicMock()
    mock.commit = MagicMock()
    mock.rollback = MagicMock()
    mock.close = MagicMock()
    return mock


@pytest.fixture
def mock_db_session():
    """Mock SQLAlchemy session"""
    mock = MagicMock()
    mock.add = MagicMock()
    mock.commit = MagicMock()
    mock.rollback = MagicMock()
    mock.query = MagicMock(return_value=MagicMock())
    mock.close = MagicMock()
    return mock


@pytest.fixture
def sample_user_data() -> Dict[str, Any]:
    """Sample user object"""
    return {
        "id": "user_123",
        "username": "testuser",
        "email": "test@example.com",
        "is_active": True,
        "created_at": datetime.now(),
        "updated_at": datetime.now()
    }


@pytest.fixture
def sample_conversation_data() -> Dict[str, Any]:
    """Sample conversation object"""
    return {
        "id": "conv_123",
        "user_id": "user_123",
        "title": "Test Conversation",
        "description": "A test conversation",
        "created_at": datetime.now(),
        "updated_at": datetime.now(),
        "is_active": True,
        "message_count": 0
    }


@pytest.fixture
def sample_message_data() -> Dict[str, Any]:
    """Sample chat message object"""
    return {
        "id": "msg_123",
        "conversation_id": "conv_123",
        "user_id": "user_123",
        "content": "Hello, this is a test message",
        "created_at": datetime.now(),
        "is_system": False,
        "role": "user"
    }


@pytest.fixture
def sample_file_data() -> Dict[str, Any]:
    """Sample file metadata"""
    return {
        "id": "file_123",
        "user_id": "user_123",
        "filename": "test_file.txt",
        "file_type": "text/plain",
        "size": 1024,
        "path": "/uploads/test_file.txt",
        "created_at": datetime.now(),
        "updated_at": datetime.now(),
        "is_deleted": False
    }


@pytest.fixture
def sample_diagram_data() -> Dict[str, Any]:
    """Sample diagram object"""
    return {
        "id": "diagram_123",
        "user_id": "user_123",
        "conversation_id": "conv_123",
        "diagram_type": "mermaid",
        "code": "graph TD\n  A[Start] --> B[End]",
        "provider_id": "mermaidv1",
        "output_format": "svg",
        "created_at": datetime.now(),
        "updated_at": datetime.now(),
        "is_saved": True
    }


@pytest.fixture
def sample_history_entry() -> Dict[str, Any]:
    """Sample history entry"""
    return {
        "id": "hist_123",
        "user_id": "user_123",
        "action": "render_diagram",
        "details": {"diagram_type": "mermaid", "provider": "mermaidv1"},
        "timestamp": datetime.now(),
        "status": "success"
    }


@pytest.fixture
def sample_settings() -> Dict[str, Any]:
    """Sample user settings"""
    return {
        "id": "settings_123",
        "user_id": "user_123",
        "theme": "dark",
        "language": "en",
        "notifications_enabled": True,
        "auto_save": True,
        "auto_render": True,
        "default_diagram_type": "mermaid",
        "created_at": datetime.now(),
        "updated_at": datetime.now()
    }


@pytest.fixture
def mock_file_service():
    """Mock file service"""
    mock = AsyncMock()
    mock.upload_file = AsyncMock(return_value={"id": "file_123", "path": "/uploads/test.txt"})
    mock.download_file = AsyncMock(return_value=b"file content")
    mock.delete_file = AsyncMock(return_value=True)
    mock.validate_file = AsyncMock(return_value=True)
    mock.get_file_info = AsyncMock(return_value={"id": "file_123", "size": 1024})
    mock.list_files = AsyncMock(return_value=[])
    return mock


@pytest.fixture
def mock_conversation_service():
    """Mock conversation service"""
    mock = AsyncMock()
    mock.create_conversation = AsyncMock(return_value={"id": "conv_123", "title": "Test"})
    mock.get_conversation = AsyncMock(return_value={"id": "conv_123", "title": "Test"})
    mock.get_history = AsyncMock(return_value=[])
    mock.save_message = AsyncMock(return_value={"id": "msg_123"})
    mock.delete_conversation = AsyncMock(return_value=True)
    mock.get_conversations = AsyncMock(return_value=[])
    return mock


@pytest.fixture
def mock_documentation_service():
    """Mock documentation service"""
    mock = AsyncMock()
    mock.generate_documentation = AsyncMock(return_value="# Generated Documentation\n\nContent here")
    mock.export_documentation = AsyncMock(return_value=b"PDF content")
    mock.save_documentation = AsyncMock(return_value={"id": "doc_123"})
    mock.update_documentation = AsyncMock(return_value={"id": "doc_123"})
    return mock


@pytest.fixture
def mock_export_service():
    """Mock export service"""
    mock = AsyncMock()
    mock.export_to_pdf = AsyncMock(return_value=b"PDF content")
    mock.export_to_json = AsyncMock(return_value='{"data": "value"}')
    mock.export_to_csv = AsyncMock(return_value=b"CSV content")
    mock.batch_export = AsyncMock(return_value={"status": "completed"})
    return mock


@pytest.fixture
def mock_history_service():
    """Mock history service"""
    mock = AsyncMock()
    mock.save_to_history = AsyncMock(return_value={"id": "hist_123"})
    mock.get_history = AsyncMock(return_value=[])
    mock.clear_history = AsyncMock(return_value=True)
    mock.export_history = AsyncMock(return_value=b"CSV content")
    mock.search_history = AsyncMock(return_value=[])
    return mock


@pytest.fixture
def mock_settings_service():
    """Mock settings service"""
    mock = AsyncMock()
    mock.get_settings = AsyncMock(return_value={"theme": "dark", "language": "en"})
    mock.update_settings = AsyncMock(return_value={"theme": "dark"})
    mock.reset_to_defaults = AsyncMock(return_value={"theme": "light"})
    mock.validate_settings = AsyncMock(return_value=True)
    return mock


@pytest.fixture
def mock_theme_service():
    """Mock theme service"""
    mock = AsyncMock()
    mock.get_current_theme = AsyncMock(return_value={"name": "dark", "colors": {}})
    mock.set_theme = AsyncMock(return_value=True)
    mock.get_available_themes = AsyncMock(return_value=["dark", "light"])
    mock.validate_theme = AsyncMock(return_value=True)
    return mock


@pytest.fixture
def conversation_list() -> List[Dict[str, Any]]:
    """List of sample conversations"""
    return [
        {
            "id": f"conv_{i}",
            "user_id": "user_123",
            "title": f"Conversation {i}",
            "created_at": datetime.now(),
            "message_count": i * 5
        }
        for i in range(1, 4)
    ]


@pytest.fixture
def message_list() -> List[Dict[str, Any]]:
    """List of sample messages"""
    return [
        {
            "id": f"msg_{i}",
            "conversation_id": "conv_123",
            "user_id": "user_123",
            "content": f"Message {i}",
            "created_at": datetime.now(),
            "is_system": i % 2 == 0
        }
        for i in range(1, 6)
    ]


@pytest.fixture
def file_list() -> List[Dict[str, Any]]:
    """List of sample files"""
    return [
        {
            "id": f"file_{i}",
            "user_id": "user_123",
            "filename": f"file_{i}.txt",
            "file_type": "text/plain",
            "size": 1024 * i,
            "created_at": datetime.now()
        }
        for i in range(1, 4)
    ]
