"""
Legacy compatibility layer for WhisperCode Web2 Backend.

This module maintains backward compatibility with the original api.py structure
while redirecting to the new modular architecture.
"""
# Import both apps to provide backward compatibility
from app.main import app as main_app
from api_legacy import app

# Import legacy functions for test compatibility (except _load_env_defaults which we override)
from api_legacy import (
    _session_summary_model,
    _conversation_state_response,
    _render_with_mermaid_cli,
    _render_with_puppeteer,
    _render_with_python_mermaid,
    _create_simple_flowchart_svg,
    _detect_language,
    _generate_filename
)

# Import env_manager for test compatibility
from common.env_manager import env_manager

# Import conversation_manager for test compatibility
from web_backend.services.conversation_service import conversation_manager

# Import file_service for test compatibility
from web_backend.services.file_service import file_service

# Import subprocess for test compatibility
import subprocess

# Import types for _load_env_defaults
from typing import List

# Test-compatible version of _load_env_defaults that uses mockable env_manager
def _load_env_defaults() -> tuple[str, str, List[str], str]:
    """Test-compatible version that uses the mockable api.env_manager."""
    env_vars = env_manager.load_env_file()
    provider = (
        env_vars.get("PROVIDER")
        or env_vars.get("DEFAULT_PROVIDER")
        or "openrouter"
    )
    models_env = env_vars.get("MODELS")
    if models_env:
        models = [m.strip() for m in models_env.split(",") if m.strip()]
    else:
        models = [
            "openai/gpt-3.5-turbo",
            "openai/gpt-4",
            "openai/gpt-4-turbo",
            "anthropic/claude-3-haiku",
            "anthropic/claude-3-sonnet",
        ]
    default_model = (
        env_vars.get("DEFAULT_MODEL")
        or (models[0] if models else "")
    )
    api_key = env_vars.get("API_KEY", "")
    return api_key, provider, models, default_model

# Import mermaid helper functions for test compatibility (with underscore aliases)
from app.utils.mermaid_helpers import (
    render_mermaid_diagram,
    render_with_mermaid_cli,
    render_with_puppeteer, 
    render_with_python_mermaid
)

# Create underscore aliases for test compatibility
_render_with_mermaid_cli = render_with_mermaid_cli
_render_with_puppeteer = render_with_puppeteer
_render_with_python_mermaid = render_with_python_mermaid

# Custom render_mermaid_diagram that uses mockable underscore functions
def render_mermaid_diagram(mermaid_code: str, output_format: str = "png", title=None):
    """Test-compatible version of render_mermaid_diagram that uses mockable functions."""
    import tempfile
    from pathlib import Path
    import base64
    
    # Create temporary files for rendering
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)
        mermaid_file = temp_path / "diagram.mmd"
        output_file = temp_path / f"diagram.{output_format}"
        
        # Write mermaid code to file
        mermaid_file.write_text(mermaid_code, encoding='utf-8')
        
        # Try rendering methods in order of preference using mockable functions
        
        # Method 1: mermaid-cli (most reliable)
        success, result = _render_with_mermaid_cli(mermaid_file, output_file)
        if success:
            return True, result, False
        
        # Method 2: Puppeteer with Node.js
        success, result = _render_with_puppeteer(mermaid_code, output_file)
        if success:
            return True, result, False
        
        # Method 3: Python-based SVG generation
        success, result = _render_with_python_mermaid(mermaid_code, output_file)
        if success:
            return True, result, False
        
        # Method 4: Client-side fallback
        encoded_code = base64.b64encode(mermaid_code.encode('utf-8')).decode('utf-8')
        fallback_data = f"data:text/plain;base64,{encoded_code}"
        return True, fallback_data, True

# Re-export the FastAPI app and legacy functions for backward compatibility
__all__ = [
    "app", 
    "env_manager",
    "conversation_manager",
    "file_service",
    "_load_env_defaults",
    "_session_summary_model", 
    "_conversation_state_response",
    "_render_with_mermaid_cli",
    "_render_with_puppeteer",
    "_render_with_python_mermaid",
    "_create_simple_flowchart_svg",
    "_detect_language",
    "_generate_filename",
    "render_with_mermaid_cli",
    "render_with_puppeteer",
    "render_with_python_mermaid",
    "render_mermaid_diagram",
    "subprocess"
]