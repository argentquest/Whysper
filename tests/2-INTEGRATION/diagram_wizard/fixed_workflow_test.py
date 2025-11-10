#!/usr/bin/env python3
"""
Fixed Workflow Test

This test follows the correct workflow pattern as designed in the DiagramFactoryService:
1. Start with auto analysis
2. Provide clarifications
3. Request to proceed 
4. Select diagram type
5. Generate diagram and SVG
"""

import asyncio
import sys
import os
from datetime import datetime

# Add the app directory to Python path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', '..', 'backend'))

from app.services.diagram_factory_service import DiagramFactoryService, DiagramSession

async def test_correct_workflow():
    """Test the workflow following the correct design pattern."""
    print("FIXED WORKFLOW TEST")
    print("=" * 60)
    
    try:
        # Initialize service
        print("\n1. [INIT] Initializing service...")
        session = DiagramSession("fixed-test-session")
        service = DiagramFactoryService(session)
        print(f"   [OK] Service initialized")
        
        # Step 1: Start with auto analysis (this is the key!)
        print("\n2. [AUTO] Starting auto analysis...")
        initial_prompt = "Create a diagram for a web application with user authentication"
        await service.start_generation(initial_prompt, diagram_type="auto")
        print(f"   [OK] Auto analysis started")
        
        # Wait for analysis
        await asyncio.sleep(3)
        
        status = service.get_status()
        print(f"   [STATUS] After auto start: {status.get('status', 'unknown')}")
        
        # Step 2: Provide clarifications
        clarifications = [
            "The web application uses React frontend with Node.js backend and PostgreSQL database",
            "It includes JWT authentication, user registration, login, and session management",
            "The system has microservices architecture with API Gateway, Auth Service, and User Service"
        ]
        
        for i, clarification in enumerate(clarifications, 1):
            print(f"\n3.{i} [CLARIFY] Providing clarification {i}...")
            await service.handle_clarification(clarification)
            await asyncio.sleep(3)
            
            status = service.get_status()
            print(f"   [STATUS] After clarification {i}: {status.get('status', 'unknown')}")
            
            # Check if we can proceed
            if status.get('status') in ['can_proceed', 'type_selection']:
                print(f"   [READY] Can proceed after clarification {i}")
                break
        
        # Step 3: Request to proceed to diagram selection
        print(f"\n4. [PROCEED] Requesting to proceed...")
        await service.handle_clarification("I have provided enough details. Please proceed to diagram type selection.")
        await asyncio.sleep(3)
        
        status = service.get_status()
        print(f"   [STATUS] After proceed request: {status.get('status', 'unknown')}")
        
        # Step 4: Select D2 diagram type
        print(f"\n5. [SELECT] Selecting D2 diagram type...")
        await service.handle_clarification("I want to create a D2 diagram")
        await asyncio.sleep(5)  # Give more time for diagram generation to start
        
        status = service.get_status()
        print(f"   [STATUS] After D2 selection: {status.get('status', 'unknown')}")
        
        # Step 5: Wait for diagram generation
        print(f"\n6. [GENERATE] Waiting for diagram generation...")
        max_wait = 60
        wait_time = 0
        
        while wait_time < max_wait:
            status = service.get_status()
            current_status = status.get('status', 'unknown')
            
            print(f"   [{wait_time:2d}s] Status: {current_status}")
            
            # Check for completion
            if current_status == 'completed':
                print(f"   [OK] Generation completed!")
                break
            elif current_status == 'error':
                print(f"   [ERROR] Generation failed!")
                break
            elif service.session.diagram_code:
                print(f"   [OK] Diagram code available!")
                break
                
            await asyncio.sleep(5)
            wait_time += 5
        
        # Step 6: Check results
        print(f"\n7. [RESULTS] Checking results...")
        if service.session.diagram_code:
            print(f"   [OK] Diagram code generated: {len(service.session.diagram_code)} characters")
            print(f"   Code preview: {service.session.diagram_code[:200]}...")
            
            # Try to render SVG
            print(f"\n8. [SVG] Rendering SVG...")
            await service.render_diagram()
            
            if service.session.svg_output:
                print(f"   [OK] SVG generated: {len(service.session.svg_output)} characters")
                
                # Save SVG
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = f"fixed_test_diagram_{timestamp}.svg"
                
                try:
                    with open(filename, 'w', encoding='utf-8') as f:
                        if not service.session.svg_output.strip().startswith('<?xml'):
                            f.write('<?xml version="1.0" encoding="UTF-8"?>\\n')
                        f.write(service.session.svg_output)
                    
                    print(f"   [OK] SVG saved to: {filename}")
                    
                    # Basic validation
                    svg_content = service.session.svg_output.lower()
                    has_svg = "<svg" in svg_content
                    has_closing = "</svg>" in svg_content
                    has_elements = any(tag in svg_content for tag in ["<path", "<rect", "<circle", "<text"])
                    
                    print(f"   [CHECK] SVG validation:")
                    print(f"     Has svg tag: {has_svg}")
                    print(f"     Has closing tag: {has_closing}")
                    print(f"     Has drawing elements: {has_elements}")
                    
                    valid_svg = has_svg and has_closing and has_elements
                    
                    if valid_svg:
                        print(f"   [SUCCESS] Valid SVG generated!")
                        return True, filename
                    else:
                        print(f"   [WARNING] SVG has validation issues")
                        return False, filename
                        
                except Exception as e:
                    print(f"   [ERROR] Failed to save SVG: {e}")
                    return False, None
            else:
                print(f"   [ERROR] No SVG output generated")
                return False, None
        else:
            print(f"   [ERROR] No diagram code generated")
            return False, None
            
    except Exception as e:
        print(f"\n[ERROR] Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False, None

async def main():
    """Main test execution."""
    start_time = datetime.now()
    
    print("DIAGRAM WIZARD FIXED WORKFLOW TEST")
    print("Testing the correct workflow pattern for SVG generation")
    print("-" * 70)
    
    success, filename = await test_correct_workflow()
    
    end_time = datetime.now()
    duration = (end_time - start_time).total_seconds()
    
    print(f"\n" + "=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)
    
    result = "[SUCCESS]" if success else "[FAILED]"
    print(f"Result: {result}")
    print(f"Duration: {duration:.1f} seconds")
    
    if success and filename:
        print(f"SVG file: {filename}")
        print("\\nTo view the diagram:")
        print(f"  1. Open {filename} in a web browser")
        print("  2. Or use an SVG viewer application")
        print("\\nThe diagram should show your web application architecture!")
    else:
        print("\\nThe test failed to generate a valid SVG.")
        print("Check the detailed output above for troubleshooting.")
    
    return success

if __name__ == "__main__":
    try:
        success = asyncio.run(main())
        exit_code = 0 if success else 1
        print(f"\\nTest completed with exit code: {exit_code}")
    except KeyboardInterrupt:
        print("\\n[INTERRUPTED] Test stopped by user")
        exit_code = 1
    except Exception as e:
        print(f"\\n[FATAL ERROR] {e}")
        exit_code = 1
    
    sys.exit(exit_code)