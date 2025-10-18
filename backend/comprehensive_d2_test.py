"""
Comprehensive D2 Test Runner
This script will:
1. Check for existing diagram code in history files
2. Generate code if not available
3. Validate all 25 D2 diagrams using D2 CLI
4. Save validation errors to files
5. Generate SVG output for all valid diagrams
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
            timeout=10
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

def render_d2_with_cli(d2_code: str, output_path: str) -> Tuple[bool, str]:
    """
    Render D2 code to SVG using the D2 CLI
    
    Args:
        d2_code (str): The D2 code to render
        output_path (str): Path to save the SVG output
        
    Returns:
        Tuple[bool, str]: (success, error_message)
    """
    # Create temporary input file
    with tempfile.NamedTemporaryFile(mode='w', suffix='.d2', delete=False) as temp_file:
        temp_file_name = temp_file.name
        temp_file.write(d2_code)
        temp_file.flush()
    
    try:
        # Run D2 to generate SVG
        result = subprocess.run(
            ['d2', temp_file_name, output_path],
            capture_output=True,
            text=True,
            check=True,
            timeout=30
        )
        
        # Check if output file was created
        if os.path.exists(output_path) and os.path.getsize(output_path) > 0:
            return (True, "")
        else:
            return (False, "D2 produced no output")
            
    except subprocess.CalledProcessError as e:
        error_msg = e.stderr.strip() or e.stdout.strip() or "D2 rendering failed"
        return (False, f"D2 rendering error: {error_msg}")
        
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

def save_history_file(test_id: int, test_name: str, description: str, diagram_code: str, history_dir: str):
    """Save the generated diagram code to a history file"""
    safe_name = test_name.replace(' ', '_').replace(':', '').replace('/', '_').replace('(', '').replace(')', '')
    history_filename = f"test_{test_id:03d}_id_{test_id}_{safe_name}.json"
    history_path = os.path.join(history_dir, history_filename)
    
    history_record = {
        "test_id": test_id,
        "test_name": test_name,
        "description": description,
        "timestamp": datetime.now().isoformat(),
        "request": {
            "prompt": description,
            "diagram_type": "d2",
            "output_format": "svg"
        },
        "parsed_result": {
            "diagram_code": diagram_code,
            "diagram_type": "d2",
            "ai_generated": True
        },
        "success": True
    }
    
    with open(history_path, 'w') as f:
        json.dump(history_record, f, indent=2)
    
    return history_path

def save_error_file(test_id: int, test_name: str, description: str, diagram_code: str, error_msg: str, output_dir: str) -> str:
    """Save error details to a file"""
    safe_name = test_name.replace(' ', '_').replace(':', '').replace('/', '_').replace('(', '').replace(')', '')
    error_filename = f"test_{test_id:03d}_{safe_name}_error.txt"
    error_path = os.path.join(output_dir, error_filename)
    
    with open(error_path, 'w') as f:
        f.write(f"Test ID: {test_id}\n")
        f.write(f"Test Name: {test_name}\n")
        f.write(f"Description: {description}\n")
        f.write(f"\nValidation Error:\n")
        f.write(error_msg)
        f.write(f"\n\nDiagram Code:\n")
        f.write(diagram_code)
    
    return error_path

def process_test(test_case: Dict[str, Any], output_dir: str, history_dir: str, svg_dir: str) -> Dict[str, Any]:
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
        "svg_file": "",
        "history_file": ""
    }
    
    # Check if we have a history file with generated code
    history_file = f"{history_dir}/test_{result['test_id']:03d}_id_{result['test_id']}"
    
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
                    result["history_file"] = os.path.basename(file_path)
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
            result["history_file"] = save_history_file(
                test_case["id"], 
                test_case["name"], 
                test_case["description"], 
                diagram_code, 
                history_dir
            )
            print(f"  Generated code ({len(diagram_code)} chars)")
        else:
            result["validation_error"] = f"Failed to generate code: {code_or_error}"
            result["error_file"] = save_error_file(
                test_case["id"], 
                test_case["name"], 
                test_case["description"], 
                "", 
                result["validation_error"], 
                output_dir
            )
            return result
    
    result["has_code"] = True
    result["diagram_code"] = diagram_code
    
    # Validate the D2 code
    print(f"  Validating D2 code...")
    is_valid, error_msg = validate_d2_with_cli(diagram_code)
    result["is_valid"] = is_valid
    result["validation_error"] = error_msg
    
    if not is_valid:
        result["error_file"] = save_error_file(
            test_case["id"], 
            test_case["name"], 
            test_case["description"], 
            diagram_code, 
            error_msg, 
            output_dir
        )
        print(f"  [FAIL] Validation failed: {error_msg[:100]}..." if len(error_msg) > 100 else f"  [FAIL] Validation failed: {error_msg}")
    else:
        print(f"  [PASS] Validation successful")
        
        # Generate SVG
        print(f"  Generating SVG...")
        safe_name = test_case["name"].replace(' ', '_').replace(':', '').replace('/', '_').replace('(', '').replace(')', '')
        svg_filename = f"test_{test_case['id']:03d}_{safe_name}.svg"
        svg_path = os.path.join(svg_dir, svg_filename)
        
        success, error_msg = render_d2_with_cli(diagram_code, svg_path)
        
        if success:
            result["svg_file"] = svg_filename
            print(f"  [PASS] SVG generated: {svg_filename}")
        else:
            print(f"  [FAIL] SVG generation failed: {error_msg[:100]}..." if len(error_msg) > 100 else f"  [FAIL] SVG generation failed: {error_msg}")
    
    return result

def main():
    """Main function to process all 25 tests"""
    
    print("Comprehensive D2 Test Runner - Processing all 25 tests")
    print("=" * 60)
    
    # Check D2 CLI availability
    try:
        result = subprocess.run(['d2', '--version'], capture_output=True, text=True, check=True, timeout=5)
        print(f"\n[D2 CLI] Version: {result.stdout.strip()}")
    except Exception as e:
        print(f"\n[ERROR] D2 CLI not available: {e}")
        return
    
    # Load test definitions
    test_file = "tests/Diagrams/test.json"
    if not os.path.exists(test_file):
        print(f"\nERROR: Test file not found: {test_file}")
        return
    
    with open(test_file, 'r') as f:
        test_data = json.load(f)
    
    # Create output directories
    output_dir = "backend/test_results_25/comprehensive"
    history_dir = "backend/tests/Diagrams/history"
    svg_dir = "backend/tests/Diagrams/history/svg"
    
    os.makedirs(output_dir, exist_ok=True)
    os.makedirs(history_dir, exist_ok=True)
    os.makedirs(svg_dir, exist_ok=True)
    
    # Process all tests
    results: List[Dict[str, Any]] = []
    test_cases = test_data["d2_capability_tests"]
    
    print(f"\nProcessing {len(test_cases)} tests...")
    
    for test_case in test_cases:
        print(f"\n{'='*60}")
        print(f"Test {test_case['id']}: {test_case['name']}")
        print(f"{'='*60}")
        
        result = process_test(test_case, output_dir, history_dir, svg_dir)
        results.append(result)
    
    # Generate summary report
    print("\n" + "=" * 60)
    print("COMPREHENSIVE TEST SUMMARY")
    print("=" * 60)
    
    total_tests = len(results)
    tests_with_code = sum(1 for r in results if r["has_code"])
    tests_generated = sum(1 for r in results if r["generated"])
    tests_valid = sum(1 for r in results if r["is_valid"])
    tests_invalid = tests_with_code - tests_valid
    tests_with_svg = sum(1 for r in results if r["svg_file"])
    tests_with_errors = sum(1 for r in results if r["error_file"])
    
    print(f"\nTotal tests: {total_tests}")
    print(f"Tests with diagram code: {tests_with_code}")
    print(f"Tests generated: {tests_generated}")
    print(f"Tests valid: {tests_valid}")
    print(f"Tests invalid: {tests_invalid}")
    print(f"Tests with SVG: {tests_with_svg}")
    print(f"Tests with errors: {tests_with_errors}")
    
    # Calculate success rate
    if tests_with_code > 0:
        success_rate = (tests_valid / tests_with_code) * 100
        print(f"\nSuccess rate: {success_rate:.1f}%")
    
    # Save detailed results
    results_file = os.path.join(output_dir, "comprehensive_test_results.json")
    with open(results_file, 'w') as f:
        json.dump({
            "timestamp": datetime.now().isoformat(),
            "summary": {
                "total_tests": total_tests,
                "tests_with_code": tests_with_code,
                "tests_generated": tests_generated,
                "tests_valid": tests_valid,
                "tests_invalid": tests_invalid,
                "tests_with_svg": tests_with_svg,
                "tests_with_errors": tests_with_errors,
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
    
    # List tests without SVG
    if tests_with_code - tests_with_svg > 0:
        print(f"\nTests without SVG ({tests_with_code - tests_with_svg}):")
        for result in results:
            if result["has_code"] and not result["svg_file"]:
                print(f"  - Test {result['test_id']}: {result['test_name']}")
    
    print("\n" + "=" * 60)
    print("COMPREHENSIVE D2 TEST COMPLETE")
    print("=" * 60)

if __name__ == "__main__":
    main()