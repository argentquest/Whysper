"""
Integration tests for documentation generation.
"""

import pytest
import tempfile
import os
import json
from fastapi.testclient import TestClient
from app.main import app


class TestDocumentationIntegration:
    """Integration tests for documentation generation."""
    
    def setup_method(self):
        """Set up test environment."""
        self.client = TestClient(app)
        
        # Create temporary test files
        self.temp_dir = tempfile.mkdtemp()
        
        # Create Python test file
        self.python_file = os.path.join(self.temp_dir, "test.py")
        with open(self.python_file, "w") as f:
            f.write("""
class TestClass:
    \"\"\"A test class for documentation generation.\"\"\"
    
    def __init__(self, value: int = 0):
        \"\"\"Initialize the test class.
        
        Args:
            value: Initial value for the test class
        \"\"\"
        self.value = value
    
    def increment(self) -> int:
        \"\"\"Increment the value.
        
        Returns:
            The incremented value
        \"\"\"
        self.value += 1
        return self.value
    
    def get_value(self) -> int:
        \"\"\"Get the current value.
        
        Returns:
            The current value
        \"\"\"
        return self.value


def test_function(param: str) -> str:
    \"\"\"A test function.
    
    Args:
        param: A string parameter
    
    Returns:
        The processed string
    \"\"\"
    return f"Processed: {param}"
""")
        
        # Create JavaScript test file
        self.js_file = os.path.join(self.temp_dir, "test.js")
        with open(self.js_file, "w") as f:
            f.write("""
/**
 * A test class for documentation generation
 */
class TestClass {
    /**
     * Initialize the test class
     * @param {number} value - Initial value
     */
    constructor(value = 0) {
        this.value = value;
    }
    
    /**
     * Increment the value
     * @returns {number} The incremented value
     */
    increment() {
        this.value += 1;
        return this.value;
    }
    
    /**
     * Get the current value
     * @returns {number} The current value
     */
    getValue() {
        return this.value;
    }
}

/**
 * A test function
 * @param {string} param - A string parameter
 * @returns {string} The processed string
 */
function testFunction(param) {
    return `Processed: ${param}`;
}
""")
    
    def teardown_method(self):
        """Clean up test environment."""
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_generate_documentation_api(self):
        """Test documentation generation API endpoint."""
        request_data = {
            "file_paths": [self.python_file],
            "documentation_type": "api",
            "output_format": "markdown",
            "include_examples": True,
            "include_diagrams": True,
            "target_audience": "developers"
        }
        
        response = self.client.post(
            "/api/v1/documentation/generate",
            json=request_data
        )
        
        assert response.status_code == 200
        data = response.json()
        
        assert "content" in data
        assert "metadata" in data
        assert "processing_time" in data
        assert "id" in data
        assert data["metadata"]["file_count"] == 1
        assert "TestClass" in data["content"]
        assert "test_function" in data["content"]
    
    def test_generate_api_docs_endpoint(self):
        """Test API documentation generation endpoint."""
        request_data = {
            "file_paths": [self.python_file],
            "output_format": "markdown",
            "target_audience": "developers"
        }
        
        response = self.client.post(
            "/api/v1/documentation/api-docs",
            json=request_data
        )
        
        assert response.status_code == 200
        data = response.json()
        
        assert "content" in data
        assert "TestClass" in data["content"]
        assert "test_function" in data["content"]
    
    def test_generate_readme_endpoint(self):
        """Test README generation endpoint."""
        request_data = {
            "file_paths": [self.python_file],
            "output_format": "markdown"
        }
        
        response = self.client.post(
            "/api/v1/documentation/readme",
            json=request_data
        )
        
        assert response.status_code == 200
        data = response.json()
        
        assert "content" in data
        assert "Installation" in data["content"] or "Usage" in data["content"]
    
    def test_get_templates_endpoint(self):
        """Test templates retrieval endpoint."""
        response = self.client.get("/api/v1/documentation/templates")
        
        assert response.status_code == 200
        data = response.json()
        
        assert "templates" in data
        assert "count" in data
        assert len(data["templates"]) > 0
        
        # Check for expected templates
        template_names = [t["name"] for t in data["templates"]]
        assert "default_template" in template_names
        assert "api_documentation" in template_names
    
    def test_export_html_endpoint(self):
        """Test HTML export endpoint."""
        # First generate documentation
        gen_request = {
            "file_paths": [self.python_file],
            "documentation_type": "api",
            "output_format": "markdown"
        }
        
        gen_response = self.client.post(
            "/api/v1/documentation/generate",
            json=gen_request
        )
        
        assert gen_response.status_code == 200
        doc_content = gen_response.json()["content"]
        
        # Then export to HTML
        export_request = {
            "documentation_id": "test",
            "content": doc_content,
            "export_format": "html",
            "filename": "test.html",
            "options": {
                "title": "Test Documentation",
                "author": "Test Author"
            }
        }
        
        export_response = self.client.post(
            "/api/v1/documentation/export",
            json=export_request
        )
        
        assert export_response.status_code == 200
        export_data = export_response.json()
        
        assert "content" in export_data
        assert "format" in export_data
        assert "filename" in export_data
        assert "content_type" in export_data
        assert export_data["format"] == "html"
        assert "<!DOCTYPE html>" in export_data["content"]
    
    def test_export_pdf_endpoint(self):
        """Test PDF export endpoint."""
        # First generate documentation
        gen_request = {
            "file_paths": [self.python_file],
            "documentation_type": "api",
            "output_format": "markdown"
        }
        
        gen_response = self.client.post(
            "/api/v1/documentation/generate",
            json=gen_request
        )
        
        assert gen_response.status_code == 200
        doc_content = gen_response.json()["content"]
        
        # Then export to PDF
        export_request = {
            "documentation_id": "test",
            "content": doc_content,
            "export_format": "pdf",
            "filename": "test.pdf",
            "options": {
                "title": "Test Documentation",
                "author": "Test Author"
            }
        }
        
        export_response = self.client.post(
            "/api/v1/documentation/export",
            json=export_request
        )
        
        # PDF export might fall back to markdown if libraries not available
        assert export_response.status_code == 200
        export_data = export_response.json()
        
        assert "content" in export_data
        assert "format" in export_data
        assert export_data["format"] == "pdf"
    
    def test_get_export_formats_endpoint(self):
        """Test export formats endpoint."""
        response = self.client.get("/api/v1/documentation/export/formats")
        
        assert response.status_code == 200
        data = response.json()
        
        assert "formats" in data
        assert "options" in data
        assert "markdown" in data["formats"]
        assert "html" in data["formats"]
        assert "pdf" in data["formats"]
    
    def test_health_check_endpoint(self):
        """Test health check endpoint."""
        response = self.client.get("/api/v1/documentation/health")
        
        assert response.status_code == 200
        data = response.json()
        
        assert "status" in data
        assert "service" in data
        assert data["status"] == "healthy"
        assert data["service"] == "documentation"
    
    def test_javascript_documentation_generation(self):
        """Test documentation generation for JavaScript code."""
        request_data = {
            "file_paths": [self.js_file],
            "documentation_type": "api",
            "output_format": "markdown",
            "include_examples": True,
            "include_diagrams": True,
            "target_audience": "developers"
        }
        
        response = self.client.post(
            "/api/v1/documentation/generate",
            json=request_data
        )
        
        assert response.status_code == 200
        data = response.json()
        
        assert "content" in data
        assert "TestClass" in data["content"]
        assert "testFunction" in data["content"]
        assert data["metadata"]["file_count"] == 1
    
    def test_multiple_files_documentation(self):
        """Test documentation generation with multiple files."""
        request_data = {
            "file_paths": [self.python_file, self.js_file],
            "documentation_type": "all",
            "output_format": "markdown",
            "include_examples": True,
            "include_diagrams": True,
            "target_audience": "developers"
        }
        
        response = self.client.post(
            "/api/v1/documentation/generate",
            json=request_data
        )
        
        assert response.status_code == 200
        data = response.json()
        
        assert "content" in data
        assert data["metadata"]["file_count"] == 2
        # Should contain code from both files
        assert "TestClass" in data["content"]
        assert "test_function" in data["content"] or "testFunction" in data["content"]
    
    def test_error_handling_no_files(self):
        """Test error handling when no files are provided."""
        request_data = {
            "file_paths": [],
            "documentation_type": "api",
            "output_format": "markdown"
        }
        
        response = self.client.post(
            "/api/v1/documentation/generate",
            json=request_data
        )
        
        # Should return an error when no files are provided
        assert response.status_code == 500 or response.status_code == 422
    
    def test_error_handling_invalid_file(self):
        """Test error handling when file doesn't exist."""
        request_data = {
            "file_paths": ["/nonexistent/file.py"],
            "documentation_type": "api",
            "output_format": "markdown"
        }
        
        response = self.client.post(
            "/api/v1/documentation/generate",
            json=request_data
        )
        
        # Should handle the error gracefully
        assert response.status_code in [200, 500, 422]
        
        if response.status_code == 200:
            data = response.json()
            # Should still return a response even if file can't be processed
            assert "content" in data


if __name__ == "__main__":
    pytest.main([__file__])