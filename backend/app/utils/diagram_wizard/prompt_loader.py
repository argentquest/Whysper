```python
"""
Prompt loader for diagram wizard system.

Loads and manages markdown-based prompts for clarification,
generation, and refinement phases.
"""

from pathlib import Path
from typing import Dict, Optional


# Global cache to store loaded prompts and avoid repeated file reads
_prompt_cache: Dict[str, str] = {}


def load_prompts() -> Dict[str, str]:
    global _prompt_cache

    # Return cached prompts if already loaded to prevent redundant file reads
    if _prompt_cache:
        return _prompt_cache

    # Determine the directory containing prompt markdown files
    prompt_dir = Path(__file__).parent / "prompts"

    # Load unified analyse/clarify prompt if it exists, otherwise load legacy separate prompts
    unified_path = prompt_dir / "ANALYSE_CLARIFY.md"
    if unified_path.exists():
        # Use a single prompt for both analyze and clarify stages
        unified_content = _load_full_file(unified_path)
        _prompt_cache["analyze_request"] = unified_content
        _prompt_cache["clarify_universal"] = unified_content
    else:
        # Fallback to separate prompt files for backward compatibility
        analyze_path = prompt_dir / "ANALYZE_PROMPT.md"
        if analyze_path.exists():
            _prompt_cache["analyze_request"] = _load_full_file(analyze_path)

        clarify_path = prompt_dir / "CLARIFY_PROMPTS.md"
        if clarify_path.exists():
            # Extract specific section for universal clarification
            _prompt_cache["clarify_universal"] = _extract_section(
                clarify_path, "Universal Clarification Prompt"
            )

    # Load generic JSON generation prompt
    json_gen_path = prompt_dir / "JSON_GENERATION_PROMPT.md"
    if json_gen_path.exists():
        _prompt_cache["json_generation"] = _load_full_file(json_gen_path)

    # Load model-specific JSON generation prompts for flexibility across different AI models
    for model in ["gpt5", "grok", "sonet45", "gemini25pro"]:
        model_json_path = prompt_dir / f"JSON_GENERATION_{model}.md"
        if model_json_path.exists():
            _prompt_cache[f"json_generation_{model}"] = _load_full_file(model_json_path)

    # Load generation prompts for different diagram formats
    generate_path = prompt_dir / "GENERATE_PROMPTS.md"
    if generate_path.exists():
        # Extract specific sections for different diagram generation methods
        _prompt_cache["generate_mermaid"] = _extract_section(
            generate_path, "Mermaid Generation Prompt"
        )
        _prompt_cache["generate_d2"] = _extract_section(
            generate_path, "D2 Generation Prompt"
        )
        _prompt_cache["generate_plantuml"] = _extract_section(
            generate_path, "PlantUML Generation Prompt"
        )

    # Load refinement prompts for different diagram formats
    refine_path = prompt_dir / "REFINE_PROMPTS.md"
    if refine_path.exists():
        # Extract specific sections for refining different diagram types
        _prompt_cache["refine_mermaid"] = _extract_section(
            refine_path, "Mermaid Refinement Prompt"
        )
        _prompt_cache["refine_d2"] = _extract_section(
            refine_path, "D2 Refinement Prompt"
        )
        _prompt_cache["refine_plantuml"] = _extract_section(
            refine_path, "PlantUML Refinement Prompt"
        )

    return _prompt_cache


def get_prompt(prompt_name: str, model_id: Optional[str] = None) -> Optional[str]:
    # Load all prompts if not already loaded
    prompts = load_prompts()

    # Prioritize model-specific prompts if a model_id is provided
    if model_id:
        model_specific_key = f"{prompt_name}_{model_id}"
        # Check if a model-specific prompt exists
        if model_specific_key in prompts:
            return prompts.get(model_specific_key)

    # Fall back to generic prompt if no model-specific version found
    return prompts.get(prompt_name)


def _load_full_file(file_path: Path) -> str:
    # Safely read entire file content with error handling
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            return f.read().strip()
    except Exception as e:
        # Log error and return empty string if file read fails
        print(f"Error loading file {file_path}: {e}")
        return ""


def _extract_section(file_path: Path, section_header: str) -> str:
    # Extract a specific markdown section from a file
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()

        # Find the start and end of the specified section
        lines = content.split("\n")
        section_start = None
        section_end = None

        # Locate section boundaries
        for i, line in enumerate(lines):
            if line.strip() == f"## {section_header}":
                section_start = i
            elif section_start is not None and line.startswith("## ") and i > section_start:
                section_end = i
                break

        # Return empty string if section not found
        if section_start is None:
            return ""

        # Extract section lines, handling cases with or without an ending section
        if section_end is None:
            section_lines = lines[section_start + 1:]
        else:
            section_lines = lines[section_start + 1 : section_end]

        # Remove leading empty lines for clean extraction
        while section_lines and not section_lines[0].strip():
            section_lines.pop(0)

        return "\n".join(section_lines).strip()

    except Exception as e:
        # Log error and return empty string if section extraction fails
        print(f"Error loading prompt from {file_path}: {e}")
        return ""
```

The comments explain the logic, purpose, and key steps in each function and section of the code.