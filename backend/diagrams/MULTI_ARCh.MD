Technical Implementation Plan: Abstracted Diagram Generator (LangGraph)

1. Overview

This document specifies the technical implementation for an abstracted, iterative diagram generator using langgraph. The system, "Diagram Factory," will take a natural language prompt, dynamically clarify requirements with the user, and then enter a generation/validation loop to produce a correct diagram.

The system is designed to be extensible, supporting multiple diagramming languages (D2, Mermaid, PlantUML) by abstracting the validation and rendering logic.

2. Core Architecture (LangGraph)

The system is a state machine (a StateGraph) with two primary loops:

Clarification Loop: An "Architect Agent" (clarify_prompt) node interviews the user to build a final_design_summary.

Validation Loop: A generate_code node attempts to create the diagram, which is checked by a validate_code node. If invalid, a refine_code node corrects it.

graph TD
    A[Start] --> B(clarify_prompt);
    B -- llm_ready: True --> C(generate_code);
    B -- llm_ready: False --> A;
    C --> D(validate_code);
    D -- is_valid: False --> E(refine_code);
    E --> D;
    D -- is_valid: True --> F(render_diagram);
    F --> G[End: SVG Output];


3. State Schema

The GraphState will be a Python TypedDict managing all data. This file should be named graph_state.py.

from typing import TypedDict, List, Dict

class GraphState(TypedDict):
    """
    The central state for the Diagram Factory graph.
    """
    # --- Input ---
    design_prompt: str
    target_language: str # e.g., "D2", "Mermaid"

    # --- Clarification Loop ---
    clarification_history: List[Dict[str, str]] # e.g., [{"role": "user", "content": "..."}, {"role": "ai", "content": "..."}]
    llm_ready: bool
    final_design_summary: str

    # --- Validation Loop ---
    diagram_code: str
    validation_error: str
    is_valid: bool

    # --- Output ---
    svg_output: str


4. Tooling Abstraction

The system's extensibility comes from a configuration map and a run_tool helper. This file should be named tool_config.py.

import subprocess
import tempfile
import os

DIAGRAM_TOOL_CONFIG = {
    "D2": {
        "validator_cmd": "d2 - validate {filepath}",
        "renderer_cmd": "d2 - layout=dagre {filepath} {output_svg}",
        "extension": ".d2"
    },
    "Mermaid": {
        "validator_cmd": "mmdc --validate {filepath}", # mermaid-cli
        "renderer_cmd": "mmdc -i {filepath} -o {output_svg}",
        "extension": ".mmd"
    },
    "PlantUML": {
        # Assumes PlantUML server or .jar is available
        "validator_cmd": None, # PlantUML often validates on render
        "renderer_cmd": "plantuml {filepath} -tsvg -o {output_dir}",
        "extension": ".puml"
    }
    # Add other languages (Structurizr, etc.) here
}

def run_tool(command: str) -> (bool, str):
    """
    Executes a shell command and returns (success, output).
    `success` is True if exit code is 0, False otherwise.
    `output` is the combined stdout and stderr.
    """
    if not command:
        return True, "" # No command to run

    try:
        # Using shell=True for simplicity, but in production, parse args
        result = subprocess.run(
            command,
            shell=True,
            check=False,
            capture_output=True,
            text=True,
            timeout=10
        )
        if result.returncode == 0:
            return True, result.stdout
        else:
            return False, f"STDOUT:\n{result.stdout}\n\nSTDERR:\n{result.stderr}"
    except Exception as e:
        return False, f"Execution failed: {str(e)}"


5. Node Implementation

These functions will be defined in nodes.py. The prompts should be stored in prompts.py.

5.1. prompts.py

CLARIFY_PROMPT = """You are an expert Chief Software Architect and a master at interviewing stakeholders. Your goal is to get a clear, unambiguous design brief from the user so you can generate a technical diagram.

Your Task:
1.  Analyze the user's latest prompt in the context of the conversation history.
2.  If the design is vague or incomplete, you must ask **one follow-up question at a time** to get the necessary detail.

Your Questioning Toolkit (Internal Monologue):
* Is the boundary of the system unclear? -> Ask about users and external systems (like C4 Level 1).
* Is the 'shape' of the system unclear? -> Ask if it's a single application or many services (Monolithic vs. Microservices).
* Is the communication style unclear? -> Ask how components will interact, e.g., direct calls or a message bus (EDA).

3.  Continue this loop until you are 100% confident you have a clear, actionable design.
4.  When satisfied, respond ONLY with the string "READY:" followed by a final, detailed summary of the design.
5.  If you need to ask a question, respond ONLY with the question.
"""

