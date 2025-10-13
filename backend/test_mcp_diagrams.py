"""
Test script to process diagram test prompts through MCP endpoints.

This script reads test prompts from backend/tests/Diagrams/test.json,
calls the MCP endpoint for each entry, and saves the request/response
data along with any generated SVG files to a history folder.
"""

import base64
import json
import os
import sys
import time
import traceback
from pathlib import Path
from typing import Dict, Any, Optional

import requests

# Add the backend directory to the Python path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from security_utils import SecurityUtils
from common.logger import get_logger

# Configure logging
logger = get_logger(__name__)

# Configuration
MCP_BASE_URL = "http://localhost:8003/mcp"
TEST_DATA_PATH = "tests/Diagrams/test.json"
HISTORY_FOLDER = "tests/Diagrams/history"
SERVER_PORT = 8003

def create_history_folder() -> None:
    """Create the history folder if it doesn't exist."""
    history_path = Path(HISTORY_FOLDER)
    history_path.mkdir(parents=True, exist_ok=True)
    logger.info(f"History folder: {history_path.absolute()}")


def load_test_data() -> Dict[str, Any]:
    """Load test data from the JSON file."""
    try:
        with open(TEST_DATA_PATH, 'r', encoding='utf-8') as f:
            test_data = json.load(f)
        logger.info(f"Loaded test data from {TEST_DATA_PATH}")
        return test_data
    except FileNotFoundError:
        logger.error(f"Test file not found: {TEST_DATA_PATH}")
        raise
    except json.JSONDecodeError as e:
        logger.error(f"Invalid JSON in test file: {e}")
        raise

