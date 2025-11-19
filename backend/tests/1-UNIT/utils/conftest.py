"""
Utility Test Fixtures

Provides reusable fixtures for testing utility functions:
- Temporary files and directories
- Sample code in various languages
- Test data
"""

import pytest
import tempfile
from pathlib import Path
from typing import Dict, List


@pytest.fixture
def temp_directory():
    """Create temporary directory for testing"""
    with tempfile.TemporaryDirectory() as tmpdir:
        yield Path(tmpdir)


@pytest.fixture
def temp_file(temp_directory):
    """Create temporary file"""
    file_path = temp_directory / "test_file.txt"
    file_path.write_text("test content")
    return file_path


@pytest.fixture
def sample_python_code() -> str:
    """Sample Python code"""
    return '''def hello_world():
    """Print hello world"""
    print("Hello, World!")
    return True

if __name__ == "__main__":
    result = hello_world()
    assert result is True
'''


@pytest.fixture
def sample_javascript_code() -> str:
    """Sample JavaScript code"""
    return '''function helloWorld() {
    console.log("Hello, World!");
    return true;
}

const result = helloWorld();
console.assert(result === true);
'''


@pytest.fixture
def sample_java_code() -> str:
    """Sample Java code"""
    return '''public class HelloWorld {
    public static void main(String[] args) {
        System.out.println("Hello, World!");
    }

    public static boolean test() {
        return true;
    }
}
'''


@pytest.fixture
def sample_cpp_code() -> str:
    """Sample C++ code"""
    return '''#include <iostream>
using namespace std;

int main() {
    cout << "Hello, World!" << endl;
    return 0;
}
'''


@pytest.fixture
def markdown_with_code_blocks() -> str:
    """Markdown with multiple code blocks"""
    return '''# Example Document

Here's some Python code:


def example():
    return "hello"
And some JavaScript:

function example() {
    return "hello";
}
More content here.

class Example {
    public static void main(String[] args) {}
}'''


@pytest.fixture
def markdown_with_inline_code() -> str:
    """Markdown with inline code"""
    return '''# Example

Use `print()` to output text.

The `if` statement is used for conditionals.
'''


@pytest.fixture
def html_with_code() -> str:
    """HTML with code elements"""
    return '''<html>
<body>
<h1>Example</h1>

<pre><code class="language-python">
def example():
    return "hello"
</code></pre>

<p>Some text with <code>inline code</code>.</p>
</body>
</html>
'''


@pytest.fixture
def mixed_language_code() -> Dict[str, str]:
    """Code samples in multiple languages"""
    return {
        "python": "def func(): pass",
        "javascript": "function func() {}",
        "java": "public class Func {}",
        "cpp": "void func() {}",
        "csharp": "public void Func() {}",
        "rust": "fn func() {}",
        "go": "func func() {}",
        "ruby": "def func; end",
    }


@pytest.fixture
def code_with_special_chars() -> str:
    """Code with special characters"""
    return '''
def special_chars():
    # String with quotes: "hello", 'world'
    s = "Test with émojis: 🎉 ✨"

    # Math symbols: ±, ×, ÷
    result = 2 ± 1

    # Unicode: α, β, γ
    variables = [α, β, γ]

    return s
'''


@pytest.fixture
def code_with_syntax_error() -> str:
    """Code with syntax errors"""
    return '''
def broken_function()
    print("Missing colon above")
    if True
        return "Missing colon on if"
'''


@pytest.fixture
def code_with_logical_error() -> str:
    """Code with logical errors"""
    return '''
def add(a, b):
    return a - b  # Wrong operation

def divide_by_zero():
    return 10 / 0
'''


@pytest.fixture
def very_long_code() -> str:
    """Very long code sample"""
    lines = ["def long_function():"]
    for i in range(1000):
        lines.append(f"    var{i} = {i}")
    lines.append("    return var999")
    return "\n".join(lines)


@pytest.fixture
def code_snippets_list() -> List[str]:
    """List of code snippets in different languages"""
    return [
        "print('Python')",  # Python
        "console.log('JavaScript')",  # JavaScript
        "System.out.println('Java');",  # Java
        "cout << 'C++' << endl;",  # C++
        "puts 'Ruby'",  # Ruby
        "echo 'PHP';",  # PHP
        "println('Rust');",  # Rust
        "fmt.Println('Go')",  # Go
    ]


@pytest.fixture
def code_by_language() -> Dict[str, str]:
    """Code samples organized by language"""
    return {
        "python": "def hello(): print('Hello')",
        "javascript": "function hello() { console.log('Hello'); }",
        "java": "public void hello() { System.out.println('Hello'); }",
        "cpp": "void hello() { std::cout << 'Hello' << std::endl; }",
        "csharp": "public void Hello() { Console.WriteLine('Hello'); }",
        "ruby": "def hello; puts 'Hello'; end",
        "go": "func hello() { fmt.Println('Hello') }",
        "rust": "fn hello() { println!('Hello'); }",
    }


@pytest.fixture
def ambiguous_code() -> str:
    """Code that's ambiguous between languages"""
    return '''
    // This could be C++, Java, or C#
    public void hello() {
        System.out.println("Hello");
    }
'''


@pytest.fixture
def session_id_valid() -> str:
    """Valid session ID"""
    return "sess_1234567890abcdefghijklmnop"


@pytest.fixture
def session_id_invalid() -> str:
    """Invalid session ID"""
    return "not_a_valid_session_id!"


@pytest.fixture
def session_id_list() -> List[str]:
    """List of session IDs"""
    return [f"sess_{i:032x}" for i in range(1, 11)]