GENERATE_PROMPT = """Translate the following design summary into clean, valid {target_language} code.

Design Summary:
{final_design_summary}

Instructions:
* Only return the raw code block.
* Do not add any explanations, apologies, or markdown backticks.
* Ensure the syntax is correct for {target_language}.
"""

REFINE_PROMPT = """The previous attempt to generate a {target_language} diagram failed validation.

Original Design Summary:
{final_design_summary}

Invalid Code:


{diagram_code}


Raw Error from Tool:
{validation_error}

Your Task:
Please analyze the raw error, compare it to the invalid code and the original design summary, and then provide the fully corrected {target_language} code. Only return the raw code block.
"""


5.2. nodes.py (Pseudo-code)

This file contains the logic for each node in the graph.

import os
import tempfile
from graph_state import GraphState
from tool_config import DIAGRAM_TOOL_CONFIG, run_tool
from prompts import CLARIFY_PROMPT, GENERATE_PROMPT, REFINE_PROMPT

# Assume an LLM client (e.g., from langchain_openai) is initialized
# llm = ChatOpenAI(model="gpt-4-turbo", temperature=0)

def clarify_prompt(state: GraphState):
    """Interviews the user to refine the design brief."""
    history = state['clarification_history']
    # llm_call = llm.invoke(CLARIFY_PROMPT, history) # Simplified
    llm_call_content = "READY: A sample design summary" # Placeholder for LLM call

    if llm_call_content.startswith("READY:"):
        summary = llm_call_content.replace("READY:", "").strip()
        return {"llm_ready": True, "final_design_summary": summary}
    else:
        question = llm_call_content
        history.append({"role": "ai", "content": question})
        return {"llm_ready": False, "clarification_history": history}

def generate_code(state: GraphState):
    """Generates the first draft of diagram code."""
    prompt = GENERATE_PROMPT.format(
        target_language=state['target_language'],
        final_design_summary=state['final_design_summary']
    )
    # llm_call = llm.invoke(prompt)
    # code = llm_call.content
    code = "diagram {}" # Placeholder for LLM call
    return {"diagram_code": code}

def validate_code(state: GraphState):
    """Validates the diagram code using the tool config."""
    code = state['diagram_code']
    lang = state['target_language']
    
    if lang not in DIAGRAM_TOOL_CONFIG:
        return {"is_valid": False, "validation_error": f"No tool config for {lang}"}
    
    config = DIAGRAM_TOOL_CONFIG[lang]
    ext = config['extension']

    with tempfile.NamedTemporaryFile(delete=False, suffix=ext, mode='w') as f:
        f.write(code)
        filepath = f.name

    try:
        # 1. Attempt explicit validation
        val_cmd = config['validator_cmd']
        if val_cmd:
            success, output = run_tool(val_cmd.format(filepath=filepath))
            if not success:
                return {"is_valid": False, "validation_error": output}

        # 2. Attempt render-validation
        render_cmd = config['renderer_cmd']
        if render_cmd:
            with tempfile.NamedTemporaryFile(delete=True, suffix='.svg') as out_f:
                output_svg = out_f.name
                output_dir = os.path.dirname(output_svg)
                
                cmd = render_cmd.format(filepath=filepath, output_svg=output_svg, output_dir=output_dir)
                success, output = run_tool(cmd)
                if not success:
                    return {"is_valid": False, "validation_error": output}

    finally:
        os.remove(filepath)

    return {"is_valid": True, "validation_error": ""}

def refine_code(state: GraphState):
    """Fixes diagram code based on validation errors."""
    prompt = REFINE_PROMPT.format(
        target_language=state['target_language'],
        final_design_summary=state['final_design_summary'],
        diagram_code=state['diagram_code'],
        validation_error=state['validation_error']
    )
    # llm_call = llm.invoke(prompt)
    # code = llm_call.content
    code = "diagram { fixed_code }" # Placeholder for LLM call
    return {"diagram_code": code, "validation_error": ""}

