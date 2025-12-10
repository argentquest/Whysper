import pytest
from unittest.mock import MagicMock, patch
import json
from diagrams.models import RenderResult, ValidationResult

try:
    from diagrams.mermaidv1.mermaid_renderer import MermaidV1Provider
except ImportError:
    MermaidV1Provider = None

@pytest.fixture
def mermaid_provider(tmp_path):
    if not MermaidV1Provider:
        pytest.skip("Mermaid provider module not found")

    p_dir = tmp_path / "mermaidv1"
    p_dir.mkdir()
    config = {
        "provider_id": "mermaidv1",
        "provider_name": "Mermaid",
        "diagram_type": "mermaid",
        "supported_output_formats": ["mermaid", "svg", "png"]
    }
    (p_dir / "config.json").write_text(json.dumps(config))
    return MermaidV1Provider(p_dir)

@patch("diagrams.mermaidv1.mermaid_renderer.subprocess.run")
def test_is_available(mock_run, mermaid_provider):
    mock_run.return_value.returncode = 0
    assert mermaid_provider.is_available() is True

    mock_run.side_effect = Exception("Not found")
    mermaid_provider._cli_available = None
    assert mermaid_provider.is_available() is False

@patch("diagrams.mermaidv1.mermaid_renderer.validate_mermaid_with_cli")
@patch("diagrams.mermaidv1.mermaid_renderer.is_mermaid_cli_available")
def test_validate_code(mock_avail, mock_val, mermaid_provider):
    mock_avail.return_value = True

    mock_val.return_value = (True, "Valid")
    res = mermaid_provider.validate_code("graph TD; A-->B;")
    assert res.is_valid

    mock_val.return_value = (False, "Syntax error")
    res = mermaid_provider.validate_code("bad")
    assert not res.is_valid

@patch("diagrams.mermaidv1.mermaid_renderer.validate_mermaid_and_render")
@patch("diagrams.mermaidv1.mermaid_renderer.is_mermaid_cli_available")
def test_render(mock_avail, mock_render_func, mermaid_provider):
    mock_avail.return_value = True

    mock_render_func.return_value = (True, "Success", "<svg>mermaid</svg>")
    res = mermaid_provider.render("graph TD; A-->B;", "svg")
    assert res.success
    assert res.content == "<svg>mermaid</svg>"

    mock_render_func.return_value = (False, "Error", None)
    res = mermaid_provider.render("graph TD; A-->B;", "svg")
    assert not res.success
