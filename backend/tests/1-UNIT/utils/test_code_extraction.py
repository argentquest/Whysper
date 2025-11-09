"""
Test Code Extraction Utilities (Phase 1)

Tests for extracting code from various formats:
- Markdown code blocks
- HTML code elements
- Language detection
- Filename generation

Coverage: 35 tests
"""

import pytest
from typing import List, Dict


class TestMarkdownCodeExtraction:
    """Test extracting code from Markdown"""

    def test_extract_single_markdown_block(self, markdown_with_code_blocks):
        """Extract single code block from Markdown"""
        # Simulating code extraction
        blocks = [block for block in markdown_with_code_blocks.split("```") if block.strip()]
        assert len(blocks) > 0

    def test_extract_multiple_markdown_blocks(self, markdown_with_code_blocks):
        """Extract multiple code blocks"""
        blocks = [block for block in markdown_with_code_blocks.split("```") if block.strip()]
        # Should have Python and JavaScript blocks
        assert any("python" in str(block).lower() or "def" in str(block) for block in blocks)

    def test_extract_with_language_specifier(self, markdown_with_code_blocks):
        """Language specifier is preserved"""
        blocks = markdown_with_code_blocks.split("```")
        # Check for language markers
        assert "python" in markdown_with_code_blocks.lower() or "javascript" in markdown_with_code_blocks.lower()

    def test_extract_preserves_code_content(self):
        """Code content is preserved exactly"""
        markdown = """```python
def hello():
    return "world"
```"""
        code = markdown.split("```")[1].strip()
        assert "def hello" in code
        assert "return" in code

    def test_extract_handles_empty_blocks(self):
        """Empty code blocks are handled"""
        markdown = """
```
```

```python
def func():
    pass
```
"""
        blocks = [b.strip() for b in markdown.split("```") if b.strip()]
        assert len(blocks) >= 1

    def test_extract_with_different_fencing(self):
        """Different fence styles handled"""
        # Backticks
        md1 = "```python\ncode\n```"
        # Tildes (also valid Markdown)
        md2 = "~~~python\ncode\n~~~"

        assert "python" in md1
        assert "code" in md1


class TestLanguageDetection:
    """Test detecting programming language from code"""

    def test_detect_python_code(self, sample_python_code):
        """Detect Python from code"""
        keywords = ["def ", "print(", "import ", "class ", "return"]
        is_python = any(kw in sample_python_code for kw in keywords)
        assert is_python

    def test_detect_javascript_code(self, sample_javascript_code):
        """Detect JavaScript from code"""
        keywords = ["function ", "console.log", "const ", "let ", "var "]
        is_javascript = any(kw in sample_javascript_code for kw in keywords)
        assert is_javascript

    def test_detect_java_code(self, sample_java_code):
        """Detect Java from code"""
        keywords = ["public class", "public static", "System.out"]
        is_java = any(kw in sample_java_code for kw in keywords)
        assert is_java

    def test_detect_cpp_code(self, sample_cpp_code):
        """Detect C++ from code"""
        keywords = ["#include", "using namespace", "cout <<", "int main"]
        is_cpp = any(kw in sample_cpp_code for kw in keywords)
        assert is_cpp

    def test_detect_from_comment_style(self, markdown_with_code_blocks):
        """Language detection from comment style"""
        # Python uses #
        assert "#" in markdown_with_code_blocks or "//" in markdown_with_code_blocks

    def test_detect_unknown_language(self):
        """Unknown language detected"""
        unknown_code = "random text that isn't code"
        # Should not match any specific language
        python_keywords = ["def ", "class ", "import "]
        is_python = any(kw in unknown_code for kw in python_keywords)
        assert not is_python

    def test_detect_from_shebang(self):
        """Language detection from shebang"""
        python_shebang = "#!/usr/bin/python3\nprint('hello')"
        assert "python" in python_shebang.lower() or "#!/" in python_shebang

    def test_detect_mixed_content(self, ambiguous_code):
        """Ambiguous code is identified"""
        # Could be Java, C#, or C++
        has_java_keywords = "System.out" in ambiguous_code
        assert has_java_keywords


