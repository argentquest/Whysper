"""
Test script for MCP endpoints
This script tests all the FastMCP endpoints to ensure they're working correctly.
"""

import json
import sys
import asyncio
import httpx
from typing import Dict, Any

# Configuration
BASE_URL = "http://localhost:8003"
MCP_BASE_URL = f"{BASE_URL}/mcp"

async def test_list_tools():
    """Test the list_tools endpoint."""
    print("\n=== Testing list_tools endpoint ===")
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{MCP_BASE_URL}/tools")
            response.raise_for_status()
            data = response.json()
            
            print(f"✓ Status: {response.status_code}")
            print(f"✓ Tools found: {len(data.get('tools', []))}")
            
            for tool in data.get('tools', []):
                print(f"  - {tool['name']}: {tool['description']}")
            
            return True
    except Exception as e:
        print(f"✗ Error: {str(e)}")
        return False

async def test_generate_diagram():
    """Test the generate_diagram endpoint."""
    print("\n=== Testing generate_diagram endpoint ===")
    try:
        payload = {
            "prompt": "Simple flowchart with start and end",
            "diagram_type": "mermaid"
        }
        
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{MCP_BASE_URL}/tools/generate_diagram",
                json=payload
            )
            response.raise_for_status()
            data = response.json()
            
            print(f"✓ Status: {response.status_code}")
            print(f"✓ Response content type: {data.get('content', [{}])[0].get('type')}")
            
            # Parse the diagram code
            text_content = data.get('content', [{}])[0].get('text', '')
            diagram_data = json.loads(text_content)
            
            if 'error' in diagram_data:
                print(f"✗ Error in response: {diagram_data['error']}")
                return False
            
            print(f"✓ Diagram type: {diagram_data.get('diagram_type')}")
            print(f"✓ Diagram code generated (length: {len(diagram_data.get('diagram_code', ''))})")
            print(f"  Diagram code preview:\n    {diagram_data.get('diagram_code', '')[:100]}...")
            
            return True
    except Exception as e:
        print(f"✗ Error: {str(e)}")
        return False

async def test_render_diagram():
    """Test the render_diagram endpoint."""
    print("\n=== Testing render_diagram endpoint ===")
    try:
        payload = {
            "code": "flowchart TD\n    A[Start] --> B[Process]\n    B --> C[End]",
            "diagram_type": "mermaid",
            "output_format": "svg"
        }
        
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{MCP_BASE_URL}/tools/render_diagram",
                json=payload
            )
            response.raise_for_status()
            data = response.json()
            
            print(f"✓ Status: {response.status_code}")
            print(f"✓ Response content type: {data.get('content', [{}])[0].get('type')}")
            
            # Parse the render result
            text_content = data.get('content', [{}])[0].get('text', '')
            render_data = json.loads(text_content)
            
            if 'error' in render_data:
                print(f"✗ Error in response: {render_data['error']}")
                return False
            
            print(f"✓ Output format: {render_data.get('output_format')}")
            print(f"✓ Image data generated (length: {len(render_data.get('image_data', ''))})")
            print(f"  Image data preview: {render_data.get('image_data', '')[:50]}...")
            
            return True
    except Exception as e:
        print(f"✗ Error: {str(e)}")
        return False

async def test_generate_and_render():
    """Test the generate_and_render endpoint."""
    print("\n=== Testing generate_and_render endpoint ===")
    try:
        payload = {
            "prompt": "Simple flowchart with start and end",
            "diagram_type": "mermaid",
            "output_format": "svg"
        }
        
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{MCP_BASE_URL}/tools/generate_and_render",
                json=payload
            )
            response.raise_for_status()
            data = response.json()
            
            print(f"✓ Status: {response.status_code}")
            print(f"✓ Response content type: {data.get('content', [{}])[0].get('type')}")
            
            # Parse the result
            text_content = data.get('content', [{}])[0].get('text', '')
            result_data = json.loads(text_content)
            
            if 'error' in result_data:
                print(f"✗ Error in response: {result_data['error']}")
                return False
            
            print(f"✓ Diagram type: {result_data.get('diagram_type')}")
            print(f"✓ Output format: {result_data.get('output_format')}")
            print(f"✓ Diagram code generated (length: {len(result_data.get('diagram_code', ''))})")
            print(f"✓ Image data generated (length: {len(result_data.get('image_data', ''))})")
            
            return True
    except Exception as e:
        print(f"✗ Error: {str(e)}")
        return False

async def test_call_tool():
    """Test the generic call_tool endpoint."""
    print("\n=== Testing call_tool endpoint ===")
    try:
        payload = {
            "name": "generate_diagram",
            "arguments": {
                "prompt": "Test diagram via call_tool",
                "diagram_type": "d2"
            }
        }
        
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{MCP_BASE_URL}/call_tool",
                json=payload
            )
            response.raise_for_status()
            data = response.json()
            
            print(f"✓ Status: {response.status_code}")
            print(f"✓ Is error: {data.get('isError', False)}")
            print(f"✓ Response content type: {data.get('content', [{}])[0].get('type')}")
            
            # Parse the result
            text_content = data.get('content', [{}])[0].get('text', '')
            result_data = json.loads(text_content)
            
            if 'error' in result_data:
                print(f"✗ Error in response: {result_data['error']}")
                return False
            
            print(f"✓ Diagram type: {result_data.get('diagram_type')}")
            print(f"✓ Diagram code generated (length: {len(result_data.get('diagram_code', ''))})")
            
            return True
    except Exception as e:
        print(f"✗ Error: {str(e)}")
        return False

async def test_health_check():
    """Test if the server is running."""
    print("\n=== Testing server health ===")
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{BASE_URL}/docs")
            if response.status_code == 200:
                print(f"✓ Server is running at {BASE_URL}")
                return True
            else:
                print(f"✗ Server returned status {response.status_code}")
                return False
    except Exception as e:
        print(f"✗ Cannot connect to server: {str(e)}")
        print(f"  Make sure the server is running at {BASE_URL}")
        return False

async def main():
    """Run all tests."""
    print("=== MCP Endpoint Test Suite ===")
    print(f"Testing FastMCP endpoints at {MCP_BASE_URL}")
    
    # First check if server is running
    if not await test_health_check():
        sys.exit(1)
    
    # Run all tests
    tests = [
        test_list_tools,
        test_generate_diagram,
        test_render_diagram,
        test_generate_and_render,
        test_call_tool
    ]
    
    results = []
    for test in tests:
        results.append(await test())
    
    # Print summary
    print("\n=== Test Results Summary ===")
    passed = sum(results)
    total = len(results)
    print(f"Passed: {passed}/{total}")
    
    if passed == total:
        print("✓ All tests passed! FastMCP endpoints are working correctly.")
    else:
        print("✗ Some tests failed. Check the output above for details.")
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main())
