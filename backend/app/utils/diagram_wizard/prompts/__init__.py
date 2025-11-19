"""
Prompts for diagram wizard system.

This package contains markdown-based prompts for:
- Clarification of user requirements
- Code generation
- Refinement on validation errors
"""

# Function to generate initial diagram requirements prompt
def generate_initial_diagram_prompt(diagram_type):
    # Select specific prompt template based on diagram type
    # Ensures consistent structure and key information gathering
    prompts = {
        'flow': "Create a flow diagram that clearly shows: 1) Key steps 2) Sequence 3) Decision points",
        'sequence': "Design a sequence diagram illustrating: 1) Actors 2) Interactions 3) Message flows",
        'class': "Generate a class diagram representing: 1) Entities 2) Relationships 3) Key attributes"
    }
    
    # Return default or type-specific prompt, with fallback mechanism
    return prompts.get(diagram_type, "Please describe the core elements of your desired diagram")

# Function to refine diagram requirements with additional context
def refine_diagram_prompt(initial_prompt, additional_details):
    # Combine initial prompt with more specific user context
    # Allows incremental improvement of diagram specification
    refined_prompt = f"{initial_prompt}\n\nAdditional Context: {additional_details}"
    
    # Add guidance for clear, actionable diagram creation
    return f"{refined_prompt}\n\nProvide clear, precise diagram elements"

# Main function to orchestrate diagram prompt generation
def create_diagram_wizard_prompt(diagram_type, user_context=None):
    # Generate initial diagram-specific prompt
    # Provides structured starting point for diagram creation
    initial_prompt = generate_initial_diagram_prompt(diagram_type)
    
    # Conditionally refine prompt if additional context provided
    # Enables more precise and contextual diagram generation
    if user_context:
        return refine_diagram_prompt(initial_prompt, user_context)
    
    # Return base prompt if no additional context
    return initial_prompt
