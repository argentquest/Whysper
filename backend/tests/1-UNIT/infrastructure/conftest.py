"""
Infrastructure Test Fixtures for Phase 2

Provides reusable fixtures for testing core infrastructure components:
- Logger configuration and context
- Environment management
- Configuration settings
- Security utilities
- AI provider base classes
- File scanning and filtering
"""

import pytest
import tempfile
import os
from pathlib import Path
from unittest.mock import Mock, MagicMock, patch
from io import StringIO
import logging
import json
from typing import Dict, Any


# ============================================================================
# LOGGER FIXTURES
# ============================================================================

@pytest.fixture
def log_context():
    """Create a basic log context"""
    from common.logger import LogContext
    return LogContext(
        user_id="user_123",
        session_id="sess_abc123",
        component="test_component",
        operation="test_operation",
        request_id="req_xyz789"
    )


@pytest.fixture
def temp_log_dir():
    """Create temporary directory for log files"""
    with tempfile.TemporaryDirectory() as tmpdir:
        yield Path(tmpdir)


@pytest.fixture
def log_file_path(temp_log_dir):
    """Create path to log file"""
    return temp_log_dir / "test.log"


@pytest.fixture
def logger_instance(log_file_path):
    """Create logger instance for testing"""
    from common.logger import CodeChatLogger
    return CodeChatLogger(
        name="test_logger",
        log_file=str(log_file_path)
    )


@pytest.fixture
def string_io_handler():
    """Create string IO handler for capturing log output"""
    return StringIO()


@pytest.fixture
def mock_logger():
    """Create mock logger"""
    mock = MagicMock(spec=logging.Logger)
    mock.info = MagicMock()
    mock.debug = MagicMock()
    mock.warning = MagicMock()
    mock.error = MagicMock()
    mock.critical = MagicMock()
    return mock


# ============================================================================
# ENVIRONMENT & CONFIG FIXTURES
# ============================================================================

@pytest.fixture
def temp_env_file():
    """Create temporary .env file"""
    with tempfile.NamedTemporaryFile(mode='w', suffix='.env', delete=False) as f:
        f.write("TEST_VAR=test_value\n")
        f.write("TEST_NUMBER=123\n")
        f.write("TEST_BOOL=true\n")
        env_path = f.name
    yield env_path
    os.unlink(env_path)


@pytest.fixture
def valid_env_vars() -> Dict[str, str]:
    """Valid environment variables for testing"""
    return {
        "API_HOST": "0.0.0.0",
        "API_PORT": "8003",
        "LOG_LEVEL": "INFO",
        "DATABASE_URL": "sqlite:///app.db",
        "OPENAI_API_KEY": "sk-test-key-12345",
        "ENABLE_LOGGING": "true"
    }


@pytest.fixture
def invalid_env_vars() -> Dict[str, str]:
    """Invalid environment variables for testing"""
    return {
        "API_PORT": "not_a_number",
        "INVALID_URL": "not a valid url",
        "API_KEY": "invalid_key_format"
    }


@pytest.fixture
def mock_settings():
    """Create mock Settings object"""
    mock = MagicMock()
    mock.api_host = "0.0.0.0"
    mock.api_port = 8003
    mock.log_level = "INFO"
    mock.database_url = "sqlite:///app.db"
    mock.openai_api_key = "sk-test-key"
    mock.enable_logging = True
    return mock


# ============================================================================
# SECURITY FIXTURES
# ============================================================================

@pytest.fixture
def api_keys_to_test() -> Dict[str, str]:
    """Sample API keys for security testing"""
    return {
        "openai": "sk-proj-abc123def456ghi789jkl012",
        "anthropic": "sk-ant-abc123def456ghi789jkl012",
        "generic": "api_key_1234567890abcdef",
        "short": "key123",
        "empty": ""
    }


@pytest.fixture
def sensitive_data() -> Dict[str, Any]:
    """Sensitive data for masking tests"""
    return {
        "api_key": "sk-proj-secret123456789",
        "password": "super_secret_password",
        "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9",
        "nested": {
            "api_key": "sk-proj-another-secret",
            "email": "test@example.com"
        }
    }


@pytest.fixture
def unsafe_paths() -> list:
    """Unsafe file paths for traversal testing"""
    return [
        "../../../etc/passwd",
        "..\\..\\..\\windows\\system32",
        "../../secrets/config.json",
        "/etc/shadow",
        "C:\\Windows\\System32\\config"
    ]


@pytest.fixture
def safe_paths() -> list:
    """Safe file paths for validation"""
    return [
        "/home/user/documents/file.txt",
        "./relative/path/to/file.py",
        "project/src/main.py",
        "./safe_directory/"
    ]


