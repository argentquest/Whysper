#!/usr/bin/env python3
"""
Simple Flow Test

Simplified test without Unicode issues to focus on the workflow logic.
"""

import asyncio
import sys
import os
from datetime import datetime

# Add the backend directory to Python path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', '..', 'backend'))

from app.services.diagram_factory_service import DiagramFactoryService, DiagramSession

async def test_simple_flow():
    """Test the simplified workflow."""
    print("SIMPLE FLOW TEST")
    print("=" * 50)
    
    try:
        # Initialize service
        print("\\n1. [INIT] Starting test...")
        session = DiagramSession("simple-test")
        service = DiagramFactoryService(session)
        print("   [OK] Service ready")
        
        # Perfect score prompt
        prompt = "Create a diagram for a web application system with user authentication and database components that shows the complete workflow architecture and how all services connect and interact in the microservices hierarchy."
        
        print("\\n2. [AUTO] Starting auto mode...")
        await service.start_generation(prompt, diagram_type="auto")
        print("   [OK] Auto analysis started")
        
        await asyncio.sleep(3)
        print(f"   [CHECK] Session diagram_type: '{service.session.diagram_type}'")
        
        # Try explicit proceed
        print("\\n3. [PROCEED] Sending 'proceed' command...")
        await service.handle_clarification("proceed")
        await asyncio.sleep(3)
        
        status = service.get_status()
        print(f"   [STATUS] Status: {status.get('status', 'unknown')}")
        
        # Try D2 selection
        print("\\n4. [D2] Sending 'd2' command...")
        await service.handle_clarification("d2")
        await asyncio.sleep(5)
        
        status = service.get_status()
        print(f"   [STATUS] Status: {status.get('status', 'unknown')}")
        print(f"   [RUNNING] Running: {status.get('isRunning', False)}")
        
        # Check for graph task
        if hasattr(service.session, 'graph_task') and service.session.graph_task:
            task = service.session.graph_task
            print(f"   [TASK] Graph task exists, done: {task.done()}")
            if task.done():
                try:
                    result = task.result()
                    print(f"   [TASK] Result type: {type(result)}")
                except Exception as e:
                    print(f"   [TASK] Task exception: {e}")
        else:
            print("   [ERROR] No graph task created")
        
        # Wait for generation
        print("\\n5. [WAIT] Waiting for generation...")
        max_wait = 30
        wait_time = 0
        
        while wait_time < max_wait:
            has_code = bool(service.session.diagram_code)
            code_length = len(service.session.diagram_code) if has_code else 0
            
            print(f"   [{wait_time:2d}s] Code: {has_code} ({code_length} chars)")
            
            if has_code and code_length > 50:
                print("   [SUCCESS] Diagram code found!")
                break
                
            await asyncio.sleep(3)
            wait_time += 3
        
        # Results
        print("\\n6. [RESULTS] Final check...")
        if service.session.diagram_code:
            code_length = len(service.session.diagram_code)
            print(f"   [SUCCESS] Code generated: {code_length} chars")
            print(f"   [PREVIEW] {service.session.diagram_code[:150]}...")
            return True
        else:
            print("   [FAILED] No code generated")
            print(f"   [DEBUG] Errors: {service.session.errors}")
            
            # Check graph state
            if hasattr(service.session, 'graph_state') and service.session.graph_state:
                graph_state = service.session.graph_state
                print(f"   [DEBUG] Graph state: {graph_state.get('current_state', 'none')}")
                print(f"   [DEBUG] LLM ready: {graph_state.get('llm_ready', False)}")
            
            return False
            
    except Exception as e:
        print(f"\\n[ERROR] Test exception: {e}")
        import traceback
        traceback.print_exc()
        return False

async def main():
    """Main execution."""
    print("DIAGRAM WIZARD SIMPLE FLOW TEST")
    print("Testing basic workflow without Unicode issues")
    print("-" * 50)
    
    start_time = datetime.now()
    success = await test_simple_flow()
    end_time = datetime.now()
    
    duration = (end_time - start_time).total_seconds()
    
    print(f"\\n" + "=" * 50)
    print("SIMPLE FLOW TEST SUMMARY")
    print("=" * 50)
    print(f"Result: {'SUCCESS' if success else 'FAILED'}")
    print(f"Duration: {duration:.1f} seconds")
    
    if success:
        print("\\nThe diagram generation workflow is working!")
    else:
        print("\\nWorkflow needs more debugging.")
    
    return success

if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1)