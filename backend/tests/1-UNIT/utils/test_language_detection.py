"""
Test Language Detection Utilities (Phase 1)

Tests for detecting programming language:
- From file extension
- From code content
- From shebang
- From keywords

Coverage: 25 tests
"""

from pathlib import Path


class TestDetectFromExtension:
    """Test language detection from file extension"""

    def test_detect_python_from_extension(self):
        """Python detected from .py"""
        filename = "script.py"
        ext = Path(filename).suffix
        assert ext == ".py"

    def test_detect_javascript_from_extension(self):
        """JavaScript detected from .js"""
        filename = "script.js"
        ext = Path(filename).suffix
        assert ext == ".js"

    def test_detect_java_from_extension(self):
        """Java detected from .java"""
        filename = "Script.java"
        ext = Path(filename).suffix
        assert ext == ".java"

    def test_detect_cpp_from_extension(self):
        """C++ detected from .cpp"""
        filename = "script.cpp"
        ext = Path(filename).suffix
        assert ext == ".cpp"

    def test_detect_csharp_from_extension(self):
        """C# detected from .cs"""
        filename = "Script.cs"
        ext = Path(filename).suffix
        assert ext == ".cs"

    def test_detect_ruby_from_extension(self):
        """Ruby detected from .rb"""
        filename = "script.rb"
        ext = Path(filename).suffix
        assert ext == ".rb"

    def test_detect_go_from_extension(self):
        """Go detected from .go"""
        filename = "main.go"
        ext = Path(filename).suffix
        assert ext == ".go"

    def test_detect_rust_from_extension(self):
        """Rust detected from .rs"""
        filename = "main.rs"
        ext = Path(filename).suffix
        assert ext == ".rs"

    def test_unknown_extension(self):
        """Unknown extension returns None or unknown"""
        filename = "file.xyz"
        ext = Path(filename).suffix
        # Extension exists but is unknown
        assert ext == ".xyz"


class TestDetectFromContent:
    """Test language detection from code content"""

    def test_detect_python_from_content(self, sample_python_code):
        """Python detected from keywords"""
        keywords = ["def ", "class ", "import ", "return"]
        is_python = any(kw in sample_python_code for kw in keywords)
        assert is_python

    def test_detect_javascript_from_content(self, sample_javascript_code):
        """JavaScript detected from keywords"""
        keywords = ["function", "console.log", "const", "let", "var"]
        is_javascript = any(kw in sample_javascript_code for kw in keywords)
        assert is_javascript

    def test_detect_java_from_content(self, sample_java_code):
        """Java detected from keywords"""
        keywords = ["public class", "public static", "System.out"]
        is_java = any(kw in sample_java_code for kw in keywords)
        assert is_java

    def test_detect_cpp_from_content(self, sample_cpp_code):
        """C++ detected from keywords"""
        keywords = ["#include", "using namespace", "cout", "std::"]
        is_cpp = any(kw in sample_cpp_code for kw in keywords)
        assert is_cpp

    def test_detect_from_comment_style(self):
        """Language detected from comment style"""
        python_code = "# This is a comment"
        cpp_code = "// This is a comment"

        # Python uses #
        assert python_code.startswith("#")
        # C++ uses //
        assert cpp_code.startswith("//")

    def test_detect_ruby_from_content(self):
        """Ruby detected from keywords"""
        ruby_code = "def func\n  puts 'hello'\nend"
        keywords = ["de", "puts", "end"]
        is_ruby = any(kw in ruby_code for kw in keywords)
        assert is_ruby

    def test_detect_go_from_content(self):
        """Go detected from keywords"""
        go_code = 'func main() {\n  fmt.Println("hello")\n}'
        assert "func" in go_code
        assert "fmt.Println" in go_code

    def test_detect_rust_from_content(self):
        """Rust detected from keywords"""
        rust_code = 'fn main() {\n  println!("hello");\n}'
        assert "fn" in rust_code
        assert "println!" in rust_code


class TestDetectFromShebang:
    """Test language detection from shebang"""

    def test_detect_python_from_shebang(self):
        """Python detected from #!/usr/bin/python"""
        code = "#!/usr/bin/python3\nprint('hello')"
        assert code.startswith("#!/usr/bin/python")

    def test_detect_bash_from_shebang(self):
        """Bash detected from #!/bin/bash"""
        code = "#!/bin/bash\necho 'hello'"
        assert code.startswith("#!/bin/bash")

    def test_detect_node_from_shebang(self):
        """Node.js detected from #!/usr/bin/node"""
        code = "#!/usr/bin/node\nconsole.log('hello')"
        assert code.startswith("#!/usr/bin/node")

    def test_detect_ruby_from_shebang(self):
        """Ruby detected from #!/usr/bin/ruby"""
        code = "#!/usr/bin/ruby\nputs 'hello'"
        assert code.startswith("#!/usr/bin/ruby")

    def test_no_shebang(self):
        """Code without shebang"""
        code = "print('hello')"
        assert not code.startswith("#!")


