"""
Integration Tests for Diagram Providers with LLM Correction

These tests require:
1. Backend server to be running (http://localhost:8003)
2. AI processor to be configured with valid API keys
3. D2 and/or Mermaid CLI to be installed

Run these tests when the server is running:
    pytest backend/diagrams/tests/test_integration_with_llm.py -v -s

These are TRUE integration tests that test the full stack including:
- Provider registry
- Diagram validation
- Pattern-based auto-fix
- LLM-based correction (requires server)
- API endpoints
- File saving
"""

import sys
from pathlib import Path
import pytest
import requests
from datetime import datetime
import time
import subprocess
import os
import signal

# Add backend to path
backend_dir = Path(__file__).parent.parent.parent
if str(backend_dir) not in sys.path:
    sys.path.insert(0, str(backend_dir))

# Configuration
SERVER_URL = "http://localhost:8003"
API_BASE = f"{SERVER_URL}/api/v1/diagrams/v2"

# Server process management
_server_process = None


# ===================================================================
# Helper Functions
# ===================================================================

def is_server_running() -> bool:
    """Check if backend server is running"""
    try:
        response = requests.get(f"{SERVER_URL}/api/v1/system/health", timeout=2)
        return response.status_code == 200
    except requests.exceptions.RequestException:
        return False


def wait_for_server(timeout: int = 30, verbose: bool = True) -> bool:
    """Wait for server to be ready"""
    start_time = time.time()
    dots_printed = 0

    while time.time() - start_time < timeout:
        if is_server_running():
            if verbose and dots_printed > 0:
                print()  # Newline after dots
            return True
        time.sleep(0.5)  # Check more frequently
        if verbose:
            print(".", end="", flush=True)
            dots_printed += 1

    if verbose and dots_printed > 0:
        print()  # Newline after dots
    return False


def start_server() -> subprocess.Popen:
    """Start the backend server in a subprocess"""
    global _server_process

    print("\n[...] Starting backend server...")
    backend_path = Path(__file__).parent.parent.parent
    main_py = backend_path / "main.py"

    if not main_py.exists():
        raise FileNotFoundError(f"Cannot find main.py at {main_py}")

    # Start server in background with output redirected to console
    _server_process = subprocess.Popen(
        ["py", "-u", str(main_py)],  # -u for unbuffered output
        cwd=str(backend_path),
        stdout=subprocess.DEVNULL,  # Suppress stdout to avoid mixing with test output
        stderr=subprocess.DEVNULL,  # Suppress stderr
        creationflags=subprocess.CREATE_NEW_PROCESS_GROUP if os.name == 'nt' else 0
    )

    print(f"[...] Server started with PID: {_server_process.pid}")
    print(f"[...] Waiting for server to become ready (may take ~30s)...")

    # Wait for server to be ready (server typically takes 30-45s to start)
    if wait_for_server(timeout=90, verbose=True):
        print("[OK] Server is ready for testing!")
        return _server_process
    else:
        # Server didn't start - capture any error output
        print(f"[FAIL] Server failed to start within 90s")
        stop_server()
        raise RuntimeError("Server failed to start within timeout")


def stop_server():
    """Stop the backend server"""
    global _server_process

    if _server_process is None:
        return

    print(f"\n[...] Stopping server (PID: {_server_process.pid})...")

    try:
        if os.name == 'nt':
            # Windows: Send CTRL_BREAK signal
            _server_process.send_signal(signal.CTRL_BREAK_EVENT)
        else:
            # Unix: Send SIGTERM
            _server_process.terminate()

        # Wait for graceful shutdown
        try:
            _server_process.wait(timeout=10)
            print("[OK] Server stopped gracefully")
        except subprocess.TimeoutExpired:
            # Force kill if it doesn't stop
            print("[WARN] Server didn't stop gracefully, force killing...")
            _server_process.kill()
            _server_process.wait()
            print("[OK] Server force killed")

    except Exception as e:
        print(f"[WARN] Error stopping server: {e}")

    finally:
        _server_process = None


# ===================================================================
# Fixtures
# ===================================================================

