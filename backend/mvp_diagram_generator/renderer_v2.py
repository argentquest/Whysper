"""
Mermaid CLI Renderer - Version 2 (Updated)

This version uses ONLY Mermaid CLI (mmdc) for all rendering.
No fallbacks, no Playwright, pure Mermaid CLI approach.

This is the most reliable and stable approach for Windows environments.
"""

import os
import subprocess
import tempfile
import base64
import asyncio
import platform
from pathlib import Path
from common.logger import get_logger

try:
    from playwright.async_api import async_playwright
except ImportError:
    async_playwright = None

logger = get_logger(__name__)

# Mermaid CLI executable name
MMDC_EXECUTABLE = "mmdc"
MMDC_TIMEOUT = 120  # seconds


def render_diagram(
    diagram_code: str,
    diagram_type: str,
    output_format: str = "svg",
    **kwargs
) -> str:
    """
    Render a diagram using Mermaid CLI (mmdc) only.

    This function acts as the main entry point for rendering diagrams.
    It validates the input, normalizes the diagram code, and delegates
    the actual rendering to the Mermaid CLI wrapper.

    Args:
        diagram_code (str): The diagram source code to render.
        diagram_type (str): Type of diagram ('mermaid', 'd2', or 'c4').
        output_format (str): Output format ('svg' or 'png'). Defaults to "svg".
        **kwargs: Additional arguments (ignored, for compatibility).

    Returns:
        str: Rendered diagram (SVG string or base64-encoded PNG).

    Raises:
        ValueError: If the output format or diagram type is unsupported.
        Exception: If rendering fails.
    """
    logger.info(f"Rendering {diagram_type} diagram to {output_format} using Mermaid CLI")

    # Validate output format
    if output_format not in ("svg", "png"):
        raise ValueError(f"Unsupported output format: {output_format}")

    # Normalize diagram code to Mermaid syntax
    if diagram_type in ("d2", "c4"):
        logger.info(f"Converting {diagram_type} to Mermaid syntax")
        diagram_code = convert_to_mermaid(diagram_code, diagram_type)
    elif diagram_type != "mermaid":
        raise ValueError(f"Unsupported diagram type: {diagram_type}")

    # Render using Mermaid CLI
    return render_with_mmdc(diagram_code, output_format)


def convert_to_mermaid(diagram_code: str, diagram_type: str) -> str:
    """
    Convert D2 or C4 diagrams to Mermaid syntax.

    For now, returns the code as-is. In production, this would:
    - Parse D2 syntax and convert to Mermaid flowchart
    - Parse C4 syntax and convert to Mermaid diagram

    Args:
        diagram_code (str): The diagram code to convert.
        diagram_type (str): The type of the original diagram ('d2' or 'c4').

    Returns:
        str: Mermaid-compatible diagram code.
    """
    logger.debug(f"Converting {diagram_type} to Mermaid (currently returns as-is)")
    # TODO: Implement actual D2->Mermaid and C4->Mermaid conversion
    # For now, assume input is already valid Mermaid or compatible
    return diagram_code


