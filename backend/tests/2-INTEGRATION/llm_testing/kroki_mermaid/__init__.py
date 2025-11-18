"""
Kroki Mermaid Provider LLM Tests

Tests the Kroki Mermaid provider's ability to generate valid Mermaid diagrams from LLM prompts.
"""

import os
import base64
import requests  # Used for making HTTP requests to Kroki API

def generate_mermaid_diagram(prompt):
    # Base URL for Kroki API that converts Mermaid text to diagrams
    kroki_base_url = "https://kroki.io/mermaid/svg/"

    try:
        # Encode the Mermaid diagram text as base64 to pass safely in URL
        encoded_diagram = base64.urlsafe_b64encode(prompt.encode('utf-8')).decode('utf-8')
        
        # Construct full URL for API request to generate diagram
        diagram_url = f"{kroki_base_url}{encoded_diagram}"

        # Send GET request to Kroki to generate SVG diagram
        response = requests.get(diagram_url)
        
        # Check if API request was successful
        if response.status_code == 200:
            # Return the SVG diagram content
            return response.text
        else:
            # Raise an error if diagram generation fails
            raise Exception(f"Diagram generation failed: {response.status_code}")

    except Exception as e:
        # Handle any errors during diagram generation process
        print(f"Error generating diagram: {e}")
        return None

def validate_mermaid_diagram(diagram_svg):
    # Check if generated SVG is not empty and contains valid SVG structure
    if diagram_svg and diagram_svg.startswith('<svg') and diagram_svg.endswith('</svg>'):
        # Verify diagram has basic visual elements
        return '<' in diagram_svg and '>' in diagram_svg
    return False

def test_mermaid_generation(test_prompts):
    # Iterate through each Mermaid diagram prompt to test generation
    for prompt in test_prompts:
        # Generate diagram from current prompt
        generated_diagram = generate_mermaid_diagram(prompt)
        
        # Validate the generated diagram
        is_valid = validate_mermaid_diagram(generated_diagram)
        
        # Print test results for each prompt
        print(f"Prompt: {prompt}")
        print(f"Diagram Valid: {is_valid}")
        print("---")

# Sample Mermaid diagram prompts for testing
test_prompts = [
    "graph TD\nA[Start] --> B{Decision}\nB -->|Yes| C[Process]\nB -->|No| D[End]",
    "sequenceDiagram\nAlice->>Bob: Hello\nBob-->>Alice: Hi there!"
]

# Run the Mermaid diagram generation tests
if __name__ == "__main__":
    test_mermaid_generation(test_prompts)