import asyncio
import sys
import os

# Add the current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from mvp_diagram_generator.renderer_v2 import render_diagram

async def debug_renderer():
    """Debug the renderer to see what's happening"""
    try:
        print("Testing renderer with simple Mermaid diagram...")
        result = await render_diagram(
            diagram_code="flowchart TD\n    A[Start] --> B[Process]\n    B --> C[End]",
            diagram_type="mermaid",
            output_format="svg"
        )
        print(f"✅ Success! SVG length: {len(result)}")
        print(f"SVG preview: {result[:200]}...")
        return True
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    asyncio.run(debug_renderer())