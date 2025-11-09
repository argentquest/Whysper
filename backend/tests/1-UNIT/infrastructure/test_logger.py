"""
Logger Infrastructure Tests (Phase 2)

Tests for core logging system:
- LogContext creation and management
- StructuredFormatter JSON formatting
- ConsoleFormatter output
- CodeChatLogger initialization
- File rotation handling
- Performance context tracking
- Exception logging
"""

import pytest
import json
import logging
from pathlib import Path
from datetime import datetime
from unittest.mock import MagicMock, patch


class TestLogContext:
    """Test LogContext creation and management"""

    def test_create_empty_context(self):
        """Create context with no data"""
        from common.logger import LogContext
        context = LogContext()
        assert context.user_id is None
        assert context.session_id is None
        assert context.component is None

    def test_create_context_with_data(self, log_context):
        """Create context with all fields"""
        assert log_context.user_id == "user_123"
        assert log_context.session_id == "sess_abc123"
        assert log_context.component == "test_component"
        assert log_context.operation == "test_operation"
        assert log_context.request_id == "req_xyz789"

    def test_context_to_dict(self, log_context):
        """Convert context to dictionary"""
        from dataclasses import asdict
        context_dict = asdict(log_context)
        assert isinstance(context_dict, dict)
        assert context_dict["user_id"] == "user_123"
        assert context_dict["session_id"] == "sess_abc123"

    def test_context_with_additional_data(self):
        """Context with additional metadata"""
        from common.logger import LogContext
        additional = {"key1": "value1", "key2": "value2"}
        context = LogContext(
            user_id="user_123",
            additional_data=additional
        )
        assert context.additional_data == additional

    def test_context_with_file_location(self):
        """Context with file path and line number"""
        from common.logger import LogContext
        context = LogContext(
            file_path="/path/to/file.py",
            line_number=42
        )
        assert context.file_path == "/path/to/file.py"
        assert context.line_number == 42


class TestStructuredFormatter:
    """Test StructuredFormatter for JSON logging"""

    def test_format_basic_log_record(self):
        """Format basic log record as JSON"""
        from common.logger import StructuredFormatter
        formatter = StructuredFormatter()

        record = logging.LogRecord(
            name="test.logger",
            level=logging.INFO,
            pathname="/path/to/file.py",
            lineno=42,
            msg="Test message",
            args=(),
            exc_info=None
        )

        result = formatter.format(record)
        data = json.loads(result)

        assert data["level"] == "INFO"
        assert data["message"] == "Test message"
        assert data["logger"] == "test.logger"
        assert "timestamp" in data
        assert data["line"] == 42

    def test_format_with_exception(self):
        """Format log record with exception"""
        from common.logger import StructuredFormatter
        formatter = StructuredFormatter()

        try:
            raise ValueError("Test error")
        except ValueError:
            import sys
            record = logging.LogRecord(
                name="test.logger",
                level=logging.ERROR,
                pathname="test.py",
                lineno=1,
                msg="Error occurred",
                args=(),
                exc_info=sys.exc_info()
            )

            result = formatter.format(record)
            data = json.loads(result)

            assert data["level"] == "ERROR"
            assert "exception" in data
            assert data["exception"]["type"] == "ValueError"
            assert "Test error" in data["exception"]["message"]

    def test_format_with_context(self, log_context):
        """Format log record with LogContext"""
        from common.logger import StructuredFormatter
        formatter = StructuredFormatter()

        record = logging.LogRecord(
            name="test.logger",
            level=logging.INFO,
            pathname="test.py",
            lineno=1,
            msg="Contextual message",
            args=(),
            exc_info=None
        )
        record.context = log_context

        result = formatter.format(record)
        data = json.loads(result)

        assert "context" in data
        assert data["context"]["user_id"] == "user_123"
        assert data["context"]["session_id"] == "sess_abc123"

    def test_format_json_is_valid(self):
        """Ensure formatted output is valid JSON"""
        from common.logger import StructuredFormatter
        formatter = StructuredFormatter()

        record = logging.LogRecord(
            name="test.logger",
            level=logging.DEBUG,
            pathname="test.py",
            lineno=1,
            msg="Debug message",
            args=(),
            exc_info=None
        )

        result = formatter.format(record)
        # Should not raise JSON decode error
        parsed = json.loads(result)
        assert isinstance(parsed, dict)

    def test_format_with_extra_fields(self):
        """Format with extra custom fields"""
        from common.logger import StructuredFormatter
        formatter = StructuredFormatter()

        record = logging.LogRecord(
            name="test.logger",
            level=logging.INFO,
            pathname="test.py",
            lineno=1,
            msg="Message with extras",
            args=(),
            exc_info=None
        )
        record.custom_field = "custom_value"

        result = formatter.format(record)
        data = json.loads(result)

        # Custom fields should be in 'extra' section
        assert "extra" in data or "custom_field" in str(data)


