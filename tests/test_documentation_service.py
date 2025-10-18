"""
Tests for documentation service.
"""

import pytest
import tempfile
import os
from app.services.documentation_service import DocumentationService, DocumentationRequest


class TestDocumentationService:
    """Test cases for DocumentationService."""
    
    def setup_method(self):
        """Set up test environment."""
        self.doc_service = DocumentationService()
    
    def test_analyze_python_code(self):
        """Test Python code analysis."""
        # Test with simple Python code
        python_code = """
class TestClass:
    def __init__(self):
        self.value = 0
    
    def increment(self):
        self.value += 1
        return self.value

def test_function():
    return "test"
"""
        
        structure = self.doc_service._analyze_python("test.py", python_code)
        
        assert structure.language == "python"
        assert len(structure.classes) == 1
        assert structure.classes[0]["name"] == "TestClass"
        assert len(structure.functions) == 1
        assert structure.functions[0]["name"] == "test_function"
    
    def test_analyze_javascript_code(self):
        """Test JavaScript code analysis."""
        # Test with simple JavaScript code
        js_code = """
class TestClass {
    constructor() {
        this.value = 0;
    }
    
    increment() {
        this.value += 1;
        return this.value;
    }
}

function testFunction() {
    return "test";
}
"""
        
        structure = self.doc_service._analyze_javascript("test.js", js_code)
        
        assert structure.language == "javascript"
        assert len(structure.classes) == 1
        assert structure.classes[0]["name"] == "TestClass"
        assert len(structure.functions) == 1
        assert structure.functions[0]["name"] == "testFunction"
    
    def test_generate_documentation_basic(self):
        """Test basic documentation generation."""
        # Create temporary test files
        with tempfile.TemporaryDirectory() as temp_dir:
            test_file = os.path.join(temp_dir, "test.py")
            with open(test_file, "w") as f:
                f.write("""
class TestClass:
    def __init__(self):
        self.value = 0
    
    def increment(self):
        self.value += 1
        return self.value

def test_function():
    return "test"
""")
            
            # Test with embedded templates (no AI)
            request = DocumentationRequest(
                file_paths=[test_file],
                documentation_type="api",
                output_format="markdown",
                include_examples=False,
                include_diagrams=False
            )
            
            result = self.doc_service.generate_documentation(request)
            
            assert result.content is not None
            assert result.metadata is not None
            assert result.processing_time > 0
            assert result.id is not None
    
    def test_extract_function_signatures(self):
        """Test function signature extraction."""
        python_code = """
def test_function(param1: str, param2: int = 10) -> bool:
    \"\"\"Test function description.\"\"\"
    return True
"""
        
        structure = self.doc_service._analyze_python("test.py", python_code)
        functions = structure.functions
        
        assert len(functions) == 1
        func = functions[0]
        assert func["name"] == "test_function"
        assert "param1" in func["args"]
        assert "param2" in func["args"]
        assert func["docstring"] == "Test function description."
    
    def test_generate_dependency_diagram(self):
        """Test dependency diagram generation."""
        # Create test structures
        from app.services.documentation_service import CodeStructure
        
        structures = [
            CodeStructure(
                file_path="test.py",
                language="python",
                imports=["os", "sys", "requests"],
                classes=[],
                functions=[],
                relationships={"imports": ["os", "sys", "requests"]}
            )
        ]
        
        diagram = self.doc_service._generate_dependency_diagram(structures)
        
        assert diagram is not None
        assert diagram["type"] == "dependency_diagram"
        assert diagram["format"] == "mermaid"
        assert "graph TD" in diagram["code"]
    
    def test_load_templates(self):
        """Test template loading."""
        templates = self.doc_service._load_templates()
        
        assert isinstance(templates, dict)
        assert len(templates) > 0
        assert "default_template" in templates
        assert "api_documentation" in templates
        assert "readme_template" in templates
    
    def test_select_template(self):
        """Test template selection."""
        request = DocumentationRequest(
            file_paths=[],
            documentation_type="api",
            output_format="markdown"
        )
        
        template = self.doc_service._select_template(request)
        assert template == "api_documentation"
        
        request.documentation_type = "readme"
        template = self.doc_service._select_template(request)
        assert template == "readme_template"
        
        request.documentation_type = "unknown"
        template = self.doc_service._select_template(request)
        assert template == "default_template"


if __name__ == "__main__":
    pytest.main([__file__])