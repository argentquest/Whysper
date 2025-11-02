"""
Mermaid v1 Provider Implementation

Self-contained Mermaid CLI renderer for validation and rendering.
Uses mmdc (mermaid-cli) for validation and rendering.
All code is contained within the diagrams folder - no external dependencies.
"""

from pathlib import Path
from typing import Optional, List, Tuple
import subprocess
import tempfile
import os
import re
import logging
from dataclasses import dataclass

from diagrams.base_diagram import BaseDiagramProvider
from diagrams.models import (
    ProviderCapability,
    ValidationResult,
    RenderResult
)

logger = logging.getLogger(__name__)


# =====================================================================
# MERMAID SYNTAX FIXER (Self-contained)
# =====================================================================

@dataclass
class MermaidFixResult:
    """Result of Mermaid syntax fixing operation"""
    is_valid: bool
    corrected_code: str
    corrections: List[str]
    warnings: List[str]
    errors: List[str]


def fix_mermaid_syntax(code: str) -> MermaidFixResult:
    """
    Attempts to fix common Mermaid syntax errors.

    Args:
        code: The Mermaid code to fix

    Returns:
        MermaidFixResult: Result containing corrected code and diagnostics
    """
    corrections = []
    warnings = []
    errors = []
    corrected_code = code.strip()

    if not corrected_code:
        errors.append("Empty Mermaid code")
        return MermaidFixResult(False, corrected_code, corrections, warnings, errors)

    # Fix 1: Ensure diagram type declaration
    if not _has_diagram_type_declaration(corrected_code):
        corrected_code = _add_diagram_type_declaration(corrected_code)
        corrections.append("Added missing diagram type declaration")

    # Fix 2: Fix arrow syntax issues
    corrected_code, arrow_fixes = _fix_arrow_syntax(corrected_code)
    corrections.extend(arrow_fixes)

    # Fix 3: Fix node syntax issues
    corrected_code, node_fixes = _fix_node_syntax(corrected_code)
    corrections.extend(node_fixes)

    # Fix 4: Fix subgraph syntax issues
    corrected_code, subgraph_fixes = _fix_subgraph_syntax(corrected_code)
    corrections.extend(subgraph_fixes)

    is_valid = len(errors) == 0

    return MermaidFixResult(is_valid, corrected_code, corrections, warnings, errors)


def _has_diagram_type_declaration(code: str) -> bool:
    """Check if code has a diagram type declaration."""
    diagram_types = [
        'graph', 'flowchart', 'sequenceDiagram', 'classDiagram',
        'stateDiagram', 'stateDiagram-v2', 'erDiagram', 'gantt',
        'pie', 'journey', 'gitGraph', 'mindmap', 'timeline'
    ]

    first_line = code.strip().split('\n')[0].strip()
    return any(first_line.startswith(dtype) for dtype in diagram_types)


def _add_diagram_type_declaration(code: str) -> str:
    """Add appropriate diagram type declaration based on content."""
    trimmed = code.strip()

    # Try to infer the diagram type
    if 'participant' in trimmed or '->>' in trimmed:
        return f"sequenceDiagram\n{trimmed}"
    elif 'class ' in trimmed or '<|--' in trimmed:
        return f"classDiagram\n{trimmed}"
    elif 'state ' in trimmed or '[*]' in trimmed:
        return f"stateDiagram-v2\n{trimmed}"
    else:
        # Default to flowchart
        return f"flowchart TD\n{trimmed}"


def _fix_arrow_syntax(code: str) -> Tuple[str, List[str]]:
    """Fix common arrow syntax issues."""
    corrections = []
    fixed = code
    original = fixed

    # Fix flowchart arrows - ensure proper spacing
    fixed = re.sub(r'(\w+)-->', r'\1 -->', fixed)
    fixed = re.sub(r'-->(\w+)', r'--> \1', fixed)

    # Fix sequence diagram arrows
    fixed = re.sub(r'(\w+)-->>', r'\1 -->>', fixed)
    fixed = re.sub(r'-->>(\w+)', r'-->> \1', fixed)

    if fixed != original:
        corrections.append("Fixed arrow spacing")

    return fixed, corrections


def _fix_node_syntax(code: str) -> Tuple[str, List[str]]:
    """Fix node ID and label issues."""
    corrections = []
    fixed = code

    # Fix nodes with special characters that need quotes
    def fix_node_label(match):
        node_id = match.group(1)
        label = match.group(2)

        # If label contains special characters, ensure it's quoted
        if any(char in label for char in [' ', '-', '(', ')', ':', ';']):
            if not (label.startswith('"') and label.endswith('"')):
                corrections.append(f"Added quotes to node label: {label}")
                return f'{node_id}["{label}"]'

        return match.group(0)

    fixed = re.sub(r'(\w+)\[([^\]]+)\]', fix_node_label, fixed)

    return fixed, corrections


