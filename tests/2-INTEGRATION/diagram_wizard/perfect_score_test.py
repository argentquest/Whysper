#!/usr/bin/env python3
"""
Perfect Score Test

This test provides information that exactly matches the keyword patterns 
required for a 3/3 score to trigger diagram generation.

Based on the keyword analysis in DiagramFactoryService:
- entity_words: user, system, database, service, component, server, api, frontend, backend, client
- action_words: login, register, create, update, delete, process, send, receive, authenticate, authorize  
- structure_words: architecture, workflow, sequence, hierarchy, relationship, connects, depends, interacts
"""

import asyncio
import sys
import os
from datetime import datetime

# Add the backend directory to Python path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', '..', 'backend'))

from app.services.diagram_factory_service import DiagramFactoryService, DiagramSession

async def test_perfect_score_workflow():
    """Test with information designed to achieve a perfect 3/3 score."""
    print("PERFECT SCORE WORKFLOW TEST")
    print("=" * 60)
    
    try:
        # Initialize service
        print("\n1. [INIT] Initializing service...")
        session = DiagramSession("perfect-score-session")
        service = DiagramFactoryService(session)
        print(f"   [OK] Service initialized")
        
        # Start with auto analysis
        print("\n2. [AUTO] Starting auto analysis...")
        
        # Carefully crafted initial prompt with all required keywords
        initial_prompt = """Create a diagram for a web application system with user authentication and database components that shows the complete workflow architecture."""
        
        await service.start_generation(initial_prompt, diagram_type="auto")
        print(f"   [OK] Auto analysis started")
        print(f"   [PROMPT] Initial prompt: {initial_prompt}")
        
        # Check initial score
        await asyncio.sleep(3)
        status = service.get_status()
        print(f"   [STATUS] After auto start: {status.get('status', 'unknown')}")
        
        # Provide a comprehensive clarification with ALL required keyword types
        print("\n3. [CLARIFY] Providing comprehensive clarification...")
        
        comprehensive_clarification = """
        The web application architecture includes the following components and relationships:
        
        ENTITIES/COMPONENTS (entity_words):
        - Frontend user interface for client interactions
        - Backend API server for processing requests  
        - Database system for data storage
        - Authentication service component
        - Admin user management system
        
        ACTIONS/PROCESSES (action_words):
        - Users can register and login to authenticate 
        - System can create, update, and delete user records
        - API processes and validates incoming requests
        - Services send and receive data between components
        - Admin can authorize user access and permissions
        
        STRUCTURE/RELATIONSHIPS (structure_words):
        - The application follows microservices architecture
        - Components have hierarchical relationships and dependencies
        - Frontend connects to backend API through defined workflow
        - Database interacts with authentication service
        - All services communicate through established protocols
        
        This creates a complete system workflow showing how users, services, and data interact through the application architecture.
        """
        
        await service.handle_clarification(comprehensive_clarification)
        await asyncio.sleep(3)
        
        # Check score after comprehensive clarification
        status = service.get_status()
        print(f"   [STATUS] After comprehensive clarification: {status.get('status', 'unknown')}")
        
        # If still not ready, try explicit proceed request
        if status.get('status') != 'can_proceed':
            print("\n4. [PROCEED] Explicitly requesting to proceed...")
            await service.handle_clarification("proceed")
            await asyncio.sleep(3)
            status = service.get_status()
            print(f"   [STATUS] After proceed request: {status.get('status', 'unknown')}")
        
        # Select D2 diagram type
        print(f"\n5. [SELECT] Selecting D2 diagram type...")
        await service.handle_clarification("I want to create a D2 diagram")
        await asyncio.sleep(5)
        
        status = service.get_status()
        print(f"   [STATUS] After D2 selection: {status.get('status', 'unknown')}")
        print(f"   [RUNNING] Is Running: {status.get('isRunning', False)}")
        
        # Wait for diagram generation with detailed monitoring
        print(f"\n6. [GENERATE] Monitoring diagram generation...")
        max_wait = 90
        wait_time = 0
        
        while wait_time < max_wait:
            status = service.get_status()
            current_status = status.get('status', 'unknown')
            is_running = status.get('isRunning', False)
            
            print(f"   [{wait_time:2d}s] Status: {current_status} | Running: {is_running}")
            
            # Check for completion conditions
            if current_status == 'completed':
                print(f"   [SUCCESS] Generation completed!")
                break
            elif current_status == 'error':
                print(f"   [ERROR] Generation failed!")
                errors = status.get('errors', [])
                if errors:
                    print(f"   [ERROR] Details: {errors}")
                break
            elif service.session.diagram_code and len(service.session.diagram_code) > 50:
                print(f"   [SUCCESS] Diagram code detected!")
                break
                
            await asyncio.sleep(5)
            wait_time += 5
        
        # Check final results
        print(f"\n7. [RESULTS] Checking final results...")
        
        if service.session.diagram_code:
            code_length = len(service.session.diagram_code)
            print(f"   [SUCCESS] Diagram code generated: {code_length} characters")
            print(f"   [PREVIEW] Code preview:")
            print(f"   {service.session.diagram_code[:300]}...")
            
            # Render SVG
            print(f"\n8. [SVG] Rendering SVG...")
            try:
                await service.render_diagram()
                
                if service.session.svg_output:
                    svg_length = len(service.session.svg_output)
                    print(f"   [SUCCESS] SVG generated: {svg_length} characters")
                    
                    # Save and validate SVG
                    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                    filename = f"perfect_score_diagram_{timestamp}.svg"
                    
                    with open(filename, 'w', encoding='utf-8') as f:
                        if not service.session.svg_output.strip().startswith('<?xml'):
                            f.write('<?xml version="1.0" encoding="UTF-8"?>\\n')
                        f.write(service.session.svg_output)
                    
                    print(f"   [SUCCESS] SVG saved to: {filename}")
                    
                    # Validate SVG
                    svg_content = service.session.svg_output.lower()
                    has_svg = "<svg" in svg_content
                    has_closing = "</svg>" in svg_content
                    has_elements = any(tag in svg_content for tag in ["<path", "<rect", "<circle", "<text", "<g"])
                    
                    print(f"   [VALIDATION] SVG structure:")
                    print(f"     Has <svg> tag: {has_svg}")
                    print(f"     Has closing tag: {has_closing}")
                    print(f"     Has drawing elements: {has_elements}")
                    
                    valid_svg = has_svg and has_closing and has_elements
                    
                    if valid_svg:
                        print(f"   [SUCCESS] Valid SVG diagram generated!")
                        return True, filename
                    else:
                        print(f"   [WARNING] SVG validation issues detected")
                        return False, filename
                else:
                    print(f"   [ERROR] SVG rendering failed - no output")
                    return False, None
                    
            except Exception as e:
                print(f"   [ERROR] SVG rendering exception: {e}")
                return False, None
        else:
            print(f"   [ERROR] No diagram code was generated")
            print(f"   [DEBUG] Session state:")
            print(f"     Errors: {service.session.errors}")
            print(f"     Is Running: {service.session.is_running}")
            
            # Check graph state
            if hasattr(service.session, 'graph_state') and service.session.graph_state:
                graph_state = service.session.graph_state
                print(f"     Graph State: {graph_state.get('current_state', 'unknown')}")
                print(f"     LLM Ready: {graph_state.get('llm_ready', False)}")
            
            return False, None
            
    except Exception as e:
        print(f"\n[ERROR] Test failed with exception: {e}")
        import traceback
        traceback.print_exc()
        return False, None

