"""
Tests for code extraction utilities.

This module tests the code block extraction functions that parse
text content for code blocks in various formats.
"""
import pytest
from app.utils.code_extraction import (
    extract_code_blocks_from_content,
    clean_html_entities,
    create_code_preview
)


class TestCodeExtraction:
    """Test code block extraction functionality."""
    
    def test_markdown_code_extraction(self):
        """Test extraction of Markdown fenced code blocks."""
        content = '''
Here's some Python code:

```python
def hello_world():
    print("Hello, World!")
    return True
```

And some JavaScript:

```javascript
function greet(name) {
    console.log(`Hello, ${name}!`);
}
```
'''
        
        blocks = extract_code_blocks_from_content(content, "test-msg-123")
        
        assert len(blocks) == 2
        
        # Check Python block
        python_block = blocks[0]
        assert python_block["language"] == "python"
        assert "def hello_world" in python_block["code"]
        assert python_block["filename"] == "extracted_code_1.py"
        assert python_block["source"] == "markdown"
        assert "test-msg-123" in python_block["id"]
        
        # Check JavaScript block
        js_block = blocks[1]
        assert js_block["language"] == "javascript"
        assert "function greet" in js_block["code"]
        assert js_block["filename"] == "extracted_code_2.js"
    
    def test_html_code_extraction_fallback(self):
        """Test extraction of HTML code blocks as fallback."""
        content = '''
<p>Here's some code:</p>
<pre><code class="language-python">
def hello_world():
    print("Hello from HTML!")
    return True
</code></pre>

<pre><code class="language-sql">
SELECT * FROM users;
</code></pre>
'''
        
        blocks = extract_code_blocks_from_content(content, "html-test")
        
        assert len(blocks) == 2
        
        # Check Python block
        python_block = blocks[0]
        assert python_block["language"] == "python"
        assert "def hello_world" in python_block["code"]
        assert python_block["source"] == "html"
        
        # Check SQL block
        sql_block = blocks[1]
        assert sql_block["language"] == "sql"
        assert "SELECT" in sql_block["code"]
    
    def test_empty_code_blocks_filtered(self):
        """Test that empty code blocks are filtered out."""
        content = '''
Valid code:
```python
print("Hello")
```

Empty block:
```javascript

```

Another empty:
```

```

More valid code:
```sql
SELECT 1;
```
'''
        
        blocks = extract_code_blocks_from_content(content, "filter-test")
        
        # Should only get 2 blocks (empty ones filtered out)
        assert len(blocks) == 2
        assert blocks[0]["language"] == "python"
        assert blocks[1]["language"] == "sql"
    
    def test_no_language_specified(self):
        """Test code extraction when no language is specified."""
        content = '''
```
function mystery() {
    return "What language am I?";
}
```
'''
        
        blocks = extract_code_blocks_from_content(content, "no-lang-test")
        
        assert len(blocks) == 1
        assert blocks[0]["language"] == "javascript"  # Should auto-detect


class TestHtmlEntityCleaning:
    """Test HTML entity cleaning functionality."""
    
    def test_basic_entity_cleaning(self):
        """Test basic HTML entity decoding."""
        html_text = "&lt;div&gt;Hello &amp; welcome&lt;/div&gt;"
        cleaned = clean_html_entities(html_text)
        assert cleaned == "<div>Hello & welcome</div>"
    
    def test_quote_entity_cleaning(self):
        """Test quote entity decoding."""
        html_text = '&quot;Hello World&quot; and &#39;test&#39;'
        cleaned = clean_html_entities(html_text)
        assert cleaned == '"Hello World" and \'test\''
    
    def test_no_entities_text(self):
        """Test text without entities remains unchanged."""
        plain_text = "Hello World"
        cleaned = clean_html_entities(plain_text)
        assert cleaned == "Hello World"


class TestCodePreview:
    """Test code preview generation functionality."""
    
    def test_short_code_preview(self):
        """Test preview of short code (under 3 lines)."""
        code = "print('Hello')\nprint('World')"
        preview = create_code_preview(code, 3)
        assert preview == "print('Hello')\nprint('World')"
        assert "..." not in preview
    
    def test_long_code_preview(self):
        """Test preview of long code (over 3 lines)."""
        code = "line1\nline2\nline3\nline4\nline5"
        preview = create_code_preview(code, 3)
        assert preview == "line1\nline2\nline3\n..."
        assert preview.count('\n') == 3  # 3 content lines + ellipsis
    
    def test_custom_line_limit(self):
        """Test preview with custom line limit."""
        code = "line1\nline2\nline3\nline4\nline5"
        preview = create_code_preview(code, 2)
        assert preview == "line1\nline2\n..."