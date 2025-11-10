#!/usr/bin/env python3
"""
Simple DiagramWizard Test Script

A simplified test that demonstrates the key workflow steps:
1. Submit initial prompt: "Create a diagram for a web application"
2. Provide 3 clarification responses  
3. Select D2 diagram type
4. Generate and render

Run this script to verify the workflow works correctly.
"""

import asyncio
import sys
import os
from datetime import datetime

# Add the app directory to Python path
sys.path.append(os.path.join(os.path.dirname(__file__), 'app'))

from app.services.diagram_factory_service import DiagramFactoryService


async def test_workflow():
    """Test the complete workflow step by step."""
    
    print("🧪 Starting Simple DiagramWizard Test")
    print("="*50)
    
    # Initialize service
    print("\n1️⃣ Initializing DiagramFactory service...")
    service = DiagramFactoryService()
    await service.initialize()
    print("✅ Service initialized")
    
    # Step 1: Initial prompt
    print("\n2️⃣ Submitting initial prompt...")
    initial_prompt = "Create a diagram for a web application"
    print(f"Prompt: {initial_prompt}")
    
    await service.start_diagram_generation(initial_prompt)
    session_id = service.session.session_id
    print(f"✅ Session started: {session_id}")
    
    # Wait for initial analysis
    await asyncio.sleep(3)
    
    # Step 2: Clarification Round 1
    print("\n3️⃣ Clarification Round 1...")
    clarification_1 = "It's a React frontend with Node.js backend for user authentication"
    print(f"Response: {clarification_1}")
    
    await service.handle_clarification(clarification_1)
    await asyncio.sleep(3)
    
    status = service.get_status()
    print(f"Status: {status.get('status')}")
    print(f"AI Response: {status.get('message', '')[:100]}...")
    
    # Step 3: Clarification Round 2  
    print("\n4️⃣ Clarification Round 2...")
    clarification_2 = "Uses PostgreSQL database, JWT tokens, and WebSocket for real-time features"
    print(f"Response: {clarification_2}")
    
    await service.handle_clarification(clarification_2)
    await asyncio.sleep(3)
    
    status = service.get_status()
    print(f"Status: {status.get('status')}")
    print(f"AI Response: {status.get('message', '')[:100]}...")
    
    # Step 4: Clarification Round 3
    print("\n5️⃣ Clarification Round 3...")
    clarification_3 = "Main components: AuthService, UserService, NotificationService, and API Gateway"
    print(f"Response: {clarification_3}")
    
    await service.handle_clarification(clarification_3)
    await asyncio.sleep(3)
    
    status = service.get_status()
    print(f"Status: {status.get('status')}")
    print(f"AI Response: {status.get('message', '')[:100]}...")
    
    # Step 5: Move to next step
    print("\n6️⃣ Requesting to move to next step...")
    next_step_request = "I have provided enough details, please move to the next step"
    print(f"Request: {next_step_request}")
    
    await service.handle_clarification(next_step_request)
    await asyncio.sleep(3)
    
    status = service.get_status()
    print(f"Status: {status.get('status')}")
    print(f"AI Response: {status.get('message', '')[:100]}...")
    
    # Step 6: Select D2 diagram
    print("\n7️⃣ Selecting D2 diagram type...")
    diagram_selection = "I want to create a D2 diagram"
    print(f"Selection: {diagram_selection}")
    
    await service.handle_clarification(diagram_selection)
    await asyncio.sleep(5)  # Give more time for generation to start
    
    status = service.get_status()
    print(f"Status: {status.get('status')}")
    print(f"AI Response: {status.get('message', '')[:100]}...")
    
    # Step 7: Wait for generation to complete
    print("\n8️⃣ Waiting for diagram generation...")
    max_wait = 60
    wait_time = 0
    
    while wait_time < max_wait:
        status = service.get_status()
        current_status = status.get('status', 'unknown')
        
        print(f"  [{wait_time:2d}s] Status: {current_status}")
        
        if current_status == 'completed' or service.session.diagram_code:
            print("✅ Generation completed!")
            break
        elif current_status == 'error':
            print("❌ Generation failed!")
            break
            
        await asyncio.sleep(5)
        wait_time += 5
    
    # Step 8: Check results
    print("\n9️⃣ Checking results...")
    
    if service.session.diagram_code:
        print(f"✅ Diagram code generated ({len(service.session.diagram_code)} chars)")
        print("Code preview:")
        print(service.session.diagram_code[:200] + "...")
        
        # Step 9: Test rendering
        print("\n🔟 Testing diagram rendering...")
        await service.render_diagram()
        
        if service.session.svg_output:
            print(f"✅ SVG output generated ({len(service.session.svg_output)} chars)")
            print("SVG preview:")
            print(service.session.svg_output[:200] + "...")
        else:
            print("❌ No SVG output generated")
            
    else:
        print("❌ No diagram code generated")
    
    # Final summary
    print("\n📊 FINAL SUMMARY")
    print("="*50)
    print(f"Session ID: {session_id}")
    print(f"Clarifications: {len(service.session.clarifications)}")
    print(f"History entries: {len(service.session.history)}")
    print(f"Errors: {len(service.session.errors)}")
    print(f"Has diagram code: {bool(service.session.diagram_code)}")
    print(f"Has SVG output: {bool(service.session.svg_output)}")
    
    if service.session.errors:
        print("\nErrors encountered:")
        for error in service.session.errors:
            print(f"  - {error}")
    
    success = bool(service.session.diagram_code and service.session.svg_output)
    print(f"\nTest Result: {'✅ PASSED' if success else '❌ FAILED'}")
    
    return success


async def main():
    """Main entry point."""
    try:
        success = await test_workflow()
        exit_code = 0 if success else 1
        
    except KeyboardInterrupt:
        print("\n\n⚠️ Test interrupted by user")
        exit_code = 1
        
    except Exception as e:
        print(f"\n\n❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
        exit_code = 1
    
    print(f"\n🏁 Test completed with exit code: {exit_code}")
    return exit_code


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)