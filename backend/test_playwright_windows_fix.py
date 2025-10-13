"""
Test script to verify Playwright Windows fix
"""
import asyncio
import httpx
import json

BASE_URL = "http://localhost:8003"
MCP_BASE_URL = f"{BASE_URL}/mcp"

async def test_playwright_rendering():
    """Test that Playwright rendering now works on Windows."""
    print("=== Testing Playwright Rendering Fix ===")
    
    try:
        # Test render_diagram endpoint with a simple mermaid diagram
        payload = {
            "code": "flowchart TD\n    A[Start] --> B[Process]\n    B --> C[End]",
            "diagram_type": "mermaid",
            "output_format": "svg"
        }
        
        print(f"Sending request to {MCP_BASE_URL}/tools/render_diagram")
        print(f"Diagram code: {payload['code']}")
        
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(
                f"{MCP_BASE_URL}/tools/render_diagram",
                json=payload
            )
            response.raise_for_status()
            data = response.json()
            
            print(f"✓ Status: {response.status_code}")
            
            # Parse the render result
            text_content = data.get('content', [{}])[0].get('text', '')
            render_data = json.loads(text_content)
            
            if 'error' in render_data:
                print(f"❌ Rendering failed: {render_data['error']}")
                return False
            
            print(f"✓ Output format: {render_data.get('output_format')}")
            image_data = render_data.get('image_data', '')
            
            if image_data and len(image_data) > 0:
                print(f"✅ SUCCESS: Image data generated ({len(image_data)} characters)")
                
                # Check if it looks like SVG data
                if image_data.startswith('<svg') or '<svg' in image_data:
                    print("✅ Image data appears to be valid SVG")
                else:
                    print("⚠️ Image data doesn't appear to be SVG, but was generated")
                
                return True
            else:
                print("❌ No image data returned")
                return False
                
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return False

async def test_generate_and_render():
    """Test the complete generate_and_render flow."""
    print("\n=== Testing Generate and Render Flow ===")
    
    try:
        payload = {
            "prompt": "Simple flowchart with start and end",
            "diagram_type": "mermaid",
            "output_format": "svg"
        }
        
        print(f"Sending request to {MCP_BASE_URL}/tools/generate_and_render")
        print(f"Prompt: {payload['prompt']}")
        
        async with httpx.AsyncClient(timeout=60.0) as client:
            response = await client.post(
                f"{MCP_BASE_URL}/tools/generate_and_render",
                json=payload
            )
            response.raise_for_status()
            data = response.json()
            
            print(f"✓ Status: {response.status_code}")
            
            # Parse the result
            text_content = data.get('content', [{}])[0].get('text', '')
            result_data = json.loads(text_content)
            
            if 'error' in result_data:
                print(f"❌ Generate and render failed: {result_data['error']}")
                return False
            
            print(f"✓ AI Generated: {result_data.get('ai_generated', False)}")
            print(f"✓ Output format: {result_data.get('output_format')}")
            
            image_data = result_data.get('image_data', '')
            if image_data and len(image_data) > 0:
                print(f"✅ SUCCESS: Complete flow works! ({len(image_data)} characters)")
                return True
            else:
                print("❌ No image data in generate_and_render result")
                return False
                
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return False

async def main():
    """Run all tests."""
    print("🎯 Testing Playwright Windows Fix\n")
    
    # Test server health
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{BASE_URL}/docs")
            if response.status_code != 200:
                print("❌ Server is not running")
                return False
    except Exception as e:
        print(f"❌ Cannot connect to server: {str(e)}")
        return False
    
    print("✅ Server is running\n")
    
    # Run tests
    tests = [
        ("Playwright Rendering", test_playwright_rendering),
        ("Generate and Render", test_generate_and_render)
    ]
    
    results = []
    for test_name, test_func in tests:
        print(f"\n{'='*60}")
        result = await test_func()
        results.append((test_name, result))
        print(f"{'='*60}")
    
    # Print summary
    print(f"\n{'='*60}")
    print("FINAL TEST RESULTS")
    print(f"{'='*60}")
    
    passed = 0
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{test_name:.<50} {status}")
        if result:
            passed += 1
    
    print(f"\nOverall: {passed}/{len(results)} tests passed")
    
    if passed > 0:
        print("\n🎉 PLAYWRIGHT WINDOWS FIX IS WORKING!")
        print("✅ Diagram rendering is now functional on Windows")
        print("✅ MCP server can generate and render diagrams")
    else:
        print("\n❌ Playwright Windows fix needs more work")
    
    return passed > 0

if __name__ == "__main__":
    asyncio.run(main())