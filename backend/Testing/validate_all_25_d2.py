"""
Validate all 25 D2 tests and capture any errors
This script will:
1. Load each test case from test.json
2. Generate D2 code if not available
3. Validate each D2 code using D2 CLI
4. Save validation errors to files
"""

import json
import os
import sys
import subprocess
import tempfile
import requests
from datetime import datetime
from typing import Dict, List, Any, Tuple

def validate_d2_with_cli(d2_code: str) -> Tuple[bool, str]:
    """
    Validate D2 code using the D2 CLI

    Args:
        d2_code (str): The D2 code to validate

    Returns:
        Tuple[bool, str]: (is_valid, error_message)
    """
    # Create temporary input file
    with tempfile.NamedTemporaryFile(mode='w', suffix='.d2', delete=False) as temp_file:
        temp_file_name = temp_file.name
        temp_file.write(d2_code)
        temp_file.flush()

    try:
        # Run D2 to validate using stdout output
        result = subprocess.run(
            ['d2', temp_file_name, '-'],
            capture_output=True,
            text=True,
            check=True,
            timeout=120
        )

        return (True, "D2 Syntax is Valid.")

    except subprocess.CalledProcessError as e:
        error_msg = e.stderr.strip() or e.stdout.strip() or "D2 validation failed"
        return (False, error_msg)

    except subprocess.TimeoutExpired:
        return (False, "D2 validation timed out")

    except FileNotFoundError:
        return (False, "D2 executable not found")

    except Exception as e:
        return (False, f"Unexpected error: {str(e)}")

    finally:
        # Clean up temporary file
        try:
            if os.path.exists(temp_file_name):
                os.unlink(temp_file_name)
        except Exception:
            pass

def render_svg_with_d2(d2_code: str, output_path: str) -> Tuple[bool, str]:
    """
    Render D2 code to SVG file using D2 CLI

    Args:
        d2_code (str): The D2 code to render
        output_path (str): Path where SVG should be saved

    Returns:
        Tuple[bool, str]: (success, error_message)
    """
    # Create temporary input file
    with tempfile.NamedTemporaryFile(mode='w', suffix='.d2', delete=False) as temp_file:
        temp_file_name = temp_file.name
        temp_file.write(d2_code)
        temp_file.flush()

    try:
        # Run D2 to render SVG
        result = subprocess.run(
            ['d2', temp_file_name, output_path],
            capture_output=True,
            text=True,
            check=True,
            timeout=120
        )

        return (True, "SVG rendered successfully.")

    except subprocess.CalledProcessError as e:
        error_msg = e.stderr.strip() or e.stdout.strip() or "D2 rendering failed"
        return (False, error_msg)

    except subprocess.TimeoutExpired:
        return (False, "D2 rendering timed out")

    except FileNotFoundError:
        return (False, "D2 executable not found")

    except Exception as e:
        return (False, f"Unexpected error: {str(e)}")

    finally:
        # Clean up temporary file
        try:
            if os.path.exists(temp_file_name):
                os.unlink(temp_file_name)
        except Exception:
            pass

def generate_diagram_code(prompt: str, test_id: int) -> Tuple[bool, str]:
    """
    Generate D2 diagram code using the MCP API
    
    Args:
        prompt (str): The prompt to generate diagram from
        test_id (int): Test ID for logging
        
    Returns:
        Tuple[bool, str]: (success, diagram_code or error_message)
    """
    try:
        response = requests.post(
            "http://localhost:8003/mcp/tools/generate_diagram",
            json={"prompt": prompt, "diagram_type": "d2"},
            timeout=60
        )
        
        if response.status_code != 200:
            return (False, f"API error: {response.status_code}")
        
        data = response.json()
        
        # Parse MCP response
        text_content = data.get('content', [{}])[0].get('text', '')
        result_data = json.loads(text_content)
        
        if 'error' in result_data:
            return (False, result_data['error'])
        
        if 'diagram_code' not in result_data:
            return (False, "No diagram code in response")
        
        return (True, result_data['diagram_code'])
        
    except Exception as e:
        return (False, f"Generation error: {str(e)}")

