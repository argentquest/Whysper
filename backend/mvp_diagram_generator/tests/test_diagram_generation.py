"""
Integration tests for diagram generation API
Tests the complete pipeline: AI generation + rendering using renderer_v2.py

Prerequisites:
- Backend server running on http://localhost:8003
- Frontend server running on http://localhost:5173
- API_KEY configured in backend/.env
"""

import pytest
import json
import requests

# Load the test prompts
with open("C:/Code2025/Whysper/backend/tests/Diagrams/test.json", "r") as f:
    test_data = json.load(f)


@pytest.mark.parametrize("prompt", test_data["d2_test_prompts"])
def test_d2_diagram_generation(prompt):
    """Test D2 diagram generation with AI + renderer_v2."""
    print(f"\n[TEST] Testing D2: {prompt['name']}")
    print(f"   Description: {prompt['description'][:100]}...")

    response = requests.post(
        "http://localhost:8003/api/v1/diagrams/generate",
        json={"prompt": prompt["description"], "diagram_type": "d2", "output_format": "svg"},
        timeout=60  # AI generation can take time
    )

    assert response.status_code == 200, f"Expected 200, got {response.status_code}"

    data = response.json()

    # Check for errors
    assert "error_info" in data, "Response missing error_info"
    assert not data["error_info"]["has_error"], f"Error: {data['error_info'].get('error_message', 'Unknown error')}"

    # Check diagram code was generated
    assert "diagram_code" in data, "Response missing diagram_code"
    assert data["diagram_code"], "Diagram code is empty"
    print(f"   [PASS] Generated D2 code: {len(data['diagram_code'])} chars")

    # Check SVG was rendered
    assert "image_data" in data, "Response missing image_data"
    assert data["image_data"], "Image data is empty"
    assert "<svg" in data["image_data"], "Image data doesn't contain SVG"
    print(f"   [PASS] Rendered SVG: {len(data['image_data'])} chars")

    # Check format
    assert data["image_format"] == "svg"

    print(f"   [PASS] Test passed: {prompt['name']}")


@pytest.mark.parametrize("prompt", test_data["mermaid_test_prompts"])
def test_mermaid_diagram_generation(prompt):
    """Test Mermaid diagram generation with AI + renderer_v2."""
    print(f"\n[TEST] Testing Mermaid: {prompt['name']}")
    print(f"   Description: {prompt['description'][:100]}...")

    response = requests.post(
        "http://localhost:8003/api/v1/diagrams/generate",
        json={"prompt": prompt["description"], "diagram_type": "mermaid", "output_format": "svg"},
        timeout=60
    )

    assert response.status_code == 200, f"Expected 200, got {response.status_code}"

    data = response.json()

    # Check for errors
    assert "error_info" in data, "Response missing error_info"
    assert not data["error_info"]["has_error"], f"Error: {data['error_info'].get('error_message', 'Unknown error')}"

    # Check diagram code was generated
    assert "diagram_code" in data, "Response missing diagram_code"
    assert data["diagram_code"], "Diagram code is empty"
    print(f"   [PASS] Generated Mermaid code: {len(data['diagram_code'])} chars")

    # Check SVG was rendered
    assert "image_data" in data, "Response missing image_data"
    assert data["image_data"], "Image data is empty"
    assert "<svg" in data["image_data"], "Image data doesn't contain SVG"
    print(f"   [PASS] Rendered SVG: {len(data['image_data'])} chars")

    # Check format
    assert data["image_format"] == "svg"

    print(f"   [PASS] Test passed: {prompt['name']}")


@pytest.mark.parametrize("prompt", test_data["c4_test_prompts"])
def test_c4_diagram_generation(prompt):
    """Test C4 diagram generation with AI + renderer_v2."""
    print(f"\n[TEST] Testing C4: {prompt['name']}")
    print(f"   Description: {prompt['description'][:100]}...")

    response = requests.post(
        "http://localhost:8003/api/v1/diagrams/generate",
        json={"prompt": prompt["description"], "diagram_type": "c4", "output_format": "svg"},
        timeout=60
    )

    assert response.status_code == 200, f"Expected 200, got {response.status_code}"

    data = response.json()

    # Check for errors
    assert "error_info" in data, "Response missing error_info"
    assert not data["error_info"]["has_error"], f"Error: {data['error_info'].get('error_message', 'Unknown error')}"

    # Check diagram code was generated
    assert "diagram_code" in data, "Response missing diagram_code"
    assert data["diagram_code"], "Diagram code is empty"
    print(f"   [PASS] Generated C4 code: {len(data['diagram_code'])} chars")

    # Check SVG was rendered
    assert "image_data" in data, "Response missing image_data"
    assert data["image_data"], "Image data is empty"
    assert "<svg" in data["image_data"], "Image data doesn't contain SVG"
    print(f"   [PASS] Rendered SVG: {len(data['image_data'])} chars")

    # Check format
    assert data["image_format"] == "svg"

    print(f"   [PASS] Test passed: {prompt['name']}")


# Quick smoke tests for PNG output
def test_png_output_mermaid():
    """Test PNG output for Mermaid."""
    response = requests.post(
        "http://localhost:8003/api/v1/diagrams/generate",
        json={
            "prompt": "Generate a simple flowchart with Start and End nodes",
            "diagram_type": "mermaid",
            "output_format": "png"
        },
        timeout=60
    )

    assert response.status_code == 200
    data = response.json()
    assert not data["error_info"]["has_error"]
    assert data["image_format"] == "png"
    assert data["image_data"]
    # PNG is base64 encoded, should not contain SVG tags
    assert "<svg" not in data["image_data"]
    print("[PASS] PNG output test passed")


if __name__ == "__main__":
    # Run with: python test_diagram_generation.py
    pytest.main([__file__, "-v", "-s"])
