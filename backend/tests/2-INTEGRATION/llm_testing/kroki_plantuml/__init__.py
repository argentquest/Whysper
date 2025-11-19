"""
Kroki PlantUML Provider LLM Tests

Tests the Kroki PlantUML provider's ability to generate valid PlantUML diagrams from LLM prompts.
"""

# Importing required libraries for HTTP requests, file handling, and testing
import requests
import os
import pytest

def test_kroki_plantuml_generation(plantuml_prompt):
    # Set up Kroki API endpoint for PlantUML diagram generation
    kroki_endpoint = "https://kroki.io/plantuml/svg"

    # Prepare request payload with the PlantUML diagram source text
    payload = {
        "diagram_source": plantuml_prompt
    }

    # Send POST request to Kroki API to generate SVG diagram
    response = requests.post(kroki_endpoint, json=payload)

    # Validate API response status and content
    assert response.status_code == 200, "API request failed"
    assert response.text.startswith('<svg'), "Response is not a valid SVG"

def test_plantuml_diagram_complexity():
    # Test diagram generation with varying complexity levels
    simple_prompt = """
    @startuml
    Alice -> Bob: Hello
    @enduml
    """

    # Generate diagram for simple PlantUML scenario
    complex_prompt = """
    @startuml
    actor User
    database Database
    participant Service

    User -> Service: Request data
    Service -> Database: Query
    Database --> Service: Return results
    Service --> User: Display data
    @enduml
    """

    # Validate diagram generation for different complexity levels
    assert len(test_kroki_plantuml_generation(simple_prompt)) > 0
    assert len(test_kroki_plantuml_generation(complex_prompt)) > 0

def test_plantuml_error_handling():
    # Test handling of invalid PlantUML syntax
    invalid_prompt = """
    @startuml
    Broken Syntax
    """

    # Verify error handling for malformed PlantUML input
    with pytest.raises(Exception):
        test_kroki_plantuml_generation(invalid_prompt)
