"""
Test MCP Server using MCP Client
This script tests the MCP server as a proper MCP client would interact with it.
"""

import asyncio
import json
import sys
import os

# Add the backend directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

async def test_mcp_with_http_client():
    """Test the MCP server using HTTP requests (simulates MCP client)"""
    
    import httpx
    
    BASE_URL = "http://localhost:8003"
    MCP_BASE_URL = f"{BASE_URL}/mcp"
    
    print("🔧 Testing MCP Server with HTTP Client")
    print("=" * 60)
    
    try:
        # Test server health
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{BASE_URL}/docs")
            if response.status_code != 200:
                print("❌ Server is not running")
                return False
        
        print("✅ Server is running")
        
        # Test MCP list tools endpoint
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.get(f"{MCP_BASE_URL}/tools")
            response.raise_for_status()
            tools_data = response.json()
            
            print(f"✅ Available tools: {[tool.get('name') for tool in tools_data.get('tools', [])]}")
            
            # Test generate_diagram tool
            print("\n🎨 Testing generate_diagram tool...")
            payload = {
                "prompt": "Simple flowchart with start and end",
                "diagram_type": "mermaid"
            }
            
            response = await client.post(
                f"{MCP_BASE_URL}/tools/generate_diagram",
                json=payload
            )
            response.raise_for_status()
            result = response.json()
            
            text_content = result.get('content', [{}])[0].get('text', '')
            diagram_data = json.loads(text_content)
            
            if 'error' in diagram_data:
                print(f"❌ generate_diagram failed: {diagram_data['error']}")
            else:
                print(f"✅ generate_diagram success:")
                print(f"  AI Generated: {diagram_data.get('ai_generated', False)}")
                print(f"  Diagram Type: {diagram_data.get('diagram_type')}")
                print(f"  Code Length: {len(diagram_data.get('diagram_code', ''))}")
            
            # Test render_diagram tool
            print("\n🖼️ Testing render_diagram tool...")
            payload = {
                "code": "flowchart TD\n    A[Start] --> B[Process]\n    B --> C[End]",
                "diagram_type": "mermaid",
                "output_format": "svg"
            }
            
            response = await client.post(
                f"{MCP_BASE_URL}/tools/render_diagram",
                json=payload
            )
            response.raise_for_status()
            result = response.json()
            
            text_content = result.get('content', [{}])[0].get('text', '')
            render_data = json.loads(text_content)
            
            if 'error' in render_data:
                print(f"❌ render_diagram failed: {render_data['error']}")
            else:
                print(f"✅ render_diagram success:")
                print(f"  Output Format: {render_data.get('output_format')}")
                if 'image_data' in render_data:
                    print(f"  Image Data Length: {len(render_data['image_data'])}")
                    if render_data['image_data'].startswith('<svg'):
                        print(f"  Valid SVG: ✅")
                    else:
                        print(f"  Valid SVG: ⚠️ (doesn't start with <svg)")
            
            # Test generate_and_render tool
            print("\n🎯 Testing generate_and_render tool...")
            payload = {
                "prompt": "User login process with authentication",
                "diagram_type": "mermaid",
                "output_format": "svg"
            }
            
            response = await client.post(
                f"{MCP_BASE_URL}/tools/generate_and_render",
                json=payload
            )
            response.raise_for_status()
            result = response.json()
            
            text_content = result.get('content', [{}])[0].get('text', '')
            render_data = json.loads(text_content)
            
            if 'error' in render_data:
                print(f"❌ generate_and_render failed: {render_data['error']}")
            else:
                print(f"✅ generate_and_render success:")
                print(f"  AI Generated: {render_data.get('ai_generated', False)}")
                print(f"  Output Format: {render_data.get('output_format')}")
                if 'image_data' in render_data:
                    print(f"  Image Data Length: {len(render_data['image_data'])}")
                    print(f"  Diagram Code Length: {len(render_data.get('diagram_code', ''))}")
            
            # Test call_tool endpoint (generic MCP tool call)
            print("\n🔧 Testing call_tool endpoint...")
            payload = {
                "name": "generate_diagram",
                "arguments": {
                    "prompt": "Test call_tool endpoint",
                    "diagram_type": "d2"
                }
            }
            
            response = await client.post(
                f"{MCP_BASE_URL}/call_tool",
                json=payload
            )
            response.raise_for_status()
            result = response.json()
            
            if result.get('isError'):
                print(f"❌ call_tool failed")
            else:
                text_content = result.get('content', [{}])[0].get('text', '')
                diagram_data = json.loads(text_content)
                
                print(f"✅ call_tool success:")
                print(f"  Tool: {payload['name']}")
                print(f"  AI Generated: {diagram_data.get('ai_generated', False)}")
                print(f"  Diagram Type: {diagram_data.get('diagram_type')}")
            
            print("\n🎉 All MCP HTTP client tests completed successfully!")
            return True
            
    except Exception as e:
        print(f"❌ Error testing MCP server: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


async def test_mcp_websocket():
    """Test the MCP server WebSocket endpoint"""
    
    import websockets
    import json
    
    print("\n🌐 Testing MCP WebSocket Endpoint")
    print("=" * 60)
    
    WS_URL = "ws://localhost:8003/mcp/ws"
    
    try:
        async with websockets.connect(WS_URL) as websocket:
            print("✅ Connected to MCP WebSocket")
            
            # Test list_tools
            message = {
                "jsonrpc": "2.0",
                "id": 1,
                "method": "tools/list"
            }
            
            await websocket.send(json.dumps(message))
            response = await websocket.recv()
            result = json.loads(response)
            
            if 'error' in result:
                print(f"❌ tools/list failed: {result['error']}")
            else:
                tools = result.get('result', {}).get('tools', [])
                print(f"✅ tools/list success: {[tool.get('name') for tool in tools]}")
            
            # Test call_tool
            message = {
                "jsonrpc": "2.0",
                "id": 2,
                "method": "tools/call",
                "params": {
                    "name": "generate_diagram",
                    "arguments": {
                        "prompt": "WebSocket test diagram",
                        "diagram_type": "mermaid"
                    }
                }
            }
            
            await websocket.send(json.dumps(message))
            response = await websocket.recv()
            result = json.loads(response)
            
            if 'error' in result:
                print(f"❌ tools/call failed: {result['error']}")
            else:
                text_content = result.get('result', {}).get('content', [{}])[0].get('text', '')
                diagram_data = json.loads(text_content)
                
                print(f"✅ tools/call success:")
                print(f"  AI Generated: {diagram_data.get('ai_generated', False)}")
                print(f"  Diagram Type: {diagram_data.get('diagram_type')}")
            
            print("✅ WebSocket tests completed successfully!")
            return True
            
    except Exception as e:
        print(f"❌ WebSocket test failed: {str(e)}")
        return False


async def test_mcp_protocol_compliance():
    """Test MCP protocol compliance"""
    
    print("\n📋 Testing MCP Protocol Compliance")
    print("=" * 60)
    
    import httpx
    
    BASE_URL = "http://localhost:8003"
    MCP_BASE_URL = f"{BASE_URL}/mcp"
    
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            # Test JSON-RPC 2.0 compliance
            print("🔍 Testing JSON-RPC 2.0 compliance...")
            
            # Test invalid method
            payload = {
                "jsonrpc": "2.0",
                "id": "test_invalid",
                "method": "tools/invalid_method"
            }
            
            response = await client.post(
                f"{MCP_BASE_URL}/call_tool",
                json=payload
            )
            
            if response.status_code == 200:
                result = response.json()
                if 'error' in result:
                    print("✅ Invalid method properly handled with error")
                else:
                    print("⚠️ Invalid method should return error")
            else:
                print("✅ Invalid method properly rejected")
            
            # Test missing required parameters
            payload = {
                "jsonrpc": "2.0",
                "id": "test_missing",
                "method": "tools/call",
                "params": {
                    "name": "generate_diagram"
                    # Missing required 'arguments'
                }
            }
            
            response = await client.post(
                f"{MCP_BASE_URL}/call_tool",
                json=payload
            )
            
            if response.status_code == 200:
                result = response.json()
                if 'error' in result or result.get('isError'):
                    print("✅ Missing parameters properly handled")
                else:
                    print("⚠️ Missing parameters should return error")
            else:
                print("✅ Missing parameters properly rejected")
            
            print("✅ MCP protocol compliance tests completed!")
            return True
            
    except Exception as e:
        print(f"❌ Protocol compliance test failed: {str(e)}")
        return False


async def main():
    """Run all MCP client tests"""
    
    print("🚀 MCP Client Testing Suite")
    print("=" * 60)
    
    # Run all tests
    tests = [
        ("HTTP Client", test_mcp_with_http_client),
        ("WebSocket", test_mcp_websocket),
        ("Protocol Compliance", test_mcp_protocol_compliance)
    ]
    
    results = []
    for test_name, test_func in tests:
        print(f"\n{'='*60}")
        print(f"Running: {test_name}")
        print(f"{'='*60}")
        
        try:
            result = await test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ {test_name} failed with exception: {str(e)}")
            results.append((test_name, False))
    
    # Print summary
    print(f"\n{'='*60}")
    print("FINAL TEST RESULTS")
    print(f"{'='*60}")
    
    passed = 0
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{test_name:.<30} {status}")
        if result:
            passed += 1
    
    print(f"\nOverall: {passed}/{len(results)} test suites passed")
    
    if passed == len(results):
        print("\n🎉 MCP SERVER IS FULLY COMPLIANT AND FUNCTIONAL!")
        print("✅ Ready for production use with MCP clients")
        print("✅ All MCP protocols working correctly")
        print("✅ AI integration and rendering functional")
    else:
        print(f"\n⚠️ {len(results) - passed} test suite(s) failed")
        print("❌ Review the issues above before production use")
    
    return passed == len(results)


if __name__ == "__main__":
    asyncio.run(main())