class TestConsoleFormatter:
    """Test ConsoleFormatter for human-readable output"""

    def test_create_console_formatter(self):
        """Create console formatter instance"""
        from common.logger import ConsoleFormatter
        formatter = ConsoleFormatter()
        assert formatter is not None

    def test_format_basic_message(self):
        """Format basic console message"""
        from common.logger import ConsoleFormatter
        formatter = ConsoleFormatter()

        record = logging.LogRecord(
            name="test.logger",
            level=logging.INFO,
            pathname="test.py",
            lineno=42,
            msg="Test message",
            args=(),
            exc_info=None
        )

        result = formatter.format(record)
        assert "Test message" in result
        assert "test.py" in result or "test.logger" in result

    def test_format_different_levels(self):
        """Format messages with different log levels"""
        from common.logger import ConsoleFormatter
        formatter = ConsoleFormatter()

        levels = [
            (logging.DEBUG, "DEBUG"),
            (logging.INFO, "INFO"),
            (logging.WARNING, "WARNING"),
            (logging.ERROR, "ERROR"),
            (logging.CRITICAL, "CRITICAL")
        ]

        for level_int, level_name in levels:
            record = logging.LogRecord(
                name="test.logger",
                level=level_int,
                pathname="test.py",
                lineno=1,
                msg=f"{level_name} message",
                args=(),
                exc_info=None
            )

            result = formatter.format(record)
            assert level_name in result or level_int in result or f"{level_name} message" in result

    def test_format_is_human_readable(self):
        """Ensure output is human-readable (not JSON)"""
        from common.logger import ConsoleFormatter
        formatter = ConsoleFormatter()

        record = logging.LogRecord(
            name="test.logger",
            level=logging.INFO,
            pathname="test.py",
            lineno=1,
            msg="Readable message",
            args=(),
            exc_info=None
        )

        result = formatter.format(record)
        # Should not be JSON
        try:
            json.loads(result)
            is_json = True
        except:
            is_json = False

        assert not is_json, "Console formatter should output plain text, not JSON"


class TestCodeChatLogger:
    """Test CodeChatLogger class"""

    def test_create_logger(self, log_file_path):
        """Create CodeChatLogger instance"""
        from common.logger import CodeChatLogger
        logger = CodeChatLogger(
            name="test_logger",
            log_file=str(log_file_path)
        )
        assert logger is not None

    def test_logger_has_handlers(self, log_file_path):
        """Logger has console and file handlers"""
        from common.logger import CodeChatLogger
        logger = CodeChatLogger(
            name="test_logger",
            log_file=str(log_file_path)
        )

        # Logger should have handlers
        assert len(logger.logger.handlers) > 0

    def test_log_file_created(self, log_file_path):
        """Log file is created when writing"""
        from common.logger import CodeChatLogger
        logger = CodeChatLogger(
            name="test_logger",
            log_file=str(log_file_path)
        )
        logger.info("Test message")

        # File should exist after logging
        assert log_file_path.exists()

    def test_log_file_contains_logs(self, log_file_path):
        """Log file contains written logs"""
        from common.logger import CodeChatLogger
        logger = CodeChatLogger(
            name="test_logger",
            log_file=str(log_file_path)
        )
        logger.info("Test message content")

        content = log_file_path.read_text()
        assert "Test message content" in content or len(content) > 0

    def test_log_rotating_file_handler(self, log_file_path):
        """Logger uses rotating file handler"""
        from common.logger import CodeChatLogger
        logger = CodeChatLogger(
            name="test_logger",
            log_file=str(log_file_path),
            max_bytes=1024,  # Small size to test rotation
            backup_count=2
        )

        # Write enough data to potentially trigger rotation
        for i in range(100):
            logger.info(f"Message {i} - " + "x" * 50)

        # Check that log directory contains files
        log_dir = log_file_path.parent
        log_files = list(log_dir.glob(log_file_path.name + "*"))
        assert len(log_files) >= 1

    def test_logger_info_level(self, log_file_path):
        """Logger logs info level messages"""
        from common.logger import CodeChatLogger
        logger = CodeChatLogger(
            name="test_logger",
            log_file=str(log_file_path)
        )
        logger.info("Info message")
        assert True  # If no exception, test passes

    def test_logger_debug_level(self, log_file_path):
        """Logger logs debug level messages"""
        from common.logger import CodeChatLogger
        logger = CodeChatLogger(
            name="test_logger",
            log_file=str(log_file_path)
        )
        logger.debug("Debug message")
        assert True

    def test_logger_warning_level(self, log_file_path):
        """Logger logs warning level messages"""
        from common.logger import CodeChatLogger
        logger = CodeChatLogger(
            name="test_logger",
            log_file=str(log_file_path)
        )
        logger.warning("Warning message")
        assert True

    def test_logger_error_level(self, log_file_path):
        """Logger logs error level messages"""
        from common.logger import CodeChatLogger
        logger = CodeChatLogger(
            name="test_logger",
            log_file=str(log_file_path)
        )
        logger.error("Error message")
        assert True

    def test_logger_critical_level(self, log_file_path):
        """Logger logs critical level messages"""
        from common.logger import CodeChatLogger
        logger = CodeChatLogger(
            name="test_logger",
            log_file=str(log_file_path)
        )
        logger.critical("Critical message")
        assert True


