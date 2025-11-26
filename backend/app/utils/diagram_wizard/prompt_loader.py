"""
Prompt loader for diagram wizard system.

Loads and manages markdown-based prompts for clarification,
generation, and refinement phases.
"""

from pathlib import Path
from typing import Dict, Optional
from common.env_manager import env_manager


# Global cache to store loaded prompts and avoid repeated file reads
_prompt_cache: Dict[str, str] = {}


def load_prompts() -> Dict[str, str]:
    """
    Load all prompts from the prompts directory into the cache.

    Reads markdown files from the 'prompts' directory and populates
    the global prompt cache. Supports unified prompts, legacy files,
    model-specific prompts, and optimized diagram generation prompts.

    Returns:
        Dict[str, str]: A dictionary mapping prompt keys to prompt content.
    """
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

    # Load optimized generation prompts for different diagram formats
    # These are standalone prompt files optimized for each diagram type
    d2_gen_path = prompt_dir / "D2_GENERATION.md"
    if d2_gen_path.exists():
        _prompt_cache["generate_d2"] = _load_full_file(d2_gen_path)

    mermaid_gen_path = prompt_dir / "MERMAID_GENERATION.md"
    if mermaid_gen_path.exists():
        _prompt_cache["generate_mermaid"] = _load_full_file(mermaid_gen_path)

    structurizr_gen_path = prompt_dir / "STRUCTURIZR_GENERATION.md"
    if structurizr_gen_path.exists():
        _prompt_cache["generate_structurizr"] = _load_full_file(structurizr_gen_path)

    # Fallback to legacy GENERATE_PROMPTS.md for backward compatibility
    generate_path = prompt_dir / "GENERATE_PROMPTS.md"
    if generate_path.exists():
        # Only load if optimized prompts weren't found
        if "generate_mermaid" not in _prompt_cache:
            _prompt_cache["generate_mermaid"] = _extract_section(
                generate_path, "Mermaid Generation Prompt"
            )
        if "generate_d2" not in _prompt_cache:
            _prompt_cache["generate_d2"] = _extract_section(
                generate_path, "D2 Generation Prompt"
            )
        if "generate_plantuml" not in _prompt_cache:
            _prompt_cache["generate_plantuml"] = _extract_section(
                generate_path, "PlantUML Generation Prompt"
            )
        if "generate_structurizr" not in _prompt_cache:
            _prompt_cache["generate_structurizr"] = _extract_section(
                generate_path, "Structurizr Generation Prompt"
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
        _prompt_cache["refine_structurizr"] = _extract_section(
            refine_path, "Structurizr Refinement Prompt"
        )

    return _prompt_cache


def get_prompt(prompt_name: str, model_id: Optional[str] = None) -> Optional[str]:
    """
    Get a prompt by name and optionally by model ID, with variable substitution.

    This function loads prompts from markdown files and performs dynamic variable
    substitution for configurable values like {SCORE_TARGET}.

    Args:
        prompt_name (str): The base name of the prompt (e.g., "clarify_universal").
        model_id (Optional[str]): Optional model ID for model-specific prompts (e.g., "gpt5", "grok").

    Returns:
        Optional[str]: The prompt string with all variables substituted, or None if not found.
    """
    # Load all prompts if not already loaded
    prompts = load_prompts()

    # Prioritize model-specific prompts if a model_id is provided
    prompt_content = None
    if model_id:
        model_specific_key = f"{prompt_name}_{model_id}"
        # Check if a model-specific prompt exists
        if model_specific_key in prompts:
            prompt_content = prompts.get(model_specific_key)

    # Fall back to generic prompt if no model-specific version found
    if prompt_content is None:
        prompt_content = prompts.get(prompt_name)

    # Perform variable substitution if prompt was found
    if prompt_content:
        # Get dynamic values from environment
        score_target = env_manager.get_score_target()

        # Replace placeholders with actual values
        prompt_content = prompt_content.replace("{SCORE_TARGET}", str(score_target))

    return prompt_content


def _load_full_file(file_path: Path) -> str:
    """
    Safely read entire file content with error handling.

    Args:
        file_path (Path): Path to the file to read.

    Returns:
        str: The content of the file, or an empty string if reading fails.
    """
    # Safely read entire file content with error handling
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            return f.read().strip()
    except Exception as e:
        # Log error and return empty string if file read fails
        print(f"Error loading file {file_path}: {e}")
        return ""


def _extract_section(file_path: Path, section_header: str) -> str:
    """
    Extract a specific markdown section from a file.

    Searches for a section starting with '## {section_header}' and returns
    the content until the next section or end of file.

    Args:
        file_path (Path): Path to the file.
        section_header (str): The header of the section to extract (without '## ').

    Returns:
        str: The content of the section, or an empty string if not found.
    """
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
