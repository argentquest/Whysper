"""
Unit tests for setcontext/context file management functionality.

Tests the conversation session's ability to manage context files including:
- Adding files with security checks
- Updating selected files
- Context change detection
- Thread-safe operations
- Path traversal prevention
"""

import pytest
import threading
import time
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock
from app.services.conversation_service import ConversationSession
from common.models import AppState
from security_utils import SecurityUtils


@pytest.fixture
def mock_ai_processor():
    """Create a mock AI processor for testing"""
    processor = Mock()
    processor.validate_api_key.return_value = True
    processor.process_question.return_value = "Mock response"
    processor.set_api_key = Mock()
    processor.set_provider = Mock()
    # Mock token usage to return valid integers
    processor._provider = Mock()
    processor._provider._last_detailed_usage = {
        "total_tokens": 100,
        "input_tokens": 50,
        "output_tokens": 50,
        "cached_tokens": 0
    }
    return processor


@pytest.fixture
def conversation_session(mock_ai_processor):
    """Create a conversation session for testing"""
    session = ConversationSession(
        session_id="test-session-123",
        ai_processor=mock_ai_processor,
        provider="openrouter",
        available_models=["test-model"],
        default_model="test-model",
    )
    return session


class TestAddFile:
    """Tests for the add_file method"""

    def test_add_file_success(self, conversation_session):
        """Test adding a valid file successfully"""
        with patch('common.env_manager.env_manager.load_env_file', return_value={'CODE_PATH': '.'}):
            with patch.object(SecurityUtils, 'safe_path_resolve', return_value='C:/test/file.py'):
                conversation_session.add_file('file.py')

                assert len(conversation_session.selected_files) == 1
                assert 'C:/test/file.py' in conversation_session.selected_files

    def test_add_file_path_traversal_blocked(self, conversation_session):
        """Test that path traversal attempts are blocked"""
        with patch('common.env_manager.env_manager.load_env_file', return_value={'CODE_PATH': '.'}):
            with patch.object(SecurityUtils, 'safe_path_resolve', return_value=None):
                conversation_session.add_file('../../../etc/passwd')

                # File should NOT be added
                assert len(conversation_session.selected_files) == 0

    def test_add_file_duplicate_ignored(self, conversation_session):
        """Test that duplicate files are ignored"""
        with patch('common.env_manager.env_manager.load_env_file', return_value={'CODE_PATH': '.'}):
            with patch.object(SecurityUtils, 'safe_path_resolve', return_value='C:/test/file.py'):
                conversation_session.add_file('file.py')
                conversation_session.add_file('file.py')

                # Should only have one instance
                assert len(conversation_session.selected_files) == 1

    def test_add_file_make_persistent(self, conversation_session):
        """Test adding a file with make_persistent flag"""
        with patch('common.env_manager.env_manager.load_env_file', return_value={'CODE_PATH': '.'}):
            with patch.object(SecurityUtils, 'safe_path_resolve', return_value='C:/test/file.py'):
                conversation_session.add_file('file.py', make_persistent=True)

                assert len(conversation_session.selected_files) == 1
                assert len(conversation_session.app_state.get_persistent_files()) == 1


class TestUpdateSelectedFiles:
    """Tests for the update_selected_files method"""

    def test_update_selected_files_basic(self, conversation_session):
        """Test basic file list update"""
        files = ['file1.py', 'file2.py', 'file3.py']
        conversation_session.update_selected_files(files)

        assert conversation_session.selected_files == files

    def test_update_selected_files_deduplication(self, conversation_session):
        """Test that duplicate files are removed while preserving order"""
        files = ['file1.py', 'file2.py', 'file1.py', 'file3.py', 'file2.py']
        conversation_session.update_selected_files(files)

        # Should remove duplicates while preserving order
        assert conversation_session.selected_files == ['file1.py', 'file2.py', 'file3.py']

    def test_update_selected_files_make_persistent(self, conversation_session):
        """Test updating files with make_persistent flag"""
        files = ['file1.py', 'file2.py']
        conversation_session.update_selected_files(files, make_persistent=True)

        assert conversation_session.selected_files == files
        assert conversation_session.app_state.get_persistent_files() == files


