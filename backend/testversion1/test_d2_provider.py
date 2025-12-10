import pytest
from unittest.mock import MagicMock, patch
import json
from diagrams.d2v1.d2_renderer import D2V1Provider
from diagrams.models import RenderResult, ValidationResult

@pytest.fixture
def d2_provider(tmp_path):
    """Create a D2V1Provider instance with temporary config"""
    p_dir = tmp_path / "d2v1"
    p_dir.mkdir()
    config = {
        "provider_id": "d2v1",
        "provider_name": "D2",
        "diagram_type": "d2",
        "supported_output_formats": ["d2", "svg", "png"]
    }
    (p_dir / "config.json").write_text(json.dumps(config))
    return D2V1Provider(p_dir)

@patch("diagrams.d2v1.d2_renderer.subprocess.run")
def test_is_available(mock_run, d2_provider):
    """Test availability check"""
    mock_run.return_value.returncode = 0
    assert d2_provider.is_available() is True

    # Test unavailable
    mock_run.side_effect = Exception("Not found")
    # Reset cache
    d2_provider._cli_available = None
    assert d2_provider.is_available() is False

@patch("diagrams.d2v1.d2_renderer.validate_d2_with_cli")
@patch("diagrams.d2v1.d2_renderer.is_d2_cli_available")
def test_validate_code(mock_avail, mock_val, d2_provider):
    """Test code validation"""
    mock_avail.return_value = True

    # Valid
    mock_val.return_value = (True, "Valid")
    res = d2_provider.validate_code("x -> y")
    assert res.is_valid
    assert res.error is None

    # Invalid
    mock_val.return_value = (False, "Syntax error")
    res = d2_provider.validate_code("bad code")
    assert not res.is_valid
    assert res.error == "Syntax error"

@patch("diagrams.d2v1.d2_renderer.validate_d2_and_render")
@patch("diagrams.d2v1.d2_renderer.is_d2_cli_available")
def test_render(mock_avail, mock_render_func, d2_provider):
    """Test rendering"""
    mock_avail.return_value = True

    # Success
    mock_render_func.return_value = (True, "Success", "<svg>d2</svg>")
    res = d2_provider.render("x -> y", "svg")
    assert res.success
    assert res.content == "<svg>d2</svg>"

    # Fail
    mock_render_func.return_value = (False, "Render error", None)
    res = d2_provider.render("x -> y", "svg")
    assert not res.success
    assert "Render error" in res.error

def test_pattern_fix(d2_provider):
    """Test pattern based auto fix logic"""
    # D2 provider has fix_d2_syntax.
    # We can test auto_fix_pattern_based method.

    # Arrow fix: " - > " to " -> "
    code = "A - > B"
    res = d2_provider.auto_fix_pattern_based(code, "Syntax error")

    # Since validate_code is mocked in actual execution (or we rely on auto_fix_pattern_based logic),
    # auto_fix_pattern_based in D2V1Provider calls fix_d2_syntax then validate_code.
    # We should mock validate_code to return True for the fixed code.

    with patch.object(d2_provider, 'validate_code') as mock_val:
        mock_val.return_value = ValidationResult(is_valid=True, code_length=len("A -> B"))

        res = d2_provider.auto_fix_pattern_based(code, "Error")

        assert res.auto_fixed
        assert "->" in res.fixed_code
        assert "- >" not in res.fixed_code