def render_with_mmdc(diagram_code: str, output_format: str) -> str:
    """
    Render using Mermaid CLI (mmdc) executable.

    Args:
        diagram_code (str): The Mermaid diagram code to render.
        output_format (str): The desired output format ('svg' or 'png').

    Returns:
        str: SVG string or base64-encoded PNG.

    Raises:
        Exception: If mmdc is not available or rendering fails.
    """

    # Check if mmdc is available
    if not is_mmdc_available():
        raise Exception(
            "Mermaid CLI (mmdc) is not available on this system. "
            "Please install with: npm install -g @mermaid-js/mermaid-cli"
        )

    # Create temporary files
    with tempfile.TemporaryDirectory() as tmpdir:
        input_file = Path(tmpdir) / "diagram.mmd"
        output_file = Path(tmpdir) / f"diagram.{output_format}"

        try:
            # Write diagram code to input file
            input_file.write_text(diagram_code, encoding="utf-8")
            logger.debug(f"Wrote diagram to: {input_file}")

            # Run mmdc command
            cmd = [
                MMDC_EXECUTABLE,
                "-i", str(input_file),
                "-o", str(output_file),
                "-f", output_format.upper(),  # mmdc expects SVG or PNG
            ]

            logger.debug(f"Running command: {' '.join(cmd)}")

            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=MMDC_TIMEOUT,
                shell=True  # Use shell on Windows to find .cmd files
            )

            if result.returncode != 0:
                error_msg = result.stderr or result.stdout or "Unknown error"
                raise Exception(f"mmdc rendering failed: {error_msg}")

            logger.debug(f"mmdc completed successfully")

            # Read output file
            if not output_file.exists():
                raise Exception(f"Output file not created: {output_file}")

            output_data = output_file.read_bytes()

            # Return based on format
            if output_format == "svg":
                # Return SVG as string
                return output_data.decode("utf-8")
            elif output_format == "png":
                # Return PNG as base64
                return base64.b64encode(output_data).decode("utf-8")

        except subprocess.TimeoutExpired:
            raise Exception(f"mmdc timed out after {MMDC_TIMEOUT} seconds")
        except Exception as e:
            logger.error(f"Error rendering diagram: {str(e)}")
            raise


def is_mmdc_available() -> bool:
    """
    Check if Mermaid CLI (mmdc) is available on the system.

    Returns:
        bool: True if mmdc is available, False otherwise.
    """
    try:
        result = subprocess.run(
            [MMDC_EXECUTABLE, "--version"],
            capture_output=True,
            text=True,
            timeout=5,
            shell=True  # Use shell on Windows
        )
        available = result.returncode == 0
        if available:
            logger.debug(f"mmdc is available: {result.stdout.strip()}")
        else:
            logger.info(f"mmdc check failed: {result.stderr}")
        return available
    except Exception as e:
        logger.info(f"Could not check mmdc availability: {str(e)}")
        return False


# DEPRECATED: Keeping old functions below for reference only
# These are no longer used - renderer now uses Mermaid CLI exclusively

