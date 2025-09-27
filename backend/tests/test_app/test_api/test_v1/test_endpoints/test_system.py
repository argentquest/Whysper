"""
Tests for system endpoints.

This module tests the system-level API endpoints including health checks
and version information.
"""
import pytest
from fastapi.testclient import TestClient


def test_root_endpoint(test_client: TestClient):
    """Test the root endpoint."""
    response = test_client.get("/api/v1/")
    assert response.status_code == 200
    data = response.json()
    assert "message" in data
    assert "WhisperCode" in data["message"]
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