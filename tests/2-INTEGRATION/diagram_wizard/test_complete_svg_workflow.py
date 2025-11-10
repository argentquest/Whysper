#!/usr/bin/env python3
"""
Complete SVG Generation Test

This test ensures the entire DiagramWizard workflow completes successfully
and produces a valid SVG output. It includes comprehensive validation and
troubleshooting to ensure we get the final SVG result.
"""

import asyncio
import sys
import os
import re
import json
from datetime import datetime

# Add the app directory to Python path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', '..', 'backend'))

from app.services.diagram_factory_service import DiagramFactoryService


class SVGWorkflowTester:
    """Enhanced tester focused on complete SVG generation."""
    
    def __init__(self):
        self.service = None
        self.session_id = None
        self.steps_completed = []
        self.start_time = None
        
    def log_step(self, step: str, details: dict = None, success: bool = True):
        """Log a workflow step with timestamp and details."""
        timestamp = datetime.now().strftime("%H:%M:%S.%f")[:-3]
        status = "✅" if success else "❌"
        
        print(f"\n[{timestamp}] {status} {step}")
        if details:
            for key, value in details.items():
                if isinstance(value, str) and len(value) > 300:
                    value = value[:300] + "..."
                print(f"    {key}: {value}")
        
        self.steps_completed.append({
            "timestamp": timestamp,
            "step": step,
            "success": success,
            "details": details or {}
        })
    
    def validate_svg(self, svg_content: str) -> dict:
        """Validate SVG content and return analysis."""
        if not svg_content:
            return {"valid": False, "error": "No SVG content"}
        
        # Basic SVG validation
        validation = {
            "valid": True,
            "length": len(svg_content),
            "has_svg_tag": "<svg" in svg_content.lower(),
            "has_closing_tag": "</svg>" in svg_content.lower(),
            "has_viewbox": "viewbox" in svg_content.lower(),
            "has_paths_or_shapes": any(tag in svg_content.lower() 
                                     for tag in ["<path", "<rect", "<circle", "<line", "<polygon", "<text"]),
            "errors": []
        }
        
        # Check for common issues
        if not validation["has_svg_tag"]:
            validation["errors"].append("Missing opening <svg> tag")
            validation["valid"] = False
            
        if not validation["has_closing_tag"]:
            validation["errors"].append("Missing closing </svg> tag")
            validation["valid"] = False
            
        if validation["length"] < 100:
            validation["errors"].append("SVG content too short (likely incomplete)")
            validation["valid"] = False
            
        if not validation["has_paths_or_shapes"]:
            validation["errors"].append("No drawing elements found (paths, shapes, text)")
            validation["valid"] = False
        
        # Extract basic info
        try:
            # Find width and height
            width_match = re.search(r'width=["\']([^"\']+)["\']', svg_content, re.IGNORECASE)
            height_match = re.search(r'height=["\']([^"\']+)["\']', svg_content, re.IGNORECASE)
            
            validation["width"] = width_match.group(1) if width_match else "unknown"
            validation["height"] = height_match.group(1) if height_match else "unknown"
            
        except Exception as e:
            validation["errors"].append(f"Error parsing SVG attributes: {e}")
        
        return validation
    
    def save_svg_output(self, svg_content: str, filename: str = None) -> str:
        """Save SVG content to file for inspection."""
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"diagram_output_{timestamp}.svg"
        
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                f.write(svg_content)
            return filename
        except Exception as e:
            print(f"❌ Failed to save SVG: {e}")
            return None
    
    async def initialize_service(self):
        """Initialize the DiagramFactory service."""
        self.start_time = datetime.now()
        self.log_step("Initializing DiagramFactory Service")
        
        try:
            from app.services.diagram_factory_service import DiagramSession
            session = DiagramSession("test-session")
            self.service = DiagramFactoryService(session)
            self.log_step("Service Initialization Complete", {
                "service_type": type(self.service).__name__,
                "has_graph": hasattr(self.service, 'graph')
            })
            return True
        except Exception as e:
            self.log_step("Service Initialization Failed", {"error": str(e)}, success=False)
            return False
    
    async def submit_initial_prompt(self):
        """Submit the initial prompt for diagram generation."""
        self.log_step("Submitting Initial Prompt")
        
        # Use a detailed prompt to ensure good diagram generation
        prompt = """Create a diagram for a web application with user authentication system.
        
        The application should show:
        - User registration and login flows
        - Database connections for user data
        - Authentication service interactions
        - Frontend and backend communication"""
        
        try:
            await self.service.start_generation(prompt)
            self.session_id = self.service.session.session_id
            
            self.log_step("Initial Prompt Submitted", {
                "session_id": self.session_id,
                "prompt_length": len(prompt),
                "prompt_preview": prompt[:100] + "..."
            })
            
            # Wait for initial processing
            await asyncio.sleep(3)
            return True
            
        except Exception as e:
            self.log_step("Initial Prompt Failed", {"error": str(e)}, success=False)
            return False
    
    async def handle_clarification_phase(self):
        """Handle the clarification phase with detailed responses."""
        self.log_step("Starting Clarification Phase")
        
        # Detailed clarifications to ensure comprehensive diagram
        clarifications = [
            """The web application is built with:
            - React.js frontend hosted on Netlify
            - Node.js/Express backend on AWS EC2
            - PostgreSQL database on AWS RDS
            - Redis for session storage
            - JWT tokens for authentication""",
            
            """User authentication flow includes:
            - User registration with email verification
            - Login with username/password or OAuth (Google, GitHub)
            - Password reset functionality
            - Multi-factor authentication option
            - Session management and logout""",
            
            """System architecture components:
            - API Gateway for routing requests
            - AuthService for handling authentication
            - UserService for profile management  
            - EmailService for notifications
            - DatabaseService for data access
            - CacheService for performance"""
        ]
        
        for i, clarification in enumerate(clarifications, 1):
            self.log_step(f"Clarification Round {i}")
            
            try:
                await self.service.handle_clarification(clarification)
                await asyncio.sleep(4)  # Give time for AI processing
                
                status = self.service.get_status()
                self.log_step(f"Clarification {i} Processed", {
                    "status": status.get('status'),
                    "response_length": len(status.get('message', '')),
                    "response_preview": status.get('message', '')[:150] + "..."
                })
                
                # Check if we can proceed
                if status.get('status') in ['can_proceed', 'type_selection']:
                    self.log_step(f"Ready to Proceed After Round {i}")
                    break
                    
            except Exception as e:
                self.log_step(f"Clarification {i} Failed", {"error": str(e)}, success=False)
                return False
        
        return True
    
    async def request_next_phase(self):
        """Request to move to the next phase."""
        self.log_step("Requesting Next Phase")
        
        try:
            await self.service.handle_clarification(
                "I have provided comprehensive details about the system. Please proceed to diagram type selection."
            )
            await asyncio.sleep(3)
            
            status = self.service.get_status()
            self.log_step("Next Phase Requested", {
                "status": status.get('status'),
                "message": status.get('message', '')[:200] + "..."
            })
            return True
            
        except Exception as e:
            self.log_step("Next Phase Request Failed", {"error": str(e)}, success=False)
            return False
    
    async def select_diagram_type(self, diagram_type: str = "D2"):
        """Select the diagram type for generation."""
        self.log_step(f"Selecting {diagram_type} Diagram Type")
        
        selection_message = f"""I want to create a {diagram_type} diagram.
        
        {diagram_type} is perfect for showing the system architecture with:
        - Clear component relationships
        - Service connections and dependencies  
        - Data flow between services
        - User interaction paths"""
        
        try:
            await self.service.handle_clarification(selection_message)
            await asyncio.sleep(5)  # Give extra time for generation to start
            
            status = self.service.get_status()
            self.log_step(f"{diagram_type} Type Selected", {
                "status": status.get('status'),
                "message": status.get('message', '')[:200] + "..."
            })
            return True
            
        except Exception as e:
            self.log_step(f"{diagram_type} Selection Failed", {"error": str(e)}, success=False)
            return False
    
    async def monitor_generation(self, max_wait: int = 120):
        """Monitor the diagram generation process."""
        self.log_step("Monitoring Diagram Generation", {"max_wait_seconds": max_wait})
        
        wait_time = 0
        last_status = None
        
        while wait_time < max_wait:
            try:
                status = self.service.get_status()
                current_status = status.get('status', 'unknown')
                
                # Only log status changes to avoid spam
                if current_status != last_status:
                    self.log_step(f"Generation Status Update", {
                        "wait_time": f"{wait_time}s",
                        "status": current_status,
                        "message": status.get('message', '')[:150] + "...",
                        "has_code": bool(self.service.session.diagram_code),
                        "code_length": len(self.service.session.diagram_code) if self.service.session.diagram_code else 0
                    })
                    last_status = current_status
                
                # Check completion conditions
                if current_status == 'completed':
                    self.log_step("Generation Completed Successfully")
                    return True
                    
                elif current_status == 'error':
                    self.log_step("Generation Failed with Error", {
                        "error_message": status.get('message', ''),
                        "session_errors": self.service.session.errors
                    }, success=False)
                    return False
                
                # Check if we have diagram code (alternative completion signal)
                if self.service.session.diagram_code and len(self.service.session.diagram_code) > 100:
                    self.log_step("Diagram Code Generated", {
                        "code_length": len(self.service.session.diagram_code),
                        "code_preview": self.service.session.diagram_code[:200] + "..."
                    })
                    return True
                
                await asyncio.sleep(5)
                wait_time += 5
                
            except Exception as e:
                self.log_step("Generation Monitoring Error", {"error": str(e)}, success=False)
                await asyncio.sleep(5)
                wait_time += 5
        
        self.log_step("Generation Timeout", {
            "timeout_after": f"{max_wait}s",
            "final_status": self.service.get_status().get('status', 'unknown')
        }, success=False)
        return False
    
    async def generate_svg(self):
        """Generate the final SVG output."""
        self.log_step("Generating SVG Output")
        
        if not self.service.session.diagram_code:
            self.log_step("No Diagram Code Available", {
                "error": "Cannot generate SVG without diagram code"
            }, success=False)
            return False
        
        try:
            # Ensure we have the diagram code
            code_length = len(self.service.session.diagram_code)
            self.log_step("Using Generated Code for SVG", {
                "code_length": code_length,
                "code_preview": self.service.session.diagram_code[:300] + "..."
            })
            
            # Call render_diagram to generate SVG
            await self.service.render_diagram()
            
            # Check if SVG was generated
            if self.service.session.svg_output:
                svg_validation = self.validate_svg(self.service.session.svg_output)
                
                self.log_step("SVG Generation Complete", {
                    "svg_length": len(self.service.session.svg_output),
                    "svg_valid": svg_validation["valid"],
                    "svg_width": svg_validation.get("width", "unknown"),
                    "svg_height": svg_validation.get("height", "unknown"),
                    "has_drawing_elements": svg_validation.get("has_paths_or_shapes", False),
                    "validation_errors": svg_validation.get("errors", [])
                })
                
                # Save SVG to file
                filename = self.save_svg_output(self.service.session.svg_output)
                if filename:
                    self.log_step("SVG Saved to File", {"filename": filename})
                
                return svg_validation["valid"]
            else:
                self.log_step("SVG Generation Failed", {
                    "error": "No SVG output generated by render_diagram()"
                }, success=False)
                return False
                
        except Exception as e:
            self.log_step("SVG Generation Exception", {"error": str(e)}, success=False)
            return False
    
    def print_final_report(self, success: bool):
        """Print a comprehensive final report."""
        end_time = datetime.now()
        duration = (end_time - self.start_time).total_seconds() if self.start_time else 0
        
        print("\n" + "="*80)
        print("📊 COMPLETE SVG WORKFLOW TEST REPORT")
        print("="*80)
        
        print(f"\n🎯 Overall Result: {'✅ SUCCESS' if success else '❌ FAILED'}")
        print(f"⏱️  Total Duration: {duration:.1f} seconds")
        print(f"📝 Steps Completed: {len(self.steps_completed)}")
        print(f"🔧 Session ID: {self.session_id or 'Not created'}")
        
        # Step-by-step breakdown
        print(f"\n📋 Step-by-Step Results:")
        for i, step in enumerate(self.steps_completed, 1):
            status = "✅" if step["success"] else "❌"
            print(f"  {i:2d}. {status} [{step['timestamp']}] {step['step']}")
        
        # Final state analysis
        if self.service and self.service.session:
            session = self.service.session
            print(f"\n🔍 Final Session Analysis:")
            print(f"  Session Errors: {len(session.errors)}")
            print(f"  Clarifications: {len(session.clarifications)}")
            print(f"  History Entries: {len(session.history)}")
            
            if session.diagram_code:
                print(f"  ✅ Diagram Code: {len(session.diagram_code)} characters")
            else:
                print(f"  ❌ No Diagram Code Generated")
            
            if session.svg_output:
                validation = self.validate_svg(session.svg_output)
                print(f"  ✅ SVG Output: {len(session.svg_output)} characters")
                print(f"  📐 SVG Dimensions: {validation.get('width', 'unknown')} x {validation.get('height', 'unknown')}")
                print(f"  🎨 Has Drawing Elements: {validation.get('has_paths_or_shapes', False)}")
                print(f"  ✔️  SVG Valid: {validation.get('valid', False)}")
                
                if validation.get('errors'):
                    print(f"  ⚠️  SVG Issues:")
                    for error in validation['errors']:
                        print(f"      - {error}")
                        
                # Show SVG preview
                print(f"\n📄 SVG Content Preview:")
                preview = session.svg_output[:500] + "..." if len(session.svg_output) > 500 else session.svg_output
                print(f"  {preview}")
                
            else:
                print(f"  ❌ No SVG Output Generated")
        
        # Success criteria
        print(f"\n✅ Success Criteria Check:")
        criteria = [
            ("Service Initialized", any("Service Initialization Complete" in step["step"] for step in self.steps_completed)),
            ("Initial Prompt Submitted", any("Initial Prompt Submitted" in step["step"] for step in self.steps_completed)),
            ("Clarifications Processed", any("Clarification" in step["step"] for step in self.steps_completed)),
            ("Diagram Type Selected", any("Type Selected" in step["step"] for step in self.steps_completed)),
            ("Generation Completed", any("Generation Completed" in step["step"] or "Code Generated" in step["step"] for step in self.steps_completed)),
            ("SVG Generated", any("SVG Generation Complete" in step["step"] for step in self.steps_completed)),
            ("SVG Valid", self.service and self.service.session and self.service.session.svg_output and self.validate_svg(self.service.session.svg_output)["valid"] if self.service else False)
        ]
        
        for criterion, met in criteria:
            status = "✅" if met else "❌"
            print(f"  {status} {criterion}")
        
        print("\n" + "="*80)
        
        if success and self.service and self.service.session and self.service.session.svg_output:
            print("🎉 SUCCESS! Complete workflow finished with valid SVG output!")
            print("📁 Check the generated .svg file to view the diagram.")
        else:
            print("⚠️  Workflow incomplete or SVG generation failed.")
            print("🔍 Check the step-by-step results above for troubleshooting.")


async def main():
    """Run the complete SVG generation test."""
    tester = SVGWorkflowTester()
    success = False
    
    try:
        # Execute the complete workflow
        if await tester.initialize_service():
            if await tester.submit_initial_prompt():
                if await tester.handle_clarification_phase():
                    if await tester.request_next_phase():
                        if await tester.select_diagram_type("D2"):
                            if await tester.monitor_generation():
                                success = await tester.generate_svg()
        
    except KeyboardInterrupt:
        print("\n\n⚠️ Test interrupted by user")
        
    except Exception as e:
        print(f"\n\n❌ Test failed with exception: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        tester.print_final_report(success)
    
    return success


if __name__ == "__main__":
    print("🚀 Starting Complete SVG Generation Test")
    print("This will run the full DiagramWizard workflow and produce an SVG file")
    print("-" * 70)
    
    success = asyncio.run(main())
    exit_code = 0 if success else 1
    
    print(f"\n🏁 Test completed with exit code: {exit_code}")
    sys.exit(exit_code)