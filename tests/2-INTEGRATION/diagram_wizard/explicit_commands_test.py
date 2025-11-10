#!/usr/bin/env python3
"""
Explicit Commands Test

This test uses exact command patterns that should match the service logic:
- Initial prompt with perfect score
- Explicit "proceed" command
- Explicit "d2" command
"""

import asyncio
import sys
import os
from datetime import datetime

# Add the app directory to Python path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', '..', 'backend'))

from app.services.diagram_factory_service import DiagramFactoryService, DiagramSession

async def test_explicit_commands():
    """Test with explicit command patterns."""
    print("EXPLICIT COMMANDS TEST")
    print("=" * 60)
    
    try:
        # Initialize service
        print("\n1. [INIT] Initializing service...")
        session = DiagramSession("explicit-test-session")
        service = DiagramFactoryService(session)
        print(f"   [OK] Service initialized")
        
        # Start with auto analysis and perfect score prompt
        print("\n2. [AUTO] Starting auto analysis with perfect score prompt...")
        
        # This prompt should achieve 3/3 score immediately
        perfect_prompt = """Create a diagram for a web application system with user authentication and database components that shows the complete workflow architecture and how all services connect and interact in the microservices hierarchy."""
        
        await service.start_generation(perfect_prompt, diagram_type="auto")
        print(f"   [OK] Auto analysis started")
        print(f"   [PROMPT] {perfect_prompt}")
        
        # Check initial score
        await asyncio.sleep(3)
        status = service.get_status()
        print(f"   [STATUS] After auto start: {status.get('status', 'unknown')}")
        clarifications = status.get('clarifications', [])
        if clarifications:
            print(f"   [RESPONSE] Latest: {clarifications[-1][:100]}...")
        
        # Use exact "proceed" command
        print("\n3. [PROCEED] Using exact 'proceed' command...")
        await service.handle_clarification("proceed")
        await asyncio.sleep(3)
        
        status = service.get_status()
        print(f"   [STATUS] After 'proceed': {status.get('status', 'unknown')}")
        clarifications = status.get('clarifications', [])
        if clarifications:
            print(f"   [RESPONSE] Latest: {clarifications[-1][:100]}...")
        
        # Use exact "d2" command
        print("\n4. [D2] Using exact 'd2' command...")
        await service.handle_clarification("d2")
        await asyncio.sleep(5)
        
        status = service.get_status()
        print(f"   [STATUS] After 'd2': {status.get('status', 'unknown')}")
        print(f"   [RUNNING] Is Running: {status.get('isRunning', False)}")
        
        # Check if graph task was created
        if hasattr(service.session, 'graph_task') and service.session.graph_task:
            print(f"   [TASK] Graph task exists: {not service.session.graph_task.done()}")
        else:
            print(f"   [ERROR] No graph task created")
        
        # Monitor generation with more detail
        print(f"\n5. [MONITOR] Detailed generation monitoring...")
        max_wait = 60
        wait_time = 0
        
        while wait_time < max_wait:
            status = service.get_status()
            current_status = status.get('status', 'unknown')
            is_running = status.get('isRunning', False)
            
            # Check session state
            has_code = bool(service.session.diagram_code)
            code_length = len(service.session.diagram_code) if service.session.diagram_code else 0
            
            print(f"   [{wait_time:2d}s] Status: {current_status} | Running: {is_running} | Code: {has_code} ({code_length} chars)")
            
            # Check graph state
            if hasattr(service.session, 'graph_state') and service.session.graph_state:
                graph_state = service.session.graph_state.get('current_state', 'unknown')
                llm_ready = service.session.graph_state.get('llm_ready', False)
                print(f"         Graph: {graph_state} | LLM Ready: {llm_ready}")
            
            # Check for completion conditions
            if current_status == 'completed':
                print(f"   [SUCCESS] Generation completed!")
                break
            elif current_status == 'error':
                print(f"   [ERROR] Generation failed!")
                break
            elif has_code and code_length > 50:
                print(f"   [SUCCESS] Diagram code detected!")
                break
                
            await asyncio.sleep(5)
            wait_time += 5
        
        # Final results
        print(f"\n6. [RESULTS] Final results...")
        
        if service.session.diagram_code:
            code_length = len(service.session.diagram_code)
            print(f"   [SUCCESS] Diagram code: {code_length} characters")
            print(f"   [PREVIEW] {service.session.diagram_code[:200]}...")
            
            # Try SVG rendering
            print(f"\n7. [SVG] Attempting SVG rendering...")
            try:
                await service.render_diagram()
                
                if service.session.svg_output:
                    svg_length = len(service.session.svg_output)
                    print(f"   [SUCCESS] SVG generated: {svg_length} characters")
                    
                    # Save SVG
                    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                    filename = f"explicit_test_diagram_{timestamp}.svg"
                    
                    with open(filename, 'w', encoding='utf-8') as f:
                        if not service.session.svg_output.strip().startswith('<?xml'):
                            f.write('<?xml version="1.0" encoding="UTF-8"?>\\n')
                        f.write(service.session.svg_output)
                    
                    print(f"   [SUCCESS] SVG saved to: {filename}")
                    return True, filename
                else:
                    print(f"   [ERROR] SVG rendering failed")
                    return False, None
                    
            except Exception as e:
                print(f"   [ERROR] SVG exception: {e}")
                return False, None
        else:
            print(f"   [ERROR] No diagram code generated")
            
            # Debug info
            print(f"   [DEBUG] Session debug info:")
            print(f"     Errors: {service.session.errors}")
            print(f"     Clarifications: {len(service.session.clarifications)}")
            print(f"     History: {len(service.session.history)}")
            print(f"     Is Running: {service.session.is_running}")
            
            if hasattr(service.session, 'graph_state') and service.session.graph_state:
                print(f"     Graph State: {service.session.graph_state.get('current_state')}")
                
            return False, None
            
    except Exception as e:
        print(f"\n[ERROR] Test exception: {e}")
        import traceback
        traceback.print_exc()
        return False, None

async def main():
    """Main test execution."""
    start_time = datetime.now()
    
    print("EXPLICIT COMMANDS TEST")
    print("Testing with exact command patterns")
    print("-" * 50)
    
    success, filename = await test_explicit_commands()
    
    end_time = datetime.now()
    duration = (end_time - start_time).total_seconds()
    
    print(f"\n" + "=" * 60)
    print("EXPLICIT COMMANDS TEST RESULTS")
    print("=" * 60)
    
    result = "[SUCCESS]" if success else "[FAILED]"
    print(f"Result: {result}")
    print(f"Duration: {duration:.1f} seconds")
    
    if success and filename:
        print(f"Generated: {filename}")
        print("\\nSUCCESS! The diagram wizard workflow is now working!")
        print("You can open the SVG file in a web browser to view the diagram.")
    else:
        print("\\nThe workflow is still not generating diagrams.")
        print("Additional debugging may be needed.")
    
    return success

if __name__ == "__main__":
    try:
        success = asyncio.run(main())
        exit_code = 0 if success else 1
    except Exception as e:
        print(f"\\nFATAL ERROR: {e}")
        exit_code = 1
    
    print(f"\\nExiting with code: {exit_code}")
    sys.exit(exit_code)