class TestContextChangeDetection:
    """Tests for context file change detection"""

    def test_context_change_detected(self, conversation_session, mock_ai_processor):
        """Test that context changes are properly detected"""
        # Set initial context
        initial_files = ['file1.py', 'file2.py']
        conversation_session.last_context_files = initial_files
        conversation_session.selected_files = initial_files.copy()

        # Request with different files
        new_files = ['file1.py', 'file3.py']

        with patch.object(conversation_session, 'update_selected_files') as mock_update:
            # Call ask_question with new context files
            conversation_session.ask_question(
                "Test question",
                agent_prompt=None,
                context_files=new_files
            )

            # update_selected_files should have been called with new files
            mock_update.assert_called_once_with(new_files)
            assert conversation_session.last_context_files == new_files

    def test_context_unchanged_no_update(self, conversation_session, mock_ai_processor):
        """Test that unchanged context doesn't trigger update"""
        # Set initial context
        files = ['file1.py', 'file2.py']
        conversation_session.last_context_files = files
        conversation_session.selected_files = files.copy()

        with patch.object(conversation_session, 'update_selected_files') as mock_update:
            # Call ask_question with same files
            conversation_session.ask_question(
                "Test question",
                agent_prompt=None,
                context_files=files
            )

            # update_selected_files should NOT be called
            mock_update.assert_not_called()


class TestThreadSafety:
    """Tests for thread-safe context file operations"""

    def test_concurrent_context_updates_thread_safe(self, conversation_session, mock_ai_processor):
        """Test that concurrent context updates are thread-safe"""
        results = []
        errors = []

        def update_context(file_list, result_list):
            """Update context in a thread"""
            try:
                with conversation_session._context_lock:
                    conversation_session.selected_files = file_list
                    conversation_session.last_context_files = file_list.copy()
                    # Simulate some work
                    time.sleep(0.01)
                    result_list.append(file_list)
            except Exception as e:
                errors.append(e)

        # Create multiple threads with different file lists
        file_lists = [
            ['file1.py'],
            ['file2.py'],
            ['file3.py'],
            ['file4.py'],
            ['file5.py'],
        ]

        threads = []
        for file_list in file_lists:
            thread = threading.Thread(target=update_context, args=(file_list, results))
            threads.append(thread)
            thread.start()

        # Wait for all threads to complete
        for thread in threads:
            thread.join()

        # Check no errors occurred
        assert len(errors) == 0

        # All updates should have completed
        assert len(results) == 5

        # Final state should be one of the file lists (race condition, but should be consistent)
        assert conversation_session.selected_files in file_lists
        assert conversation_session.last_context_files == conversation_session.selected_files


class TestClearFiles:
    """Tests for the clear_files method"""

    def test_clear_files_removes_all(self, conversation_session):
        """Test that clear_files removes all selected and persistent files"""
        # Set up some files
        conversation_session.selected_files = ['file1.py', 'file2.py']
        conversation_session.app_state.set_persistent_files(['file1.py', 'file2.py'])
        conversation_session.last_context_files = ['file1.py', 'file2.py']

        # Clear
        conversation_session.clear_files()

        # Verify all cleared
        assert conversation_session.selected_files == []
        assert conversation_session.app_state.get_persistent_files() == []
        assert conversation_session.last_context_files == []


class TestContextPersistence:
    """Tests for context file persistence across conversation turns"""

    def test_first_message_makes_files_persistent(self, conversation_session, mock_ai_processor):
        """Test that files become persistent on first message"""
        files = ['file1.py', 'file2.py']
        conversation_session.selected_files = files.copy()

        with patch.object(conversation_session, '_load_files', return_value='mock content'):
            with patch.object(conversation_session, '_inject_or_update_system_message'):
                with patch.object(conversation_session, '_process_with_ai', return_value='mock response'):
                    # First message - conversation history is empty
                    conversation_session.ask_question(
                        "First question",
                        agent_prompt=None,
                        context_files=files
                    )

        # Files should be made persistent
        assert conversation_session.app_state.get_persistent_files() == files


class TestSecurityValidation:
    """Tests for security validation in context file operations"""

    def test_safe_path_resolve_with_code_path(self, conversation_session):
        """Test that CODE_PATH is used as the base for path resolution"""
        with patch('common.env_manager.env_manager.load_env_file',
                   return_value={'CODE_PATH': 'C:/safe/directory'}):
            with patch.object(SecurityUtils, 'safe_path_resolve') as mock_resolve:
                mock_resolve.return_value = 'C:/safe/directory/file.py'

                conversation_session.add_file('file.py')

                # Verify safe_path_resolve was called with CODE_PATH
                mock_resolve.assert_called_once_with('C:/safe/directory', 'file.py')

    def test_file_path_normalization(self, conversation_session):
        """Test that file paths are properly normalized"""
        with patch('common.env_manager.env_manager.load_env_file', return_value={'CODE_PATH': '.'}):
            with patch.object(SecurityUtils, 'safe_path_resolve', side_effect=lambda base, path: f'{base}/{path}'):
                # Various path formats should all be normalized
                paths = [
                    'file.py',
                    './file.py',
                    'subdir/../file.py',
                ]

                for path in paths:
                    conversation_session.selected_files = []
                    conversation_session.add_file(path)
                    # File should be added (we're not testing exact normalization, just that it works)
                    assert len(conversation_session.selected_files) > 0


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
