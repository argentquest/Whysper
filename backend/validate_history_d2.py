"""
Validate all D2 diagrams from history files and capture any errors
This script will:
1. Load all D2 diagram code from history files
2. Validate each D2 code using D2 CLI
3. Save validation errors to files
4. Generate a summary report
"""

import json
import os
import sys
import subprocess
import tempfile
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
    
    return error_filename

def save_d2_file(test_id: int, test_name: str, diagram_code: str, output_dir: str) -> str:
    """Save D2 code to a file"""
    safe_name = test_name.replace(' ', '_').replace(':', '').replace('/', '_').replace('(', '').replace(')', '')
    d2_filename = f"test_{test_id:03d}_{safe_name}.d2"
    d2_path = os.path.join(output_dir, d2_filename)
    
    with open(d2_path, 'w') as f:
        f.write(diagram_code)
    
    return d2_filename

def main():
    """Main function to validate all D2 diagrams from history files"""
    
    print("D2 History Validator - Validating all D2 diagrams from history")
    print("=" * 60)
    
    # Check D2 CLI availability
    try:
        result = subprocess.run(['d2', '--version'], capture_output=True, text=True, check=True, timeout=5)
        print(f"\n[D2 CLI] Version: {result.stdout.strip()}")
    except Exception as e:
        print(f"\n[ERROR] D2 CLI not available: {e}")
        return
    
    # Find all history files
    history_dirs = [
        "backend/tests/Diagrams/history",
        "backend/backend/tests/Diagrams/history"
    ]
    
    history_files = []
    for history_dir in history_dirs:
        if os.path.exists(history_dir):
            for filename in os.listdir(history_dir):
                if filename.startswith("test_") and filename.endswith(".json"):
                    history_files.append(os.path.join(history_dir, filename))
    
    if not history_files:
        print(f"\n[ERROR] No history files found in: {', '.join(history_dirs)}")
        return
    
    history_files.sort()
    print(f"\n[INFO] Found {len(history_files)} history files")
    
    # Create output directories
    output_dir = "backend/test_results_25/history_validation"
    d2_dir = os.path.join(output_dir, "d2_code")
    errors_dir = os.path.join(output_dir, "errors")
    
    os.makedirs(output_dir, exist_ok=True)
    os.makedirs(d2_dir, exist_ok=True)
    os.makedirs(errors_dir, exist_ok=True)
    
    # Process all history files
    results: List[Dict[str, Any]] = []
    
    for history_file in history_files:
        try:
            # Load the history file
            with open(history_file, 'r') as f:
                data = json.load(f)
            
            test_id = data.get("test_id")
            test_name = data.get("test_name", f"Test {test_id}")
            description = data.get("description", "")
            
            # Extract diagram code
            diagram_code = None
            if "parsed_result" in data and "diagram_code" in data["parsed_result"]:
                diagram_code = data["parsed_result"]["diagram_code"]
            elif "diagram_code" in data:
                diagram_code = data["diagram_code"]
            
            if not diagram_code:
                result = {
                    "test_id": test_id,
                    "test_name": test_name,
                    "description": description,
                    "has_code": False,
                    "is_valid": False,
                    "validation_error": "No diagram code found",
                    "error_file": "",
                    "d2_file": ""
                }
                results.append(result)
                continue
            
            result = {
                "test_id": test_id,
                "test_name": test_name,
                "description": description,
                "has_code": True,
                "diagram_code": diagram_code,
                "is_valid": False,
                "validation_error": "",
                "error_file": "",
                "d2_file": ""
            }
            
            print(f"\n[TEST] Test {test_id}: {test_name}")
            
            # Validate the D2 code
            is_valid, error_msg = validate_d2_with_cli(diagram_code)
            result["is_valid"] = is_valid
            result["validation_error"] = error_msg
            
            # Save D2 code to file
            d2_filename = save_d2_file(test_id, test_name, diagram_code, d2_dir)
            result["d2_file"] = d2_filename
            
            if is_valid:
                print(f"  [PASS] D2 code is valid")
            else:
                print(f"  [FAIL] D2 code is invalid: {error_msg[:100]}..." if len(error_msg) > 100 else f"  [FAIL] D2 code is invalid: {error_msg}")
                error_filename = save_error_file(test_id, test_name, description, diagram_code, error_msg, errors_dir)
                result["error_file"] = error_filename
            
            results.append(result)
            
        except Exception as e:
            print(f"  [ERROR] Failed to process {history_file}: {e}")
    
    # Generate summary report
    print("\n" + "=" * 60)
    print("VALIDATION SUMMARY")
    print("=" * 60)
    
    total_tests = len(results)
    tests_with_code = sum(1 for r in results if r["has_code"])
    tests_valid = sum(1 for r in results if r["is_valid"])
    tests_invalid = tests_with_code - tests_valid
    tests_with_errors = sum(1 for r in results if r["error_file"])
    
    print(f"\nTotal tests: {total_tests}")
    print(f"Tests with diagram code: {tests_with_code}")
    print(f"Tests valid: {tests_valid}")
    print(f"Tests invalid: {tests_invalid}")
    print(f"Tests with error files: {tests_with_errors}")
    
    # Calculate success rate
    if tests_with_code > 0:
        success_rate = (tests_valid / tests_with_code) * 100
        print(f"\nSuccess rate: {success_rate:.1f}%")
    
    # Save detailed results
    results_file = os.path.join(output_dir, "history_validation_results.json")
    with open(results_file, 'w') as f:
        json.dump({
            "timestamp": datetime.now().isoformat(),
            "summary": {
                "total_tests": total_tests,
                "tests_with_code": tests_with_code,
                "tests_valid": tests_valid,
                "tests_invalid": tests_invalid,
                "tests_with_errors": tests_with_errors,
                "success_rate": success_rate if tests_with_code > 0 else 0
            },
            "results": results
        }, f, indent=2)
    
    print(f"\nDetailed results saved to: {results_file}")
    print(f"D2 code files saved to: {d2_dir}")
    
    # List failed tests
    if tests_invalid > 0:
        print(f"\nFailed tests ({tests_invalid}):")
        for result in results:
            if result["has_code"] and not result["is_valid"]:
                print(f"  - Test {result['test_id']}: {result['test_name']}")
                print(f"    Error file: {result['error_file']}")
                print(f"    D2 file: {result['d2_file']}")
    
    print("\n" + "=" * 60)
    print("D2 HISTORY VALIDATION COMPLETE")
    print("=" * 60)

if __name__ == "__main__":
    main()