"""
Simple D2 Server Validation
Validates that the D2 server is working correctly with temperature 0.1
"""

import json
import os
import subprocess
import tempfile
import requests
from typing import Tuple


def validate_d2_with_cli(d2_code: str) -> Tuple[bool, str]:
    # Create a temporary file to store D2 code for CLI validation
    # This allows us to pass the code to the D2 CLI for syntax checking
    with tempfile.NamedTemporaryFile(mode="w", suffix=".d2", delete=False) as temp_file:
        temp_file_name = temp_file.name
        temp_file.write(d2_code)
        temp_file.flush()

    try:
        # Run D2 CLI to validate the code, capturing any output or errors
        # Uses subprocess to execute D2 command-line tool and check syntax
        result = subprocess.run(["d2", temp_file_name, "-"], capture_output=True, text=True, check=True, timeout=120)

        return (True, "D2 Syntax is Valid.")

    except subprocess.CalledProcessError as e:
        # Handle errors from D2 CLI execution (non-zero exit code)
        error_msg = e.stderr.strip() or e.stdout.strip() or "D2 validation failed"
        return (False, error_msg)

    except subprocess.TimeoutExpired:
        # Handle case where D2 validation takes too long
        return (False, "D2 validation timed out")

    except FileNotFoundError:
        # Handle scenario where D2 executable is not installed
        return (False, "D2 executable not found")

    except Exception as e:
        # Catch any other unexpected errors during validation
        return (False, f"Unexpected error: {str(e)}")

    finally:
        # Always attempt to clean up the temporary file
        # Prevents leaving behind temporary files
        try:
            if os.path.exists(temp_file_name):
                os.unlink(temp_file_name)
        except Exception:
            pass


def main():
    # Print header for validation process
    print("D2 Server Validation")
    print("=" * 60)

    # Check if D2 CLI is available and get its version
    # Ensures the CLI tool is installed and functioning
    try:
        result = subprocess.run(["d2", "--version"], capture_output=True, text=True, check=True, timeout=5)
        print(f"\n[D2 CLI] Version: {result.stdout.strip()}")
    except Exception as e:
        print(f"\n[ERROR] D2 CLI not available: {e}")
        return

    # Read temperature setting from environment file
    # Used to verify the specific configuration being tested
    try:
        with open("backend/.env", "r") as f:
            env_content = f.read()
            for line in env_content.split("\n"):
                if line.startswith("TEMPERATURE="):
                    temperature = line.split("=")[1].strip('"')
                    print(f"\n[SERVER] Temperature setting: {temperature}")
                    break
    except Exception as e:
        print(f"\n[ERROR] Could not read temperature setting: {e}")
        return

    # Prepare to test diagram generation via API
    print("\n[TEST] Generating simple D2 diagram...")

    test_prompt = "Generate a simple D2 diagram showing User -> Server -> Database"

    try:
        # Make API call to diagram generation endpoint
        # Sends a test prompt to generate a D2 diagram
        response = requests.post(
            "http://localhost:8003/mcp/tools/generate_diagram",
            json={"prompt": test_prompt, "diagram_type": "d2"},
            timeout=30,
        )

        # Check if API call was successful
        if response.status_code != 200:
            print(f"  [FAIL] API error: {response.status_code}")
            return

        # Parse the JSON response
        data = response.json()
        text_content = data.get("content", [{}])[0].get("text", "")
        result_data = json.loads(text_content)

        # Validate the generated diagram data
        if "error" in result_data:
            print(f"  [FAIL] Generation error: {result_data['error']}")
            return

        if "diagram_code" not in result_data:
            print("  [FAIL] No diagram code in response")
            return

        # Extract the generated D2 diagram code
        diagram_code = result_data["diagram_code"]
        print(f"  Generated code ({len(diagram_code)} chars)")

        # Validate the generated D2 code using CLI
        print("\n[TEST] Validating D2 code...")
        is_valid, error_msg = validate_d2_with_cli(diagram_code)

        # Report validation results
        if is_valid:
            print("  [PASS] D2 code is valid")
            print(f"\n[SUCCESS] D2 server is working correctly with temperature {temperature}")
            print("\nGenerated D2 code:")
            print("```")
            print(diagram_code)
            print("```")
        else:
            print(f"  [FAIL] D2 code is invalid: {error_msg}")

    except Exception as e:
        print(f"  [ERROR] Test failed: {e}")


if __name__ == "__main__":
    main()