async def render_with_playwright(
    diagram_code: str, diagram_type: str, output_format: str,
    frontend_url: str, encoded_code: str, timeout: int
) -> str:
    """DEPRECATED: Render using Playwright browser with Windows fixes."""
    
    browser = None
    try:
        # Initialize Playwright with Windows-specific settings
        playwright = await async_playwright().__aenter__()
        
        # Try different browser launch strategies for Windows
        launch_options = {
            'headless': True,
            'args': [
                '--no-sandbox',
                '--disable-dev-shm-usage',
                '--disable-gpu',
                '--disable-web-security',
                '--disable-features=VizDisplayCompositor'
            ]
        }
        
        # Windows-specific fixes
        if platform.system() == 'Windows':
            launch_options['args'].extend([
                '--disable-background-timer-throttling',
                '--disable-backgrounding-occluded-windows',
                '--disable-renderer-backgrounding'
            ])
        
        logger.debug("Launching Playwright browser...")
        browser = await playwright.chromium.launch(**launch_options)
        page = await browser.new_page()

        # Set viewport size for consistent rendering
        await page.set_viewport_size({"width": 1920, "height": 1080})

        # Listen to console messages for debugging
        def handle_console(msg):
            if msg.type != 'warning':  # Reduce log noise
                logger.debug(f"Browser console: {msg.text}")
        page.on("console", handle_console)

        # Try React dev server first
        render_url = f"{frontend_url}/render?type={diagram_type}&code={encoded_code}"
        logger.debug(f"Trying React dev server: {render_url[:100]}...")
        
        react_server_available = False
        try:
            response = await page.goto(render_url, timeout=5000)
            if response and response.ok:
                react_server_available = True
                logger.debug("React dev server loaded successfully")
        except Exception as e:
            logger.info(f"React dev server not available: {str(e)}")
        
        if not react_server_available:
            logger.info("Falling back to static HTML renderer...")
            
            # Fall back to static HTML
            temp_html_content = create_standalone_html(diagram_code, diagram_type)
            
            # Write to temporary file
            with tempfile.NamedTemporaryFile(mode='w', suffix='.html', delete=False, encoding='utf-8') as f:
                f.write(temp_html_content)
                temp_file_path = f.name
            
            logger.debug(f"Using static HTML fallback: {temp_file_path}")
            response = await page.goto(f"file://{temp_file_path}", timeout=timeout)
            
            if not response or not response.ok:
                raise Exception("Failed to load static HTML renderer")
            
            # Clean up temp file after use
            asyncio.create_task(cleanup_temp_file(temp_file_path))

        # Wait for rendering to complete
        logger.debug("Waiting for diagram to render...")
        try:
            await page.wait_for_selector("body.render-complete", timeout=timeout)
            logger.debug("Diagram rendered successfully")
        except Exception as e:
            # Check if there was a render error
            error_present = await page.locator("body.render-error").count()
            if error_present > 0:
                error_text = await page.locator("#error").inner_text()
                raise Exception(f"Diagram rendering failed: {error_text}")
            raise Exception(f"Timeout waiting for diagram render: {str(e)}")

        # Extract the rendered content
        result = ""

        if output_format == "svg":
            # Get the SVG content from the React component's div
            await page.wait_for_selector("svg", timeout=5000)
            svg_content = await page.locator("body > div > div").inner_html()

            if not svg_content or "<svg" not in svg_content:
                raise Exception("No SVG content found in rendered diagram")

            result = svg_content
            logger.debug(f"SVG content extracted: {len(svg_content)} characters")

        elif output_format == "png":
            # Take a screenshot of the diagram
            logger.debug("Taking PNG screenshot...")
            await page.wait_for_selector("svg", timeout=5000)
            diagram_element = page.locator("body > div > div")

            # Wait a moment for any animations to complete
            await page.wait_for_timeout(500)

            screenshot_bytes = await diagram_element.screenshot(type="png")
            result = base64.b64encode(screenshot_bytes).decode("utf-8")
            logger.debug(f"PNG screenshot taken: {len(screenshot_bytes)} bytes")

        else:
            raise ValueError(f"Unsupported output format: {output_format}")

        return result

    finally:
        if browser:
            await browser.close()


async def render_with_static_html(
    diagram_code: str, diagram_type: str, output_format: str,
    frontend_url: str, encoded_code: str, timeout: int
) -> str:
    """Fallback rendering using static HTML without Playwright."""
    
    logger.info("Using static HTML fallback (no Playwright)")
    
    # For SVG output, we can generate basic SVG directly
    if output_format == "svg":
        if diagram_type == "mermaid":
            return generate_basic_mermaid_svg(diagram_code)
        elif diagram_type == "d2":
            return generate_basic_d2_svg(diagram_code)
        elif diagram_type == "c4":
            return generate_basic_c4_svg(diagram_code)
    
    # For PNG or complex cases, we need Playwright
    raise Exception(f"Static HTML fallback not supported for {output_format} output")


async def render_with_python_svg(
    diagram_code: str, diagram_type: str, output_format: str,
    frontend_url: str, encoded_code: str, timeout: int
) -> str:
    """Pure Python SVG generation fallback."""
    
    logger.info("Using pure Python SVG generation")
    
    if output_format != "svg":
        raise Exception("Python SVG generation only supports SVG output")
    
    # Generate basic SVG based on diagram type
    if diagram_type == "mermaid":
        return generate_basic_mermaid_svg(diagram_code)
    else:
        raise Exception(f"Python SVG generation not implemented for {diagram_type}")