def _fix_subgraph_syntax(code: str) -> Tuple[str, List[str]]:
    """Fix subgraph syntax issues."""
    corrections = []
    fixed = code

    # Count subgraph declarations and end statements
    subgraph_count = len(re.findall(r'\bsubgraph\b', fixed, re.IGNORECASE))
    end_count = len(re.findall(r'^\s*end\s*$', fixed, re.MULTILINE))

    # Add missing 'end' statements
    if subgraph_count > end_count:
        missing = subgraph_count - end_count
        fixed += '\n' + '\n'.join(['end'] * missing)
        corrections.append(f"Added {missing} missing 'end' statement(s)")

    return fixed, corrections


# =====================================================================
# MERMAID CLI VALIDATOR (Self-contained)
# =====================================================================

def validate_mermaid_with_cli(mermaid_code: str, mermaid_executable: str = "mmdc") -> Tuple[bool, str]:
    """
    Validates Mermaid code syntax by running the mmdc executable as a subprocess.

    Args:
        mermaid_code: The Mermaid code to validate
        mermaid_executable: Path to the mmdc executable (default: "mmdc")

    Returns:
        Tuple[bool, str]: (is_valid, message)
    """
    with tempfile.NamedTemporaryFile(mode='w', suffix='.mmd', delete=False) as temp_input:
        temp_input_name = temp_input.name
        temp_input.write(mermaid_code)
        temp_input.flush()

    temp_output_name = temp_input_name.replace('.mmd', '.svg')

    try:
        result = subprocess.run(
            [mermaid_executable, '-i', temp_input_name, '-o', temp_output_name],
            capture_output=True,
            text=True,
            check=True,
            timeout=120,
            shell=True
        )

        return (True, "Mermaid Syntax is Valid.")

    except subprocess.CalledProcessError as e:
        error_message = e.stderr.strip() or e.stdout.strip() or "Unknown Mermaid syntax error"
        cleaned_error = _clean_mermaid_error(error_message)
        return (False, f"Mermaid Syntax Error:\n{cleaned_error}")

    except subprocess.TimeoutExpired:
        return (False, "Mermaid validation timed out")

    except FileNotFoundError:
        return (False, "Mermaid CLI (mmdc) not found. Install with: npm install -g @mermaid-js/mermaid-cli")

    except Exception as e:
        return (False, f"Unexpected error during validation: {str(e)}")

    finally:
        try:
            if os.path.exists(temp_input_name):
                os.unlink(temp_input_name)
            if os.path.exists(temp_output_name):
                os.unlink(temp_output_name)
        except Exception:
            pass


def is_mermaid_cli_available(mermaid_executable: str = "mmdc") -> bool:
    """
    Check if the Mermaid CLI (mmdc) executable is available.

    Args:
        mermaid_executable: Path to the mmdc executable

    Returns:
        bool: True if available, False otherwise
    """
    try:
        # On Windows, mmdc is a .cmd file, so we need shell=True
        # Or we can try both with and without .cmd extension
        import platform
        is_windows = platform.system() == "Windows"

        result = subprocess.run(
            [mermaid_executable, "--version"],
            capture_output=True,
            text=True,
            check=True,
            timeout=10,
            shell=is_windows  # Use shell on Windows for .cmd files
        )
        return True
    except Exception:
        return False


def validate_mermaid_and_render(
    mermaid_code: str,
    output_format: str = "svg",
    mermaid_executable: str = "mmdc"
) -> Tuple[bool, str, Optional[str]]:
    """
    Validates Mermaid code and renders it if valid.

    Args:
        mermaid_code: The Mermaid code to validate and render
        output_format: Output format ('svg' or 'png')
        mermaid_executable: Path to the mmdc executable

    Returns:
        Tuple[bool, str, Optional[str]]: (is_valid, message, rendered_output)
    """
    with tempfile.NamedTemporaryFile(mode='w', suffix='.mmd', delete=False) as temp_input:
        temp_input_name = temp_input.name
        temp_input.write(mermaid_code)
        temp_input.flush()

    output_ext = '.svg' if output_format == 'svg' else '.png'
    temp_output_name = temp_input_name.replace('.mmd', output_ext)

    try:
        result = subprocess.run(
            [mermaid_executable, '-i', temp_input_name, '-o', temp_output_name],
            capture_output=True,
            text=True,
            check=True,
            timeout=120,
            shell=True
        )

        # Read the output file
        with open(temp_output_name, 'rb' if output_format == 'png' else 'r') as f:
            if output_format == 'png':
                import base64
                rendered_output = base64.b64encode(f.read()).decode('utf-8')
            else:
                rendered_output = f.read()

        return (True, "Mermaid diagram rendered successfully", rendered_output)

    except subprocess.CalledProcessError as e:
        error_message = e.stderr.strip() or e.stdout.strip() or "Unknown Mermaid error"
        cleaned_error = _clean_mermaid_error(error_message)
        return (False, f"Mermaid Rendering Error:\n{cleaned_error}", None)

    except Exception as e:
        return (False, f"Unexpected error during rendering: {str(e)}", None)

    finally:
        try:
            if os.path.exists(temp_input_name):
                os.unlink(temp_input_name)
            if os.path.exists(temp_output_name):
                os.unlink(temp_output_name)
        except Exception:
            pass