# ============================================================================
# FILE SYSTEM FIXTURES
# ============================================================================

@pytest.fixture
def test_file_structure(temp_log_dir):
    """Create test file structure"""
    structure = {
        "python_files": [
            temp_log_dir / "script1.py",
            temp_log_dir / "script2.py",
            temp_log_dir / "module.py"
        ],
        "js_files": [
            temp_log_dir / "app.js",
            temp_log_dir / "utils.js"
        ],
        "ignored_files": [
            temp_log_dir / ".gitignore",
            temp_log_dir / "__pycache__",
            temp_log_dir / "node_modules"
        ]
    }

    # Create files
    for file_list in structure.values():
        for file_path in file_list:
            if isinstance(file_path, Path):
                file_path.touch()
            elif isinstance(file_path, str):
                Path(file_path).touch()

    return structure


@pytest.fixture
def file_patterns():
    """File inclusion/exclusion patterns"""
    return {
        "include": ["*.py", "*.js", "*.ts"],
        "exclude": ["__pycache__", "node_modules", ".git", "*.pyc"],
        "ignore_dirs": [".git", "__pycache__", "node_modules", "venv"]
    }


@pytest.fixture
def large_file_content() -> str:
    """Generate large file content for testing"""
    lines = ["line " + str(i) for i in range(1000)]
    return "\n".join(lines)


# ============================================================================
# DATA MODEL FIXTURES
# ============================================================================

@pytest.fixture
def sample_app_config() -> Dict[str, Any]:
    """Sample application configuration"""
    return {
        "api_host": "0.0.0.0",
        "api_port": 8003,
        "log_level": "INFO",
        "database_url": "sqlite:///app.db",
        "max_connections": 10,
        "timeout": 30,
        "enable_cors": True,
        "cors_origins": ["http://localhost:3000", "https://example.com"]
    }


@pytest.fixture
def sample_conversation_message() -> Dict[str, Any]:
    """Sample conversation message"""
    return {
        "id": "msg_123",
        "conversation_id": "conv_123",
        "user_id": "user_123",
        "content": "Hello, how can you help?",
        "role": "user",
        "created_at": "2024-01-01T00:00:00Z",
        "metadata": {
            "source": "api",
            "version": "1.0"
        }
    }


@pytest.fixture
def sample_question_status() -> Dict[str, Any]:
    """Sample question status"""
    return {
        "question_id": "q_123",
        "status": "completed",
        "progress": 100,
        "created_at": "2024-01-01T00:00:00Z",
        "completed_at": "2024-01-01T00:05:00Z",
        "result": {
            "diagram_code": "graph TD\nA-->B",
            "provider": "mermaid"
        }
    }


# ============================================================================
# AI PROVIDER FIXTURES
# ============================================================================

@pytest.fixture
def mock_ai_config():
    """Mock AI provider configuration"""
    mock = MagicMock()
    mock.provider_name = "openai"
    mock.api_key = "sk-test-key"
    mock.model = "gpt-4"
    mock.temperature = 0.7
    mock.max_tokens = 2000
    mock.timeout = 30
    return mock


@pytest.fixture
def mock_ai_provider():
    """Mock AI provider instance"""
    mock = MagicMock()
    mock.provider_name = "openai"
    mock.is_available = MagicMock(return_value=True)
    mock.generate = MagicMock(return_value="Generated response")
    mock.count_tokens = MagicMock(return_value=42)
    mock.validate = MagicMock(return_value=True)
    return mock


@pytest.fixture
def ai_provider_configs() -> Dict[str, Dict[str, Any]]:
    """Sample configurations for different AI providers"""
    return {
        "openai": {
            "provider_name": "openai",
            "api_key": "sk-proj-abc123",
            "model": "gpt-4",
            "temperature": 0.7,
            "max_tokens": 2000
        },
        "anthropic": {
            "provider_name": "anthropic",
            "api_key": "sk-ant-abc123",
            "model": "claude-3-opus",
            "temperature": 0.5,
            "max_tokens": 4000
        },
        "invalid": {
            "provider_name": "invalid_provider",
            "api_key": None,
            "model": None
        }
    }


# ============================================================================
# DIAGRAM PROVIDER FIXTURES
# ============================================================================

@pytest.fixture
def mock_diagram_provider():
    """Mock diagram provider instance"""
    mock = MagicMock()
    mock.provider_id = "mermaid_v1"
    mock.provider_name = "Mermaid"
    mock.supported_formats = ["svg", "png"]
    mock.render = MagicMock(return_value="<svg>...</svg>")
    mock.validate = MagicMock(return_value=True)
    mock.correct = MagicMock(return_value="corrected code")
    return mock


