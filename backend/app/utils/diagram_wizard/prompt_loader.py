"""
Prompt loader for diagram wizard system.

Loads and manages markdown-based prompts for clarification,
generation, and refinement phases.
"""

from pathlib import Path
from typing import Dict, Optional


# Cache for loaded prompts
_prompt_cache: Dict[str, str] = {}


def load_prompts() -> Dict[str, str]:
    """
    Load all prompts from markdown files.

    Returns:
        Dictionary mapping prompt names to content
    """
    global _prompt_cache

    if _prompt_cache:
        return _prompt_cache

    prompt_dir = Path(__file__).parent / "prompts"

    # Load analyze request prompt (full file content)
    analyze_path = prompt_dir / "ANALYZE_PROMPT.md"
    if analyze_path.exists():
        _prompt_cache["analyze_request"] = _load_full_file(analyze_path)

    # Load JSON generation prompt (full file content)
    json_gen_path = prompt_dir / "JSON_GENERATION_PROMPT.md"
    if json_gen_path.exists():
        _prompt_cache["json_generation"] = _load_full_file(json_gen_path)

    # Load clarification prompts
    clarify_path = prompt_dir / "CLARIFY_PROMPTS.md"
    if clarify_path.exists():
        _prompt_cache["clarify_mermaid"] = _extract_section(
            clarify_path, "Mermaid Prompts"
        )
        _prompt_cache["clarify_d2"] = _extract_section(clarify_path, "D2 Prompts")
        _prompt_cache["clarify_plantuml"] = _extract_section(
            clarify_path, "PlantUML Prompts"
        )

    # Load generation prompts
    generate_path = prompt_dir / "GENERATE_PROMPTS.md"
    if generate_path.exists():
        _prompt_cache["generate_mermaid"] = _extract_section(
            generate_path, "Mermaid Generation Prompt"
        )
        _prompt_cache["generate_d2"] = _extract_section(
            generate_path, "D2 Generation Prompt"
        )
        _prompt_cache["generate_plantuml"] = _extract_section(
            generate_path, "PlantUML Generation Prompt"
        )

    # Load refinement prompts
    refine_path = prompt_dir / "REFINE_PROMPTS.md"
    if refine_path.exists():
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


def get_prompt(prompt_name: str) -> Optional[str]:
    """
    Get a specific prompt by name.

    Args:
        prompt_name: Name of the prompt (e.g., "clarify_mermaid")

    Returns:
        Prompt content or None if not found
    """
    prompts = load_prompts()
    return prompts.get(prompt_name)


def _load_full_file(file_path: Path) -> str:
    """
    Load the full content of a file.

    Args:
        file_path: Path to the file to load

    Returns:
        Full file content or empty string if error occurs
    """
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            return f.read().strip()
    except Exception as e:
        print(f"Error loading file {file_path}: {e}")
        return ""


def _extract_section(file_path: Path, section_header: str) -> str:
    """
    Extract content from a markdown section.

    Args:
        file_path: Path to markdown file
        section_header: Section header to extract (e.g., "Mermaid Prompts")

    Returns:
        Content of the section
    """
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()

        # Find section header
        lines = content.split("\n")
        section_start = None
        section_end = None

        for i, line in enumerate(lines):
            if line.strip() == f"## {section_header}":
                section_start = i
            elif section_start is not None and line.startswith("## ") and i > section_start:
                section_end = i
                break

        if section_start is None:
            return ""

        # Extract section content
        if section_end is None:
            section_lines = lines[section_start + 1:]
        else:
            section_lines = lines[section_start + 1 : section_end]

        # Remove leading empty lines
        while section_lines and not section_lines[0].strip():
            section_lines.pop(0)

        return "\n".join(section_lines).strip()

    except Exception as e:
        print(f"Error loading prompt from {file_path}: {e}")
        return ""
