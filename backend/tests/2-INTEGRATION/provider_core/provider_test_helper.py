"""
Common test utilities for provider system tests

This module provides helper classes for testing diagram providers using
the provider system endpoints (/api/v1/diagrams/v2/*).
"""

import requests
import json
from typing import Tuple, Dict, Any, Optional
from pathlib import Path


class ProviderTestHelper:
    """Helper for testing diagram providers via provider system endpoints"""

    def __init__(self, backend_url: str = "http://localhost:8003"):
        """
        Initialize the test helper.

        Args:
            backend_url: Base URL for the backend API
        """
        self.backend_url = backend_url
        self.provider_endpoint = f"{backend_url}/api/v1/diagrams/v2"
        self.mvp_endpoint = f"{backend_url}/api/v1/diagrams"

    def render_with_provider(
        self,
        code: str,
        diagram_type: str,
        provider_id: str,
        output_format: str = "svg",
        auto_fix: bool = True,
        timeout: int = 120,
    ) -> Tuple[bool, Optional[str], Dict[str, Any]]:
        """
        Render diagram using specific provider.

        Args:
            code: Diagram code to render
            diagram_type: Type of diagram (d2, mermaid, c4, etc.)
            provider_id: ID of provider to use
            output_format: Output format (svg or png)
            auto_fix: Whether to allow pattern-based auto-fix
            timeout: Request timeout in seconds

        Returns:
            Tuple[bool, Optional[str], Dict]: (success, content_or_error, metadata)
        """
        try:
            response = requests.post(
                f"{self.provider_endpoint}/render",
                json={
                    "code": code,
                    "diagram_type": diagram_type,
                    "provider_id": provider_id,
                    "output_format": output_format,
                    "auto_fix": auto_fix,
                    "use_llm": False,  # Don't use LLM for testing (cost/speed)
                },
                timeout=timeout,
            )

            if response.status_code != 200:
                error_msg = f"HTTP {response.status_code}: {response.text[:200]}"
                return (False, error_msg, {"status_code": response.status_code})

            data = response.json()

            if data.get("success"):
                metadata = {
                    "validation": data.get("validation", {}),
                    "provider_id": data.get("provider_id"),
                    "output_format": data.get("output_format"),
                    "metadata": data.get("metadata", {}),
                }
                return (True, data.get("content"), metadata)
            else:
                error_msg = data.get("error", "Unknown error")
                return (False, error_msg, {"error": error_msg})

        except requests.exceptions.Timeout:
            return (False, "Request timeout", {"timeout": True})
        except requests.exceptions.ConnectionError as e:
            return (False, f"Connection error: {str(e)}", {"connection_error": True})
        except Exception as e:
            return (False, f"Unexpected error: {str(e)}", {"exception": str(type(e))})

    def validate_with_provider(
        self, code: str, diagram_type: str, provider_id: str, auto_fix: bool = True, use_llm: bool = False
    ) -> Tuple[bool, Optional[str], Optional[str]]:
        """
        Validate diagram using specific provider.

        Args:
            code: Diagram code to validate
            diagram_type: Type of diagram
            provider_id: ID of provider to use
            auto_fix: Whether to allow pattern-based auto-fix
            use_llm: Whether to use LLM correction

        Returns:
            Tuple[bool, Optional[str], Optional[str]]: (is_valid, error_or_message, fixed_code)
        """
        try:
            response = requests.post(
                f"{self.provider_endpoint}/validate",
                json={
                    "code": code,
                    "diagram_type": diagram_type,
                    "provider_id": provider_id,
                    "auto_fix": auto_fix,
                    "use_llm": use_llm,
                },
                timeout=120,
            )

            if response.status_code != 200:
                error_msg = f"HTTP {response.status_code}"
                return (False, error_msg, None)

            data = response.json()
            fixed_code = data.get("fixed_code") if data.get("auto_fixed") else None

            return (data.get("is_valid"), data.get("error"), fixed_code)

        except Exception as e:
            return (False, str(e), None)

    def generate_diagram_with_llm(
        self, prompt: str, diagram_type: str, timeout: int = 120
    ) -> Tuple[bool, Optional[str], Optional[str]]:
        """
        Generate diagram code using LLM (MVP endpoint).

        This uses the MVP endpoint to generate diagram code from a prompt.
        The returned code can then be rendered with any provider.

        Args:
            prompt: Natural language description of the diagram
            diagram_type: Type of diagram to generate (d2, mermaid, etc.)
            timeout: Request timeout in seconds

        Returns:
            Tuple[bool, Optional[str], Optional[str]]: (success, code_or_error, validation_error)
        """
        try:
            response = requests.post(
                f"{self.mvp_endpoint}/generate",
                json={
                    "prompt": prompt,
                    "diagram_type": diagram_type,
                    "output_format": "code",  # Get code only, not rendered
                },
                timeout=timeout,
            )

            if response.status_code != 200:
                return (False, f"API error: {response.status_code}", "HTTP Error")

            data = response.json()

            # Check if generation was successful
            error_info = data.get("error_info", {})
            if error_info.get("has_error", False):
                error = error_info.get("error_message", "Unknown error")
                return (False, error, error)

            # Get diagram code from response
            diagram_code = data.get("diagram_code")
            if not diagram_code:
                return (False, "No diagram code generated", "Generation Error")

            return (True, diagram_code, None)

        except Exception as e:
            return (False, str(e), str(e))

    def list_providers(self) -> Dict[str, Any]:
        """
        Get list of available providers.

        Returns:
            Dict containing provider information
        """
        try:
            response = requests.get(f"{self.provider_endpoint}/providers", timeout=30)

            if response.status_code == 200:
                return response.json()
            else:
                return {"error": f"HTTP {response.status_code}"}

        except Exception as e:
            return {"error": str(e)}


