from diagrams.provider_registry import ProviderRegistry

def test_imports():
    assert ProviderRegistry is not None

def test_api_health(client):
    """
    Test the health endpoint of the diagram provider API.
    Expects 200 or 503 (if no providers available).
    """
    response = client.get("/api/v1/diagrams/v2/health")
    # It might return 503 if no providers are available (CLI tools missing)
    # The response should be JSON
    assert response.status_code in [200, 503]
    data = response.json()
    assert "status" in data
