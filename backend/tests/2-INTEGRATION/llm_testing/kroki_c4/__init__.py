"""
Kroki C4 Provider LLM Tests

Tests the Kroki C4 provider's ability to generate valid C4 architecture diagrams from LLM prompts.
"""

def test_kroki_c4_generation():
    # Initialize test parameters and configuration for C4 diagram generation
    # Ensure we have a consistent starting point for diagram creation tests
    test_prompt = "Create a microservices architecture for an e-commerce platform"
    provider = KrokiC4Provider()
    
    # Attempt to generate C4 diagram from the given text prompt
    # Verify that the provider can successfully convert natural language to architectural representation
    diagram = provider.generate_diagram(test_prompt)
    
    # Validate the generated diagram meets basic structural requirements
    # Ensures the output is not empty and contains expected C4 diagram elements
    assert diagram is not None, "Diagram generation failed"
    assert len(diagram) > 0, "Generated diagram is empty"
    
    # Check that the diagram contains key C4 modeling components
    # Validates that the diagram includes system, containers, or component representations
    assert "Component" in diagram or "System" in diagram, "Missing C4 model components"
    
    # Verify diagram syntax and compatibility with Kroki rendering
    # Ensures the generated diagram can be successfully rendered by Kroki
    rendered_diagram = kroki.render(diagram)
    assert rendered_diagram is not None, "Diagram rendering failed"

def test_complex_architecture_generation():
    # Test generation of more complex architectural scenarios
    # Validate provider's ability to handle nuanced system descriptions
    complex_prompt = "Design a distributed banking system with microservices and event-driven architecture"
    provider = KrokiC4Provider()
    
    # Generate diagram for complex architectural description
    # Test provider's capability to interpret sophisticated system designs
    complex_diagram = provider.generate_diagram(complex_prompt)
    
    # Perform comprehensive validation of complex diagram
    # Check for multiple system interactions and architectural complexity
    assert "System" in complex_diagram, "Complex system not properly represented"
    assert "Container" in complex_diagram, "Missing container definitions"
    assert "Relationship" in complex_diagram, "No system interactions defined"

def test_error_handling():
    # Validate error handling capabilities of C4 diagram generation
    # Ensure robust response to invalid or ambiguous inputs
    provider = KrokiC4Provider()
    
    # Test generation with minimal or unclear input
    # Verify graceful handling of edge case scenarios
    with pytest.raises(ValueError):
        provider.generate_diagram("")
    
    with pytest.raises(TypeError):
        provider.generate_diagram(None)