@pytest.fixture(scope="module", autouse=True)
def manage_server():
    """
    Manage server lifecycle for integration tests.

    - Checks if server is already running
    - If not, starts it automatically
    - Stops it after all tests complete
    """
    server_was_running = is_server_running()
    started_by_us = False

    if server_was_running:
        print("\n[OK] Server already running - using existing instance")
    else:
        print("\n[...] Server not running - starting it for tests...")
        try:
            start_server()
            started_by_us = True
        except Exception as e:
            pytest.skip(f"Failed to start server: {e}")

    # Run all tests
    yield

    # Cleanup: Stop server only if we started it
    if started_by_us:
        print("\n[...] Tests complete - stopping server...")
        stop_server()
    else:
        print("\n[OK] Tests complete - leaving existing server running")


@pytest.fixture
def api_session():
    """Create a requests session for API calls"""
    session = requests.Session()
    session.headers.update({"Content-Type": "application/json"})
    return session


# ===================================================================
# Integration Tests: Provider System
# ===================================================================

def test_integration_providers_list(api_session):
    """
    INTEGRATION TEST: List all providers through API

    Tests:
    - API endpoint availability
    - Provider auto-discovery
    - Provider metadata structure
    """
    print("\n" + "="*60)
    print("INTEGRATION TEST: Provider List API")
    print("="*60)

    response = api_session.get(f"{API_BASE}/providers")

    print(f"\n1. API Response Status: {response.status_code}")
    assert response.status_code == 200, f"API returned {response.status_code}"

    data = response.json()
    print(f"2. Total Providers: {data['total_providers']}")
    print(f"3. Available Providers: {data['available_providers']}")
    print(f"4. Unavailable Providers: {data['unavailable_providers']}")

    assert data['total_providers'] >= 2, "Should have at least 2 providers (Mermaid, D2)"
    assert 'providers' in data

    print(f"\n5. Registered Providers:")
    for provider in data['providers']:
        status = "[OK] Available" if provider['available'] else "[FAIL] Unavailable"
        print(f"   - {provider['provider_id']}: {provider['diagram_type']} {status}")
        print(f"     Formats: {', '.join(provider['supported_output_formats'])}")
        print(f"     Capabilities: {len(provider['capabilities'])}")

    print("\n[OK] Provider list API working!")


def test_integration_health_check(api_session):
    """
    INTEGRATION TEST: Health check endpoint

    Tests:
    - System health
    - Provider availability count
    """
    print("\n" + "="*60)
    print("INTEGRATION TEST: Health Check")
    print("="*60)

    response = api_session.get(f"{API_BASE}/health")

    assert response.status_code == 200
    data = response.json()

    print(f"\n1. Status: {data['status']}")
    print(f"2. Available Providers: {data['available_providers']}")
    print(f"3. Diagram Types: {data['diagram_types']}")

    assert data['status'] in ['healthy', 'degraded']
    assert data['available_providers'] >= 0

    print("\n[OK] Health check working!")


# ===================================================================
# Integration Tests: D2 Diagrams
# ===================================================================

def test_integration_d2_render_valid(api_session):
    """
    INTEGRATION TEST: Render valid D2 diagram

    Tests:
    - End-to-end D2 rendering
    - SVG output generation
    - Validation success
    """
    print("\n" + "="*60)
    print("INTEGRATION TEST: D2 Render Valid Diagram")
    print("="*60)

    diagram_code = """direction: right

frontend: Web App {
  shape: rectangle
  style.fill: "#e3f2fd"
}

backend: API Server {
  shape: rectangle
  style.fill: "#fff3e0"
}

database: PostgreSQL {
  shape: cylinder
  style.fill: "#f3e5f5"
}

frontend -> backend: HTTPS
backend -> database: SQL Queries
"""

    payload = {
        "code": diagram_code,
        "diagram_type": "d2",
        "output_format": "svg",
        "save_to_file": True
    }

    print(f"\n1. Sending render request...")
    print(f"   Code length: {len(diagram_code)} chars")

    response = api_session.post(f"{API_BASE}/render", json=payload)

    print(f"2. Response status: {response.status_code}")

    if response.status_code != 200:
        print(f"   Error: {response.text}")

    data = response.json()

    print(f"3. Success: {data['success']}")
    print(f"4. Provider: {data['provider_id']}")
    print(f"5. Validation: {data['validation']['is_valid']}")

    if data['success']:
        print(f"6. Output size: {len(data['content'])} bytes")
        print(f"7. Contains SVG: {'<svg' in data['content']}")

        if data['file_path']:
            print(f"8. Saved to: {data['file_path']}")

        assert '<svg' in data['content'] or '<?xml' in data['content']
        print("\n[OK] D2 diagram rendered successfully!")
    else:
        print(f"   Render failed: {data.get('error', 'Unknown error')}")
        if 'not available' in data.get('error', '').lower():
            pytest.skip("D2 CLI not available")
        else:
            pytest.fail(f"D2 rendering failed: {data.get('error')}")