def generate_basic_mermaid_svg(diagram_code: str) -> str:
    """Generate a basic SVG from Mermaid-like syntax."""
    
    lines = diagram_code.strip().split('\n')
    nodes = []
    connections = []
    
    for line in lines:
        line = line.strip()
        if '-->' in line:
            parts = line.split('-->')
            if len(parts) >= 2:
                from_node = parts[0].strip()
                to_part = parts[1].strip()
                to_node = to_part.split('[')[0].strip() if '[' in to_part else to_part
                nodes.extend([from_node, to_node])
                connections.append((from_node, to_node))
    
    # Create basic SVG
    width = max(400, len(nodes) * 150)
    height = max(300, len(connections) * 100 + 100)
    
    svg = f'''<svg width="{width}" height="{height}" xmlns="http://www.w3.org/2000/svg">
    <defs>
        <marker id="arrowhead" markerWidth="10" markerHeight="7" 
         refX="9" refY="3.5" orient="auto">
            <polygon points="0 0, 10 3.5, 0 7" fill="#333" />
        </marker>
    </defs>
    <style>
        .node {{ fill: #e1f5fe; stroke: #01579b; stroke-width: 2; }}
        .node-text {{ font-family: Arial; font-size: 14px; text-anchor: middle; }}
        .edge {{ stroke: #333; stroke-width: 2; fill: none; marker-end: url(#arrowhead); }}
    </style>'''
    
    # Add nodes
    for i, node in enumerate(set(nodes)):
        x = (i + 1) * (width / (len(set(nodes)) + 1))
        y = height // 2
        svg += f'''
    <rect class="node" x="{x-50}" y="{y-25}" width="100" height="50" rx="5"/>
    <text class="node-text" x="{x}" y="{y+5}">{node}</text>'''
    
    # Add connections
    for i, (from_node, to_node) in enumerate(connections):
        from_idx = list(set(nodes)).index(from_node)
        to_idx = list(set(nodes)).index(to_node)
        x1 = (from_idx + 1) * (width / (len(set(nodes)) + 1))
        x2 = (to_idx + 1) * (width / (len(set(nodes)) + 1))
        y = height // 2
        svg += f'''
    <line class="edge" x1="{x1}" y1="{y+25}" x2="{x2-50}" y2="{y-25}"/>'''
    
    svg += '\n</svg>'
    return svg


def generate_basic_d2_svg(diagram_code: str) -> str:
    """Generate a basic SVG from D2-like syntax."""
    
    lines = diagram_code.strip().split('\n')
    connections = []
    
    for line in lines:
        if '->' in line:
            parts = line.split('->')
            if len(parts) >= 2:
                from_node = parts[0].strip()
                to_node = parts[1].strip()
                connections.append((from_node, to_node))
    
    # Create basic SVG similar to Mermaid
    width = max(400, len(connections) * 200)
    height = 200
    
    svg = f'''<svg width="{width}" height="{height}" xmlns="http://www.w3.org/2000/svg">
    <defs>
        <marker id="arrowhead" markerWidth="10" markerHeight="7" 
         refX="9" refY="3.5" orient="auto">
            <polygon points="0 0, 10 3.5, 0 7" fill="#333" />
        </marker>
    </defs>
    <style>
        .node {{ fill: #f3e5f5; stroke: #4a148c; stroke-width: 2; }}
        .node-text {{ font-family: Arial; font-size: 14px; text-anchor: middle; }}
        .edge {{ stroke: #333; stroke-width: 2; fill: none; marker-end: url(#arrowhead); }}
    </style>'''
    
    # Add nodes and connections
    for i, (from_node, to_node) in enumerate(connections):
        x1 = (i + 1) * 150
        x2 = (i + 2) * 150
        y = height // 2
        
        # From node
        svg += f'''
    <rect class="node" x="{x1-50}" y="{y-25}" width="100" height="50" rx="5"/>
    <text class="node-text" x="{x1}" y="{y+5}">{from_node}</text>'''
        
        # To node
        svg += f'''
    <rect class="node" x="{x2-50}" y="{y-25}" width="100" height="50" rx="5"/>
    <text class="node-text" x="{x2}" y="{y+5}">{to_node}</text>'''
        
        # Connection
        svg += f'''
    <line class="edge" x1="{x1+50}" y1="{y}" x2="{x2-50}" y2="{y}"/>'''
    
    svg += '\n</svg>'
    return svg


