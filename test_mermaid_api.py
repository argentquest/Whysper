"""
Simple test script for Mermaid API endpoints
Tests the /api/v1/mermaid/* endpoints
"""

import requests
import json
import sys

# Fix encoding for Windows console
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')

BASE_URL = "http://localhost:8003/api/v1/mermaid"


def print_section(title: str):
    """Print a section header."""
    print("\n" + "=" * 80)
    print(f"  {title}")
    print("=" * 80)


def test_health():
    """Test the health endpoint"""
    print_section("Testing Mermaid Health Endpoint")

    try:
        response = requests.get(f"{BASE_URL}/health", timeout=5)
        print(f"Status Code: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")

        if response.status_code == 200:
            print("✅ Health check passed")
            return True
        else:
            print("❌ Health check failed")
            return False

    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to backend server")
        print("   Make sure the backend is running on port 8003")
        return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False


def test_info():
    """Test the info endpoint"""
    print_section("Testing Mermaid Info Endpoint")

    try:
        response = requests.get(f"{BASE_URL}/info", timeout=5)
        print(f"Status Code: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")

        if response.status_code == 200:
            data = response.json()
            if data.get("available"):
                print("✅ Mermaid CLI is available")
                return True
            else:
                print("❌ Mermaid CLI not available")
                return False
        else:
            print("❌ Info request failed")
            return False

    except Exception as e:
        print(f"❌ Error: {e}")
        return False


def test_validate_valid():
    """Test validation with valid Mermaid code"""
    print_section("Testing Mermaid Validation (Valid Code)")

    valid_code = """flowchart TD
    A[Start] --> B{Is it valid?}
    B -->|Yes| C[Render]
    B -->|No| D[Fix Syntax]
    D --> B
    C --> E[End]"""

    payload = {
        "code": valid_code,
        "auto_fix": True
    }

    try:
        response = requests.post(f"{BASE_URL}/validate", json=payload, timeout=10)
        print(f"Status Code: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")

        if response.status_code == 200:
            data = response.json()
            if data.get("is_valid"):
                print("✅ Validation passed")
                return True
            else:
                print("❌ Valid code marked as invalid")
                return False
        else:
            print("❌ Validation request failed")
            return False

    except Exception as e:
        print(f"❌ Error: {e}")
        return False


def test_validate_invalid():
    """Test validation with invalid Mermaid code (missing diagram type)"""
    print_section("Testing Mermaid Validation (Invalid Code with Auto-Fix)")

    invalid_code = """A[Start] --> B{Is it valid?}
    B -->|Yes| C[Render]
    B -->|No| D[Fix Syntax]"""

    payload = {
        "code": invalid_code,
        "auto_fix": True
    }

    try:
        response = requests.post(f"{BASE_URL}/validate", json=payload, timeout=30)
        print(f"Status Code: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")

        if response.status_code == 200:
            data = response.json()
            if data.get("auto_fixed"):
                print("✅ Auto-fix successful")
                print(f"\nFixed code:\n{data.get('fixed_code')}")
                return True
            else:
                print("⚠️  Code was invalid and could not be auto-fixed")
                return False
        else:
            print("❌ Validation request failed")
            return False

    except Exception as e:
        print(f"❌ Error: {e}")
        return False


def test_render():
    """Test rendering a Mermaid diagram to SVG"""
    print_section("Testing Mermaid Rendering to SVG")

    mermaid_code = """flowchart LR
    A[Client] --> B[Load Balancer]
    B --> C[Server 1]
    B --> D[Server 2]
    C --> E[Database]
    D --> E"""

    payload = {
        "code": mermaid_code,
        "return_svg": True,
        "save_to_file": False,
        "output_format": "svg"
    }

    try:
        response = requests.post(f"{BASE_URL}/render", json=payload, timeout=30)
        print(f"Status Code: {response.status_code}")

        if response.status_code == 200:
            data = response.json()
            print(f"Success: {data.get('success')}")
            print(f"Validation: {json.dumps(data.get('validation'), indent=2)}")
            print(f"Metadata: {json.dumps(data.get('metadata'), indent=2)}")

            if data.get('svg_content'):
                svg_length = len(data.get('svg_content', ''))
                print(f"SVG Content Length: {svg_length} characters")
                print(f"SVG Preview: {data.get('svg_content')[:200]}...")
                print("✅ Rendering successful")
                return True
            else:
                print("❌ No SVG content returned")
                print(f"Error: {data.get('error')}")
                return False
        else:
            print("❌ Render request failed")
            print(f"Response: {response.text}")
            return False

    except Exception as e:
        print(f"❌ Error: {e}")
        return False


def test_render_with_error():
    """Test rendering with a diagram that has errors"""
    print_section("Testing Mermaid Rendering (Error Handling)")

    bad_code = """flowchart TD
    A --> B
    B --> end"""  # 'end' is a reserved keyword

    payload = {
        "code": bad_code,
        "return_svg": True,
        "output_format": "svg"
    }

    try:
        response = requests.post(f"{BASE_URL}/render", json=payload, timeout=30)
        print(f"Status Code: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")

        if response.status_code == 200:
            data = response.json()
            if not data.get("success"):
                print("✅ Error properly detected and returned")
                print(f"Error message: {data.get('error')[:200]}...")
                return True
            else:
                print("⚠️  Invalid code was somehow rendered successfully")
                return False
        else:
            print("❌ Request failed")
            return False

    except Exception as e:
        print(f"❌ Error: {e}")
        return False


def main():
    """Run all tests"""
    print("=" * 80)
    print("  MERMAID API ENDPOINT TEST SUITE")
    print("=" * 80)
    print(f"Testing API at: {BASE_URL}")

    results = {}

    # Test 1: Health check
    results["Health Check"] = test_health()

    if not results["Health Check"]:
        print("\n⚠️  Backend server is not responding. Cannot continue tests.")
        print("   Start the backend with: Start.bat")
        return

    # Test 2: Info endpoint
    results["Info Endpoint"] = test_info()

    # Test 3: Validate valid code
    results["Validate Valid"] = test_validate_valid()

    # Test 4: Validate invalid code with auto-fix
    results["Validate & Auto-Fix"] = test_validate_invalid()

    # Test 5: Render diagram
    results["Render SVG"] = test_render()

    # Test 6: Error handling
    results["Error Handling"] = test_render_with_error()

    # Summary
    print_section("TEST SUMMARY")

    passed = sum(1 for result in results.values() if result)
    total = len(results)

    for test_name, result in results.items():
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status}  {test_name}")

    print()
    print(f"Results: {passed}/{total} tests passed")

    if passed == total:
        print("\n🎉 All API tests passed!")
    else:
        print(f"\n⚠️  {total - passed} test(s) failed")


if __name__ == "__main__":
    main()