def call_mcp_endpoint(endpoint: str, data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    """
    Call an MCP endpoint with the provided data.
    
    Args:
        endpoint: The MCP endpoint to call (e.g., "tools/generate_and_render")
        data: The data to send to the endpoint
        
    Returns:
        The response data or None if there was an error
    """
    url = f"{MCP_BASE_URL}/{endpoint}"
    
    try:
        logger.info(f"Calling MCP endpoint: {url}")
        debug_info = {
            'endpoint': endpoint,
            'data_keys': list(data.keys()),
            'data_length': len(str(data))
        }
        debug_msg = f"Request data: {SecurityUtils.safe_debug_info(debug_info)}"
        logger.debug(debug_msg)
        
        response = requests.post(url, json=data, timeout=60)
        response.raise_for_status()
        
        result = response.json()
        
        # Check if the response indicates an error (e.g., API key not configured)
        if result.get('isError'):
            logger.error(f"Endpoint returned error: {result}")
        
        # Check content for error messages
        content = result.get('content', [])
        if content and len(content) > 0:
            text_content = content[0].get('text', '')
            if 'API key is not configured' in text_content:
                logger.error("API key is not configured in the backend")
                logger.error("Please set the API_KEY in the backend/.env file")
        
        logger.info(f"Successfully received response from {endpoint}")
        return result
        
    except requests.exceptions.ConnectionError:
        logger.error(f"Connection error: Could not connect to {url}")
        err_msg = f"Make sure the backend server is running on port {SERVER_PORT}"
        logger.error(err_msg)
        return None
    except requests.exceptions.Timeout:
        logger.error(f"Timeout error: Request to {url} timed out")
        return None
    except requests.exceptions.HTTPError as e:
        logger.error(f"HTTP error: {e}")
        logger.error(f"Response status: {e.response.status_code}")
        logger.error(f"Response body: {e.response.text}")
        return None
    except Exception as e:
        logger.error(f"Unexpected error calling MCP endpoint: {e}")
        logger.error(traceback.format_exc())
        return None

def save_request_response(
    test_id: int,
    test_name: str,
    request_data: Dict[str, Any],
    response_data: Dict[str, Any],
    diagram_type: str
) -> None:
    """
    Save the request and response data as a JSON file.
    
    Args:
        test_id: The test ID
        test_name: The test name
        request_data: The request data sent to the endpoint
        response_data: The response data received from the endpoint
        diagram_type: The type of diagram (d2, mermaid, c4)
    """
    # Create a filename using the test ID and name
    safe_name = "".join(
        c for c in test_name if c.isalnum() or c in (' ', '-', '_')
    ).rstrip()
    safe_name = safe_name.replace(' ', '_')
    filename = f"{test_id:02d}_{diagram_type}_{safe_name}.json"
    filepath = Path(HISTORY_FOLDER) / filename
    
    # Prepare the data to save
    save_data = {
        "test_id": test_id,
        "test_name": test_name,
        "diagram_type": diagram_type,
        "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
        "request": request_data,
        "response": response_data
    }
    
    try:
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(save_data, f, indent=2, ensure_ascii=False)
        logger.info(f"Saved request/response to {filepath}")
    except Exception as e:
        logger.error(f"Error saving request/response: {e}")

def save_svg_file(
    test_id: int,
    test_name: str,
    svg_data: str,
    diagram_type: str
) -> None:
    """
    Save the SVG data to a file.
    
    Args:
        test_id: The test ID
        test_name: The test name
        svg_data: The SVG data (base64 encoded or plain text)
        diagram_type: The type of diagram (d2, mermaid, c4)
    """
    # Create a filename using the test ID and name
    safe_name = "".join(
        c for c in test_name if c.isalnum() or c in (' ', '-', '_')
    ).rstrip()
    safe_name = safe_name.replace(' ', '_')
    filename = f"{test_id:02d}_{diagram_type}_{safe_name}.svg"
    filepath = Path(HISTORY_FOLDER) / filename
    
    try:
        # Check if the SVG data is base64 encoded
        if svg_data.startswith('data:image/svg+xml;base64,'):
            # Extract the base64 part
            base64_data = svg_data.split(',', 1)[1]
            svg_content = base64.b64decode(base64_data).decode('utf-8')
        else:
            # Assume it's plain SVG content
            svg_content = svg_data
        
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(svg_content)
        logger.info(f"Saved SVG file to {filepath}")
    except Exception as e:
        logger.error(f"Error saving SVG file: {e}")

def process_test_entry(test_entry: Dict[str, Any], diagram_type: str) -> bool:
    """
    Process a single test entry by calling the MCP endpoint and saving results.
    
    Args:
        test_entry: The test entry data
        diagram_type: The type of diagram (d2, mermaid, c4)
        
    Returns:
        True if successful, False otherwise
    """
    test_id = test_entry.get('id')
    test_name = test_entry.get('name', 'Unknown')
    description = test_entry.get('description', '')
    
    logger.info(f"Processing test {test_id}: {test_name} ({diagram_type})")
    
    # Prepare the request data
    request_data = {
        "prompt": description,
        "diagram_type": diagram_type,
        "output_format": "svg"
    }
    
    # Call the MCP endpoint
    response_data = call_mcp_endpoint(
        "tools/generate_and_render",
        request_data
    )
    
    if response_data is None:
        logger.error(f"Failed to get response for test {test_id}")
        return False
    
    # Save the request and response
    save_request_response(
        test_id,
        test_name,
        request_data,
        response_data,
        diagram_type
    )
    
    # Extract and save the SVG data if available
    try:
        content = response_data.get('content', [])
        if content and len(content) > 0:
            text_content = content[0].get('text', '')
            if text_content:
                result_data = json.loads(text_content)
                if 'image_data' in result_data:
                    save_svg_file(
                        test_id,
                        test_name,
                        result_data['image_data'],
                        diagram_type
                    )
    except Exception as e:
        logger.error(f"Error processing SVG data: {e}")
    
    return True


def main():
    """Main function to process all test entries."""
    logger.info("Starting MCP diagram test script")
    
    # Create the history folder
    create_history_folder()
    
    # Load the test data
    try:
        test_data = load_test_data()
    except Exception as e:
        logger.error(f"Failed to load test data: {e}")
        return 1
    
    # Process each test category
    success_count = 0
    total_count = 0
    
    for category, entries in test_data.items():
        diagram_type = category.replace('_test_prompts', '')
        logger.info(f"Processing {len(entries)} {diagram_type} tests")
        
        for entry in entries:
            total_count += 1
            if process_test_entry(entry, diagram_type):
                success_count += 1
            
            # Add a longer delay between requests to ensure completion
            # and avoid overwhelming the server
            time.sleep(3)
    
    completion_msg = f"Completed processing: {success_count}/{total_count} tests successful"
    logger.info(completion_msg)
    return 0 if success_count == total_count else 1


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)