#!/usr/bin/env python3
"""Check all Python files in backend directory for syntax errors."""

import ast
import sys
from pathlib import Path
import re
import py_compile
import tempfile

def check_syntax_errors(file_path):
    """Check if a Python file has syntax errors using multiple methods."""
    errors = []

    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
    except Exception as e:
        return [f"Cannot read file: {str(e)}"]

    # Method 1: Try to compile
    try:
        compile(content, str(file_path), 'exec')
    except SyntaxError as e:
        errors.append(f"COMPILE ERROR: {e.msg} at line {e.lineno}")
    except Exception as e:
        errors.append(f"COMPILE ERROR: {str(e)}")

    # Method 2: Try AST parsing
    try:
        ast.parse(content)
    except SyntaxError as e:
        errors.append(f"AST PARSE ERROR: {e.msg} at line {e.lineno}")
    except Exception as e:
        errors.append(f"AST PARSE ERROR: {str(e)}")

    # Method 3: Try py_compile
    try:
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False, encoding='utf-8') as tmp:
            tmp.write(content)
            tmp_path = tmp.name
        py_compile.compile(tmp_path, doraise=True)
        Path(tmp_path).unlink(missing_ok=True)
    except py_compile.PyCompileError as e:
        errors.append(f"PY_COMPILE ERROR: {str(e)}")
    except Exception as e:
        errors.append(f"PY_COMPILE ERROR: {str(e)}")
    finally:
        try:
            Path(tmp_path).unlink(missing_ok=True)
        except:
            pass

    return errors if errors else None

def check_orphaned_quotes(file_path):
    """Check for orphaned triple quotes and other issues."""
    issues = []
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()

        # Check for markdown code block markers
        if '```' in content:
            count = content.count('```')
            issues.append(f"Contains markdown code block markers (``` found {count} times)")

        # Count triple quotes (need to be more sophisticated to avoid counting inside strings)
        triple_double = content.count('"""')
        triple_single = content.count("'''")

        if triple_double % 2 != 0:
            issues.append(f"Unmatched triple double quotes (count: {triple_double})")

        if triple_single % 2 != 0:
            issues.append(f"Unmatched triple single quotes (count: {triple_single})")

        return issues
    except Exception as e:
        return [f"Cannot read file: {str(e)}"]

def main():
    backend_dir = Path(r'c:\Code2025\Whysper\backend')
    py_files = sorted(backend_dir.rglob('*.py'))

    syntax_errors = []
    quote_issues = []

    print(f"Checking {len(py_files)} Python files...\n", file=sys.stderr)

    for i, py_file in enumerate(py_files, 1):
        if i % 20 == 0:
            print(f"Progress: {i}/{len(py_files)} files checked...", file=sys.stderr)

        # Check syntax errors
        errors = check_syntax_errors(py_file)
        if errors:
            syntax_errors.append((str(py_file), errors))

        # Check for orphaned quotes
        issues = check_orphaned_quotes(py_file)
        if issues:
            quote_issues.append((str(py_file), issues))

    # Print files with syntax errors
    print("\n" + "="*80, file=sys.stderr)
    print("=== FILES WITH SYNTAX ERRORS ===", file=sys.stderr)
    print("="*80, file=sys.stderr)
    if syntax_errors:
        for file_path, errors in syntax_errors:
            print(f"\n{file_path}", file=sys.stderr)
            for error in errors:
                print(f"  {error}", file=sys.stderr)
    else:
        print("No syntax errors found!", file=sys.stderr)

    # Print files with quote issues (that might not be syntax errors yet)
    print("\n" + "="*80, file=sys.stderr)
    print("=== FILES WITH POTENTIAL QUOTE ISSUES ===", file=sys.stderr)
    print("="*80, file=sys.stderr)
    if quote_issues:
        for file_path, issues in quote_issues:
            if file_path not in [f for f, _ in syntax_errors]:
                print(f"\n{file_path}", file=sys.stderr)
                for issue in issues:
                    print(f"  - {issue}", file=sys.stderr)
    else:
        print("No quote issues found!", file=sys.stderr)

    # Output clean list of files with syntax errors to stdout
    print("\n" + "="*80, file=sys.stderr)
    print("=== FINAL LIST (SYNTAX ERRORS ONLY) ===", file=sys.stderr)
    print("="*80, file=sys.stderr)
    if syntax_errors:
        for file_path, _ in syntax_errors:
            print(file_path)
    else:
        print("No files with syntax errors!", file=sys.stderr)

    # Return exit code
    sys.exit(1 if syntax_errors else 0)

if __name__ == '__main__':
    main()
