#!/usr/bin/env python3
"""
Simple SVG Test Runner (Windows compatible)

Runs the DiagramWizard workflow test without Unicode characters
that might cause issues on Windows console.
"""

import asyncio
import sys
import os
from datetime import datetime

# Add the app directory to Python path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', '..', 'backend'))


async def run_quick_validation():
    """Run a quick validation to check if the system is ready."""
    print("Quick System Check...")
    
    try:
        from app.services.diagram_factory_service import DiagramFactoryService, DiagramSession
        import uuid
        
        # Create session and service
        session_id = str(uuid.uuid4())
        session = DiagramSession(session_id)
        service = DiagramFactoryService(session)
        
        print("  [OK] DiagramFactory service can be initialized")
        return True
        
    except ImportError as e:
        print(f"  [ERROR] Import error: {e}")
        return False
    except Exception as e:
        print(f"  [ERROR] Service initialization error: {e}")
        return False


async def run_full_workflow():
    """Run the complete workflow test."""
    print("\nStarting Complete Workflow Test...")
    print("=" * 50)
    
    try:
        from app.services.diagram_factory_service import DiagramFactoryService, DiagramSession
        
        # Initialize service
        print("\n1. Initializing service...")
        session = DiagramSession("test-session")
        service = DiagramFactoryService(session)
        session_id = session.session_id
        print("   [OK] Service initialized")
        
        # Submit initial prompt
        print("\n2. Submitting initial prompt...")
        initial_prompt = "Create a diagram for a web application with user authentication"
        await service.start_generation(initial_prompt)
        session_id = service.session.session_id
        print(f"   [OK] Session started: {session_id}")
        
        # Wait for initial analysis
        await asyncio.sleep(3)
        
        # Clarification 1
        print("\n3. Clarification Round 1...")
        clarification_1 = "The web application uses React frontend with Node.js backend and PostgreSQL database"
        await service.handle_clarification(clarification_1)
        await asyncio.sleep(3)
        
        status = service.get_status()
        print(f"   Status: {status.get('status')}")
        print(f"   AI Response: {status.get('message', '')[:100]}...")
        
        # Clarification 2
        print("\n4. Clarification Round 2...")
        clarification_2 = "Uses JWT tokens for authentication, WebSocket for real-time features, and Redis for caching"
        await service.handle_clarification(clarification_2)
        await asyncio.sleep(3)
        
        status = service.get_status()
        print(f"   Status: {status.get('status')}")
        print(f"   AI Response: {status.get('message', '')[:100]}...")
        
        # Clarification 3
        print("\n5. Clarification Round 3...")
        clarification_3 = "Main components: AuthService, UserService, NotificationService, API Gateway, and DatabaseService"
        await service.handle_clarification(clarification_3)
        await asyncio.sleep(3)
        
        status = service.get_status()
        print(f"   Status: {status.get('status')}")
        print(f"   AI Response: {status.get('message', '')[:100]}...")
        
        # Move to next step
        print("\n6. Requesting to proceed...")
        await service.handle_clarification("I have provided enough details, please proceed to diagram type selection")
        await asyncio.sleep(3)
        
        status = service.get_status()
        print(f"   Status: {status.get('status')}")
        print(f"   AI Response: {status.get('message', '')[:100]}...")
        
        # Select D2 diagram
        print("\n7. Selecting D2 diagram type...")
        await service.handle_clarification("I want to create a D2 diagram")
        await asyncio.sleep(5)
        
        status = service.get_status()
        print(f"   Status: {status.get('status')}")
        print(f"   AI Response: {status.get('message', '')[:100]}...")
        
        # Wait for generation
        print("\n8. Waiting for diagram generation...")
        max_wait = 90
        wait_time = 0
        
        while wait_time < max_wait:
            status = service.get_status()
            current_status = status.get('status', 'unknown')
            
            print(f"   [{wait_time:2d}s] Status: {current_status}")
            
            if current_status == 'completed' or service.session.diagram_code:
                print("   [OK] Generation completed!")
                break
            elif current_status == 'error':
                print("   [ERROR] Generation failed!")
                break
                
            await asyncio.sleep(5)
            wait_time += 5
        
        # Check for diagram code
        print("\n9. Checking diagram code...")
        if service.session.diagram_code:
            print(f"   [OK] Diagram code generated ({len(service.session.diagram_code)} chars)")
            print("   Code preview:")
            print(f"   {service.session.diagram_code[:200]}...")
            
            # Render SVG
            print("\n10. Rendering SVG...")
            await service.render_diagram()
            
            if service.session.svg_output:
                print(f"   [OK] SVG generated ({len(service.session.svg_output)} chars)")
                
                # Save SVG
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = f"test_diagram_{timestamp}.svg"
                
                try:
                    with open(filename, 'w', encoding='utf-8') as f:
                        if not service.session.svg_output.strip().startswith('<?xml'):
                            f.write('<?xml version="1.0" encoding="UTF-8"?>\n')
                        f.write(service.session.svg_output)
                    
                    print(f"   [OK] SVG saved to: {filename}")
                    
                    # Basic SVG validation
                    svg_content = service.session.svg_output.lower()
                    has_svg_tag = "<svg" in svg_content
                    has_closing_tag = "</svg>" in svg_content
                    has_drawing = any(tag in svg_content for tag in ["<path", "<rect", "<circle", "<text"])
                    
                    print(f"   SVG validation:")
                    print(f"     Has <svg> tag: {has_svg_tag}")
                    print(f"     Has closing tag: {has_closing_tag}")
                    print(f"     Has drawing elements: {has_drawing}")
                    
                    svg_valid = has_svg_tag and has_closing_tag and has_drawing
                    
                    if svg_valid:
                        print("   [SUCCESS] Valid SVG generated!")
                        return True, filename
                    else:
                        print("   [WARNING] SVG has validation issues")
                        return False, filename
                        
                except Exception as e:
                    print(f"   [ERROR] Failed to save SVG: {e}")
                    return False, None
            else:
                print("   [ERROR] No SVG output generated")
                return False, None
        else:
            print("   [ERROR] No diagram code generated")
            return False, None
            
    except Exception as e:
        print(f"\n[ERROR] Workflow failed: {e}")
        import traceback
        traceback.print_exc()
        return False, None