async def main():
    """Main test execution."""
    start_time = datetime.now()
    
    print("DIAGRAM WIZARD PERFECT SCORE TEST")
    print("Testing with carefully crafted input to achieve 3/3 score")
    print("-" * 70)
    
    success, filename = await test_perfect_score_workflow()
    
    end_time = datetime.now()
    duration = (end_time - start_time).total_seconds()
    
    print(f"\n" + "=" * 60)
    print("FINAL TEST RESULTS")
    print("=" * 60)
    
    result = "[SUCCESS]" if success else "[FAILED]"
    print(f"Test Result: {result}")
    print(f"Duration: {duration:.1f} seconds")
    
    if success and filename:
        print(f"Generated File: {filename}")
        print("\\nThe test successfully generated a valid SVG diagram!")
        print("Open the file in a web browser to view the diagram.")
    else:
        print("\\nThe test failed to generate a valid SVG diagram.")
        print("This indicates issues with the diagram generation workflow.")
        print("Check the detailed output above for troubleshooting information.")
    
    return success

if __name__ == "__main__":
    try:
        success = asyncio.run(main())
        exit_code = 0 if success else 1
        print(f"\\nProcess completed with exit code: {exit_code}")
    except KeyboardInterrupt:
        print("\\n[INTERRUPTED] Test stopped by user")
        exit_code = 1  
    except Exception as e:
        print(f"\\n[FATAL] Unhandled exception: {e}")
        exit_code = 1
    
    sys.exit(exit_code)