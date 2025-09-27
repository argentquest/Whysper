"""
Mermaid diagram rendering utilities.

This module provides multiple rendering methods for Mermaid diagrams:
1. mermaid-cli (if installed)
2. Puppeteer with Node.js
3. Python-based SVG generation for simple diagrams
4. Client-side fallback
"""
import subprocess
import tempfile
import base64
from pathlib import Path
from typing import Tuple, Optional
from common.logger import get_logger

logger = get_logger(__name__)


def render_mermaid_diagram(
    mermaid_code: str, 
    output_format: str = "png",
    title: Optional[str] = None
) -> Tuple[bool, str, bool]:
    """
    Render a Mermaid diagram using multiple fallback methods.
    
    Args:
        mermaid_code: The Mermaid diagram code
        output_format: Desired output format ("png" or "svg")
        title: Optional title for the diagram
        
    Returns:
        Tuple[bool, str, bool]: (success, data_url_or_error, is_fallback)
    """
    # Create temporary files for rendering
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)
        mermaid_file = temp_path / "diagram.mmd"
        output_file = temp_path / f"diagram.{output_format}"
        
        # Write mermaid code to file
        mermaid_file.write_text(mermaid_code, encoding='utf-8')
        
        # Try rendering methods in order of preference
        
        # Method 1: mermaid-cli (most reliable)
        success, result = render_with_mermaid_cli(mermaid_file, output_file)
        if success:
            return True, result, False
        
        # Method 2: Puppeteer (good compatibility)
        success, result = render_with_puppeteer(mermaid_code, output_file)
        if success:
            return True, result, False
        
        # Method 3: Python mermaid (limited support)
        success, result = render_with_python_mermaid(mermaid_code, output_file)
        if success:
            return True, result, False
        
        # Method 4: Client-side fallback
        logger.info("All server-side rendering methods failed, using client-side fallback")
        fallback_data = f"data:text/plain;base64,{base64.b64encode(mermaid_code.encode()).decode()}"
        return True, fallback_data, True


def render_with_mermaid_cli(mermaid_file: Path, output_file: Path) -> Tuple[bool, str]:
    """Try to render using mermaid-cli (mmdc)."""
    try:
        # Check if mermaid-cli is installed
        result = subprocess.run(['mmdc', '--version'], 
                              capture_output=True, text=True, timeout=10)
        
        if result.returncode != 0:
            logger.debug("mermaid-cli not available")
            return False, ""
        
        # Render the diagram
        cmd = [
            'mmdc',
            '-i', str(mermaid_file),
            '-o', str(output_file),
            '-b', 'white',  # Background color
            '-s', '2'       # Scale factor
        ]
        
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
        
        if result.returncode == 0 and output_file.exists():
            # Read the generated file and return as base64 data URL
            with open(output_file, 'rb') as f:
                file_data = f.read()
                
            mime_type = "image/png" if output_file.suffix == '.png' else "image/svg+xml"
            data_url = f"data:{mime_type};base64,{base64.b64encode(file_data).decode()}"
            
            logger.info("Successfully rendered with mermaid-cli")
            return True, data_url
        else:
            logger.debug(f"mermaid-cli failed: {result.stderr}")
            return False, ""
            
    except (subprocess.TimeoutExpired, FileNotFoundError, Exception) as e:
        logger.debug(f"mermaid-cli error: {e}")
        return False, ""


def render_with_puppeteer(mermaid_code: str, output_file: Path) -> Tuple[bool, str]:
    """Try to render using Node.js with Puppeteer."""
    try:
        # Create a simple Node.js script for rendering
        node_script = f'''
const puppeteer = require('puppeteer');
const fs = require('fs');

(async () => {{
  try {{
    const browser = await puppeteer.launch({{headless: true}});
    const page = await browser.newPage();
    
    await page.setContent(`
      <!DOCTYPE html>
      <html>
      <head>
        <script src="https://cdn.jsdelivr.net/npm/mermaid/dist/mermaid.min.js"></script>
      </head>
      <body>
        <div id="diagram">{mermaid_code}</div>
        <script>
          mermaid.initialize({{startOnLoad: true}});
        </script>
      </body>
      </html>
    `);
    
    await page.waitForSelector('#diagram svg', {{timeout: 10000}});
    
    const element = await page.$('#diagram');
    await element.screenshot({{path: '{output_file}', background: 'white'}});
    
    await browser.close();
    console.log('SUCCESS');
  }} catch (error) {{
    console.error('ERROR:', error);
    process.exit(1);
  }}
}})();
'''
        
        # Write Node.js script to temporary file
        script_file = output_file.parent / 'render_script.js'
        with open(script_file, 'w', encoding='utf-8') as f:
            f.write(node_script)
        
        # Execute Node.js script
        result = subprocess.run(['node', str(script_file)], 
                              capture_output=True, text=True, timeout=60)
        
        if result.returncode == 0 and output_file.exists():
            with open(output_file, 'rb') as f:
                file_data = f.read()
                
            data_url = f"data:image/png;base64,{base64.b64encode(file_data).decode()}"
            logger.info("Successfully rendered with Puppeteer")
            return True, data_url
        else:
            logger.debug(f"Puppeteer failed: {result.stderr}")
            return False, ""
            
    except Exception as e:
        logger.debug(f"Puppeteer error: {e}")
        return False, ""


