#!/usr/bin/env python3
"""
DiagramWizard Workflow Test Script

Tests the complete diagram wizard workflow without frontend:
1. Initial prompt submission
2. Multiple clarification rounds
3. Diagram type selection
4. Code generation
5. Rendering

This verifies the LangGraph phases work correctly and there are no AI feedback loops.
"""

import asyncio
import json
import uuid
from datetime import datetime
from typing import Dict, Any

# Import the DiagramFactory service
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', '..', 'backend'))

from app.services.diagram_factory_service import DiagramFactoryService


class DiagramWizardTester:
    """Test harness for DiagramWizard workflow."""
    
    def __init__(self):
        self.service = None
        self.session_id = None
        self.test_results = []
        
    async def setup(self):
        """Initialize the diagram factory service."""
        print("[SETUP] Setting up DiagramWizard test environment...")
        from app.services.diagram_factory_service import DiagramSession
        session = DiagramSession(session_id="test_" + str(uuid.uuid4()))
        self.service = DiagramFactoryService(session)
        self.session_id = session.session_id
        print(f"[OK] DiagramWizard service initialized with session {self.session_id}")
        
    def log_step(self, step_name: str, details: Dict[str, Any]):
        """Log a test step with timestamp."""
        timestamp = datetime.now().strftime("%H:%M:%S.%f")[:-3]
        print(f"\n[{timestamp}] [STEP] {step_name}")
        
        # Log details
        for key, value in details.items():
            if isinstance(value, str) and len(value) > 200:
                value = value[:200] + "..."
            print(f"  {key}: {value}")
            
        # Store for analysis
        self.test_results.append({
            "timestamp": timestamp,
            "step": step_name,
            "details": details
        })
        
    async def test_initial_prompt(self):
        """Test Phase 1: Initial prompt submission."""
        self.log_step("PHASE 1: Initial Prompt Submission", {
            "action": "Starting new diagram session"
        })
        
        initial_prompt = """Create a diagram for a web application that handles user authentication, 
        data storage, and real-time notifications."""
        
        try:
            await self.service.start_generation(initial_prompt, "d2")
            self.session_id = self.service.session.session_id
            
            self.log_step("Initial Prompt Submitted", {
                "session_id": self.session_id,
                "prompt": initial_prompt,
                "prompt_length": len(initial_prompt)
            })
            
            # Wait for initial analysis
            await asyncio.sleep(2)
            
            status = self.service.get_status()
            self.log_step("Initial Analysis Complete", {
                "status": status.get("status"),
                "message": status.get("message", "")[:200],
                "clarifications_count": len(self.service.session.clarifications)
            })
            
            return True
            
        except Exception as e:
            self.log_step("ERROR: Initial Prompt Failed", {
                "error": str(e)
            })
            return False
    
    async def test_clarification_rounds(self):
        """Test Phase 1 continued: Multiple clarification rounds."""
        
        clarifications = [
            {
                "round": 1,
                "response": """The web application is built with React frontend and Node.js backend. 
                Users can register, login, and receive push notifications for important events."""
            },
            {
                "round": 2, 
                "response": """Authentication uses JWT tokens stored in localStorage. 
                The database is PostgreSQL with user profiles, sessions, and notification preferences. 
                Real-time notifications use WebSocket connections."""
            },
            {
                "round": 3,
                "response": """The system has three main components: AuthService for login/register, 
                NotificationService for real-time messages, and UserService for profile management. 
                There's also an API Gateway that routes requests."""
            }
        ]
        
        for clarification in clarifications:
            self.log_step(f"CLARIFICATION ROUND {clarification['round']}", {
                "action": "Submitting user clarification"
            })
            
            try:
                await self.service.handle_clarification(clarification["response"])
                
                # Wait for AI processing
                await asyncio.sleep(3)
                
                status = self.service.get_status()
                self.log_step(f"Clarification {clarification['round']} Processed", {
                    "user_input": clarification["response"][:100],
                    "status": status.get("status"),
                    "ai_response": status.get("message", "")[:200],
                    "total_clarifications": len(self.service.session.clarifications),
                    "graph_state": str(self.service.session.graph_state.get("current_state", "unknown"))
                })
                
                # Check if AI is ready to proceed
                if status.get("status") in ["can_proceed", "type_selection"]:
                    self.log_step(f"AI Ready After Round {clarification['round']}", {
                        "ai_decision": "Ready to proceed to diagram type selection",
                        "final_message": status.get("message", "")[:200]
                    })
                    break
                    
            except Exception as e:
                self.log_step(f"ERROR: Clarification Round {clarification['round']}", {
                    "error": str(e)
                })
                return False
        
        return True
    
    async def test_diagram_type_selection(self):
        """Test Phase 1 final: Diagram type selection."""
        self.log_step("PHASE 2: Diagram Type Selection", {
            "action": "User selecting D2 diagram type"
        })
        
        try:
            # Simulate user selecting D2 diagram type
            await self.service.handle_clarification("I want to create a D2 diagram")
            
            # Wait for processing
            await asyncio.sleep(3)
            
            status = self.service.get_status()
            self.log_step("Diagram Type Selected", {
                "user_choice": "D2 diagram",
                "status": status.get("status"),
                "message": status.get("message", "")[:200],
                "graph_state": str(self.service.session.graph_state.get("current_state", "unknown"))
            })
            
            return True
            
        except Exception as e:
            self.log_step("ERROR: Diagram Type Selection", {
                "error": str(e)
            })
            return False
    
    async def test_diagram_generation(self):
        """Test Phase 2: Diagram code generation."""
        self.log_step("PHASE 3: Diagram Code Generation", {
            "action": "Waiting for LangGraph to generate diagram code"
        })

        try:
            # Wait for the graph workflow to complete
            max_wait = 300  # 300 seconds max (5 minutes for AI processing)
            wait_time = 0
            
            while wait_time < max_wait:
                status = self.service.get_status()
                current_status = status.get("status", "unknown")
                
                self.log_step("Generation Progress Check", {
                    "wait_time": f"{wait_time}s",
                    "current_status": current_status,
                    "message": status.get("message", "")[:150],
                    "has_diagram_code": bool(self.service.session.diagram_code),
                    "code_length": len(self.service.session.diagram_code) if self.service.session.diagram_code else 0
                })
                
                if current_status == "completed" or self.service.session.diagram_code:
                    self.log_step("Diagram Generation Complete", {
                        "final_status": current_status,
                        "diagram_code_length": len(self.service.session.diagram_code),
                        "code_preview": self.service.session.diagram_code[:300] if self.service.session.diagram_code else "None"
                    })
                    return True
                
                elif current_status == "error":
                    self.log_step("ERROR: Diagram Generation Failed", {
                        "status": current_status,
                        "error_message": status.get("message", ""),
                        "session_errors": self.service.session.errors
                    })
                    return False
                
                await asyncio.sleep(5)
                wait_time += 5
            
            self.log_step("TIMEOUT: Diagram Generation", {
                "timeout_after": f"{max_wait}s",
                "final_status": status.get("status"),
                "final_message": status.get("message", "")
            })
            return False
            
        except Exception as e:
            self.log_step("ERROR: Diagram Generation Exception", {
                "error": str(e)
            })
            return False
    
    async def test_diagram_rendering(self):
        """Test Phase 3: Diagram rendering."""
        self.log_step("PHASE 4: Diagram Rendering", {
            "action": "Attempting to render generated diagram code"
        })
        
        if not self.service.session.diagram_code:
            self.log_step("ERROR: No Diagram Code to Render", {
                "error": "Cannot render - no diagram code available"
            })
            return False
        
        try:
            # Test rendering with the generated code
            await self.service.render_diagram()
            
            status = self.service.get_status()
            self.log_step("Diagram Rendering Complete", {
                "status": status.get("status"),
                "has_svg_output": bool(self.service.session.svg_output),
                "svg_length": len(self.service.session.svg_output) if self.service.session.svg_output else 0,
                "svg_preview": self.service.session.svg_output[:200] if self.service.session.svg_output else "None"
            })
            
            return bool(self.service.session.svg_output)
            
        except Exception as e:
            self.log_step("ERROR: Diagram Rendering Failed", {
                "error": str(e)
            })
            return False
    
    def print_test_summary(self, success: bool):
        """Print a comprehensive test summary."""
        print("\n" + "="*80)
        print("[TEST] DIAGRAM WIZARD WORKFLOW TEST SUMMARY")
        print("="*80)
        
        print(f"Overall Result: {'[OK] PASSED' if success else '[FAIL] FAILED'}")
        print(f"Session ID: {self.session_id}")
        print(f"Total Test Steps: {len(self.test_results)}")
        print(f"Test Duration: {len(self.test_results) * 3}+ seconds")
        
        # Session state summary
        if self.service and self.service.session:
            session = self.service.session
            print(f"\n[STATS] Final Session State:")
            print(f"  Clarifications: {len(session.clarifications)}")
            print(f"  History Entries: {len(session.history)}")
            print(f"  Errors: {len(session.errors)}")
            print(f"  Has Diagram Code: {bool(session.diagram_code)}")
            print(f"  Has SVG Output: {bool(session.svg_output)}")
            
            if session.graph_state:
                print(f"  Graph State: {session.graph_state.get('current_state', 'unknown')}")
                print(f"  LLM Ready: {session.graph_state.get('llm_ready', False)}")
                print(f"  Question Count: {session.graph_state.get('question_count', 0)}")
        
        # Detailed step breakdown
        print(f"\n[DETAILS] Test Step Details:")
        for i, result in enumerate(self.test_results, 1):
            status_icon = "[OK]" if "ERROR" not in result["step"] else "[FAIL]"
            print(f"  {i:2d}. {status_icon} [{result['timestamp']}] {result['step']}")
        
        # Success criteria check
        print(f"\n[CRITERIA] Success Criteria:")
        has_initial = any("Initial Prompt" in r["step"] for r in self.test_results)
        has_clarifications = any("Clarification" in r["step"] for r in self.test_results)
        has_type_selection = any("Type Selection" in r["step"] for r in self.test_results)
        has_generation = any("Generation Complete" in r["step"] for r in self.test_results)
        has_rendering = any("Rendering Complete" in r["step"] for r in self.test_results)
        
        print(f"  Initial Prompt: {'[OK]' if has_initial else '[FAIL]'}")
        print(f"  Clarifications: {'[OK]' if has_clarifications else '[FAIL]'}")
        print(f"  Type Selection: {'[OK]' if has_type_selection else '[FAIL]'}")
        print(f"  Code Generation: {'[OK]' if has_generation else '[FAIL]'}")
        print(f"  SVG Rendering: {'[OK]' if has_rendering else '[FAIL]'}")
        
        print("\n" + "="*80)