def generate_basic_c4_svg(diagram_code: str) -> str:
    """Generate a basic SVG from C4-like syntax."""
    
    # Simple C4 to basic SVG conversion
    lines = diagram_code.strip().split('\n')
    connections = []
    
    for line in lines:
        if 'Rel(' in line:
            # Extract relationship from C4 syntax
            import re
            match = re.search(r'Rel\([^,]+,\s*([^,]+),', line)
            if match:
                connections.append(("System", match.group(1)))
    
    # Generate basic SVG
    width = 600
    height = 300
    
    svg = f'''<svg width="{width}" height="{height}" xmlns="http://www.w3.org/2000/svg">
    <defs>
        <marker id="arrowhead" markerWidth="10" markerHeight="7" 
         refX="9" refY="3.5" orient="auto">
            <polygon points="0 0, 10 3.5, 0 7" fill="#333" />
        </marker>
    </defs>
    <style>
        .system {{ fill: #fff3e0; stroke: #e65100; stroke-width: 2; }}
        .person {{ fill: #e8f5e8; stroke: #2e7d32; stroke-width: 2; }}
        .text {{ font-family: Arial; font-size: 14px; text-anchor: middle; }}
        .edge {{ stroke: #333; stroke-width: 2; fill: none; marker-end: url(#arrowhead); }}
    </style>'''
    
    # Add basic system
    svg += f'''
    <rect class="system" x="250" y="100" width="100" height="60" rx="5"/>
    <text class="text" x="300" y="135">System</text>'''
    
    # Add connections
    for i, (from_node, to_node) in enumerate(connections):
        svg += f'''
    <line class="edge" x1="100" y1="130" x2="250" y2="130"/>
    <text class="text" x="175" y="120">{to_node}</text>'''
    
    svg += '\n</svg>'
    return svg


def create_standalone_html(diagram_code: str, diagram_type: str) -> str:
    """Create a standalone HTML file with the diagram code embedded."""
    
    # Create a complete standalone HTML that doesn't rely on URL parameters
    html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Diagram Renderer</title>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}

        body {{
            font-family: Arial, sans-serif;
            background: white;
            display: flex;
            justify-content: center;
            align-items: center;
            min-height: 100vh;
            padding: 20px;
        }}

        #diagram-container {{
            max-width: 100%;
            max-height: 100vh;
            overflow: auto;
        }}

        #loading {{
            text-align: center;
            color: #666;
            font-size: 18px;
        }}

        #error {{
            padding: 20px;
            background: #fff2f0;
            border: 1px solid #ffccc7;
            border-radius: 4px;
            color: #cf1322;
            max-width: 800px;
        }}

        #error h3 {{
            margin-bottom: 10px;
        }}

        #error pre {{
            background: #f5f5f5;
            padding: 10px;
            border-radius: 4px;
            overflow-x: auto;
            font-size: 12px;
            margin-top: 10px;
        }}

        /* Ensure SVG is visible */
        svg {{
            max-width: 100%;
            height: auto;
        }}

        /* Mark as ready for Playwright to detect */
        body.render-complete #diagram-container {{
            border: 1px solid transparent;
        }}
    </style>