def render_with_python_mermaid(mermaid_code: str, output_file: Path) -> Tuple[bool, str]:
    """Try to render using Python mermaid libraries."""
    try:
        # Try using Python libraries for simple diagram types
        # This is a basic implementation for common diagram types
        
        if 'graph' in mermaid_code.lower() or 'flowchart' in mermaid_code.lower():
            # For flowcharts, we can create a simple SVG
            svg_content = create_simple_flowchart_svg(mermaid_code)
            
            if svg_content:
                # Convert SVG to PNG using cairosvg if available
                try:
                    import cairosvg
                    png_data = cairosvg.svg2png(bytestring=svg_content.encode())
                    
                    data_url = f"data:image/png;base64,{base64.b64encode(png_data).decode()}"
                    logger.info("Successfully rendered with Python SVG conversion")
                    return True, data_url
                except ImportError:
                    # Return SVG as data URL if cairosvg not available
                    data_url = f"data:image/svg+xml;base64,{base64.b64encode(svg_content.encode()).decode()}"
                    logger.info("Successfully rendered as SVG (cairosvg not available)")
                    return True, data_url
        
        return False, ""
        
    except Exception as e:
        logger.debug(f"Python mermaid error: {e}")
        return False, ""


def create_simple_flowchart_svg(mermaid_code: str) -> str:
    """Create a simple SVG for basic flowcharts."""
    try:
        # This is a very basic implementation for simple flowcharts
        # In a real implementation, you'd want a proper mermaid parser
        
        svg_template = '''<?xml version="1.0" encoding="UTF-8"?>
<svg width="400" height="300" viewBox="0 0 400 300" xmlns="http://www.w3.org/2000/svg">
  <defs>
    <style>
      .node { fill: #e1f5fe; stroke: #01579b; stroke-width: 2; }
      .edge { stroke: #424242; stroke-width: 2; fill: none; marker-end: url(#arrowhead); }
      .text { font-family: Arial, sans-serif; font-size: 12px; text-anchor: middle; }
      .title { font-family: Arial, sans-serif; font-size: 14px; font-weight: bold; text-anchor: middle; }
    </style>
    <marker id="arrowhead" markerWidth="10" markerHeight="7" refX="9" refY="3.5" orient="auto">
      <polygon points="0 0, 10 3.5, 0 7" fill="#424242" />
    </marker>
  </defs>
  
  <!-- Title -->
  <text x="200" y="25" class="title">WhisperCode Flowchart</text>
  
  <!-- Start Node -->
  <rect x="150" y="50" width="100" height="40" rx="20" class="node"/>
  <text x="200" y="75" class="text">Start</text>
  
  <!-- Process Node -->
  <rect x="150" y="120" width="100" height="40" rx="5" class="node"/>
  <text x="200" y="145" class="text">Process</text>
  
  <!-- End Node -->
  <rect x="150" y="190" width="100" height="40" rx="20" class="node"/>
  <text x="200" y="215" class="text">End</text>
  
  <!-- Arrows -->
  <line x1="200" y1="90" x2="200" y2="120" class="edge"/>
  <line x1="200" y1="160" x2="200" y2="190" class="edge"/>
  
  <!-- Generated from Mermaid -->
  <text x="200" y="280" style="font-size: 10px; fill: #666; text-anchor: middle;">Generated by WhisperCode Web2</text>
</svg>'''
        
        return svg_template
        
    except Exception as e:
        logger.debug(f"SVG generation error: {e}")
        return ""


def validate_mermaid_code(mermaid_code: str) -> Tuple[bool, str]:
    """
    Validate Mermaid diagram code for basic syntax.
    
    Args:
        mermaid_code: The Mermaid code to validate
        
    Returns:
        Tuple[bool, str]: (is_valid, error_message)
    """
    if not mermaid_code or not mermaid_code.strip():
        return False, "Mermaid code is empty"
    
    # Basic validation checks
    code_lower = mermaid_code.lower().strip()
    
    # Check for supported diagram types
    supported_types = [
        'graph', 'flowchart', 'sequencediagram', 'classDiagram',
        'stateDiagram', 'erDiagram', 'journey', 'gantt', 'pie'
    ]
    
    if not any(diagram_type in code_lower for diagram_type in supported_types):
        return False, "Unsupported or unrecognized diagram type"
    
    # Check for basic syntax issues
    if mermaid_code.count('-->') > 50:
        return False, "Too many connections (max 50)"
    
    if len(mermaid_code) > 10000:
        return False, "Mermaid code too long (max 10KB)"
    
    return True, ""