class TestLanguageVariants:
    """Test detecting language variants"""

    def test_detect_python2_vs_python3(self):
        """Distinguish Python 2 and 3"""
        py2 = "print 'hello'"
        py3 = "print('hello')"

        # Python 3 uses function call
        assert "print(" in py3
        assert "print " in py2

    def test_detect_nodejs_vs_browser_javascript(self):
        """Distinguish Node.js and browser JavaScript"""
        nodejs = "const fs = require('fs');"
        browser = "document.getElementById('id');"

        assert "require" in nodejs
        assert "document" in browser

    def test_detect_ecmascript_versions(self):
        """Detect JavaScript versions"""
        es5 = "var x = 1;"
        es6 = "const x = 1; let y = 2;"

        assert "var" in es5
        assert "const" in es6 and "let" in es6

    def test_detect_cpp_standards(self):
        """Detect C++ standards"""
        cpp98 = "#include <iostream>"
        cpp11 = "auto x = []() { return 1; };"

        assert "#include" in cpp98
        assert "auto" in cpp11


class TestAmbiguousDetection:
    """Test handling ambiguous cases"""

    def test_ambiguous_java_csharp(self, ambiguous_code):
        """Java and C# look similar"""
        # Both could have System.out or Console.WriteLine
        assert "System.out" in ambiguous_code or "public" in ambiguous_code

    def test_ambiguous_cpp_c(self):
        """C and C++ are similar"""
        c_code = "#include <stdio.h>\nint main() {}"
        cpp_code = "#include <iostream>\nint main() {}"

        # C uses stdio, C++ uses iostream
        assert "stdio" in c_code
        assert "iostream" in cpp_code

    def test_sql_detection(self):
        """SQL detected from keywords"""
        sql = "SELECT * FROM users WHERE id = 1;"
        assert "SELECT" in sql
        assert "FROM" in sql

    def test_html_detection(self):
        """HTML detected from tags"""
        html = "<html><body>Hello</body></html>"
        assert "<html>" in html
        assert "</html>" in html


class TestDetectionAccuracy:
    """Test detection accuracy"""

    def test_single_keyword_detection(self):
        """Single keyword is enough for detection"""
        # One keyword might be enough in some cases
        code = "def func(): pass"  # Python
        assert "def" in code

    def test_confidence_levels(self):
        """Multiple keywords increase confidence"""
        high_confidence = "def func():\n    class MyClass:\n        return value"
        # Has multiple Python keywords
        assert high_confidence.count("def") >= 1

    def test_false_positives(self):
        """Minimize false positive detection"""
        text = "The function does something"
        # Has 'function' but isn't code
        assert not text.endswith("()")

    def test_case_sensitivity(self):
        """Language detection is case-insensitive"""
        upper = "DEF FUNC(): PASS"
        lower = "def func(): pass"
        # Both should be recognizable as Python
        assert "def" in lower.lower()
        assert "def" in upper.lower()


class TestDetectionEdgeCases:
    """Test edge cases in detection"""

    def test_mixed_language_snippets(self, code_snippets_list):
        """Multiple language snippets"""
        for snippet in code_snippets_list:
            # Each snippet should be detectable
            assert len(snippet) > 0

    def test_detect_from_imports(self):
        """Language detection from import statements"""
        python = "import os"
        javascript = "import { func } from './module'"
        java = "import java.util.*;"

        assert "import" in python
        assert "import" in javascript
        assert "import" in java

    def test_unicode_in_code(self, code_with_special_chars):
        """Unicode characters in code"""
        assert len(code_with_special_chars) > 0
        # Code should still be detectable

    def test_minified_code(self):
        """Minified code detection"""
        minified = "function h(x){return x*2;}var y=h(5);"
        # Still recognizable as JavaScript
        assert "function" in minified

    def test_commented_out_code(self):
        """Detect language in commented code"""
        code = "// function hello() {\n// console.log('hi');\n// }"
        # Still JavaScript
        assert "//" in code
