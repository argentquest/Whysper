#!/usr/bin/env python3
"""
Script to add comprehensive inline comments to TypeScript/TSX and Python files.
This script analyzes code structure and adds explanatory comments for:
- Function/method bodies
- Complex logic blocks
- State management
- API calls
- Conditional branches
- Loops and iterations
- Error handling
"""

import os
import re
import sys
from pathlib import Path
from typing import List, Tuple, Dict
import anthropic

# Initialize Anthropic client
client = anthropic.Anthropic(api_key=os.environ.get("ANTHROPIC_API_KEY"))

def read_file(filepath: str) -> str:
    """Read file contents safely with UTF-8 encoding."""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            return f.read()
    except Exception as e:
        print(f"Error reading {filepath}: {e}")
        return None

def write_file(filepath: str, content: str) -> bool:
    """Write file contents safely with UTF-8 encoding."""
    try:
        with open(filepath, 'w', encoding='utf-8', newline='\n') as f:
            f.write(content)
        return True
    except Exception as e:
        print(f"Error writing {filepath}: {e}")
        return False

def get_file_type(filepath: str) -> str:
    """Determine if file is TypeScript/TSX or Python."""
    ext = Path(filepath).suffix
    if ext in ['.ts', '.tsx']:
        return 'typescript'
    elif ext == '.py':
        return 'python'
    return 'unknown'

def add_inline_comments_with_claude(filepath: str, content: str, file_type: str) -> str:
    """Use Claude to add comprehensive inline comments to the code."""

    # Create language-specific instructions
    if file_type == 'typescript':
        lang_instructions = """
Language: TypeScript/TSX
Comment Style: // for single line, /* */ for multi-line blocks

Add comments for:
- React hooks (useState, useEffect, etc.) - explain what state/effect does
- Component rendering logic - explain conditional rendering
- Event handlers - explain what triggers them and what they do
- API calls - explain endpoint purpose and data flow
- State updates - explain why state is being changed
- Props destructuring - explain what props are used for
- Type guards and type assertions
- Async/await patterns
- Array operations (map, filter, reduce)
- Object transformations
"""
    else:  # python
        lang_instructions = """
Language: Python
Comment Style: # for single line, \"\"\" \"\"\" for multi-line blocks

Add comments for:
- Class methods - explain method purpose and flow
- Async/await operations - explain async workflow
- Database queries - explain what data is being fetched/stored
- API endpoint handlers - explain request/response flow
- State transitions - explain state changes
- LLM calls - explain prompt purpose and expected response
- Error handling - explain recovery strategy
- List comprehensions and generators
- Dictionary operations
- Context managers
"""

    prompt = f"""You are a code documentation expert. Add comprehensive INLINE comments to this code.

{lang_instructions}

CRITICAL RULES:
1. ADD comments INSIDE function/method bodies explaining HOW the code works
2. DO NOT add JSDoc/docstrings (those already exist or aren't needed)
3. DO NOT remove or modify existing comments
4. DO NOT change any code logic or structure
5. DO NOT add comments that just repeat what the code obviously does
6. FOCUS on explaining WHY and HOW, especially for:
   - Complex logic
   - Non-obvious variable purposes
   - State management decisions
   - API call purposes
   - Conditional logic reasoning
   - Loop iteration purposes
   - Error handling strategies

GOOD EXAMPLES:

TypeScript:
```typescript
// BEFORE:
const fetchData = async () => {{
  const response = await fetch('/api/data');
  const data = await response.json();
  setData(data);
}};

// AFTER:
const fetchData = async () => {{
  // Call backend API to retrieve latest data
  const response = await fetch('/api/data');

  // Parse JSON response into usable data structure
  const data = await response.json();

  // Update component state to trigger re-render with new data
  setData(data);
}};
```

Python:
```python
# BEFORE:
def process_items(items):
    result = []
    for item in items:
        if item.valid:
            result.append(item.transform())
    return result

# AFTER:
def process_items(items):
    # Initialize list to collect processed results
    result = []

    # Iterate through all items to filter and transform valid ones
    for item in items:
        # Only process items that pass validation check
        if item.valid:
            # Transform valid item and add to results
            result.append(item.transform())

    return result
```

Now add inline comments to this code:

```{file_type}
{content}
```

Return ONLY the complete code with inline comments added. No explanations, no markdown code blocks, just the code."""

    try:
        message = client.messages.create(
            model="claude-sonnet-4-5-20250929",
            max_tokens=16000,
            temperature=0,
            messages=[{
                "role": "user",
                "content": prompt
            }]
        )

        # Extract the code from response
        response_text = message.content[0].text

        # Remove markdown code blocks if present
        code_block_pattern = r'```(?:typescript|python|tsx|ts|py)?\n(.*?)\n```'
        match = re.search(code_block_pattern, response_text, re.DOTALL)
        if match:
            return match.group(1)

        # If no code block, return the whole response (Claude might return raw code)
        return response_text.strip()

    except Exception as e:
        print(f"Error calling Claude API for {filepath}: {e}")
        return None

