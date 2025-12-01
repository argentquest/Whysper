"""
Validate all 25 Mermaid tests using the Kroki Mermaid Provider Endpoint
"""

import json
import os
import sys
import requests
from datetime import datetime
from typing import Dict, List, Any, Tuple


def generate_diagram_with_llm(
    prompt: str, test_id: int, diagram_type: str = "mermaid", provider: str = "krokimermaid"
) -> Tuple[bool, str, str]:
    """Generate and render diagram using the MVP Diagram Generation Endpoint"""
    try:
        response = requests.post(
            "http://localhost:8003/api/v1/diagrams/generate",
            json={"prompt": prompt, "diagram_type": diagram_type, "provider": provider, "output_format": "svg"},
            timeout=120,
        )

        if response.status_code != 200:
            return (False, f"API error: {response.status_code}", "HTTP Error")

        data = response.json()

        # Check if generation was successful
        error_info = data.get("error_info", {})
        if error_info.get("has_error", False):
            error = error_info.get("error_message", "Unknown error")
            return (False, error, error)

        # Get SVG content from response
        image_data = data.get("image_data", "")
        if not image_data:
            return (False, "No image data in response", "Invalid response")

        try:
            import base64
            import gzip

            if isinstance(image_data, str):
                try:
                    decoded_bytes = base64.b64decode(image_data)
                    if decoded_bytes[:2] == b"\x1f\x8b":
                        svg_content = gzip.decompress(decoded_bytes).decode("utf-8")
                    else:
                        svg_content = decoded_bytes.decode("utf-8")
                except BaseException:
                    svg_content = image_data
            else:
                if isinstance(image_data, bytes):
                    if image_data[:2] == b"\x1f\x8b":
                        svg_content = gzip.decompress(image_data).decode("utf-8")
                    else:
                        try:
                            svg_content = image_data.decode("utf-8")
                        except UnicodeDecodeError:
                            svg_content = image_data.decode("latin-1", errors="replace")
                else:
                    svg_content = str(image_data)

            if "<svg" not in svg_content:
                return (False, "Generated content is not valid SVG", "Invalid SVG")
            return (True, svg_content, "")
        except Exception as decode_error:
            return (False, f"Failed to decode SVG: {str(decode_error)}", str(decode_error))

    except Exception as e:
        return (False, f"Generation error: {str(e)}", str(e))


def process_test(test_case: Dict[str, Any], output_dir: str, script_dir: str, provider: str) -> Dict[str, Any]:
    """Process a single test case"""

    result = {
        "test_id": test_case["id"],
        "test_name": test_case["name"],
        "description": test_case["description"],
        "has_svg": False,
        "is_valid": False,
        "validation_error": "",
        "error_file": "",
        "svg_file": "",
    }

    print("  Rendering diagram via provider endpoint...")

    prompt = test_case["description"]

    success, svg_or_error, validation_error = generate_diagram_with_llm(prompt, test_case["id"], "mermaid", provider)

    if not success:
        result["is_valid"] = False
        result["validation_error"] = svg_or_error
        result["error_file"] = save_error_file(result, output_dir)
        print(
            f"  [FAIL] Rendering failed: {svg_or_error[:100]}..."
            if len(svg_or_error) > 100
            else f"  [FAIL] Rendering failed: {svg_or_error}"
        )
        return result

    svg_content = svg_or_error
    safe_test_name = "".join(c if c.isalnum() or c in (" ", "-", "_") else "_" for c in result["test_name"])
    safe_test_name = safe_test_name.replace(" ", "_")
    svg_filename = f"test_{result['test_id']:03d}_{safe_test_name}.svg"
    svg_path = os.path.join(os.path.dirname(output_dir), "svg", svg_filename)

    os.makedirs(os.path.dirname(svg_path), exist_ok=True)

    try:
        if isinstance(svg_content, bytes):
            if svg_content[:2] == b"\x1f\x8b":
                import gzip

                svg_content = gzip.decompress(svg_content).decode("utf-8")
            else:
                try:
                    svg_content = svg_content.decode("utf-8")
                except UnicodeDecodeError:
                    svg_content = svg_content.decode("latin-1", errors="replace")
        elif isinstance(svg_content, str):
            svg_content = svg_content.encode("utf-8", errors="replace").decode("utf-8")

        with open(svg_path, "w", encoding="utf-8") as f:
            f.write(svg_content)
        result["has_svg"] = True
        result["svg_file"] = svg_filename
        print(f"  [SVG] Saved to: {svg_filename}")
    except Exception as e:
        print(f"  [SVG ERROR] Failed to save: {e}")
        result["svg_file"] = ""

    result["is_valid"] = True
    result["validation_error"] = validation_error if validation_error else "Mermaid Syntax is Valid"

    print("  [PASS] Diagram rendered successfully")

    return result


