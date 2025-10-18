"""
Simple D2 Server Validation
Validates that the D2 server is working correctly with temperature 0.1
"""

import json
import os
import subprocess
import tempfile
import requests
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

def main():
    """Main function to validate the D2 server"""
    
    print("D2 Server Validation")
    print("=" * 60)
    
    # Check D2 CLI availability
    try:
        result = subprocess.run(['d2', '--version'], capture_output=True, text=True, check=True, timeout=5)
        print(f"\n[D2 CLI] Version: {result.stdout.strip()}")
    except Exception as e:
        print(f"\n[ERROR] D2 CLI not available: {e}")
        return
    
    # Check temperature setting
    try:
        with open('backend/.env', 'r') as f:
            env_content = f.read()
            for line in env_content.split('\n'):
                if line.startswith('TEMPERATURE='):
                    temperature = line.split('=')[1].strip('"')
                    print(f"\n[SERVER] Temperature setting: {temperature}")
                    break
    except Exception as e:
        print(f"\n[ERROR] Could not read temperature setting: {e}")
        return
    
    # Test a simple diagram generation
    print(f"\n[TEST] Generating simple D2 diagram...")
    
    test_prompt = "Generate a simple D2 diagram showing User -> Server -> Database"
    
    try:
        response = requests.post(
            "http://localhost:8003/mcp/tools/generate_diagram",
            json={"prompt": test_prompt, "diagram_type": "d2"},
            timeout=30
        )
        
        if response.status_code != 200:
            print(f"  [FAIL] API error: {response.status_code}")
            return
        
        data = response.json()
        text_content = data.get('content', [{}])[0].get('text', '')
        result_data = json.loads(text_content)
        
        if 'error' in result_data:
            print(f"  [FAIL] Generation error: {result_data['error']}")
            return
        
        if 'diagram_code' not in result_data:
            print(f"  [FAIL] No diagram code in response")
            return
        
        diagram_code = result_data['diagram_code']
        print(f"  Generated code ({len(diagram_code)} chars)")
        
        # Validate the D2 code
        print(f"\n[TEST] Validating D2 code...")
        is_valid, error_msg = validate_d2_with_cli(diagram_code)
        
        if is_valid:
            print(f"  [PASS] D2 code is valid")
            print(f"\n[SUCCESS] D2 server is working correctly with temperature {temperature}")
            print(f"\nGenerated D2 code:")
            print(f"```")
            print(diagram_code)
            print(f"```")
        else:
            print(f"  [FAIL] D2 code is invalid: {error_msg}")
            
    except Exception as e:
        print(f"  [ERROR] Test failed: {e}")

if __name__ == "__main__":
    main()