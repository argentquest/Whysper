"""
Kroki Structurizr Provider LLM Tests

Tests the Kroki Structurizr provider's ability to generate valid Structurizr diagrams from LLM prompts.
"""

import json
import os
import re
import requests

# Configuration for Kroki API endpoint and diagram type
KROKI_BASE_URL = "https://kroki.io"
DIAGRAM_TYPE = "structurizr"

def validate_structurizr_diagram(prompt_text):
    # Sanitize input by removing potential malicious characters or patterns
    sanitized_text = re.sub(r'[<>]', '', prompt_text)

    # Prepare request payload with Structurizr diagram definition
    payload = {
        "diagram_type": DIAGRAM_TYPE,
        "diagram_source": sanitized_text
    }

    try:
        # Send POST request to Kroki API to validate and generate diagram
        response = requests.post(
            f"{KROKI_BASE_URL}/{DIAGRAM_TYPE}", 
            json=payload, 
            headers={'Content-Type': 'application/json'}
        )

        # Check response status and content for successful diagram generation
        if response.status_code == 200:
            # Parse response to confirm valid diagram generation
            diagram_data = response.json()
            return {
                'valid': True,
                'diagram': diagram_data,
                'message': 'Structurizr diagram successfully generated'
            }
        else:
            # Handle API errors or invalid diagram generation
            return {
                'valid': False,
                'error': f'Diagram generation failed: {response.text}',
                'status_code': response.status_code
            }

    except requests.RequestException as e:
        # Catch and handle any network or request-related exceptions
        return {
            'valid': False,
            'error': f'Request failed: {str(e)}',
            'exception': True
        }

def test_structurizr_diagrams(test_prompts):
    # Initialize results container for tracking diagram validation
    validation_results = []

    # Iterate through each test prompt to validate Structurizr diagram
    for prompt in test_prompts:
        result = validate_structurizr_diagram(prompt)
        validation_results.append(result)

    # Return comprehensive results of diagram validation
    return validation_results
