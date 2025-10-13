#!/usr/bin/env python3
"""
Debug script to test AI integration and identify why fallback is being used
"""
import asyncio
import json
import sys
import os
import logging

# Set up logging to see debug output
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

# Add the backend directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

async def test_ai_integration_step_by_step():
    """Test AI integration step by step to identify where it fails."""
    try:
        print("=== AI Integration Debug Test ===\n")
        
        # Step 1: Test imports
        print("1. Testing imports...")
        try:
            from app.core.config import get_settings
            print("   ✓ app.core.config imported successfully")
        except Exception as e:
            print(f"   ✗ Failed to import app.core.config: {e}")
            return False
        
        try:
            from common.ai import create_ai_processor
            print("   ✓ common.ai imported successfully")
        except Exception as e:
            print(f"   ✗ Failed to import common.ai: {e}")
            return False
        
        try:
            from app.utils.code_extraction import extract_code_blocks_from_content
            print("   ✓ app.utils.code_extraction imported successfully")
        except Exception as e:
            print(f"   ✗ Failed to import app.utils.code_extraction: {e}")
            return False
        
        # Step 2: Test settings
        print("\n2. Testing settings...")
        try:
            settings = get_settings()
            print(f"   ✓ Settings loaded successfully")
            print(f"   ✓ API key present: {bool(settings.api_key)}")
            print(f"   ✓ Provider: openrouter")
            print(f"   ✓ Model: {settings.default_model}")
        except Exception as e:
            print(f"   ✗ Failed to load settings: {e}")
            return False
        
        # Step 3: Test prompt file paths
        print("\n3. Testing prompt file paths...")
        diagram_types = ["mermaid", "d2", "c4"]
        for diagram_type in diagram_types:
            # Test hardcoded path
            hardcoded_path = f"C:\\Code2025\\Whysper\\prompts\\coding\\agent\\{diagram_type}-architecture.md"
            relative_path = f"prompts/coding/agent/{diagram_type}-architecture.md"
            
            print(f"   Testing {diagram_type}:")
            print(f"     Hardcoded path exists: {os.path.exists(hardcoded_path)}")
            print(f"     Relative path exists: {os.path.exists(relative_path)}")
            
            if os.path.exists(relative_path):
                try:
                    with open(relative_path, "r") as f:
                        content = f.read()
                    print(f"     ✓ Can read file, length: {len(content)}")
                except Exception as e:
                    print(f"     ✗ Cannot read file: {e}")
        
        # Step 4: Test AI processor creation
        print("\n4. Testing AI processor creation...")
        try:
            ai_processor = create_ai_processor(settings.api_key, "openrouter")
            print("   ✓ AI processor created successfully")
            print(f"   ✓ Processor type: {type(ai_processor).__name__}")
            print(f"   ✓ Provider: {ai_processor.provider}")
            print(f"   ✓ API key valid: {ai_processor.validate_api_key()}")
        except Exception as e:
            print(f"   ✗ Failed to create AI processor: {e}")
            return False
        
        # Step 5: Test simple AI call
        print("\n5. Testing simple AI call...")
        try:
            # Load a prompt file
            prompt_path = "prompts/coding/agent/mermaid-architecture.md"
            with open(prompt_path, "r") as f:
                agent_prompt = f.read()
            
            conversation_history = [
                {"role": "system", "content": agent_prompt},
                {"role": "user", "content": "Create a simple flowchart showing a login process"},
            ]
            
            print("   Making AI call...")
            full_response = ai_processor.process_question(
                question="Create a simple flowchart showing a login process",
                conversation_history=conversation_history,
                codebase_content="",
                model=settings.default_model,
            )
            
            print(f"   ✓ AI call successful, response length: {len(full_response)}")
            print(f"   Response preview: {full_response[:200]}...")
            
            # Step 6: Test code extraction
            print("\n6. Testing code extraction...")
            code_blocks = extract_code_blocks_from_content(
                full_response, "diagram_generation"
            )
            
            if code_blocks:
                print(f"   ✓ Code blocks found: {len(code_blocks)}")
                print(f"   First code block preview: {code_blocks[0]['code'][:100]}...")
                return True
            else:
                print("   ✗ No code blocks found in AI response")
                return False
                
        except Exception as e:
            print(f"   ✗ AI call failed: {e}")
            import traceback
            traceback.print_exc()
            return False
        
    except Exception as e:
        print(f"✗ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        return False

async def test_mcp_server_directly():
    """Test the MCP server function directly."""
    print("\n=== Testing MCP Server Directly ===\n")
    
    try:
        from mcp_server.fastmcp_server import generate_diagram_impl
        
        test_prompt = "Simple flowchart showing user login process"
        diagram_type = "mermaid"
        
        print(f"Testing generate_diagram_impl with prompt: {test_prompt}")
        result = await generate_diagram_impl(test_prompt, diagram_type)
        
        result_data = json.loads(result)
        print(f"✓ MCP server function executed")
        print(f"AI generated: {result_data.get('ai_generated', False)}")
        
        if result_data.get('ai_generated'):
            print("✅ AI INTEGRATION WORKING!")
            diagram_code = result_data.get('diagram_code', '')
            print(f"Diagram code length: {len(diagram_code)}")
            print(f"Preview: {diagram_code[:200]}...")
        else:
            print("⚠ AI integration failed, fallback used")
            print(f"Fallback reason: {result_data.get('fallback_reason', 'Unknown')}")
            print(f"Diagram code: {result_data.get('diagram_code', '')}")
        
        return result_data.get('ai_generated', False)
        
    except Exception as e:
        print(f"✗ MCP server test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

async def main():
    """Run all debug tests."""
    print("Starting AI Integration Debug...\n")
    
    # Test step by step
    step_by_step_success = await test_ai_integration_step_by_step()
    
    # Test MCP server directly
    mcp_success = await test_mcp_server_directly()
    
    print(f"\n{'='*60}")
    print("DEBUG TEST RESULTS")
    print(f"{'='*60}")
    print(f"Step-by-step AI integration: {'✅ PASS' if step_by_step_success else '❌ FAIL'}")
    print(f"MCP server integration: {'✅ PASS' if mcp_success else '❌ FAIL'}")
    
    if step_by_step_success and mcp_success:
        print("\n🎉 AI INTEGRATION IS WORKING!")
        print("The script should make actual AI calls, not use fallback.")
    elif step_by_step_success and not mcp_success:
        print("\n🔍 ISSUE IDENTIFIED:")
        print("AI integration works but MCP server has issues.")
        print("Check the MCP server implementation.")
    else:
        print("\n❌ ROOT CAUSE IDENTIFIED:")
        print("Basic AI integration is failing.")
        print("Check configuration, API key, or network connectivity.")
    
    return step_by_step_success and mcp_success

if __name__ == "__main__":
    asyncio.run(main())