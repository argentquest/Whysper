"""
Routers package for FastAPI application.
"""== MCP Endpoint Test Suite ===
Testing FastMCP endpoints at http://localhost:8003/mcp

=== Testing server health ===
✓ Server is running at http://localhost:8003

=== Testing list_tools endpoint ===
✓ Status: 200
✓ Tools found: 3
  - generate_diagram: Generate diagram code from a natural language prompt.
  - render_diagram: Render diagram code to SVG or PNG format.
  - generate_and_render: Generate and render a diagram in one step.

=== Testing generate_diagram endpoint ===
✓ Status: 200
✓ Response content type: text
✓ Diagram type: mermaid
✓ Diagram code generated (length: 85)
  Diagram code preview:
    flowchart TD
    A[Start] --> B[Simple flowchart with start and end]
    B --> C[End]...

=== Testing render_diagram endpoint ===
✓ Status: 200
✓ Response content type: text
✗ Error in response:

=== Testing generate_and_render endpoint ===
✓ Status: 200
✓ Response content type: text
✗ Error in response: Diagram rendering failed:

=== Testing call_tool endpoint ===
✓ Status: 200
✓ Is error: False
✓ Response content type: text
✓ Diagram type: d2
✓ Diagram code generated (length: 40)

=== Test Results Summary ===
Passed: 3/5
✗ Some tests failed. Check the output above for details.