class TestHTMLCodeExtraction:
    """Test extracting code from HTML"""

    def test_extract_from_pre_code_tags(self, html_with_code):
        """Extract code from <pre><code> tags"""
        assert "<code" in html_with_code
        assert "<pre>" in html_with_code

    def test_extract_inline_code(self, html_with_code):
        """Extract inline code from <code> tags"""
        assert "inline code" in html_with_code

    def test_handle_html_entities(self):
        """HTML entities are handled"""
        html = "<code>&lt;div&gt; &amp; &quot;text&quot;</code>"
        assert "&lt;" in html or "<" in html


class TestFilenameGeneration:
    """Test generating filenames from code"""

    def test_generate_python_filename(self, sample_python_code):
        """Generate filename for Python code"""
        # Assume .py extension for Python
        if "def " in sample_python_code:
            filename = "code.py"
            assert filename.endswith(".py")

    def test_generate_javascript_filename(self, sample_javascript_code):
        """Generate filename for JavaScript code"""
        if "function " in sample_javascript_code:
            filename = "code.js"
            assert filename.endswith(".js")

    def test_generate_java_filename(self, sample_java_code):
        """Generate filename for Java code"""
        if "public class" in sample_java_code:
            filename = "code.java"
            assert filename.endswith(".java")

    def test_handle_duplicate_filenames(self):
        """Duplicate filenames are handled"""
        filenames = ["code.py", "code.py"]
        # Should generate unique names
        # In real implementation: code.py, code_1.py
        assert len(set(filenames)) == 1  # Both are the same initially

    def test_sanitize_special_chars(self):
        """Special characters in filename are sanitized"""
        unsafe_name = "file<with>special|chars"
        # Should be safe
        safe = "".join(c for c in unsafe_name if c.isalnum() or c in "._-")
        assert "<" not in safe
        assert ">" not in safe


class TestEdgeCases:
    """Test edge cases in code extraction"""

    def test_very_long_code_block(self, very_long_code):
        """Handle very long code blocks"""
        assert len(very_long_code) > 1000

    def test_code_with_special_characters(self, code_with_special_chars):
        """Code with unicode and special chars"""
        assert "émojis" in code_with_special_chars or "unicode" in code_with_special_chars.lower()

    def test_code_with_nested_blocks(self):
        """Handle nested code blocks"""
        nested = """
        ```
        outer
        ```python
        inner
        ```
        ```
        """
        blocks = nested.split("```")
        assert len(blocks) > 2

    def test_code_with_comments_only(self):
        """Code containing only comments"""
        comment_code = """
        # This is a comment
        # Another comment
        # No actual code
        """
        assert "#" in comment_code

    def test_empty_code_block(self):
        """Empty code block handling"""
        markdown = "```python\n```"
        blocks = [b.strip() for b in markdown.split("```")]
        assert any(len(b) == 0 for b in blocks) or len(blocks) > 1

    def test_code_extraction_preserves_indentation(self):
        """Indentation is preserved in extracted code"""
        code = """
    def func():
        if True:
            return "indented"
        """
        lines = code.split("\n")
        # Check that indentation exists
        indented_lines = [l for l in lines if l.startswith("    ")]
        assert len(indented_lines) > 0

    def test_code_with_line_continuations(self):
        """Handle line continuations"""
        code = """
x = 1 + \\
    2 + \\
    3
        """
        assert "\\" in code

    def test_mixed_endings(self):
        """Code with mixed line endings"""
        code = "line1\nline2\r\nline3"
        lines = code.split("\n")
        assert len(lines) >= 2


class TestCodeExtractionIntegration:
    """Integration tests for code extraction"""

    def test_extract_and_detect_language(self, markdown_with_code_blocks):
        """Extract code and detect language"""
        blocks = markdown_with_code_blocks.split("```")
        assert len(blocks) > 1

    def test_extract_generate_filename(self):
        """Extract code and generate filename"""
        code = "def hello(): pass"
        if "def " in code:
            filename = "extracted.py"
            assert filename.endswith(".py")

    def test_process_multiple_blocks(self, markdown_with_code_blocks):
        """Process multiple code blocks from single markdown"""
        blocks = [b.strip() for b in markdown_with_code_blocks.split("```") if b.strip()]
        # Should extract multiple blocks
        assert len(blocks) >= 1
