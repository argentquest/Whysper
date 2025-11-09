"""
Main entry point for diagram factory system.

Provides a standalone CLI interface for testing the LangGraph-based
diagram generation workflow.
"""

import asyncio
import sys
from typing import Dict, Any

from .langgraph_builder import get_diagram_factory_graph
from .graph_state import GraphState, DiagramType
from .session_store import DiagramSessionStore


async def run_diagram_factory(
    design_prompt: str,
    diagram_type: str = "Mermaid",
    user_id: str = "test_user",
    conversation_id: str = "test_conversation"
) -> Dict[str, Any]:
    """
    Run the complete diagram factory workflow.
    
    Args:
        design_prompt: Initial user prompt
        diagram_type: Type of diagram (Mermaid, D2, PlantUML)
        user_id: User identifier
        conversation_id: Conversation identifier
    
    Returns:
        Final state with diagram output
    """
    # Create session store
    session_store = DiagramSessionStore()
    
    # Create initial state
    initial_state: GraphState = {
        "design_prompt": design_prompt,
        "diagram_type": DiagramType(diagram_type) if diagram_type in [dt.value for dt in DiagramType] else DiagramType(diagram_type.capitalize()),
        "clarification_history": [{"role": "user", "content": design_prompt}],
        "llm_ready": False,
        "question_count": 0,
        "refinement_attempt": 0,
        "current_state": "initialized"
    }
    
    # Get the compiled graph
    graph = get_diagram_factory_graph()
    
    print(f"Starting diagram factory for {diagram_type} diagram...")
    print(f"Initial prompt: {design_prompt}")
    
    # Run the graph
    try:
        result = await graph.ainvoke(initial_state)
        
        print("\n=== Diagram Factory Result ===")
        print(f"Final state: {result.get('current_state', 'unknown')}")
        print(f"Diagram code generated: {'Yes' if result.get('diagram_code') else 'No'}")
        print(f"Diagram rendered: {'Yes' if result.get('svg_output') else 'No'}")
        
        if result.get('validation_error'):
            print(f"Validation error: {result['validation_error']}")
        
        if result.get('svg_output'):
            print(f"SVG length: {len(result['svg_output'])} characters")
        
        return result
        
    except Exception as e:
        print(f"Error running diagram factory: {e}")
        return {
            "current_state": "error",
            "error_message": str(e)
        }


async def interactive_mode():
    """
    Interactive CLI mode for testing diagram factory.
    """
    print("=== Diagram Factory Interactive Mode ===")
    print("Enter 'quit' to exit")
    
    while True:
        try:
            prompt = input("\nEnter diagram description: ").strip()
            if prompt.lower() == 'quit':
                break
            
            if not prompt:
                continue
            
            # Get diagram type
            diagram_type = input("Diagram type (Mermaid/D2/PlantUML) [Mermaid]: ").strip()
            if not diagram_type:
                diagram_type = "Mermaid"
            
            # Run diagram factory
            result = await run_diagram_factory(prompt, diagram_type)
            
            # Show result
            if result.get('svg_output'):
                save = input("Save SVG to file? (y/n): ").strip().lower()
                if save == 'y':
                    filename = f"diagram_{len(prompt)}.svg"
                    with open(filename, 'w') as f:
                        f.write(result['svg_output'])
                    print(f"Saved to {filename}")
            
            print("\n" + "="*50 + "\n")
            
        except KeyboardInterrupt:
            print("\nExiting...")
            break
        except Exception as e:
            print(f"Error: {e}")


async def demo_mode():
    """
    Demo mode with predefined examples.
    """
    examples = [
        {
            "prompt": "A simple flowchart showing user login process",
            "type": "Mermaid"
        },
        {
            "prompt": "Microservices architecture with API gateway",
            "type": "D2"
        },
        {
            "prompt": "User authentication sequence diagram",
            "type": "PlantUML"
        }
    ]
    
    print("=== Diagram Factory Demo Mode ===")
    
    for i, example in enumerate(examples, 1):
        print(f"\n--- Example {i} ---")
        print(f"Prompt: {example['prompt']}")
        print(f"Type: {example['type']}")
        
        result = await run_diagram_factory(example['prompt'], example['type'])
        
        if result.get('svg_output'):
            filename = f"demo_{i}_{example['type'].lower()}.svg"
            with open(filename, 'w') as f:
                f.write(result['svg_output'])
            print(f"Saved to {filename}")
        
        print("\n" + "="*50 + "\n")


def print_usage():
    """Print usage information."""
    print("""
Diagram Factory - LangGraph-based Diagram Generation

Usage:
    python main.py [mode]

Modes:
    interactive - Interactive CLI mode
    demo         - Run demo examples
    help          - Show this help

Examples:
    python main.py interactive
    python main.py demo
    """)


async def main():
    """Main entry point."""
    args = sys.argv[1:]
    
    if not args or args[0] == "help":
        print_usage()
        return
    
    mode = args[0].lower()
    
    if mode == "interactive":
        await interactive_mode()
    elif mode == "demo":
        await demo_mode()
    else:
        print(f"Unknown mode: {mode}")
        print_usage()


if __name__ == "__main__":
    asyncio.run(main())