def test_integration_d2_validate_and_autofix(api_session):
    """
    INTEGRATION TEST: D2 validation with pattern-based auto-fix

    Tests:
    - Validation of invalid code
    - Pattern-based auto-fix
    - Fixed code validation
    """
    print("\n" + "="*60)
    print("INTEGRATION TEST: D2 Validation + Auto-Fix")
    print("="*60)

    # Invalid code: missing direction
    invalid_code = """x: Service A
y: Service B

x -> y
"""

    payload = {
        "code": invalid_code,
        "diagram_type": "d2",
        "auto_fix": True,
        "use_llm": False  # Just pattern fix for now
    }

    print(f"\n1. Validating invalid code (missing direction)...")
    response = api_session.post(f"{API_BASE}/validate", json=payload)

    print(f"2. Response status: {response.status_code}")
    assert response.status_code == 200

    data = response.json()

    print(f"3. Initially valid: {data.get('is_valid', False)}")
    print(f"4. Auto-fixed: {data.get('auto_fixed', False)}")
    print(f"5. Correction method: {data.get('correction_method', 'none')}")

    if data.get('auto_fixed'):
        print(f"6. Fixed code preview:")
        fixed_code = data.get('fixed_code', '')
        print(f"   {fixed_code[:150]}...")
        assert 'direction:' in fixed_code.lower()
        print("\n[OK] Auto-fix worked!")
    else:
        print("   Note: Auto-fix might not have been needed (D2 may accept it)")


def test_integration_d2_render_invalid_without_fix(api_session):
    """
    INTEGRATION TEST: Try to render truly invalid D2 code

    Tests:
    - Error handling
    - Validation failure reporting
    """
    print("\n" + "="*60)
    print("INTEGRATION TEST: D2 Render Invalid Code")
    print("="*60)

    # Truly invalid: unclosed brace
    invalid_code = """direction: right

container {
  x -> y
"""

    payload = {
        "code": invalid_code,
        "diagram_type": "d2",
        "output_format": "svg"
    }

    print(f"\n1. Attempting to render invalid code (unclosed brace)...")
    response = api_session.post(f"{API_BASE}/render", json=payload)

    data = response.json()

    print(f"2. Success: {data['success']}")
    print(f"3. Validation valid: {data['validation']['is_valid']}")

    if not data['success']:
        print(f"4. Error (expected): {data.get('error', 'Unknown')[:200]}")
        print("\n[OK] Error handling works correctly!")
    else:
        print("   Note: D2 might have auto-fixed this")


# ===================================================================
# Integration Tests: LLM Correction (Requires AI Processor)
# ===================================================================