def process_test(test_case: Dict[str, Any], output_dir: str, script_dir: str) -> Dict[str, Any]:
    """Process a single test case"""

    result = {
        "test_id": test_case["id"],
        "test_name": test_case["name"],
        "description": test_case["description"],
        "has_code": False,
        "diagram_code": "",
        "is_valid": False,
        "validation_error": "",
        "generated": False,
        "error_file": "",
        "svg_file": ""
    }

    # Check if we have a history file with generated code
    # History files are in the same directory as the script
    history_file = os.path.join(script_dir, "history", f"test_{result['test_id']:03d}_id_{result['test_id']}")
    
    # Try different possible file extensions
    possible_files = [
        f"{history_file}.json",
        history_file,
    ]
    
    diagram_code = None
    for file_path in possible_files:
        if os.path.exists(file_path):
            try:
                with open(file_path, 'r') as f:
                    data = json.load(f)
                    # Extract diagram code from the response
                    if "parsed_result" in data and "diagram_code" in data["parsed_result"]:
                        diagram_code = data["parsed_result"]["diagram_code"]
                    elif "diagram_code" in data:
                        diagram_code = data["diagram_code"]
                    break
            except Exception as e:
                print(f"  Warning: Could not read {file_path}: {e}")
    
    if not diagram_code:
        # Generate code from the prompt
        print(f"  No history file found, generating code...")
        success, code_or_error = generate_diagram_code(test_case["description"], test_case["id"])
        
        if success:
            diagram_code = code_or_error
            result["generated"] = True
            print(f"  Generated code ({len(diagram_code)} chars)")
        else:
            result["validation_error"] = f"Failed to generate code: {code_or_error}"
            result["error_file"] = save_error_file(result, output_dir)
            return result
    
    result["has_code"] = True
    result["diagram_code"] = diagram_code

    # Validate the D2 code
    print(f"  Validating D2 code...")
    is_valid, error_msg = validate_d2_with_cli(diagram_code)
    result["is_valid"] = is_valid
    result["validation_error"] = error_msg

    if not is_valid:
        result["error_file"] = save_error_file(result, output_dir)
        print(f"  [FAIL] Validation failed: {error_msg[:100]}..." if len(error_msg) > 100 else f"  [FAIL] Validation failed: {error_msg}")
    else:
        print(f"  [PASS] Validation successful")

        # Render SVG file if validation passed
        # Clean test name for filename (remove special characters)
        safe_test_name = "".join(c if c.isalnum() or c in (' ', '-', '_') else '_' for c in result['test_name'])
        safe_test_name = safe_test_name.replace(' ', '_')
        svg_filename = f"test_{result['test_id']:03d}_{safe_test_name}.svg"
        svg_path = os.path.join(os.path.dirname(output_dir), "svg", svg_filename)

        # Create SVG directory if it doesn't exist
        os.makedirs(os.path.dirname(svg_path), exist_ok=True)

        print(f"  Rendering SVG...")
        svg_success, svg_error = render_svg_with_d2(diagram_code, svg_path)

        if svg_success:
            result["svg_file"] = svg_filename
            print(f"  [SVG] Saved to: {svg_filename}")
        else:
            print(f"  [SVG WARN] Failed to render: {svg_error}")
            result["svg_file"] = ""

    return result

def save_error_file(result: Dict[str, Any], output_dir: str) -> str:
    """Save error details to a file"""
    error_filename = f"test_{result['test_id']:03d}_error.txt"
    error_path = os.path.join(output_dir, error_filename)
    
    with open(error_path, 'w') as f:
        f.write(f"Test ID: {result['test_id']}\n")
        f.write(f"Test Name: {result['test_name']}\n")
        f.write(f"Description: {result['description']}\n")
        f.write(f"Generated: {result['generated']}\n")
        f.write(f"\nValidation Error:\n")
        f.write(result['validation_error'])
        f.write(f"\n\nDiagram Code:\n")
        f.write(result['diagram_code'])
    
    return error_filename

