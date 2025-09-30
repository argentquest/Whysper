"""
Tests for system endpoints.

This module tests the system-level API endpoints including health checks,
version information, agents, and subagents functionality.
"""
import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch


def test_root_endpoint(test_client: TestClient):
    """Test the root endpoint."""
    response = test_client.get("/api/v1/")
    assert response.status_code == 200
    data = response.json()
    assert "message" in data
    assert "Whysper" in data["message"]
    assert "version" in data


def test_health_endpoint(test_client: TestClient):
    """Test the health check endpoint."""
    response = test_client.get("/api/v1/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert "timestamp" in data
    assert "version" in data


def test_version_endpoint(test_client: TestClient):
    """Test the version endpoint."""
    response = test_client.get("/api/v1/version")
    assert response.status_code == 200
    data = response.json()
    assert "api_version" in data
    assert "api_title" in data
    assert "python_version" in data
    assert "platform" in data


def test_list_agents_endpoint(test_client: TestClient):
    """Test the list agents endpoint."""
    response = test_client.get("/api/v1/settings/agents")
    assert response.status_code == 200
    data = response.json()

    # Should return a list of agent prompts
    assert isinstance(data, list)
    if data:  # Only check structure if there are agents
        agent = data[0]
        assert "name" in agent
        assert "title" in agent
        assert "description" in agent
        assert "category" in agent
        assert "filename" in agent


def test_list_subagents_endpoint(test_client: TestClient):
    """Test the list subagents endpoint."""
    response = test_client.get("/api/v1/settings/subagents")
    assert response.status_code == 200
    data = response.json()

    # Should return a list of subagent commands
    assert isinstance(data, list)


@patch('app.services.settings_service.settings_service.get_agent_prompts')
def test_list_agents_with_mocked_data(mock_get_agent_prompts, test_client: TestClient):
    """Test that agents endpoint returns agent prompts from SettingsService."""
    # Mock the agent prompts response
    mock_agent_prompts = [
        {
            "name": "test-prompt",
            "title": "Test Prompt",
            "description": "A test prompt",
            "category": ["Testing"],
            "filename": "test-prompt.md"
        }
    ]
    mock_get_agent_prompts.return_value = mock_agent_prompts

    response = test_client.get("/api/v1/settings/agents")
    assert response.status_code == 200
    data = response.json()

    assert data == mock_agent_prompts
    mock_get_agent_prompts.assert_called_once()


@patch('app.services.settings_service.settings_service.get_subagent_commands')
def test_list_subagents_with_mocked_data(mock_get_subagent_commands, test_client: TestClient):
    """Test that subagents endpoint returns subagent commands from SettingsService."""
    # Mock the subagent commands response
    mock_subagent_commands = [
        {
            "category": "Refactoring",
            "title": "Refactor Code",
            "subcommand": "Refactor this code..."
        }
    ]
    mock_get_subagent_commands.return_value = mock_subagent_commands

    response = test_client.get("/api/v1/settings/subagents")
    assert response.status_code == 200
    data = response.json()

    assert data == mock_subagent_commands
    mock_get_subagent_commands.assert_called_once()