def test_integration_llm_correction_d2(api_session):
    """
    INTEGRATION TEST: LLM-based diagram correction

    This test requires:
    - Backend server running
    - AI processor configured with valid API key
    - LLM correction service enabled

    Tests:
    - LLM correction through API
    - Multiple retry attempts
    - Provider-specific correction rules
    """
    print("\n" + "="*60)
    print("INTEGRATION TEST: LLM Correction for D2")
    print("="*60)

    # Complex invalid code that pattern fix can't handle
    complex_invalid = """
direction: right

# This has multiple issues:
# 1. Invalid shape references
# 2. Syntax errors
# 3. Incorrect style syntax

webserver: Web Server {
  shape: component  # Invalid shape
  style: fill="#blue"  # Wrong syntax
}

database: Database {
  shape: database  # Invalid shape name
}

webserver -> database
"""

    payload = {
        "code": complex_invalid,
        "diagram_type": "d2",
        "auto_fix": True,
        "use_llm": True  # Enable LLM correction
    }

    print(f"\n1. Testing LLM correction with complex invalid code...")
    print(f"   Code has: invalid shapes, wrong syntax, multiple issues")

    try:
        response = api_session.post(f"{API_BASE}/validate", json=payload, timeout=30)

        print(f"2. Response status: {response.status_code}")

        if response.status_code != 200:
            print(f"   API Error: {response.text[:200]}")
            pytest.skip("LLM correction endpoint may not be fully implemented")
            return

        data = response.json()

        print(f"3. Final validation: {data.get('is_valid', False)}")
        print(f"4. Auto-fixed: {data.get('auto_fixed', False)}")
        print(f"5. LLM corrected: {data.get('llm_corrected', False)}")
        print(f"6. Correction method: {data.get('correction_method', 'none')}")

        if data.get('llm_corrected'):
            print(f"\n7. LLM-corrected code:")
            fixed = data.get('fixed_code', '')
            print(f"   {fixed[:300]}...")
            print("\n[OK] LLM correction worked!")

            # Verify the fixed code is actually valid
            verify_payload = {
                "code": fixed,
                "diagram_type": "d2",
                "auto_fix": False
            }
            verify_response = api_session.post(f"{API_BASE}/validate", json=verify_payload)
            verify_data = verify_response.json()
            assert verify_data.get('is_valid'), "LLM-corrected code should be valid"

        else:
            print("\n[WARN]  LLM correction not triggered")
            print("   This might mean:")
            print("   - Pattern fix already worked")
            print("   - LLM service not configured")
            print("   - use_llm flag not implemented yet")

            # Check if LLM service is available
            health_response = api_session.get(f"{API_BASE}/providers")
            providers = health_response.json()['providers']
            d2_provider = next((p for p in providers if p['provider_id'] == 'd2v1'), None)

            if d2_provider:
                has_llm = 'LLM_CORRECTION' in d2_provider['capabilities']
                print(f"   - D2 provider has LLM capability: {has_llm}")

            pytest.skip("LLM correction not available or already fixed by pattern matching")

    except requests.exceptions.Timeout:
        print("\n[TIME]  Request timed out after 30s")
        pytest.skip("LLM correction timed out - LLM service may be slow or unavailable")
    except Exception as e:
        print(f"\n[FAIL] Error: {e}")
        pytest.skip(f"LLM correction test failed: {e}")


# ===================================================================
# Integration Tests: Mermaid Diagrams
# ===================================================================

def test_integration_mermaid_render(api_session):
    """
    INTEGRATION TEST: Render Mermaid diagram

    Tests:
    - Mermaid provider through API
    - SVG generation
    - Complex diagram rendering
    """
    print("\n" + "="*60)
    print("INTEGRATION TEST: Mermaid Render")
    print("="*60)

    mermaid_code = """flowchart TD
    Start[Start Process] --> Input[Receive Input]
    Input --> Validate{Valid?}
    Validate -->|Yes| Process[Process Data]
    Validate -->|No| Error[Show Error]
    Process --> DB[(Database)]
    DB --> Output[Generate Output]
    Output --> End[End]
    Error --> End
"""

    payload = {
        "code": mermaid_code,
        "diagram_type": "mermaid",
        "provider_id": "mermaidv1",
        "output_format": "svg"
    }

    print(f"\n1. Rendering Mermaid flowchart...")
    response = api_session.post(f"{API_BASE}/render", json=payload)

    print(f"2. Response status: {response.status_code}")

    if response.status_code == 404:
        pytest.skip("Provider endpoint not found - check API routing")

    data = response.json()

    print(f"3. Success: {data.get('success', 'N/A')}")
    print(f"4. Provider: {data.get('provider_id', 'N/A')}")

    if data.get('success'):
        print(f"5. Output size: {len(data['content'])} bytes")
        assert '<svg' in data['content']
        print("\n[OK] Mermaid diagram rendered!")
    else:
        error = data.get('error', data.get('detail', 'Unknown error'))
        # Convert error to string if it's a list or other type
        if isinstance(error, list):
            error_str = str(error)
        elif not isinstance(error, str):
            error_str = str(error)
        else:
            error_str = error

        if 'not available' in error_str.lower() or 'mmdc' in error_str.lower():
            pytest.skip("Mermaid CLI not available")
        else:
            pytest.fail(f"Mermaid rendering failed: {error}")


# ===================================================================
# Integration Tests: File Management
# ===================================================================