def process_file(filepath: str, dry_run: bool = False) -> Tuple[bool, int]:
    """
    Process a single file to add inline comments.
    Returns (success, lines_added)
    """
    print(f"Processing: {filepath}")

    # Read original content
    original_content = read_file(filepath)
    if original_content is None:
        return False, 0

    # Skip if file is too small (likely just imports or empty)
    if len(original_content.strip()) < 50:
        print(f"  Skipping (too small): {filepath}")
        return True, 0

    # Determine file type
    file_type = get_file_type(filepath)
    if file_type == 'unknown':
        print(f"  Skipping (unknown type): {filepath}")
        return True, 0

    # Add comments using Claude
    commented_content = add_inline_comments_with_claude(filepath, original_content, file_type)
    if commented_content is None:
        return False, 0

    # Count new comment lines added
    original_comment_lines = len([line for line in original_content.split('\n')
                                  if line.strip().startswith('//') or line.strip().startswith('#')])
    new_comment_lines = len([line for line in commented_content.split('\n')
                            if line.strip().startswith('//') or line.strip().startswith('#')])
    lines_added = new_comment_lines - original_comment_lines

    if dry_run:
        print(f"  [DRY RUN] Would add ~{lines_added} comment lines")
        return True, lines_added

    # Write updated content
    if write_file(filepath, commented_content):
        print(f"  Added ~{lines_added} comment lines")
        return True, lines_added
    else:
        return False, 0

def process_files(file_list: List[str], dry_run: bool = False) -> Dict[str, any]:
    """Process multiple files and return statistics."""
    stats = {
        'total': len(file_list),
        'processed': 0,
        'failed': 0,
        'lines_added': 0,
        'files': []
    }

    for filepath in file_list:
        success, lines = process_file(filepath, dry_run)

        if success:
            stats['processed'] += 1
            stats['lines_added'] += lines
            stats['files'].append(filepath)
        else:
            stats['failed'] += 1

    return stats

def main():
    """Main entry point for the script."""
    import argparse

    parser = argparse.ArgumentParser(description='Add inline comments to code files')
    parser.add_argument('files', nargs='+', help='Files to process')
    parser.add_argument('--dry-run', action='store_true', help='Show what would be done without making changes')

    args = parser.parse_args()

    # Process all files
    stats = process_files(args.files, args.dry_run)

    # Print summary
    print("\n" + "="*60)
    print("SUMMARY")
    print("="*60)
    print(f"Total files: {stats['total']}")
    print(f"Processed: {stats['processed']}")
    print(f"Failed: {stats['failed']}")
    print(f"Comment lines added: {stats['lines_added']}")
    print("="*60)

    return 0 if stats['failed'] == 0 else 1

if __name__ == '__main__':
    sys.exit(main())
