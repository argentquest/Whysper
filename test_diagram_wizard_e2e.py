#!/usr/bin/env python3
"""
End-to-End Test Script for Diagram Wizard Backend API

This script tests the complete diagram wizard workflow from initial request
to final SVG generation using HTTP API calls to the running backend server.
It simulates a user creating a D2 diagram through the full clarification
and generation process via the REST API endpoints.

Requirements:
- Backend services running on localhost:8000
- Valid API_KEY configured in backend
- D2 provider available

Usage:
    python test_diagram_wizard_e2e.py

Environment Variables:
    BACKEND_URL: Backend server URL (default: http://localhost:8000)
"""

import asyncio
import os
import sys
import json
import time
import requests
from typing import Dict, Any, List
from pathlib import Path


class DiagramWizardAPITester:
    """End-to-end tester for diagram wizard API endpoints."""

    def __init__(self, backend_url: str = "http://localhost:8000"):
        self.backend_url = backend_url.rstrip("/")
        self.session_id = f"test_session_{int(time.time())}"
        self.conversation_id = f"conv_{self.session_id}"
        self.headers = {"Content-Type": "application/json"}

    def create_initial_request(self) -> Dict[str, Any]:
        """Create initial user request for a D2 diagram."""
        return {
            "design_prompt": "Create a D2 diagram showing a simple web application architecture with a frontend, backend API, and database",
            "diagram_type": "D2",
            "session_id": self.session_id,
            "user_id": "test_user",
            "conversation_id": self.conversation_id,
            "created_at": time.time(),
            "clarification_history": [],
            "clarity_scores": [],
            "question_count": 0,
            "current_state": "CLARIFYING"
        }

    def simulate_user_response(self, question: str, response: str) -> Dict[str, Any]:
        """Simulate a user responding to a clarification question."""
        print(f"🤖 AI Question: {question}")
        print(f"👤 User Response: {response}")

        return {
            "clarification_history": [
                {"role": "assistant", "content": question},
                {"role": "user", "content": response}
            ],
            "question_count": 1
        }

    async def run_workflow_step(self, endpoint: str, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Run one step of the workflow via API call."""
        print(f"\n🔄 Calling API endpoint: {endpoint}")

        url = f"{self.backend_url}{endpoint}"
        print(f"📡 POST {url}")

        try:
            response = requests.post(url, json=payload, headers=self.headers, timeout=120)
            response.raise_for_status()

            result = response.json()
            print(f"✅ API call successful - Status: {response.status_code}")
            return result

        except requests.exceptions.RequestException as e:
            print(f"❌ API call failed: {e}")
            if hasattr(e, 'response') and e.response:
                print(f"Response status: {e.response.status_code}")
                print(f"Response body: {e.response.text[:500]}...")
            raise

    async def run_full_workflow(self):
        """Run the complete diagram wizard workflow via API."""
        print("🚀 Starting End-to-End Diagram Wizard API Test")
        print("=" * 60)

        # Step 1: Create initial request
        initial_state = self.create_initial_request()
        print(f"📝 Initial request: {initial_state['design_prompt'][:100]}...")

        # Step 2: Start diagram wizard workflow
        print("🎯 Starting diagram wizard workflow...")
        state = await self.run_workflow_step("/api/v1/diagram/start", initial_state)

        # Step 3: Handle clarification loop
        clarification_iterations = 0
        max_clarifications = 3

        while clarification_iterations < max_clarifications:
            current_state = state.get("state", {})

            if current_state.get("llm_ready", False):
                print("✅ AI determined clarification is complete")
                break

            if current_state.get("clarification_timeout", False):
                print("⏰ Clarification timed out - proceeding anyway")
                break

            # Check if we need user input
            if current_state.get("current_state") == "CLARIFYING":
                # Simulate user providing more details
                question = "Please describe the components in your web application architecture."
                response = "The web app has a React frontend, Node.js backend API, PostgreSQL database, and Redis cache."

                user_input = self.simulate_user_response(question, response)

                # Continue workflow with user input
                payload = {
                    "session_id": self.session_id,
                    "user_response": response,
                    **user_input
                }
                state = await self.run_workflow_step("/api/v1/diagram/clarify", payload)
                clarification_iterations += 1
            else:
                break

        # Step 4: Approve render
        print("✅ Approving diagram for rendering...")
        payload = {"session_id": self.session_id}
        state = await self.run_workflow_step("/api/v1/diagram/approve_render", payload)

        # Step 5: Render diagram
        print("🎨 Rendering diagram to SVG...")
        payload = {"session_id": self.session_id}
        state = await self.run_workflow_step("/api/v1/diagram/render", payload)

        # Final result
        final_state = state.get("state", {})
        return final_state

    def validate_results(self, final_state: Dict[str, Any]) -> bool:
        """Validate the final workflow results."""
        print("\n🔍 Validating Results")
        print("=" * 30)

        success = True

        # Check required fields
        required_fields = ["svg_output", "diagram_code", "diagram_type"]
        for field in required_fields:
            if field not in final_state or not final_state[field]:
                print(f"❌ Missing required field: {field}")
                success = False
            else:
                print(f"✅ {field}: present")

        # Check diagram type
        if final_state.get("diagram_type") != "D2":
            print(f"⚠️ Expected D2 diagram, got: {final_state.get('diagram_type')}")
        else:
            print("✅ Diagram type: D2")

        # Check SVG output
        svg = final_state.get("svg_output", "")
        if svg and len(svg) > 100:  # Reasonable SVG size
            print(f"✅ SVG output: {len(svg)} characters")
        else:
            print(f"❌ SVG output too small or missing: {len(svg)} characters")
            success = False

        # Check workflow completion
        if final_state.get("current_state") == "READY":
            print("✅ Workflow completed successfully")
        else:
            print(f"⚠️ Workflow ended in state: {final_state.get('current_state')}")
            success = False

        return success

    def save_results(self, final_state: Dict[str, Any], output_dir: str = "test_output"):
        """Save test results to files."""
        os.makedirs(output_dir, exist_ok=True)

        # Save final state
        with open(f"{output_dir}/final_state.json", "w") as f:
            json.dump(final_state, f, indent=2)

        # Save SVG output
        svg_content = final_state.get("svg_output", "")
        if svg_content:
            with open(f"{output_dir}/diagram.svg", "w") as f:
                f.write(svg_content)

        # Save diagram code
        code = final_state.get("diagram_code", "")
        if code:
            with open(f"{output_dir}/diagram.d2", "w") as f:
                f.write(code)

        print(f"💾 Results saved to {output_dir}/")


async def main():
    """Main test execution."""
    print("🧪 Diagram Wizard End-to-End API Test")
    print("Testing complete workflow via REST API endpoints")
    print()

    # Get backend URL
    backend_url = os.getenv("BACKEND_URL", "http://localhost:8003")
    print(f"🔗 Backend URL: {backend_url}")
    print()

    # Test backend connectivity
    try:
        response = requests.get(f"{backend_url}/health", timeout=10)
        if response.status_code == 200:
            print("✅ Backend server is running and healthy")
        else:
            print(f"⚠️ Backend health check returned status: {response.status_code}")
    except requests.exceptions.RequestException as e:
        print(f"❌ Cannot connect to backend server: {e}")
        print("Make sure the backend is running on the specified URL")
        sys.exit(1)

    # Create tester
    tester = DiagramWizardAPITester(backend_url)

    try:
        # Run full workflow
        start_time = time.time()
        final_state = await tester.run_full_workflow()
        end_time = time.time()

        print(f"\n⏱️ Total execution time: {end_time - start_time:.2f} seconds")

        # Validate results
        success = tester.validate_results(final_state)

        # Save results
        tester.save_results(final_state)

        if success:
            print("\n🎉 TEST PASSED: Diagram wizard workflow completed successfully!")
            print("📊 Summary:")
            print(f"   - Diagram Type: {final_state.get('diagram_type')}")
            print(f"   - Code Length: {len(final_state.get('diagram_code', ''))} chars")
            print(f"   - SVG Length: {len(final_state.get('svg_output', ''))} chars")
            print(f"   - Final State: {final_state.get('current_state')}")
        else:
            print("\n❌ TEST FAILED: Issues found in workflow results")
            sys.exit(1)

    except Exception as e:
        print(f"\n💥 TEST CRASHED: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())