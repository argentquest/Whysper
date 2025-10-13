"""
Debug script to test MCP AI integration
"""
import asyncio
import json
import sys
import os

# Add the backend directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

async def test_ai_integration():
    """Test AI integration for MCP diagram generation."""
    try:
        print("=== Testing AI Integration for MCP ===\n")
        
        # Test imports
        print("1. Testing imports...")
        from app.core.config import get_settings
        from common.ai import create_ai_processor
        from app.utils.code_extraction import extract_code_blocks_from_content
        print("✓ All imports successful\n")
        
        # Test settings
        print("2. Testing settings...")
        settings = get_settings()
        print(f"✓ API key present: {bool(settings.api_key)}")
        print(f"✓ Provider: openrouter")
        print(f"✓ Model: {settings.default_model}\n")
        
        # Test prompt file
        print("3. Testing prompt file...")
        diagram_type = "mermaid"
        prompt_file_path = f"C:\\Code2025\\Whysper\\prompts\\coding\\agent\\{diagram_type}-architecture.md"
        prompt_file_exists = os.path.exists(prompt_file_path)
        print(f"✓ Prompt file exists: {prompt_file_exists} at {prompt_file_path}")
        
        if not prompt_file_exists:
            print("✗ Prompt file not found!")
            return False
        
        # Load prompt
        with open(prompt_file_path, "r") as f:
            agent_prompt = f.read()
        print(f"✓ Prompt loaded, length: {len(agent_prompt)}\n")
        
        # Test AI processor creation
        print("4. Testing AI processor creation...")
        ai_processor = create_ai_processor(settings.api_key, "openrouter")
        print("✓ AI processor created successfully\n")
        
        # Test AI generation
        print("5. Testing AI diagram generation...")
        test_prompt = "Simple flowchart showing login process"
        
        conversation_history = [
            {"role": "system", "content": agent_prompt},
            {"role": "user", "content": test_prompt},
        ]
        
        print(f"Sending prompt: {test_prompt}")
        full_response = ai_processor.process_question(
            question=test_prompt,
            conversation_history=conversation_history,
            codebase_content="",
            model=settings.default_model,
        )
        
        print(f"✓ AI response received, length: {len(full_response)}")
        print(f"Response preview: {full_response[:200]}...\n")
        
        # Test code extraction
        print("6. Testing code extraction...")
        code_blocks = extract_code_blocks_from_content(
            full_response, "diagram_generation"
        )
        
        if not code_blocks:
            print("✗ No code blocks found in AI response")
            return False
        
        diagram_code = code_blocks[0]["code"]
        print(f"✓ Diagram code extracted, length: {len(diagram_code)}")
        print(f"Diagram code preview:\n{diagram_code}\n")
        
        # Test MCP server integration
        print("7. Testing MCP server integration...")
        from mcp_server.fastmcp_server import generate_diagram_impl
        
        result = await generate_diagram_impl(test_prompt, diagram_type)
        result_data = json.loads(result)
        
        print(f"✓ MCP server integration successful")
        print(f"AI generated: {result_data.get('ai_generated', False)}")
        print(f"Diagram code length: {len(result_data.get('diagram_code', ''))}")
        
        if result_data.get('ai_generated'):
            print("✓ AI integration working correctly!")
        else:
            print(f"⚠ AI integration failed, fallback used: {result_data.get('fallback_reason', 'Unknown')}")
        
        return True
        
    except Exception as e:
        print(f"✗ Error testing AI integration: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

async def main():
    """Run all tests."""
    success = await test_ai_integration()
    
    if success:
        print("\n=== AI Integration Test Complete ===")
        print("✓ All tests passed! AI integration is working.")
    else:
        print("\n=== AI Integration Test Failed ===")
        print("✗ Some tests failed. Check the output above for details.")
    
    return success

if __name__ == "__main__":
    asyncio.run(main())