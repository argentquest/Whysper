"""
Language detection utilities for code blocks.

This module provides intelligent programming language detection using keyword
analysis and pattern matching. It supports 15+ programming languages and
generates appropriate filenames with correct file extensions.

Supported Languages:
- Python: def, import, print(), if __name__
- JavaScript: function, const, let, var, console.log, =>
- Java: public class, private, public static void
- C/C++: #include, int main, printf, cout, using namespace, std::
- Rust: fn, let mut, println!, match
- Go: func, package, import "", fmt.print
- PHP: <?php, echo, $
- SQL: SELECT, INSERT, UPDATE, DELETE, FROM, WHERE (checked first)
- HTML: <html, <div, <body, <script
- CSS: {, }, color:, background:
- Markdown: #, ##, ###
- Bash: #!/bin/bash, echo, if [, fi

Detection Strategy:
1. SQL keywords checked first (to avoid false Python matches on 'FROM')
2. Language-specific keyword patterns matched against lowercase code
3. Falls back to 'text' for unrecognized content
4. Case-insensitive matching for reliability

File Extension Mapping:
- Comprehensive mapping from language names to file extensions
- Support for common and specialized file types
- Fallback to .txt for unknown languages
"""
import re
from typing import Dict


def detect_language(code: str) -> str:
    """
    Detect the programming language of a code block using keyword analysis.
    
    Uses a priority-based keyword matching system to identify programming
    languages. SQL is checked first to avoid false matches with Python's
    'from' keyword. Falls back to 'text' for unrecognized content.
    
    Args:
        code: The code content to analyze (can be multiline)
        
    Returns:
        str: The detected language identifier (lowercase)
        
    Example:
        >>> detect_language("def hello():\\n    print('world')")
        'python'
        >>> detect_language("SELECT * FROM users")
        'sql'
    """
    # Normalize code to lowercase and strip whitespace for consistent matching
    code_lower = code.lower().strip()
    
    # Check for specific language patterns in priority order
    # SQL is checked first since FROM is also a Python keyword
    if any(keyword in code_lower for keyword in ['select ', 'insert ', 'update ', 'delete ', 'select*', 'from ', 'order by', 'group by', 'where ']):
        return "sql"
    
    # Python detection: common keywords and patterns
    elif any(keyword in code_lower for keyword in ['def ', 'import ', 'from ', 'print(', 'if __name__']):
        return "python"
    
    # JavaScript detection: ES6+ and traditional patterns
    elif any(keyword in code_lower for keyword in ['function', 'const ', 'let ', 'var ', 'console.log', '=>']):
        return "javascript"
    
    # Java detection: class structure and access modifiers
    elif any(keyword in code_lower for keyword in ['public class', 'private ', 'public static void']):
        return "java"
    
    # C/C++ detection: includes and main function
    elif any(keyword in code_lower for keyword in ['#include', 'int main', 'printf', 'cout']):
        return "cpp"
    
    # Additional C++ specific patterns (namespaces, STL)
    elif any(keyword in code_lower for keyword in ['using namespace', 'std::']):
        return "cpp"
    
    # Rust detection: unique syntax patterns
    elif any(keyword in code_lower for keyword in ['fn ', 'let mut', 'println!', 'match ']):
        return "rust"
    
    # Go detection: package structure and fmt usage
    elif any(keyword in code_lower for keyword in ['func ', 'package ', 'import "', 'fmt.print']):
        return "go"
    
    # PHP detection: PHP tags and variables
    elif any(keyword in code_lower for keyword in ['<?php', 'echo ', '$']):
        return "php"
    
    # HTML detection: common tags
    elif any(keyword in code_lower for keyword in ['<html', '<div', '<body', '<script']):
        return "html"
    
    # CSS detection: selectors and properties
    elif any(keyword in code_lower for keyword in ['{', '}', 'color:', 'background:']):
        return "css"
    
    # Markdown detection: headers
    elif any(keyword in code_lower for keyword in ['# ', '## ', '### ']):
        return "markdown"
    
    # Bash/shell script detection: shebang and commands
    elif any(keyword in code_lower for keyword in ['#!/bin/bash', 'echo ', 'if [', 'fi']):
        return "bash"
    
    # Fallback for unrecognized content
    else:
        return "text"


def generate_filename(language: str, index: int) -> str:
    """
    Generate a descriptive filename for an extracted code block.
    
    Creates a standardized filename with the format 'extracted_code_{index}.{ext}'
    where the extension is determined by the programming language. This ensures
    proper syntax highlighting and IDE support when code blocks are saved.
    
    Args:
        language: The programming language identifier (case-insensitive)
        index: The sequential number of the code block (1-based indexing)
        
    Returns:
        str: Generated filename with appropriate file extension
        
    Example:
        >>> generate_filename("python", 1)
        'extracted_code_1.py'
        >>> generate_filename("JAVASCRIPT", 2)
        'extracted_code_2.js'
        >>> generate_filename("unknown", 3)
        'extracted_code_3.txt'
    """
    # Comprehensive language to file extension mapping
    # Covers common programming languages, markup, and data formats
    extensions: Dict[str, str] = {
        # Programming languages
        "python": "py",           # Python scripts
        "javascript": "js",       # JavaScript files
        "typescript": "ts",       # TypeScript files
        "java": "java",          # Java source files
        "cpp": "cpp",            # C++ source files
        "c": "c",                # C source files
        "rust": "rs",            # Rust source files
        "go": "go",              # Go source files
        "php": "php",            # PHP scripts
        
        # Database and query languages
        "sql": "sql",            # SQL scripts
        
        # Web technologies
        "html": "html",          # HTML documents
        "css": "css",            # CSS stylesheets
        
        # Documentation and markup
        "markdown": "md",        # Markdown documents
        
        # Shell and scripting
        "bash": "sh",            # Bash shell scripts
        "shell": "sh",           # Generic shell scripts
        
        # Data formats
        "json": "json",          # JSON data files
        "xml": "xml",            # XML documents
        "yaml": "yaml",          # YAML configuration files
        
        # Container and deployment
        "dockerfile": "dockerfile", # Docker container definitions
        
        # Fallback
        "text": "txt",           # Plain text files
    }
    
    # Get extension for language (case-insensitive), default to .txt
    extension = extensions.get(language.lower(), "txt")
    
    # Generate standardized filename with sequential numbering
    return f"extracted_code_{index}.{extension}"