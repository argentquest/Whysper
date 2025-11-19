#!/usr/bin/env python3
"""
Comprehensive Inline Comments Automation Script

Adds detailed inline comments to all TypeScript/TSX and Python files in the project.
Uses OpenRouter API (configured in backend/.env) to generate comments intelligently.

Features:
- Processes all TS/TSX files in frontend/src
- Processes all Python files in backend
- Preserves existing code and comments
- Adds strategic inline comments explaining logic
- Batch processing for efficiency
- Progress tracking and error handling
- Git integration for commits
"""

import os
import sys
import json
import subprocess
from pathlib import Path
from typing import List, Dict, Tuple
import re
from datetime import datetime

# Add backend to path for environment loading
sys.path.insert(0, str(Path(__file__).parent / "backend"))

try:
    from app.common.env_manager import env_manager
    API_KEY = env_manager.get("API_KEY")
    API_URL = env_manager.get("OPENROUTER_API_URL", "https://openrouter.ai/api/v1/chat/completions")
except Exception as e:
    print(f"Error loading environment: {e}")
    print("Make sure backend/.env is configured properly")
    sys.exit(1)

if not API_KEY:
    print("ERROR: API_KEY not found in backend/.env")
    print("Please configure your OpenRouter API key in backend/.env")
    sys.exit(1)


class InlineCommentator:
    """Handles adding inline comments to code files."""

    def __init__(self):
        self.api_key = API_KEY
        self.api_url = API_URL
        self.files_processed = 0
        self.files_skipped = 0
        self.errors = []
        self.progress_log = []

    def log_progress(self, message: str):
        """Log progress message."""
        timestamp = datetime.now().strftime("%H:%M:%S")
        log_entry = f"[{timestamp}] {message}"
        print(log_entry)
        self.progress_log.append(log_entry)

    def get_file_category(self, file_path: str) -> str:
        """Determine file category (component, hook, service, etc)."""
        parts = file_path.lower().split(os.sep)

        if "components" in parts:
            return "component"
        elif "hooks" in parts:
            return "hook"
        elif "services" in parts:
            return "service"
        elif "utils" in parts:
            return "utility"
        elif "types" in parts:
            return "type"
        elif "models" in parts or "database" in parts:
            return "model"
        elif "api" in parts and "endpoints" in parts:
            return "endpoint"
        elif "test" in parts:
            return "test"
        else:
            return "utility"

    def generate_comments(self, code: str, file_type: str, category: str) -> str:
        """Generate inline comments using Claude API via OpenRouter."""

        if file_type == "typescript":
            prompt = f"""Add comprehensive inline comments to this TypeScript/TSX code.

FILE CATEGORY: {category}

Requirements:
- Add comments explaining HOW each function/method works
- Comment complex logic steps
- Explain variable purposes
- Explain conditional branches
- Explain loops and iterations
- Comment API calls and side effects
- Keep ALL existing code EXACTLY the same
- Only add comments (no code changes)
- Use // style comments
- Add a comment every 3-5 lines of code
- Focus on WHY and HOW, not just WHAT

Code:
```typescript
{code}
```

Return ONLY the enhanced code with comments. No markdown, no explanations."""

        else:  # Python
            prompt = f"""Add comprehensive inline comments to this Python code.

FILE CATEGORY: {category}

Requirements:
- Add comments explaining HOW each function/method works
- Comment complex logic steps
- Explain variable purposes
- Explain conditional branches
- Explain loops and iterations
- Comment API calls and side effects
- Keep ALL existing code EXACTLY the same
- Only add comments (no code changes)
- Use # style comments
- Add a comment every 3-5 lines of code
- Focus on WHY and HOW, not just WHAT

Code:
```python
{code}
```

Return ONLY the enhanced code with comments. No markdown, no explanations."""

        try:
            import requests

            response = requests.post(
                self.api_url,
                headers={
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json"
                },
                json={
                    "model": "openai/gpt-4o",
                    "messages": [
                        {"role": "user", "content": prompt}
                    ],
                    "max_tokens": len(code) * 2 + 500,
                    "temperature": 0.3  # Low temperature for consistency
                },
                timeout=60
            )

            if response.status_code != 200:
                self.errors.append(f"API Error: {response.status_code} - {response.text}")
                return code

            result = response.json()
            if "choices" in result and len(result["choices"]) > 0:
                enhanced_code = result["choices"][0]["message"]["content"]
                # Remove markdown code blocks if present
                enhanced_code = enhanced_code.replace("```typescript\n", "").replace("```python\n", "").replace("```\n", "").replace("```", "")
                return enhanced_code.strip()

            return code

        except Exception as e:
            self.errors.append(f"API call failed: {str(e)}")
            return code

    def process_file(self, file_path: str) -> bool:
        """Process a single file to add inline comments."""
        try:
            # Determine file type
            if file_path.endswith((".ts", ".tsx")):
                file_type = "typescript"
            elif file_path.endswith(".py"):
                file_type = "python"
            else:
                return False

            # Read file
            with open(file_path, 'r', encoding='utf-8') as f:
                original_code = f.read()

            # Skip if file is very small or already has many comments
            lines = original_code.split('\n')
            comment_ratio = sum(1 for line in lines if line.strip().startswith(('#', '//'))) / len(lines) if lines else 0

            if comment_ratio > 0.4:  # Already heavily commented
                self.log_progress(f"⏭️  SKIP (heavily commented): {file_path}")
                self.files_skipped += 1
                return True

            if len(lines) < 10:  # Too small to comment
                self.log_progress(f"⏭️  SKIP (too small): {file_path}")
                self.files_skipped += 1
                return True

            # Get category for better comments
            category = self.get_file_category(file_path)

            # Generate comments
            self.log_progress(f"🔄 Processing ({category}): {file_path}")
            enhanced_code = self.generate_comments(original_code, file_type, category)

            # Validate (rough check that code wasn't broken)
            original_lines = len(original_code.split('\n'))
            enhanced_lines = len(enhanced_code.split('\n'))

            # Enhanced code should be similar in structure
            if enhanced_lines < original_lines * 0.8:
                self.log_progress(f"⚠️  WARN (reduced lines): {file_path}")
                return False

            # Write back
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(enhanced_code)

            self.log_progress(f"✅ DONE: {file_path} (+{enhanced_lines - original_lines} lines)")
            self.files_processed += 1
            return True

        except Exception as e:
            self.errors.append(f"{file_path}: {str(e)}")
            self.log_progress(f"❌ ERROR: {file_path} - {str(e)}")
            return False

    def get_files_to_process(self, pattern: str) -> List[str]:
        """Get all files matching pattern."""
        files = []
        root = Path(__file__).parent

        if "frontend" in pattern:
            base_path = root / "frontend" / "src"
            extensions = (".ts", ".tsx")
        else:  # backend
            base_path = root / "backend"
            extensions = (".py",)

        # Exclude directories
        exclude_dirs = {".git", ".venv", "venv", "node_modules", "__pycache__", ".pytest_cache", "dist", "build"}

        for file_path in base_path.rglob("*"):
            if any(excluded in file_path.parts for excluded in exclude_dirs):
                continue
            if file_path.is_file() and file_path.suffix in extensions:
                files.append(str(file_path))

        return sorted(files)

    def process_batch(self, pattern: str, batch_size: int = 5):
        """Process files in batches."""
        files = self.get_files_to_process(pattern)
        self.log_progress(f"\n{'='*60}")
        self.log_progress(f"Processing {len(files)} files matching: {pattern}")
        self.log_progress(f"{'='*60}\n")

        for i, file_path in enumerate(files, 1):
            self.log_progress(f"[{i}/{len(files)}] ", end="")
            self.process_file(file_path)

            # Small delay between requests to avoid rate limiting
            if i % batch_size == 0:
                self.log_progress(f"\n⏸️  Waiting before next batch...")
                import time
                time.sleep(5)

        return len(files)

    def generate_report(self) -> str:
        """Generate processing report."""
        report = f"""
{'='*60}
INLINE COMMENTS AUTOMATION REPORT
{'='*60}

Processed: {self.files_processed}
Skipped: {self.files_skipped}
Errors: {len(self.errors)}

{'ERRORS:' if self.errors else 'No errors!'}
"""
        if self.errors:
            for error in self.errors[:10]:  # Show first 10 errors
                report += f"\n  - {error}"

        report += f"\n\n{'='*60}\n"
        return report

    def save_progress(self):
        """Save progress log to file."""
        log_file = Path(__file__).parent / "inline_comments_progress.log"
        with open(log_file, 'w') as f:
            f.write('\n'.join(self.progress_log))
        print(f"\nProgress saved to: {log_file}")


