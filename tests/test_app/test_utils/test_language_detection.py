"""
Tests for language detection utilities.

This module tests the language detection and filename generation functions.
"""
import pytest
from app.utils.language_detection import detect_language, generate_filename


class TestLanguageDetection:
    """Test language detection functionality."""
    
    def test_python_detection(self):
        """Test Python language detection."""
        python_code = '''
def hello_world():
    print("Hello, World!")
    import os
    return True
'''
        assert detect_language(python_code) == "python"
    
    def test_javascript_detection(self):
        """Test JavaScript language detection."""
        js_code = '''
function greet(name) {
    console.log(`Hello, ${name}!`);
    const result = name.toUpperCase();
    return result;
}
'''
        assert detect_language(js_code) == "javascript"
    
    def test_sql_detection(self):
        """Test SQL language detection."""
        sql_code = '''
SELECT id, name, email
FROM users
WHERE created_at > '2025-01-01'
ORDER BY name;
'''
        assert detect_language(sql_code) == "sql"
    
    def test_html_detection(self):
        """Test HTML language detection."""
        html_code = '''
<html>
<head><title>Test</title></head>
<body>
    <div>Hello World</div>
</body>
</html>
'''
        assert detect_language(html_code) == "html"
    
    def test_unknown_language_fallback(self):
        """Test fallback to 'text' for unknown languages."""
        unknown_code = "This is just plain text without any language indicators."
        assert detect_language(unknown_code) == "text"


class TestFilenameGeneration:
    """Test filename generation functionality."""
    
    def test_python_filename(self):
        """Test Python filename generation."""
        filename = generate_filename("python", 1)
        assert filename == "extracted_code_1.py"
    
    def test_javascript_filename(self):
        """Test JavaScript filename generation."""
        filename = generate_filename("javascript", 2)
        assert filename == "extracted_code_2.js"
    
    def test_sql_filename(self):
        """Test SQL filename generation."""
        filename = generate_filename("sql", 3)
        assert filename == "extracted_code_3.sql"
    
    def test_unknown_language_filename(self):
        """Test filename generation for unknown languages."""
        filename = generate_filename("unknown", 4)
        assert filename == "extracted_code_4.txt"
    
    def test_case_insensitive_language(self):
        """Test that language detection is case insensitive."""
        filename = generate_filename("PYTHON", 5)
        assert filename == "extracted_code_5.py"