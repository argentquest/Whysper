# Documentation Generator - Simple Integration Guide

This guide provides step-by-step instructions for integrating the Documentation Generator feature into the main Whysper application without database dependencies.

## 📋 Integration Checklist

- [ ] Backend API Routes Registration
- [ ] Frontend Component Integration
- [ ] Navigation Menu Updates
- [ ] Environment Configuration
- [ ] Testing and Validation

## 🔧 Backend Integration

### 1. Update API Router

Add the documentation endpoints to your main API router:

```python
# backend/app/api/v1/api.py
from .endpoints import documentation_updated

api_router.include_router(
    documentation_updated.router,
    prefix="/documentation",
    tags=["documentation"]
)
```

### 2. Update Main Application

Ensure the documentation service is available in your main application:

```python
# backend/main.py
# Services will be automatically initialized when imported
```

### 3. Environment Configuration

Add any required environment variables to your `.env` file:

```env
# Documentation Generator Settings
DOCUMENTATION_TEMPLATES_DIR=backend/templates/documentation
EXPORT_TEMPLATES_DIR=backend/templates/export
```

## 🎨 Frontend Integration

### 1. Add Component to Main App

Import and add the DocumentationGenerator component to your main application:

```typescript
// frontend/src/App.tsx
import DocumentationGenerator from './components/documentation/DocumentationGeneratorUpdated';

// Add to your component tree
<DocumentationGenerator 
  selectedFiles={selectedFiles}
  onDocumentationGenerated={(content) => {
    // Handle generated documentation
    console.log('Documentation generated:', content);
  }}
/>
```

### 2. Update Navigation Menu

Add the Documentation Generator to your navigation menu:

```typescript
// frontend/src/components/Navigation/Menu.tsx
import { FileTextOutlined } from '@ant-design/icons';

// Add to menu items
{
  key: 'documentation',
  icon: <FileTextOutlined />,
  label: 'Documentation Generator',
  path: '/documentation'
}
```

### 3. Add Route

Add the route for the Documentation Generator:

```typescript
// frontend/src/App.tsx or router configuration
<Route path="/documentation" element={<DocumentationGenerator />} />
```

## 🧪 Testing Integration

### 1. Run Unit Tests

```bash
# Run documentation service tests
pytest backend/tests/test_documentation_service.py

# Run integration tests
pytest backend/tests/test_documentation_integration.py
```

### 2. Manual Testing

Test the following workflows:

1. **Basic Documentation Generation**
   - Select a Python file
   - Choose API documentation type
   - Generate and preview documentation

2. **Export Functionality**
   - Generate documentation
   - Export to HTML format
   - Export to PDF format (if libraries available)

3. **Multi-language Support**
   - Select JavaScript files
   - Generate documentation
   - Verify language-specific features

## 🚀 Deployment Considerations

### 1. Dependencies

Install optional dependencies for enhanced export functionality:

```bash
# For PDF export with WeasyPrint
pip install weasyprint

# For PDF export with ReportLab
pip install reportlab

# For Word document export
pip install python-docx

# For enhanced HTML export
pip install markdown2
```

### 2. Docker Configuration

If using Docker, add the following to your Dockerfile:

```dockerfile
# Install optional dependencies
RUN pip install weasyprint reportlab python-docx markdown2 || true
```

## 📚 Usage Examples

### Basic Usage

```typescript
// Generate API documentation
const handleGenerate = async () => {
  const request = {
    file_paths: selectedFiles,
    documentation_type: 'api',
    output_format: 'markdown',
    include_examples: true,
    include_diagrams: true,
    target_audience: 'developers'
  };
  
  const response = await api.post('/api/v1/documentation/generate', request);
  setDocumentation(response.data.content);
};
```

### Export Usage

```typescript
// Export to HTML
const handleExport = async () => {
  const request = {
    content: documentation,
    export_format: 'html',
    filename: 'documentation.html',
    options: {
      title: 'My Documentation',
      author: 'My Name'
    }
  };
  
  const response = await api.post('/api/v1/documentation/export', request);
  
  // Download the file
  const blob = new Blob([response.data.content], { 
    type: response.data.content_type 
  });
  const url = window.URL.createObjectURL(blob);
  const link = document.createElement('a');
  link.href = url;
  link.download = response.data.filename;
  link.click();
};
```

## 🔍 Troubleshooting

### Common Issues

1. **Service Not Available**
   - Check if services are properly imported
   - Verify environment configuration
   - Check for missing dependencies

2. **Export Fails**
   - Verify optional dependencies are installed
   - Check template files exist
   - Review error logs for specific issues

3. **Frontend Component Not Loading**
   - Check import paths
   - Verify component is properly registered
   - Check for TypeScript errors

## 📈 Monitoring

### API Metrics

Monitor the following metrics:
- Documentation generation requests
- Export requests by format
- Processing time
- Error rates

## 🎯 Best Practices

1. **Error Handling**: Implement comprehensive error handling and user-friendly messages
2. **Performance**: Optimize for large codebases with async processing
3. **Security**: Validate file paths and sanitize user inputs
4. **Testing**: Maintain comprehensive test coverage

## 🎉 Benefits for Developers

This feature will provide Whysper users with:

- **Time Savings**: Automatically generate comprehensive documentation from code
- **Consistency**: Maintain consistent documentation style across projects
- **Multiple Formats**: Export to various formats for different use cases
- **Language Support**: Work with multiple programming languages
- **Professional Output**: Generate publication-ready documentation
- **Easy Integration**: Simple integration into existing workflows

---

## 📞 Support

For integration issues:
1. Check the error logs
2. Review the troubleshooting section
3. Run the test suite to identify issues

The Documentation Generator feature is now ready for integration into your Whysper application!