def render_diagram(state: GraphState):
    """Renders the final, valid diagram code to SVG."""
    code = state['diagram_code']
    lang = state['target_language']
    config = DIAGRAM_TOOL_CONFIG[lang]
    ext = config['extension']

    with tempfile.NamedTemporaryFile(delete=False, suffix=ext, mode='w') as f:
        filepath = f.name
        f.write(code)
    
    with tempfile.NamedTemporaryFile(delete=False, suffix='.svg') as out_f:
        output_svg = out_f.name
    
    output_dir = os.path.dirname(output_svg)
    render_cmd = config['renderer_cmd'].format(filepath=filepath, output_svg=output_svg, output_dir=output_dir)
    
    success, output = run_tool(render_cmd)
    
    if not success:
        return {"svg_output": f"Render failed: {output}"}

    with open(output_svg, 'r') as f:
        svg_content = f.read()

    os.remove(filepath)
    os.remove(output_svg)

    return {"svg_output": svg_content}



6. Graph Definition (main.py)

This file ties all nodes and edges together.

from langgraph.graph import StateGraph, END
from graph_state import GraphState
# Import all node functions from nodes.py
# from nodes import clarify_prompt, generate_code, validate_code, refine_code, render_diagram

# --- 1. Define Routers ---

def route_clarification(state: GraphState):
    if state['llm_ready']:
        return "generate_code"
    else:
        # Stop and wait for user input
        return END

def route_validation(state: GraphState):
    if state['is_valid']:
        return "render_diagram"
    else:
        return "refine_code"

# --- 2. Build the Graph ---

workflow = StateGraph(GraphState)

# Add Nodes
# workflow.add_node("clarify_prompt", clarify_prompt)
# workflow.add_node("generate_code", generate_code)
# workflow.add_node("validate_code", validate_code)
# workflow.add_node("refine_code", refine_code)
# workflow.add_node("render_diagram", render_diagram)

# Set Entry Point
workflow.set_entry_point("clarify_prompt")

# Add Edges
workflow.add_edge("generate_code", "validate_code")
workflow.add_edge("refine_code", "validate_code")
workflow.add_edge("render_diagram", END)

# Add Conditional Edges
workflow.add_conditional_edges(
    "clarify_prompt",
    route_clarification,
    {"generate_code": "generate_code", END: END}
)
workflow.add_conditional_edges(
    "validate_code",
    route_validation,
    {"render_diagram": "render_diagram", "refine_code": "refine_code"}
)

# --- 3. Compile and Run ---
app = workflow.compile()

# Example of how to run the CLI-based loop
# (This logic would be more complex, handling user input)
print("Graph compiled successfully.")

# initial_state = {
#     "design_prompt": "My new e-commerce site",
#     "target_language": "D2",
#     "clarification_history": [{"role": "user", "content": "My new e-commerce site"}],
#     "llm_ready": False
# }

# for event in app.stream(initial_state, stream_mode="values"):
#     print(event)
#     # If 'llm_ready' is False and we are at the END,
#     # get user_input, update clarification_history,
#     # and re-invoke app.stream()


7. Directory Structure

diagram-factory/
├── .venv/
├── main.py             # 6. Graph Definition
├── nodes.py            # 5. Node Implementation (logic)
├── prompts.py          # 5. Node Implementation (prompts)
├── tool_config.py      # 4. Tooling Abstraction
├── graph_state.py      # 3. State Schema
└── requirements.txt    # langgraph, langchain-openai, etc.


8. Initial CLI Setup Commands

# 1. Create directory and CD into it
mkdir diagram-factory
cd diagram-factory

# 2. Create and activate a virtual environment
python3 -m venv .venv
source .venv/bin/activate

# 3. Install dependencies
# (Create a requirements.txt file first)
echo "langgraph
langchain-openai
" > requirements.txt
pip install -r requirements.txt

# 4. Install required external diagramming tools
# (This is a manual step for the user)
echo "Please ensure D2, mermaid-cli (mmdc), and PlantUML are installed and in your PATH."
# Example (macOS):
# brew install d2
# npm install -g @mermaid-js/mermaid-cli
# brew install plantuml

# 5. Create the Python files
touch main.py nodes.py prompts.py tool_config.py graph_state.py

# 6. Populate the files with the content from this plan.
# (This would be done by the developer)

# 7. Run the main application
# (main.py would be expanded to be a full CLI app)
echo "Setup complete. You can now populate the .py files and run main.py."