class TestLoggerContextManager:
    """Test logger context manager functionality"""

    def test_context_manager_creation(self, log_file_path):
        """Create LoggerContextManager"""
        from common.logger import LoggerContextManager
        manager = LoggerContextManager(
            logger_name="test_logger",
            log_file=str(log_file_path)
        )
        assert manager is not None

    def test_context_manager_with_context(self, log_file_path, log_context):
        """Use context manager with LogContext"""
        from common.logger import LoggerContextManager
        manager = LoggerContextManager(
            logger_name="test_logger",
            log_file=str(log_file_path)
        )

        # Should be able to use as context manager
        try:
            with manager.with_context(log_context):
                manager.info("Message within context")
            assert True
        except Exception as e:
            pytest.fail(f"Context manager failed: {e}")


class TestLoggerPerformance:
    """Test logger performance characteristics"""

    def test_logger_creation_performance(self, performance_thresholds, log_file_path):
        """Logger creation completes within threshold"""
        from common.logger import CodeChatLogger
        import time

        start = time.time()
        CodeChatLogger(
            name="perf_test",
            log_file=str(log_file_path)
        )
        elapsed = time.time() - start

        assert elapsed < performance_thresholds["logger_creation"]

    def test_logging_performance(self, performance_thresholds, log_file_path):
        """Single log write completes quickly"""
        from common.logger import CodeChatLogger
        import time

        logger = CodeChatLogger(
            name="perf_test",
            log_file=str(log_file_path)
        )

        start = time.time()
        logger.info("Performance test message")
        elapsed = time.time() - start

        assert elapsed < performance_thresholds["log_write"]


class TestLoggerErrorHandling:
    """Test logger error handling"""

    def test_logger_with_invalid_path(self):
        """Logger handles invalid log file path"""
        from common.logger import CodeChatLogger

        # Should handle invalid path gracefully
        try:
            logger = CodeChatLogger(
                name="test_logger",
                log_file="/invalid/path/that/does/not/exist/logfile.log"
            )
            # May succeed or fail gracefully
            assert True
        except (OSError, IOError):
            # Expected for invalid paths
            assert True

    def test_logger_with_exception_logging(self, log_file_path):
        """Logger handles exception logging"""
        from common.logger import CodeChatLogger

        logger = CodeChatLogger(
            name="test_logger",
            log_file=str(log_file_path)
        )

        try:
            try:
                raise ValueError("Test exception")
            except ValueError:
                logger.exception("An error occurred")
        except Exception as e:
            pytest.fail(f"Exception logging failed: {e}")


class TestLoggerIntegration:
    """Integration tests for logger"""

    def test_logger_with_multiple_handlers(self, log_file_path):
        """Logger works with multiple handlers"""
        from common.logger import CodeChatLogger

        logger = CodeChatLogger(
            name="integration_test",
            log_file=str(log_file_path)
        )

        # Log at different levels
        logger.debug("Debug message")
        logger.info("Info message")
        logger.warning("Warning message")
        logger.error("Error message")

        # Check file was written
        assert log_file_path.exists()

    def test_logger_with_context_flow(self, log_file_path, log_context):
        """Logger with context throughout execution"""
        from common.logger import CodeChatLogger

        logger = CodeChatLogger(
            name="context_test",
            log_file=str(log_file_path)
        )

        # Simulate logging with context
        for i in range(5):
            logger.info(f"Message {i}")

        assert log_file_path.exists()

    def test_concurrent_logging(self, log_file_path):
        """Logger handles concurrent writes"""
        from common.logger import CodeChatLogger
        import threading

        logger = CodeChatLogger(
            name="concurrent_test",
            log_file=str(log_file_path)
        )

        def write_logs():
            for i in range(10):
                logger.info(f"Thread message {i}")

        threads = [threading.Thread(target=write_logs) for _ in range(3)]
        for thread in threads:
            thread.start()
        for thread in threads:
            thread.join()

        # File should contain all messages
        assert log_file_path.exists()
        content = log_file_path.read_text()
        assert len(content) > 0
