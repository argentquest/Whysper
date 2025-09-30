"""
Tests for SettingsService functionality.

This module tests the SettingsService class, including YAML frontmatter parsing
and agent prompt loading functionality.
"""

import pytest
import tempfile
import os
from pathlib import Path
from unittest.mock import patch, Mock, mock_open

from app.services.settings_service import SettingsService


class TestSettingsService:
    """Test cases for SettingsService."""

    @pytest.fixture
    def settings_service(self):
        """Create a SettingsService instance for testing."""
        return SettingsService()

    def test_parse_yaml_frontmatter_with_valid_yaml(self, settings_service):
        """Test parsing YAML frontmatter with valid content."""
        content = """---
title: "Test Title"
description: "Test Description"
category: ["cat1", "cat2"]
author: "Test Author"
---

# Content
Test content here."""

        result = settings_service._parse_yaml_frontmatter(content)

        assert result is not None
        assert result["title"] == "Test Title"
        assert result["description"] == "Test Description"
        assert result["category"] == ["cat1", "cat2"]
        assert result["author"] == "Test Author"

    def test_parse_yaml_frontmatter_without_yaml(self, settings_service):
        """Test parsing content without YAML frontmatter."""
        content = """# Just Markdown Content

This is regular markdown without YAML frontmatter."""

        result = settings_service._parse_yaml_frontmatter(content)

        assert result is None

    def test_parse_yaml_frontmatter_malformed(self, settings_service):
        """Test parsing malformed YAML frontmatter."""
        content = """---
title: "Test"
invalid yaml here: [unclosed
---

# Content"""

        result = settings_service._parse_yaml_frontmatter(content)

        # The parser is lenient and parses what it can
        assert result is not None
        assert result["title"] == "Test"
        assert "invalid yaml here" in result

    @patch('os.path.exists')
    @patch('os.listdir')
    @patch('builtins.open', new_callable=mock_open)
    def test_get_agent_prompts_with_mocked_files(self, mock_file_open, mock_listdir, mock_exists, settings_service):
        """Test loading agent prompts with mocked file operations."""
        # Setup mocks
        mock_exists.return_value = True
        mock_listdir.return_value = ["test-prompt.md"]

        # Mock file content with YAML frontmatter
        mock_file_content = """---
title: "Test Agent Prompt"
description: "A test agent prompt"
category: ["Testing"]
---

# Test Content
Test content here."""
        mock_file_open.return_value.read.return_value = mock_file_content

        prompts = settings_service.get_agent_prompts()

        assert len(prompts) == 1
        prompt = prompts[0]
        assert prompt["name"] == "test-prompt"
        assert prompt["title"] == "Test Agent Prompt"
        assert prompt["description"] == "A test agent prompt"
        assert prompt["category"] == ["Testing"]
        assert prompt["filename"] == "test-prompt.md"

    @patch('os.path.exists')
    def test_get_agent_prompts_directory_not_found(self, mock_exists, settings_service):
        """Test handling when agent prompts directory doesn't exist."""
        mock_exists.return_value = False

        prompts = settings_service.get_agent_prompts()

        assert prompts == []

    @patch('os.path.exists')
    @patch('os.listdir')
    def test_get_agent_prompts_empty_directory(self, mock_listdir, mock_exists, settings_service):
        """Test loading agent prompts from empty directory."""
        mock_exists.return_value = True
        mock_listdir.return_value = []

        prompts = settings_service.get_agent_prompts()

        assert prompts == []

    @patch('os.path.exists')
    @patch('builtins.open', new_callable=mock_open)
    def test_get_subagent_commands_success(self, mock_file_open, mock_exists, settings_service):
        """Test loading subagent commands successfully."""
        mock_exists.return_value = True

        mock_file_content = """[
    {
        "category": "Refactoring",
        "title": "Refactor Code",
        "subcommand": "Refactor this code..."
    }
]"""
        mock_file_open.return_value.read.return_value = mock_file_content

        commands = settings_service.get_subagent_commands()

        assert len(commands) == 1
        assert commands[0]["category"] == "Refactoring"
        assert commands[0]["title"] == "Refactor Code"

    @patch('os.path.exists')
    def test_get_subagent_commands_file_not_found(self, mock_exists, settings_service):
        """Test handling when subagent commands file doesn't exist."""
        mock_exists.return_value = False

        commands = settings_service.get_subagent_commands()

        assert commands == []

    @patch('os.path.exists')
    @patch('builtins.open', new_callable=mock_open)
    def test_get_agent_prompt_content_success(self, mock_file_open, mock_exists, settings_service):
        """Test loading agent prompt content successfully."""
        mock_exists.return_value = True

        mock_file_content = "# Test Content\n\nThis is test content."
        mock_file_open.return_value.read.return_value = mock_file_content

        content = settings_service.get_agent_prompt_content("test.md")

        assert content == "# Test Content\n\nThis is test content."

    @patch('os.path.exists')
    def test_get_agent_prompt_content_not_found(self, mock_exists, settings_service):
        """Test handling when agent prompt file doesn't exist."""
        mock_exists.return_value = False

        content = settings_service.get_agent_prompt_content("missing.md")

        assert content == ""