async def main():
    """Run the complete DiagramWizard workflow test."""
    print("[START] Starting DiagramWizard Workflow Test")
    print("This will test the complete LangGraph workflow without frontend")
    print("-" * 60)

    tester = DiagramWizardTester()
    success = True

    try:
        # Setup
        await tester.setup()

        # Phase 1: Initial prompt and clarifications
        if success:
            success = await tester.test_initial_prompt()

        if success:
            success = await tester.test_clarification_rounds()

        if success:
            success = await tester.test_diagram_type_selection()

        # Phase 2: Generation
        if success:
            success = await tester.test_diagram_generation()

        # Phase 3: Rendering
        if success:
            success = await tester.test_diagram_rendering()

        # Summary
        tester.print_test_summary(success)

        # Save detailed results to file
        results_file = f"test_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(results_file, 'w') as f:
            json.dump(tester.test_results, f, indent=2)
        print(f"\n[SAVE] Detailed test results saved to: {results_file}")

    except KeyboardInterrupt:
        print("\n\n[WARNING] Test interrupted by user")
        tester.print_test_summary(False)

    except Exception as e:
        print(f"\n\n[ERROR] Test failed with exception: {e}")
        tester.print_test_summary(False)
        raise


if __name__ == "__main__":
    asyncio.run(main())