async def main():
    """Main test execution."""
    print("DIAGRAM WIZARD SVG GENERATION TEST")
    print("=" * 50)
    print("Testing complete workflow from prompt to SVG...")
    
    start_time = datetime.now()
    
    # Quick validation
    if not await run_quick_validation():
        print("\n[ERROR] System check failed. Cannot proceed.")
        return False
    
    print("[OK] System check passed.")
    
    # Run workflow
    success, filename = await run_full_workflow()
    
    # Summary
    end_time = datetime.now()
    duration = (end_time - start_time).total_seconds()
    
    print("\n" + "=" * 50)
    print("TEST SUMMARY")
    print("=" * 50)
    
    result = "[SUCCESS]" if success else "[FAILED]"
    print(f"Result: {result}")
    print(f"Duration: {duration:.1f} seconds")
    
    if success and filename:
        print(f"SVG file: {filename}")
        print("\nTo view the diagram:")
        print(f"  1. Open {filename} in a web browser")
        print(f"  2. Or use an SVG viewer application")
        print("\nThe diagram should show your web application architecture!")
    else:
        print("\nTroubleshooting:")
        print("  - Check if backend services are running")
        print("  - Verify LLM provider configuration") 
        print("  - Check network connectivity")
    
    return success


if __name__ == "__main__":
    try:
        success = asyncio.run(main())
        exit_code = 0 if success else 1
        
    except KeyboardInterrupt:
        print("\n\n[INTERRUPTED] Test stopped by user")
        exit_code = 1
        
    except Exception as e:
        print(f"\n\n[FATAL ERROR] {e}")
        exit_code = 1
    
    print(f"\nTest completed with exit code: {exit_code}")
    sys.exit(exit_code)