def _clean_mermaid_error(error_message: str) -> str:
    """Clean up Mermaid CLI error messages."""
    # Remove ANSI color codes
    ansi_escape = re.compile(r'\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])')
    cleaned = ansi_escape.sub('', error_message)

    # Extract relevant lines
    lines = cleaned.split('\n')
    relevant_lines = []

    for line in lines:
        if not line.strip():
            continue
        if 'at Object.' in line or 'at Function.' in line:
            continue
        if line.strip().startswith('at ') and '(' in line:
            continue
        relevant_lines.append(line)

    if relevant_lines:
        return '\n'.join(relevant_lines[:10])

    return error_message


# =====================================================================
# MERMAID V1 PROVIDER
# =====================================================================

class MermaidV1Provider(BaseDiagramProvider):
    """
    Mermaid CLI Provider v1

    Self-contained provider using the official Mermaid CLI (mmdc).
    Supports validation, rendering to SVG/PNG, and pattern-based auto-fix.
    """

    @property
    def provider_id(self) -> str:
        return "mermaidv1"

    @property
    def provider_name(self) -> str:
        return "Mermaid CLI Renderer v1"

    @property
    def diagram_type(self) -> str:
        return "mermaid"

    @property
    def supported_output_formats(self) -> List[str]:
        return ["mermaid", "svg", "png"]

    @property
    def capabilities(self) -> List[ProviderCapability]:
        return [
            ProviderCapability.VALIDATE,
            ProviderCapability.RENDER_SVG,
            ProviderCapability.RENDER_PNG,
            ProviderCapability.AUTO_FIX,
            ProviderCapability.LLM_CORRECTION
        ]

    def __init__(self, provider_folder: Path):
        """Initialize Mermaid v1 provider"""
        super().__init__(provider_folder)

        # Get executable path from config or use default
        # CRITICAL FIX: Use `or` operator to handle null values correctly
        custom_settings = self.config.custom or {}
        self.mermaid_executable = custom_settings.get("executable_path") or "mmdc"
        self._cli_available = None

        self.logger.info(f"Mermaid provider using executable: {self.mermaid_executable}")

    def is_available(self) -> bool:
        """Check if Mermaid CLI is available"""
        if self._cli_available is None:
            self._cli_available = is_mermaid_cli_available(self.mermaid_executable)

            if self._cli_available:
                self.logger.info("Mermaid CLI is available")
            else:
                self.logger.warning("Mermaid CLI not found - install with: npm install -g @mermaid-js/mermaid-cli")

        return self._cli_available

    def get_version(self) -> Optional[str]:
        """Get Mermaid CLI version"""
        if not self.is_available():
            return None

        try:
            result = subprocess.run(
                [self.mermaid_executable, "--version"],
                capture_output=True,
                text=True,
                timeout=5,
                shell=True
            )
            return result.stdout.strip()
        except Exception:
            return "Unknown"

    def validate_code(self, code: str, **options) -> ValidationResult:
        """Validate Mermaid code using CLI"""
        if not self.is_available():
            return ValidationResult(
                is_valid=False,
                error="Mermaid CLI (mmdc) not available",
                code_length=len(code)
            )

        self.logger.debug(f"Validating Mermaid code ({len(code)} chars)")

        try:
            is_valid, message = validate_mermaid_with_cli(code, self.mermaid_executable)

            return ValidationResult(
                is_valid=is_valid,
                error=None if is_valid else message,
                code_length=len(code)
            )

        except Exception as e:
            error_msg = f"Validation exception: {str(e)}"
            self.logger.error(error_msg, exc_info=True)
            return ValidationResult(
                is_valid=False,
                error=error_msg,
                code_length=len(code)
            )

    def auto_fix_pattern_based(self, code: str, error_message: str, **options) -> ValidationResult:
        """Attempt pattern-based auto-fix"""
        self.logger.info("Attempting pattern-based auto-fix...")

        try:
            fix_result = fix_mermaid_syntax(code)

            if fix_result.corrections:
                self.logger.info(f"Applied {len(fix_result.corrections)} pattern fix(es):")
                for correction in fix_result.corrections:
                    self.logger.info(f"  - {correction}")

            # Validate the fixed code
            validation_result = self.validate_code(fix_result.corrected_code, **options)

            if validation_result.is_valid:
                validation_result.auto_fixed = True
                validation_result.fixed_code = fix_result.corrected_code
                validation_result.correction_method = "pattern"
                self.logger.info("Pattern-based fix successful")
            else:
                self.logger.debug("Pattern-based fix did not resolve errors")

            return validation_result

        except Exception as e:
            self.logger.error(f"Pattern-based fix exception: {e}", exc_info=True)
            return ValidationResult(
                is_valid=False,
                error=error_message,
                auto_fixed=False,
                code_length=len(code)
            )

    def render(self, code: str, output_format: str = "svg", **options) -> RenderResult:
        """Render Mermaid diagram to specified format"""
        if not self.is_available():
            return RenderResult(
                success=False,
                content=None,
                output_format=output_format,
                validation=ValidationResult(
                    is_valid=False,
                    error="Mermaid CLI not available",
                    code_length=len(code)
                ),
                metadata={},
                error="Mermaid CLI (mmdc) not available"
            )

        # If output format is 'mermaid', just return the code
        if output_format.lower() == "mermaid":
            return RenderResult(
                success=True,
                content=code,
                output_format="mermaid",
                validation=ValidationResult(is_valid=True, code_length=len(code)),
                metadata={"provider": self.provider_id}
            )

        # Validate supported format
        if output_format.lower() not in ["svg", "png"]:
            return RenderResult(
                success=False,
                content=None,
                output_format=output_format,
                validation=ValidationResult(
                    is_valid=False,
                    error=f"Unsupported output format: {output_format}",
                    code_length=len(code)
                ),
                metadata={},
                error=f"Unsupported output format: {output_format}"
            )

        self.logger.debug(f"Rendering Mermaid to {output_format.upper()}...")

        try:
            is_valid, message, rendered_output = validate_mermaid_and_render(
                code,
                output_format=output_format.lower(),
                mermaid_executable=self.mermaid_executable
            )

            if is_valid and rendered_output:
                output_size = len(rendered_output)
                self.logger.info(
                    f"Rendered to {output_format.upper()} "
                    f"({output_size} bytes, {output_size/1024:.1f} KB)"
                )

                return RenderResult(
                    success=True,
                    content=rendered_output,
                    output_format=output_format,
                    validation=ValidationResult(is_valid=True, code_length=len(code)),
                    metadata={
                        "provider": self.provider_id,
                        "output_size_bytes": output_size,
                        "executable": self.mermaid_executable
                    }
                )
            else:
                self.logger.error(f"Rendering failed: {message[:200]}")
                return RenderResult(
                    success=False,
                    content=None,
                    output_format=output_format,
                    validation=ValidationResult(
                        is_valid=False,
                        error=message,
                        code_length=len(code)
                    ),
                    metadata={"provider": self.provider_id},
                    error=message
                )

        except Exception as e:
            error_msg = f"Rendering exception: {str(e)}"
            self.logger.error(error_msg, exc_info=True)
            return RenderResult(
                success=False,
                content=None,
                output_format=output_format,
                validation=ValidationResult(
                    is_valid=False,
                    error=error_msg,
                    code_length=len(code)
                ),
                metadata={"provider": self.provider_id},
                error=error_msg
            )

    def get_llm_correction_rules(self) -> Optional[str]:
        """Provide Mermaid-specific rules for LLM correction"""
        return """
MERMAID-SPECIFIC RULES:
- Always start with a diagram type (flowchart TD, sequenceDiagram, etc.)
- Use proper arrow syntax with spaces: A --> B (not A-->B)
- Quote labels containing special characters: A["Label with spaces"]
- NEVER use reserved keywords as node IDs (end, start, subgraph, graph, flowchart)
- Close all subgraphs with 'end' keyword
- For sequence diagrams: use participant declarations and proper arrow syntax (-->>, -->)
- For class diagrams: use proper inheritance syntax (<|--, --|>)
- Keep syntax simple and standard - avoid experimental features
""".strip()
