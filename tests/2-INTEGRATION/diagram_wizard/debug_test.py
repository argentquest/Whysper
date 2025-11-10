#!/usr/bin/env python3
"""
Debug Test for Diagram Wizard

This test provides detailed debugging output to see exactly what's happening
in each step of the workflow and why it's not progressing to diagram generation.
"""

import asyncio
import sys
import os
from datetime import datetime

# Add the backend directory to Python path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', '..', 'backend'))

from app.services.diagram_factory_service import DiagramFactoryService, DiagramSession

async def debug_workflow():
    """Debug the workflow step by step."""
    print("DEBUG: Starting detailed workflow analysis")
    print("=" * 60)
    
    try:
        # Initialize service
        print("\n1. [INIT] Initializing service...")
        session = DiagramSession("debug-session")
        service = DiagramFactoryService(session)
        print(f"   [OK] Service initialized with session: {session.session_id}")
        
        # Submit initial prompt
        print("\n2. [PROMPT] Submitting initial prompt...")
        initial_prompt = "Create a diagram for a web application with user authentication"
        await service.start_generation(initial_prompt)
        print(f"   [OK] Prompt submitted: {initial_prompt}")
        
        # Wait for processing
        await asyncio.sleep(3)
        
        # Check status after initial submission
        status = service.get_status()
        print(f"\n3. [STATUS] Status after initial prompt:")
        print(f"   Session ID: {status.get('session_id')}")
        print(f"   Is Running: {status.get('isRunning')}")
        print(f"   History entries: {len(status.get('history', []))}")
        print(f"   Clarifications: {len(status.get('clarifications', []))}")
        print(f"   Diagram Code: '{status.get('diagramCode', '')}'")
        print(f"   SVG Output: '{status.get('svgOutput', '')}'")
        print(f"   Errors: {status.get('errors', [])}")
        
        # Print clarifications if any
        clarifications = status.get('clarifications', [])
        if clarifications:
            print(f"\n4. [CLARIFY] Latest Clarifications:")
            for i, clarification in enumerate(clarifications[-3:], 1):
                preview = clarification[:150] + "..." if len(clarification) > 150 else clarification
                print(f"   {i}. {preview}")
        
        # Print history
        history = status.get('history', [])
        if history:
            print(f"\n5. [HISTORY] Conversation History:")
            for i, (role, content) in enumerate(history, 1):
                preview = content[:100] + "..." if len(content) > 100 else content
                print(f"   {i}. [{role}] {preview}")
        
        # Try one clarification
        print(f"\n6. [TEST] Submitting clarification...")
        clarification = "The web application uses React frontend with Node.js backend and PostgreSQL database"
        await service.handle_clarification(clarification)
        
        await asyncio.sleep(3)
        
        # Check status after clarification
        status = service.get_status()
        print(f"\n7. [STATUS2] Status after clarification:")
        print(f"   Is Running: {status.get('isRunning')}")
        print(f"   History entries: {len(status.get('history', []))}")
        print(f"   Clarifications: {len(status.get('clarifications', []))}")
        print(f"   Latest clarification response:")
        
        clarifications = status.get('clarifications', [])
        if clarifications:
            latest = clarifications[-1]
            print(f"   {latest[:300]}...")
        
        # Check if graph state exists
        if hasattr(service.session, 'graph_state') and service.session.graph_state:
            print(f"\n8. [GRAPH] LangGraph State:")
            graph_state = service.session.graph_state
            print(f"   Current State: {graph_state.get('current_state')}")
            print(f"   LLM Ready: {graph_state.get('llm_ready')}")
            print(f"   Question Count: {graph_state.get('question_count')}")
            print(f"   Clarification History: {len(graph_state.get('clarification_history', []))}")
        else:
            print(f"\n8. [ERROR] No LangGraph state found")
        
        # Check if task is running
        if hasattr(service.session, 'graph_task') and service.session.graph_task:
            print(f"\n9. [TASK] Graph Task Status:")
            task = service.session.graph_task
            print(f"   Done: {task.done()}")
            if task.done():
                try:
                    result = task.result()
                    print(f"   Result: {type(result)} - {str(result)[:200]}...")
                except Exception as e:
                    print(f"   Exception: {e}")
            else:
                print(f"   Still running...")
        else:
            print(f"\n9. [ERROR] No graph task found")
            
        return status
        
    except Exception as e:
        print(f"\n[ERROR] DEBUG ERROR: {e}")
        import traceback
        traceback.print_exc()
        return None

async def main():
    """Main debug execution."""
    print("DIAGRAM WIZARD DEBUG TEST")
    print("This test provides detailed insight into the workflow execution")
    
    result = await debug_workflow()
    
    print(f"\n" + "=" * 60)
    print("DEBUG SUMMARY")
    print("=" * 60)
    
    if result:
        print("[OK] Debug test completed successfully")
        print("Review the detailed output above to identify any issues")
    else:
        print("[ERROR] Debug test failed")
        print("Check the error details above")

if __name__ == "__main__":
    asyncio.run(main())