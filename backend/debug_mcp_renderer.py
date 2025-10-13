import asyncio
import sys
import os
import json

# Add the current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from mvp_diagram_generator.renderer_v2 import render_diagram

async def debug_mcp_renderer():
    """Debug the renderer exactly as the MCP server calls it"""
    try:
        print("Testing render_diagram exactly as MCP server calls it...")
        
        # Test with the exact same parameters as the MCP test
        result = await render_diagram(
            diagram_code="flowchart TD\n    A[Start] --> B[Process]\n    B --> C[End]",
            diagram_type="mermaid",
            output_format="svg"
        )
        
        print(f"✅ Success! SVG length: {len(result)}")
        
        # Parse as JSON to match MCP server behavior
        response_data = {
            "image_data": result,
            "output_format": "svg",
            "diagram_type": "mermaid"
        }
        
        json_result = json.dumps(response_data, indent=2)
        print(f"✅ JSON result length: {len(json_result)}")
        print(f"JSON preview: {json_result[:200]}...")
        
        # Test the exact MCP server response format
        mcp_response = {
            "content": [{"type": "text", "text": json_result}],
            "isError": False
        }
        
        print(f"✅ MCP response format valid")
        return True
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    asyncio.run(debug_mcp_renderer())