"""Main entry point for diagram factory system.

Provides a standalone CLI interface for testing the LangGraph-based
diagram generation workflow.
"""

import asyncio
import sys
from typing import Dict, Any

from common.logger import get_logger
from .langgraph_builder import get_diagram_factory_graph
from .graph_state import GraphState, DiagramType

logger = get_logger(__name__)


async def run_diagram_factory(
    design_prompt: str,
    diagram_type: str = "Mermaid",
    user_id: str = "test_user",
    conversation_id: str = "test_conversation",
) -> Dict[str, Any]:
    """Runs the diagram factory workflow.

    Args:
        design_prompt (str): The user's description of the desired diagram.
        diagram_type (str, optional): The type of diagram to generate (e.g., "Mermaid", "D2").
                                      Defaults to "Mermaid".
        user_id (str, optional): The ID of the user requesting the diagram.
                                 Defaults to "test_user".
        conversation_id (str, optional): The ID of the conversation session.
                                         Defaults to "test_conversation".

    Returns:
        Dict[str, Any]: The final state of the diagram generation workflow,
                        including the generated code and SVG output if successful.
    """
    # Construct initial state with configuration parameters
    # Ensures correct diagram type and sets up initial tracking variables
    initial_state: GraphState = {
        "design_prompt": design_prompt,
        "diagram_type": (
            DiagramType(diagram_type)
            if diagram_type in [dt.value for dt in DiagramType]
            else DiagramType(diagram_type.capitalize())
        ),
        "clarification_history": [{"role": "user", "content": design_prompt}],
        "llm_ready": False,
        "question_count": 0,
        "refinement_attempt": 0,
        "current_state": "initialized",
    }

    # Retrieve the pre-configured LangGraph workflow for diagram generation
    # Pass None as service since we are in standalone mode
    graph = get_diagram_factory_graph(service=None)

    # Log the start of diagram generation process
    logger.info(f"Starting diagram factory for {diagram_type} diagram...")
    logger.info(f"Initial prompt: {design_prompt}")

    # Execute the graph workflow and handle potential errors
    try:
        # Asynchronously invoke the graph with initial state
        result = await graph.ainvoke(initial_state)

        # Provide detailed logging of the diagram generation result
        logger.info("\n=== Diagram Factory Result ===")
        logger.info(f"Final state: {result.get('current_state', 'unknown')}")
        logger.info(f"Diagram code generated: {'Yes' if result.get('diagram_code') else 'No'}")
        logger.info(f"Diagram rendered: {'Yes' if result.get('svg_output') else 'No'}")

        # Log any validation errors
        if result.get("validation_error"):
            logger.info(f"Validation error: {result['validation_error']}")

        # Log SVG output size for diagnostics
        if result.get("svg_output"):
            logger.info(f"SVG length: {len(result['svg_output'])} characters")

        return result

    except Exception as e:
        # Capture and log any unexpected errors during diagram generation
        logger.info(f"Error running diagram factory: {e}")
        return {"current_state": "error", "error_message": str(e)}


async def interactive_mode():
    """Runs the diagram factory in interactive CLI mode.

    Allows users to input diagram descriptions and types via standard input,
    generates the diagrams, and optionally saves the output to a file.
    """
    logger.info("=== Diagram Factory Interactive Mode ===")
    logger.info("Enter 'quit' to exit")

    while True:
        try:
            # Prompt for diagram description
            prompt = input("\nEnter diagram description: ").strip()
            if prompt.lower() == "quit":
                break

            # Skip empty inputs
            if not prompt:
                continue

            # Allow user to specify diagram type
            diagram_type = input("Diagram type (Mermaid/D2/PlantUML) [Mermaid]: ").strip()
            if not diagram_type:
                diagram_type = "Mermaid"

            # Generate diagram and handle result
            result = await run_diagram_factory(prompt, diagram_type)

            # Optional SVG file saving
            if result.get("svg_output"):
                save = input("Save SVG to file? (y/n): ").strip().lower()
                if save == "y":
                    filename = f"diagram_{len(prompt)}.svg"
                    with open(filename, "w") as f:
                        f.write(result["svg_output"])
                    logger.info(f"Saved to {filename}")

            logger.info("\n" + "=" * 50 + "\n")

        except KeyboardInterrupt:
            logger.info("\nExiting...")
            break
        except Exception as e:
            logger.info(f"Error: {e}")


async def demo_mode():
    """Runs the diagram factory with predefined demo examples.

    Iterates through a list of example prompts and diagram types,
    generating diagrams for each to showcase capabilities.
    """
    # Predefined examples to showcase diagram generation capabilities
    examples = [
        {"prompt": "A simple flowchart showing user login process", "type": "Mermaid"},
        {"prompt": "Microservices architecture with API gateway", "type": "D2"},
        {"prompt": "User authentication sequence diagram", "type": "PlantUML"},
    ]

    logger.info("=== Diagram Factory Demo Mode ===")

    # Iterate through examples and generate diagrams
    for i, example in enumerate(examples, 1):
        logger.info(f"\n--- Example {i} ---")
        logger.info(f"Prompt: {example['prompt']}")
        logger.info(f"Type: {example['type']}")

        # Generate diagram for each example
        result = await run_diagram_factory(example["prompt"], example["type"])

        # Save SVG output if generated
        if result.get("svg_output"):
            filename = f"demo_{i}_{example['type'].lower()}.svg"
            with open(filename, "w") as f:
                f.write(result["svg_output"])
            logger.info(f"Saved to {filename}")

        logger.info("\n" + "=" * 50 + "\n")


def print_usage():
    """Prints usage instructions for the command-line interface."""
    # Display command-line usage instructions
    logger.info(
        """
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
    """
    )


async def main():
    """Main entry point for script execution.

    Parses command-line arguments and dispatches to the appropriate mode.
    """
    # Parse command-line arguments and execute corresponding mode
    args = sys.argv[1:]

    # Show help if no arguments or help requested
    if not args or args[0] == "help":
        print_usage()
        return

    mode = args[0].lower()

    # Route to appropriate mode based on argument
    if mode == "interactive":
        await interactive_mode()
    elif mode == "demo":
        await demo_mode()
    else:
        logger.info(f"Unknown mode: {mode}")
        print_usage()


if __name__ == "__main__":
    asyncio.run(main())