@pytest.fixture
def diagram_codes() -> Dict[str, str]:
    """Sample diagram codes for different providers"""
    return {
        "mermaid_simple": "graph LR\n  A[Start] --> B[End]",
        "mermaid_complex": """graph TD
    A[Start] --> B{Decision}
    B -->|Yes| C[Process]
    B -->|No| D[Skip]
    C --> E[End]""",
        "d2_simple": "A -> B",
        "d2_complex": """User -> Browser -> Server
Server -> Database
Database -> Server
Server -> Browser -> User""",
        "invalid": "this is not valid diagram code @#$%"
    }


@pytest.fixture
def mock_provider_registry():
    """Mock provider registry"""
    mock = MagicMock()
    mock.list_providers = MagicMock(return_value=[
        {"provider_id": "mermaid_v1", "name": "Mermaid"},
        {"provider_id": "d2_v1", "name": "D2"}
    ])
    mock.get_provider = MagicMock(return_value=MagicMock())
    mock.register = MagicMock()
    return mock


# ============================================================================
# SYSTEM MESSAGE FIXTURES
# ============================================================================

@pytest.fixture
def sample_system_message() -> str:
    """Sample system message template"""
    return """You are a helpful assistant that creates diagrams.
User details: {user_name}
Session: {session_id}
Available providers: {providers}

Instructions:
1. Generate clear, concise diagrams
2. Use appropriate diagram types
3. Include helpful labels"""


@pytest.fixture
def system_message_placeholders() -> Dict[str, str]:
    """Placeholders for system messages"""
    return {
        "user_name": "John Doe",
        "session_id": "sess_abc123",
        "providers": "mermaid, d2, plantuml",
        "timestamp": "2024-01-01T00:00:00Z"
    }


# ============================================================================
# REQUEST/RESPONSE FIXTURES
# ============================================================================

@pytest.fixture
def mock_http_request():
    """Mock HTTP request object"""
    mock = MagicMock()
    mock.method = "POST"
    mock.url = "http://localhost:8003/api/v1/diagrams/render"
    mock.headers = {
        "Content-Type": "application/json",
        "Authorization": "Bearer test_token"
    }
    mock.body = json.dumps({"code": "graph TD\nA-->B"})
    return mock


@pytest.fixture
def mock_http_response():
    """Mock HTTP response object"""
    mock = MagicMock()
    mock.status_code = 200
    mock.content_type = "application/json"
    mock.body = json.dumps({
        "success": True,
        "data": "<svg>...</svg>",
        "metadata": {"provider": "mermaid"}
    })
    return mock


# ============================================================================
# ERROR SCENARIO FIXTURES
# ============================================================================

@pytest.fixture
def error_scenarios() -> Dict[str, Exception]:
    """Common error scenarios for testing"""
    return {
        "value_error": ValueError("Invalid value"),
        "type_error": TypeError("Wrong type"),
        "key_error": KeyError("Missing key"),
        "runtime_error": RuntimeError("Runtime error"),
        "os_error": OSError("OS error"),
        "timeout_error": TimeoutError("Request timed out"),
        "connection_error": ConnectionError("Connection failed")
    }


@pytest.fixture
def network_errors():
    """Network error scenarios"""
    return {
        "connection_refused": ConnectionRefusedError("Connection refused"),
        "host_unreachable": ConnectionError("Host unreachable"),
        "timeout": TimeoutError("Connection timeout"),
        "dns_error": OSError("Name or service not known")
    }


# ============================================================================
# PERFORMANCE FIXTURES
# ============================================================================

@pytest.fixture
def performance_thresholds() -> Dict[str, float]:
    """Performance thresholds (in seconds)"""
    return {
        "logger_creation": 0.1,
        "log_write": 0.01,
        "config_load": 0.5,
        "file_scan": 1.0,
        "api_call": 5.0
    }


@pytest.fixture
def load_test_data() -> Dict[str, int]:
    """Data sizes for load testing"""
    return {
        "small": 100,
        "medium": 1000,
        "large": 10000,
        "huge": 100000
    }


# ============================================================================
# MOCK SERVICE FIXTURES
# ============================================================================

@pytest.fixture
def mock_db_connection():
    """Mock database connection"""
    mock = MagicMock()
    mock.connect = MagicMock(return_value=True)
    mock.disconnect = MagicMock()
    mock.execute = MagicMock(return_value=MagicMock())
    mock.is_connected = MagicMock(return_value=True)
    return mock


@pytest.fixture
def mock_external_api():
    """Mock external API service"""
    mock = MagicMock()
    mock.call = MagicMock(return_value={"status": "success", "data": {}})
    mock.validate_response = MagicMock(return_value=True)
    mock.parse_error = MagicMock(return_value="Error message")
    return mock