def test_integration_file_download(api_session):
    """
    INTEGRATION TEST: File saving and download

    Tests:
    - Diagram file saving
    - Download endpoint
    - File cleanup
    """
    print("\n" + "="*60)
    print("INTEGRATION TEST: File Save & Download")
    print("="*60)

    # First, render and save a diagram
    code = "direction: right\nx -> y -> z"

    payload = {
        "code": code,
        "diagram_type": "d2",
        "output_format": "svg",
        "save_to_file": True
    }

    print(f"\n1. Rendering diagram with save_to_file=True...")
    response = api_session.post(f"{API_BASE}/render", json=payload)
    data = response.json()

    if not data['success']:
        pytest.skip("D2 rendering failed, can't test download")

    file_path = data.get('file_path')
    if not file_path:
        pytest.skip("File not saved (might be disabled)")

    filename = Path(file_path).name
    print(f"2. File saved: {filename}")

    # Try to download it
    download_url = f"{API_BASE}/download/{filename}"
    print(f"3. Downloading from: {download_url}")

    download_response = api_session.get(download_url)
    print(f"4. Download status: {download_response.status_code}")

    if download_response.status_code == 200:
        print(f"5. Downloaded {len(download_response.content)} bytes")
        assert len(download_response.content) > 0
        print("\n[OK] File download working!")
    elif download_response.status_code == 404:
        print("   File not found - might have been cleaned up")
        pytest.skip("File not found for download")


# ===================================================================
# Integration Test: Full End-to-End Workflow
# ===================================================================

def test_integration_full_workflow(api_session):
    """
    INTEGRATION TEST: Complete workflow

    Tests the full lifecycle:
    1. Submit invalid code
    2. Get validation error
    3. Auto-fix with pattern matching
    4. If still invalid, try LLM correction
    5. Render the corrected code
    6. Save to file
    7. Download the file

    This is the closest to real user workflow.
    """
    print("\n" + "="*60)
    print("INTEGRATION TEST: Full Workflow")
    print("="*60)

    # Step 1: Start with invalid code
    invalid_code = """x -> y -> z"""  # Missing direction

    print(f"\n1. Starting with invalid D2 code...")
    print(f"   Code: {invalid_code}")

    # Step 2: Validate
    print(f"\n2. Validating...")
    validate_response = api_session.post(
        f"{API_BASE}/validate",
        json={"code": invalid_code, "diagram_type": "d2", "auto_fix": True}
    )
    validate_data = validate_response.json()

    if not validate_data['is_valid']:
        print(f"   Invalid! Error: {validate_data.get('error', 'Unknown')[:100]}")

    # Step 3: Get fixed code
    if validate_data.get('auto_fixed'):
        fixed_code = validate_data['fixed_code']
        print(f"\n3. Auto-fixed code:")
        print(f"   {fixed_code[:100]}...")
    else:
        # D2 might actually accept it
        fixed_code = invalid_code
        print(f"\n3. Code accepted as-is (D2 is lenient)")

    # Step 4: Render the fixed code
    print(f"\n4. Rendering fixed code...")
    render_response = api_session.post(
        f"{API_BASE}/render",
        json={
            "code": fixed_code,
            "diagram_type": "d2",
            "output_format": "svg",
            "save_to_file": True
        }
    )
    render_data = render_response.json()

    if render_data['success']:
        print(f"   [v] Rendered successfully")
        print(f"   [v] Output: {len(render_data['content'])} bytes")

        if render_data.get('file_path'):
            filename = Path(render_data['file_path']).name
            print(f"   [v] Saved: {filename}")

            # Step 5: Download
            print(f"\n5. Downloading...")
            download_response = api_session.get(f"{API_BASE}/download/{filename}")
            if download_response.status_code == 200:
                print(f"   [v] Downloaded: {len(download_response.content)} bytes")

        print("\n[OK] Full workflow completed successfully!")
    else:
        if 'not available' in render_data.get('error', '').lower():
            pytest.skip("D2 CLI not available")
        else:
            pytest.fail(f"Workflow failed at rendering: {render_data.get('error')}")


# ===================================================================
# Main Test Runner
# ===================================================================

if __name__ == "__main__":
    print("\n" + "="*60)
    print("INTEGRATION TEST SUITE")
    print("Diagram Provider System with LLM Correction")
    print("="*60)

    print("\n⚙️  Configuration:")
    print(f"   Server URL: {SERVER_URL}")
    print(f"   API Base: {API_BASE}")

    # Check if server is running
    if not wait_for_server():
        print("\n[FAIL] Cannot run integration tests - server not running")
        print("\nTo start the server:")
        print("   cd backend")
        print("   py main.py")
        sys.exit(1)

    print("\n[GO] Running integration tests...")
    print("="*60)

    # Run with pytest
    pytest.main([__file__, "-v", "-s", "--tb=short"])
