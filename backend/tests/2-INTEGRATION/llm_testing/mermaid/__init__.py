"""
LLM-based Mermaid Diagram Generation and Validation Tests

This module contains tests for generating Mermaid diagrams using LLM prompts
and validating them against the Mermaid CLI.
"""

import os
import subprocess
import tempfile

from dotenv import load_dotenv

# Load environment variables from .env file for sensitive configuration
load_dotenv()


def generate_mermaid_prompt(diagram_type, context=None):
    # Select the appropriate prompt template based on diagram type
    # Allows for flexible diagram generation with optional contextual details
    prompts = {
        "flowchart": "Create a Mermaid flowchart that demonstrates: {context}",
        "sequence": "Design a Mermaid sequence diagram showing: {context}",
        "class": "Generate a Mermaid class diagram representing: {context}",
    }

    # Safely retrieve prompt template, defaulting to a generic template if type not found
    prompt_template = prompts.get(diagram_type, "Create a Mermaid diagram: {context}")

    # Format the prompt with the given context, handling cases with or without context
    return prompt_template.format(context=context or "")


def validate_mermaid_syntax(mermaid_code):
    # Create a temporary file to store the Mermaid diagram code for CLI validation
    with tempfile.NamedTemporaryFile(mode="w", delete=False, suffix=".mmd") as temp_file:
        temp_file.write(mermaid_code)
        temp_file_path = temp_file.name

    try:
        # Use Mermaid CLI to validate the syntax by attempting to parse the diagram
        # Raises subprocess error if syntax is invalid
        result = subprocess.run(
            ["mmdc", "-i", temp_file_path, "-t", "dark", "-o", "/dev/null"], capture_output=True, text=True, check=True
        )
        return True
    except subprocess.CalledProcessError as e:
        # Log and return False if Mermaid CLI reports syntax errors
        print(f"Mermaid syntax validation failed: {e.stderr}")
        return False
    finally:
        # Always clean up the temporary file after validation
        os.unlink(temp_file_path)


def test_generate_flowchart():
    # Test generation of a simple flowchart with predefined context
    context = "system login process with decision points"
    mermaid_code = generate_mermaid_prompt("flowchart", context)

    # Validate the generated Mermaid code using CLI
    assert validate_mermaid_syntax(mermaid_code), "Flowchart generation failed syntax validation"


def test_generate_sequence_diagram():
    # Test generation of a sequence diagram representing user interaction flow
    context = "user authentication and authorization sequence"
    mermaid_code = generate_mermaid_prompt("sequence", context)

    # Ensure the generated diagram passes Mermaid syntax validation
    assert validate_mermaid_syntax(mermaid_code), "Sequence diagram generation failed syntax validation"


def test_generate_class_diagram():
    # Test generation of a class diagram modeling software architecture
    context = "e-commerce platform class relationships"
    mermaid_code = generate_mermaid_prompt("class", context)

    # Validate Mermaid code syntax before further processing
    assert validate_mermaid_syntax(mermaid_code), "Class diagram generation failed syntax validation"