def save_error_file(result: Dict[str, Any], output_dir: str) -> str:
    """Save error details to a file"""
    error_filename = f"test_{result['test_id']:03d}_error.txt"
    error_path = os.path.join(output_dir, error_filename)

    with open(error_path, "w") as f:
        f.write(f"Test ID: {result['test_id']}\n")
        f.write(f"Test Name: {result['test_name']}\n")
        f.write(f"Description: {result['description']}\n")
        f.write("\nValidation Error:\n")
        f.write(result["validation_error"])

    return error_filename


def main():
    """Main function to process all tests"""

    test_file = None
    test_label = ""

    if len(sys.argv) > 1:
        arg = sys.argv[1].lower()
        if arg in ["25", "test25"]:
            test_file = "test25.json"
            test_label = "25"
        elif arg in ["50", "test50"]:
            test_file = "test50.json"
            test_label = "50"
        else:
            print(f"ERROR: Invalid argument '{sys.argv[1]}'. Use '25' or '50'")
            print("Usage: python validate_all_25_krokimermaid.py [25|50]")
            return
    else:
        test_file = "test25.json"
        test_label = "25"

    script_dir = os.path.dirname(os.path.abspath(__file__))
    test_file_path = os.path.join(script_dir, test_file)

    print(f"Kroki Mermaid Provider Renderer - Processing test{test_label} tests")
    print("=" * 60)

    try:
        response = requests.get("http://localhost:8003/api/v1/diagrams/v2/health", timeout=5)
        if response.status_code == 200:
            data = response.json()
            print(f"\n[Backend] Status: {data.get('status', 'unknown')}")
            print(f"[Providers] Available: {data.get('available_providers', 0)}")
    except Exception as e:
        print(f"\n[ERROR] Backend not available: {e}")
        print("Make sure the backend is running at http://localhost:8003")
        return

    if not os.path.exists(test_file_path):
        print(f"\nERROR: Test file not found: {test_file_path}")
        return

    print(f"\nLoading tests from: {test_file_path}")

    with open(test_file_path, "r") as f:
        test_data = json.load(f)

    output_dir = os.path.join(script_dir, f"test_results_{test_label}", "errors")
    os.makedirs(output_dir, exist_ok=True)

    results: List[Dict[str, Any]] = []
    test_cases = test_data["mermaid_capability_tests"]

    print(f"\nProcessing {len(test_cases)} tests...")

    for test_case in test_cases:
        print(f"\n{'=' * 60}")
        print(f"Test {test_case['id']}: {test_case['name']}")
        print(f"{'=' * 60}")

        result = process_test(test_case, output_dir, script_dir, "krokimermaid")
        results.append(result)

    print("\n" + "=" * 60)
    print("VALIDATION SUMMARY")
    print("=" * 60)

    total_tests = len(results)
    tests_with_svg = sum(1 for r in results if r["has_svg"])
    tests_valid = sum(1 for r in results if r["is_valid"])
    tests_invalid = total_tests - tests_valid

    print(f"\nTotal tests: {total_tests}")
    print(f"Tests with SVG: {tests_with_svg}")
    print(f"Tests valid: {tests_valid}")
    print(f"Tests invalid: {tests_invalid}")

    if total_tests > 0:
        success_rate = (tests_valid / total_tests) * 100
        print(f"\nSuccess rate: {success_rate:.1f}%")

    results_file = os.path.join(output_dir, "validation_results.json")
    with open(results_file, "w") as f:
        json.dump(
            {
                "timestamp": datetime.now().isoformat(),
                "summary": {
                    "total_tests": total_tests,
                    "tests_with_svg": tests_with_svg,
                    "tests_valid": tests_valid,
                    "tests_invalid": tests_invalid,
                    "success_rate": success_rate if total_tests > 0 else 0,
                },
                "results": results,
            },
            f,
            indent=2,
        )

    print(f"\nDetailed results saved to: {results_file}")

    if tests_invalid > 0:
        print(f"\nFailed tests ({tests_invalid}):")
        for result in results:
            if not result["is_valid"]:
                print(f"  - Test {result['test_id']}: {result['test_name']}")
                if result["error_file"]:
                    print(f"    Error file: {result['error_file']}")

    print("\n" + "=" * 60)
    print("MERMAID VALIDATION COMPLETE")
    print("=" * 60)


if __name__ == "__main__":
    main()