</head>
<body>
    <div id="loading">Loading diagram renderer...</div>
    <div id="diagram-container" style="display: none;"></div>
    <div id="error" style="display: none;"></div>

    <!-- Mermaid library -->
    <script type="module">
        import mermaid from 'https://cdn.jsdelivr.net/npm/mermaid@10/dist/mermaid.esm.min.mjs';

        // Initialize Mermaid
        mermaid.initialize({{
            startOnLoad: false,
            theme: 'default',
            securityLevel: 'loose',
            fontFamily: 'Arial, sans-serif',
            flowchart: {{
                useMaxWidth: true,
                htmlLabels: true,
                curve: 'basis',
            }},
        }});

        // Make mermaid available globally
        window.mermaidLib = mermaid;
        window.mermaidLoaded = true;

        console.log('✅ Mermaid library loaded');
        checkAndRender();
    </script>

    <!-- D2 library -->
    <script type="module">
        // Import D2 from CDN
        import {{ D2 }} from 'https://cdn.jsdelivr.net/npm/@terrastruct/d2@latest/dist/index.js';

        // Make D2 available globally
        window.D2Lib = D2;
        window.d2Loaded = true;

        console.log('✅ D2 library loaded');
        checkAndRender();
    </script>

    <!-- Main rendering logic -->
    <script>
        /**
         * C4 to D2 converter (simplified version from c4ToD2.ts)
         */
        function convertC4ToD2(c4Code) {{
            if (!c4Code) return '';

            const lines = c4Code.trim().split('\\n');
            const d2Lines = [];

            // Add direction for better layout
            d2Lines.push('direction: down');
            d2Lines.push('');

            // Process line by line
            for (const line of lines) {{
                const trimmedLine = line.trim();

                // Skip empty lines, comments, and C4 declaration
                if (!trimmedLine || trimmedLine.startsWith('#') || /^C4(Context|Container|Component)/i.test(trimmedLine)) {{
                    continue;
                }}

                // Parse entity definitions: Type(id, "label", "description")
                const entityMatch = trimmedLine.match(/^(\\w+)\\s*\\(\\s*(\\w+)\\s*,\\s*"([^"]+)"(?:\\s*,\\s*"([^"]*)")?\\s*\\)/);
                if (entityMatch) {{
                    const [, type, id, label] = entityMatch;
                    const shape = getC4Shape(type);
                    d2Lines.push(`${{id}}: {{`);
                    d2Lines.push(`  label: "${{label}}"`);
                    d2Lines.push(`  shape: ${{shape}}`);
                    d2Lines.push('}}');
                    d2Lines.push('');
                    continue;
                }}

                // Parse relationships: Rel(from, to, "label")
                const relMatch = trimmedLine.match(/^Rel(?:_[A-Z]+)?\\s*\\(\\s*(\\w+)\\s*,\\s*(\\w+)\\s*,\\s*"([^"]+)"\\s*\\)/);
                if (relMatch) {{
                    const [, from, to, label] = relMatch;
                    d2Lines.push(`${{from}} -> ${{to}}: "${{label}}"`);
                    continue;
                }}
            }}

            return d2Lines.join('\\n');
        }}

        /**
         * Map C4 entity types to D2 shapes
         */
        function getC4Shape(type) {{
            const shapeMap = {{
                'Person': 'person',
                'Person_Ext': 'person',
                'System': 'rectangle',
                'System_Ext': 'rectangle',
                'SystemDb': 'cylinder',
                'Container': 'rectangle',
                'ContainerDb': 'cylinder',
                'Component': 'rectangle',
                'ComponentDb': 'cylinder',
            }};
            return shapeMap[type] || 'rectangle';
        }}

        /**
         * Render Mermaid diagram
         */
        async function renderMermaid(code) {{
            console.log('🎨 Rendering Mermaid diagram...');

            if (!window.mermaidLib) {{
                throw new Error('Mermaid library not loaded');
            }}

            try {{
                // Validate syntax first
                await window.mermaidLib.parse(code);
                console.log('✅ Mermaid syntax validated');

                // Generate unique ID
                const id = `mermaid-${{Date.now()}}`;

                // Render the diagram
                const {{ svg }} = await window.mermaidLib.render(id, code);
                console.log('✅ Mermaid SVG generated');

                return svg;
            }} catch (error) {{
                console.error('❌ Mermaid rendering error:', error);
                throw error;
            }}
        }}

        /**
         * Render D2 diagram
         */
        async function renderD2(code) {{
            console.log('🎯 Rendering D2 diagram...');

            if (!window.D2Lib) {{
                throw new Error('D2 library not loaded');
            }}

            try {{
                // Create D2 instance
                const d2 = new window.D2Lib();
                console.log('✅ D2 instance created');

                // Compile D2 code
                const result = await d2.compile(code, {{
                    options: {{
                        layout: 'dagre',
                        sketch: false,
                    }}
                }});
                console.log('✅ D2 code compiled');

                // Render to SVG
                const svg = await d2.render(result.diagram, result.renderOptions);
                console.log('✅ D2 SVG generated');

                return svg;
            }} catch (error) {{
                console.error('❌ D2 rendering error:', error);
                throw error;
            }}
        }}

        /**
         * Main rendering function
         */
        async function renderDiagram() {{
            const loadingEl = document.getElementById('loading');
            const containerEl = document.getElementById('diagram-container');
            const errorEl = document.getElementById('error');

            try {{
                // Use embedded diagram code and type
                const diagramCode = `{diagram_code.replace('`', '\\`')}";
                const diagramType = `{diagram_type}";
                
                console.log('📋 Render parameters:', {{ type: diagramType, codeLength: diagramCode.length }});

                if (!diagramCode) {{
                    throw new Error('No diagram code provided');
                }}

                let svg;

                // Handle different diagram types
                if (diagramType === 'mermaid') {{
                    svg = await renderMermaid(diagramCode);
                }} else if (diagramType === 'd2') {{
                    svg = await renderD2(diagramCode);
                }} else if (diagramType === 'c4') {{
                    console.log('🏗️ Converting C4 to D2...');
                    const d2Code = convertC4ToD2(diagramCode);
                    console.log('✅ C4 converted to D2');
                    svg = await renderD2(d2Code);
                }} else {{
                    throw new Error(`Unknown diagram type: ${{diagramType}}`);
                }}

                // Insert SVG into container
                containerEl.innerHTML = svg;
                containerEl.style.display = 'flex';
                loadingEl.style.display = 'none';

                // Mark as complete for Playwright
                document.body.classList.add('render-complete');

                console.log('✅ Diagram rendered successfully');
            }} catch (error) {{
                console.error('❌ Rendering failed:', error);

                loadingEl.style.display = 'none';
                errorEl.style.display = 'block';
                errorEl.innerHTML = `
                    <h3>Rendering Error</h3>
                    <p>${{error.message}}</p>
                    <pre>${{error.stack || ''}}</pre>
                `;

                // Mark as error for Playwright
                document.body.classList.add('render-error');
            }}
        }}

        /**
         * Check if all libraries are loaded and start rendering
         */
        function checkAndRender() {{
            if (window.mermaidLoaded && window.d2Loaded) {{
                console.log('✅ All libraries loaded, starting render...');
                renderDiagram();
            }}
        }}

        // Auto-start if libraries are already loaded
        if (document.readyState === 'loading') {{
            document.addEventListener('DOMContentLoaded', checkAndRender);
        }} else {{
            checkAndRender();
        }}
    </script>
