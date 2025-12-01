"""Simple test script to validate diagram factory compilation."""

try:
    from app.utils.diagram_wizard.langgraph_builder import get_diagram_factory_graph

    graph = get_diagram_factory_graph()
    print("✅ Graph compiled successfully!")
    print(f"✅ Graph has {len(graph.get_graph().nodes)} nodes")
    print(f"✅ Graph has {len(graph.get_graph().edges)} edges")

    # Test basic state initialization
    from app.utils.diagram_wizard.graph_state import GraphState, DiagramType

    test_state = GraphState(
        {
            "design_prompt": "Test prompt",
            "diagram_type": DiagramType.MERMAID,
            "clarification_history": [{"role": "user", "content": "Test prompt"}],
            "llm_ready": False,
            "question_count": 0,
            "refinement_attempt": 0,
            "current_state": "initialized",
        }
    )

    print("✅ GraphState initialization works")
    print(f"✅ Test state: {test_state}")

except ImportError as e:
    print(f"❌ Import error: {e}")
    print("❌ Missing dependencies or path issues")
except Exception as e:
    print(f"❌ Unexpected error: {e}")