class DiagramTestRunner:
    """Runner for diagram provider tests"""

    def __init__(self, provider_id: str, diagram_type: str, test_output_dir: str = "test_results_25"):
        """
        Initialize test runner.

        Args:
            provider_id: ID of provider to test
            diagram_type: Type of diagrams to test
            test_output_dir: Directory for test results
        """
        self.provider_id = provider_id
        self.diagram_type = diagram_type
        self.test_output_dir = Path(test_output_dir)
        self.helper = ProviderTestHelper()
        self.results = []

    def run_tests(self, test_cases: list, test_name: str = "Diagram Tests") -> Dict[str, Any]:
        """
        Run all test cases and save results.

        Args:
            test_cases: List of test case dictionaries with 'id', 'description', 'code'
            test_name: Name of test suite

        Returns:
            Dict with summary statistics
        """
        print(f"\n{'=' * 80}")
        print(f"Running {test_name} with {self.provider_id}")
        print(f"{'=' * 80}\n")

        passed = 0
        failed = 0

        for i, test_case in enumerate(test_cases, 1):
            test_id = test_case.get("id", i)
            description = test_case.get("description", f"Test {i}")
            code = test_case.get("code", "")

            # Render with provider
            success, content, metadata = self.helper.render_with_provider(
                code=code, diagram_type=self.diagram_type, provider_id=self.provider_id, output_format="svg"
            )

            result = {
                "test_id": test_id,
                "description": description,
                "success": success,
                "error": None if success else content,
                "content_length": len(content) if success else 0,
                "metadata": metadata,
            }

            self.results.append(result)

            if success:
                passed += 1
                status = "✅ PASS"
                # Save SVG
                svg_file = self.test_output_dir / "svg" / f"test_{test_id:03d}.svg"
                svg_file.parent.mkdir(parents=True, exist_ok=True)
                with open(svg_file, "w", encoding="utf-8") as f:
                    f.write(content)
            else:
                failed += 1
                status = "❌ FAIL"
                # Save error
                error_file = self.test_output_dir / "errors" / f"test_{test_id:03d}_error.txt"
                error_file.parent.mkdir(parents=True, exist_ok=True)
                with open(error_file, "w", encoding="utf-8") as f:
                    f.write(f"Test ID: {test_id}\n")
                    f.write(f"Test Name: {description}\n")
                    f.write(f"Description: {description}\n\n")
                    f.write(f"Validation Error:\n{content}\n")

            print(f"{status} Test {test_id:2d}: {description[:60]}")

        # Summary
        total = len(test_cases)
        success_rate = (passed / total * 100) if total > 0 else 0

        summary = {
            "provider_id": self.provider_id,
            "diagram_type": self.diagram_type,
            "total_tests": total,
            "passed": passed,
            "failed": failed,
            "success_rate": success_rate,
            "test_name": test_name,
        }

        print(f"\n{'=' * 80}")
        print(f"SUMMARY: {passed}/{total} tests passed ({success_rate:.1f}%)")
        print(f"Provider: {self.provider_id}")
        print(f"{'=' * 80}\n")

        # Save validation results
        self._save_validation_results()

        return summary

    def _save_validation_results(self):
        """Save validation results as JSON"""
        validation_file = self.test_output_dir / "errors" / "validation_results.json"
        validation_file.parent.mkdir(parents=True, exist_ok=True)

        with open(validation_file, "w", encoding="utf-8") as f:
            json.dump(self.results, f, indent=2)

    def get_results(self) -> list:
        """Get detailed test results"""
        return self.results