</body>
</html>"""
    
    return html_content


async def cleanup_temp_file(file_path: str):
    """Clean up temporary file after a short delay."""
    await asyncio.sleep(1)  # Wait a bit to ensure browser is done with it
    try:
        os.unlink(file_path)
        logger.debug(f"Cleaned up temp file: {file_path}")
    except Exception as e:
        logger.info(f"Failed to clean up temp file {file_path}: {e}")


async def test_render():
    """Test function to verify the renderer works"""
    # Test Mermaid
    mermaid_code = """
    flowchart TD
        A[Start] --> B{Is it working?}
        B -->|Yes| C[Great!]
        B -->|No| D[Debug]
        D --> A
    """

    print("Testing Mermaid rendering...")
    svg = await render_diagram(mermaid_code, "mermaid", "svg")
    print(f"✅ Mermaid SVG length: {len(svg)}")

    # Test D2
    d2_code = """
    frontend -> backend: API Call
    backend -> database: Query
    database -> backend: Results
    backend -> frontend: Response
    """

    print("Testing D2 rendering...")
    svg = await render_diagram(d2_code, "d2", "svg")
    print(f"✅ D2 SVG length: {len(svg)}")

    # Test C4
    c4_code = """
    C4Context
    Person(user, "User", "A user of the system")
    System(app, "Application", "The main application")
    Rel(user, app, "Uses")
    """

    print("Testing C4 rendering...")
    svg = await render_diagram(c4_code, "c4", "svg")
    print(f"✅ C4 SVG length: {len(svg)}")

    print("All tests passed! ✅")


if __name__ == "__main__":
    # Run test
    asyncio.run(test_render())