def main():
    """Main entry point."""
    print("\n" + "="*60)
    print("INLINE COMMENTS AUTOMATION")
    print("="*60 + "\n")

    commentator = InlineCommentator()

    try:
        # Process frontend files
        print("\n📁 FRONTEND FILES (TS/TSX)")
        frontend_count = commentator.process_batch("frontend", batch_size=5)

        # Process backend files
        print("\n\n📁 BACKEND FILES (Python)")
        backend_count = commentator.process_batch("backend", batch_size=5)

        # Generate report
        report = commentator.generate_report()
        print(report)

        # Save progress
        commentator.save_progress()

        # Commit changes
        if commentator.files_processed > 0:
            print("\n📝 Creating git commits...")

            if frontend_count > 0:
                subprocess.run([
                    "git", "add", "frontend/src"
                ], cwd=Path(__file__).parent)
                subprocess.run([
                    "git", "commit", "-m",
                    f"docs: Add comprehensive inline comments to all frontend files ({frontend_count} TS/TSX files)"
                ], cwd=Path(__file__).parent)
                print(f"✅ Committed frontend files")

            if backend_count > 0:
                subprocess.run([
                    "git", "add", "backend"
                ], cwd=Path(__file__).parent)
                subprocess.run([
                    "git", "commit", "-m",
                    f"docs: Add comprehensive inline comments to all backend files ({backend_count} Python files)"
                ], cwd=Path(__file__).parent)
                print(f"✅ Committed backend files")

        return 0

    except KeyboardInterrupt:
        print("\n\n⚠️  Interrupted by user")
        commentator.save_progress()
        return 1
    except Exception as e:
        print(f"\n\n❌ Fatal error: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
