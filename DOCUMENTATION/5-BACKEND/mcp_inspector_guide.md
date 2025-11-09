# MCP Inspector Testing Guide

This guide shows how to test the Whysper MCP server using MCP Inspector.

## Prerequisites

1. Install MCP Inspector:
```bash
npm install -g @modelcontextprotocol/inspector
```

2. Ensure your MCP server is running:
```bash
cd backend
py main.py
```

## Method 1: Direct MCP Server Testing

### Step 1: Create MCP Inspector Configuration

Create a file named `mcp-inspector-config.json`:

```json
{
  "mcpServers": {
    "whysper-diagram-generator": {
      "command": "python",
      "args": [
        "-m",
        "mcp_server.fastmcp_server"
      ],
      "cwd": "C:\\Code2025\\Whysper\\backend"
    }
  }
}
```

### Step 2: Run MCP Inspector

```bash
mcp-inspector mcp-inspector-config.json
```

This will start MCP Inspector and connect to your MCP server directly.

## Method 2: HTTP MCP Server Testing

Since your MCP server is running as an HTTP server, we need to use a different approach.

### Step 1: Install MCP HTTP Client

```bash
pip install mcp-client
```

### Step 2: Create Test Script

Create `test_mcp_with_client.py`:

```python
import asyncio
import json
from mcp.client import Client
from mcp.client.http import HTTPClientTransport

async def test_mcp_server():
    """Test the MCP server using HTTP transport"""
    
    # Connect to the MCP server via HTTP
    transport = HTTPClientTransport("http://localhost:8003/mcp")
    client = Client(transport)
    
    try:
        # Initialize connection
        await client.initialize()
        print("✅ Connected to MCP server")
        
        # List available tools
        tools = await client.list_tools()
        print(f"✅ Available tools: {[tool.name for tool in tools.tools]}")
        
        # Test generate_diagram tool
        if any(tool.name == "generate_diagram" for tool in tools.tools):
            print("\n🎨 Testing generate_diagram tool...")
            result = await client.call_tool(
                "generate_diagram", 
                {
                    "prompt": "Simple flowchart with start and end",
                    "diagram_type": "mermaid"
                }
            )
            print("✅ generate_diagram result:")
            print(json.dumps(result.content[0].text, indent=2))
        
        # Test render_diagram tool
        if any(tool.name == "render_diagram" for tool in tools.tools):
            print("\n🖼️ Testing render_diagram tool...")
            result = await client.call_tool(
                "render_diagram", 
                {
                    "code": "flowchart TD\n    A[Start] --> B[Process]\n    B --> C[End]",
                    "diagram_type": "mermaid",
                    "output_format": "svg"
                }
            )
            print("✅ render_diagram result:")
            render_data = json.loads(result.content[0].text)
            if "image_data" in render_data:
                print(f"Generated SVG ({len(render_data['image_data'])} characters)")
            else:
                print(json.dumps(result.content[0].text, indent=2))
        
        # Test generate_and_render tool
        if any(tool.name == "generate_and_render" for tool in tools.tools):
            print("\n🎯 Testing generate_and_render tool...")
            result = await client.call_tool(
                "generate_and_render", 
                {
                    "prompt": "User login process with authentication",
                    "diagram_type": "mermaid",
                    "output_format": "svg"
                }
            )
            print("✅ generate_and_render result:")
            render_data = json.loads(result.content[0].text)
            if "image_data" in render_data:
                print(f"Generated SVG ({len(render_data['image_data'])} characters)")
                print(f"AI Generated: {render_data.get('ai_generated', False)}")
            else:
                print(json.dumps(result.content[0].text, indent=2))
        
        print("\n🎉 All MCP tests completed successfully!")
        
    except Exception as e:
        print(f"❌ Error testing MCP server: {str(e)}")
        import traceback
        traceback.print_exc()
    
    finally:
        await client.close()

if __name__ == "__main__":
    asyncio.run(test_mcp_server())
```

### Step 3: Run the Test

```bash
cd backend
py test_mcp_with_client.py
```

## Method 3: Manual HTTP Testing

You can also test the MCP endpoints directly using curl or any HTTP client:

### List Tools
```bash
curl -X GET "http://localhost:8003/mcp/tools"
```

### Call Tool
```bash
curl -X POST "http://localhost:8003/mcp/call_tool" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "generate_diagram",
    "arguments": {
      "prompt": "Simple flowchart",
      "diagram_type": "mermaid"
    }
  }'
```

## Expected Results

When testing, you should see:

1. **Connection Success**: "✅ Connected to MCP server"
2. **Tools Listed**: Three tools should be available:
   - generate_diagram
   - render_diagram
   - generate_and_render
3. **Tool Execution**: Each tool should return valid results
4. **AI Integration**: The generate_diagram tool should show "ai_generated": true

## Troubleshooting

### Connection Issues
- Ensure the backend server is running on port 8003
- Check that the MCP endpoints are accessible at `/mcp/*`

### Tool Errors
- Verify the AI integration is working (check API key)
- Ensure the diagram rendering fallbacks are functioning

### MCP Inspector Issues
- Make sure you have the latest version of MCP Inspector
- Check the configuration file paths are correct

## Advanced Testing

For more comprehensive testing, you can:

1. Test different diagram types (mermaid, d2, c4)
2. Test both SVG and PNG output formats
3. Test error handling with invalid inputs
4. Test WebSocket connection at `/mcp/ws`

This will give you confidence that the MCP server is working correctly with real MCP clients.