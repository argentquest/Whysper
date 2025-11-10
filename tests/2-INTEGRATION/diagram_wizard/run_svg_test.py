#!/usr/bin/env python3
"""
SVG Test Runner

Quick runner script to execute the complete SVG workflow test.
This is the main script to run when you want to verify the entire
DiagramWizard workflow produces a valid SVG output.
"""

import asyncio
import sys
import os
from datetime import datetime

# Import our comprehensive test
from test_complete_svg_workflow import SVGWorkflowTester


def print_header():
    """Print test header."""
    print("🚀 DIAGRAM WIZARD SVG GENERATION TEST")
    print("="*70)
    print("This test will:")
    print("  1. Initialize DiagramWizard service")
    print("  2. Submit initial prompt about web application")
    print("  3. Provide 3 rounds of clarifications")
    print("  4. Select D2 diagram type")
    print("  5. Generate diagram code via LangGraph")
    print("  6. Render SVG output")
    print("  7. Validate SVG and save to file")
    print()
    print("Expected output: A valid SVG file showing web app architecture")
    print("-"*70)


def print_footer(success: bool, duration: float):
    """Print test footer."""
    print("-"*70)
    status = "✅ SUCCESS" if success else "❌ FAILED"
    print(f"Test Result: {status}")
    print(f"Duration: {duration:.1f} seconds")
    
    if success:
        print("\n🎉 SVG generation workflow completed successfully!")
        print("📁 Check for generated .svg files in the current directory")
        print("🌐 You can open the .svg file in a web browser to view the diagram")
    else:
        print("\n⚠️  Workflow failed or incomplete")
        print("🔍 Check the detailed output above for troubleshooting")
        print("🐛 Common issues:")
        print("   - Backend services not running")
        print("   - LLM provider not configured")
        print("   - Network connectivity issues")
        print("   - Invalid diagram code generation")
    
    print(f"\n🕒 Test completed at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")


async def run_quick_validation():
    """Run a quick validation to check if the system is ready."""
    print("🔧 Quick System Check...")
    
    try:
        # Test imports
        sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', '..', 'backend'))
        from app.services.diagram_factory_service import DiagramFactoryService
        
        # Test service creation
        from app.services.diagram_factory_service import DiagramSession
        session = DiagramSession("test-session")
        service = DiagramFactoryService(session)
        
        print("  ✅ DiagramFactory service can be initialized")
        return True
        
    except ImportError as e:
        print(f"  ❌ Import error: {e}")
        print("     Make sure you're running from the backend directory")
        return False
    except Exception as e:
        print(f"  ❌ Service initialization error: {e}")
        print("     Check if backend dependencies are properly configured")
        return False


async def main():
    """Main test execution."""
    print_header()
    
    start_time = datetime.now()
    
    # Quick validation first
    if not await run_quick_validation():
        print("\n❌ System check failed. Cannot proceed with test.")
        return False
    
    print("✅ System check passed. Starting comprehensive test...\n")
    
    # Run the comprehensive test
    tester = SVGWorkflowTester()
    success = False
    
    try:
        # Execute full workflow
        if await tester.initialize_service():
            if await tester.submit_initial_prompt():
                if await tester.handle_clarification_phase():
                    if await tester.request_next_phase():
                        if await tester.select_diagram_type("D2"):
                            if await tester.monitor_generation():
                                success = await tester.generate_svg()
        
        tester.print_final_report(success)
        
    except KeyboardInterrupt:
        print("\n\n⚠️ Test interrupted by user (Ctrl+C)")
        tester.print_final_report(False)
        
    except Exception as e:
        print(f"\n\n❌ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        tester.print_final_report(False)
    
    # Calculate duration and print footer
    end_time = datetime.now()
    duration = (end_time - start_time).total_seconds()
    print_footer(success, duration)
    
    return success


if __name__ == "__main__":
    try:
        success = asyncio.run(main())
        exit_code = 0 if success else 1
        
    except KeyboardInterrupt:
        print("\n\n⚠️ Test interrupted")
        exit_code = 1
        
    except Exception as e:
        print(f"\n\n❌ Fatal error: {e}")
        exit_code = 1
    
    sys.exit(exit_code)