def main():
    """Main function to process all tests"""

    # Determine which test file to use
    test_file = None
    test_label = ""

    # Check command line argument
    if len(sys.argv) > 1:
        arg = sys.argv[1].lower()
        if arg in ['25', 'test25']:
            test_file = "test25.json"
            test_label = "25"
        elif arg in ['50', 'test50']:
            test_file = "test50.json"
            test_label = "50"
        else:
            print(f"ERROR: Invalid argument '{sys.argv[1]}'. Use '25' or '50'")
            print("Usage: python validate_all_25_d2.py [25|50]")
            return
    else:
        # Default to test25.json if no argument provided
        test_file = "test25.json"
        test_label = "25"

    # Get the directory where this script is located
    script_dir = os.path.dirname(os.path.abspath(__file__))
    test_file_path = os.path.join(script_dir, test_file)

    print(f"D2 CLI Validator - Processing test{test_label} tests")
    print("=" * 60)

    # Check D2 CLI availability
    try:
        result = subprocess.run(['d2', '--version'], capture_output=True, text=True, check=True, timeout=5)
        print(f"\n[D2 CLI] Version: {result.stdout.strip()}")
    except Exception as e:
        print(f"\n[ERROR] D2 CLI not available: {e}")
        return

    # Load test definitions
    if not os.path.exists(test_file_path):
        print(f"\nERROR: Test file not found: {test_file_path}")
        return

    print(f"\nLoading tests from: {test_file_path}")

    with open(test_file_path, 'r') as f:
        test_data = json.load(f)

    # Create output directory
    output_dir = os.path.join(script_dir, f"test_results_{test_label}", "errors")
    os.makedirs(output_dir, exist_ok=True)
    
    # Process all tests
    results: List[Dict[str, Any]] = []
    test_cases = test_data["d2_capability_tests"]
    
    print(f"\nProcessing {len(test_cases)} tests...")
    
    for test_case in test_cases:
        print(f"\n{'='*60}")
        print(f"Test {test_case['id']}: {test_case['name']}")
        print(f"{'='*60}")

        result = process_test(test_case, output_dir, script_dir)
        results.append(result)
    
    # Generate summary report
    print("\n" + "=" * 60)
    print("VALIDATION SUMMARY")
    print("=" * 60)
    
    total_tests = len(results)
    tests_with_code = sum(1 for r in results if r["has_code"])
    tests_valid = sum(1 for r in results if r["is_valid"])
    tests_generated = sum(1 for r in results if r["generated"])
    tests_invalid = tests_with_code - tests_valid
    
    print(f"\nTotal tests: {total_tests}")
    print(f"Tests with diagram code: {tests_with_code}")
    print(f"Tests generated: {tests_generated}")
    print(f"Tests valid: {tests_valid}")
    print(f"Tests invalid: {tests_invalid}")
    
    # Calculate success rate
    if tests_with_code > 0:
        success_rate = (tests_valid / tests_with_code) * 100
        print(f"\nSuccess rate: {success_rate:.1f}%")
    
    # Save detailed results
    results_file = os.path.join(output_dir, "validation_results.json")
    with open(results_file, 'w') as f:
        json.dump({
            "timestamp": datetime.now().isoformat(),
            "summary": {
                "total_tests": total_tests,
                "tests_with_code": tests_with_code,
                "tests_generated": tests_generated,
                "tests_valid": tests_valid,
                "tests_invalid": tests_invalid,
                "success_rate": success_rate if tests_with_code > 0 else 0
            },
            "results": results
        }, f, indent=2)
    
    print(f"\nDetailed results saved to: {results_file}")
    
    # List failed tests
    if tests_invalid > 0:
        print(f"\nFailed tests ({tests_invalid}):")
        for result in results:
            if result["has_code"] and not result["is_valid"]:
                print(f"  - Test {result['test_id']}: {result['test_name']}")
                print(f"    Error file: {result['error_file']}")
    
    print("\n" + "=" * 60)
    print("D2 VALIDATION COMPLETE")
    print("=" * 60)

if __name__ == "__main__":
    main()