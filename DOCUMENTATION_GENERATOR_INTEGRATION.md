# Documentation Generator Integration Guide

This guide provides step-by-step instructions for integrating the Documentation Generator feature into the main Whysper application.

## 📋 Integration Checklist

- [ ] Backend Services Integration
- [ ] API Routes Registration
- [ ] Frontend Component Integration
- [ ] Navigation Menu Updates
- [ ] Database Models (if needed)
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
from app.services.documentation_service import documentation_service
from app.services.export_service import export_service

# These will be automatically initialized when imported
```

### 3. Environment Configuration

Add any required environment variables to your `.env` file:

```env
# Documentation Generator Settings
DOCUMENTATION_TEMPLATES_DIR=backend/templates/documentation
EXPORT_TEMPLATES_DIR=backend/templates/export

# Optional: External libraries for enhanced export
WEASYPRINT_ENABLED=false
REPORTLAB_ENABLED=false
PYTHON_DOCX_ENABLED=false
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

## 🗄️ Database Integration (Optional)

If you want to persist generated documentation, add the following models:

```python
# backend/models/documentation.py
from sqlalchemy import Column, String, Text, DateTime, Boolean, Integer, JSON, Float
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class Documentation(Base):
    __tablename__ = "documentations"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    project_id = Column(String, nullable=False, index=True)
    title = Column(String(255), nullable=False)
    content = Column(Text, nullable=False)
    documentation_type = Column(String(50), nullable=False)
    output_format = Column(String(20), nullable=False, default="markdown")
    template = Column(String(100))
    file_paths = Column(JSON)
    metadata = Column(JSON)
    diagrams = Column(JSON)
    examples = Column(JSON)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    processing_time = Column(Float)
    token_usage = Column(JSON)
    is_public = Column(Boolean, default=False)
    user_id = Column(String, nullable=False)
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

4. **Error Handling**
   - Test with no files selected
   - Test with invalid file paths
   - Verify error messages

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

### 3. Performance Optimization

For large codebases, consider:

1. **Async Processing**: Implement background processing for large documentation generation
2. **Caching**: Cache generated documentation to avoid regeneration
3. **Rate Limiting**: Implement rate limiting for API endpoints
4. **File Size Limits**: Set reasonable limits for file processing

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

### Debug Mode

Enable debug mode for detailed logging:

```python
# backend/app/services/documentation_service.py
import logging
logging.basicConfig(level=logging.DEBUG)
```

```typescript
// frontend/src/components/documentation/DocumentationGeneratorUpdated.tsx
console.log('Debug mode enabled');
```

## 📈 Monitoring and Analytics

### 1. API Metrics

Monitor the following metrics:
- Documentation generation requests
- Export requests by format
- Processing time
- Error rates

### 2. User Analytics

Track user interactions:
- Most used documentation types
- Preferred export formats
- Common file types processed

## 🎯 Best Practices

1. **Error Handling**: Implement comprehensive error handling and user-friendly messages
2. **Performance**: Optimize for large codebases with async processing
3. **Security**: Validate file paths and sanitize user inputs
4. **Testing**: Maintain comprehensive test coverage
5. **Documentation**: Keep API documentation up to date

## 🔮 Future Enhancements

Consider these future enhancements:
1. **Real-time Collaboration**: Multi-user documentation editing
2. **Version Control**: Integration with Git for documentation versioning
3. **Custom Templates**: User-customizable documentation templates
4. **Advanced AI**: Enhanced AI-powered documentation improvements
5. **Integration**: Integration with external documentation platforms

---

## 📞 Support

For integration issues:
1. Check the error logs
2. Review the troubleshooting section
3. Run the test suite to identify issues
4. Create an issue with detailed error information

The Documentation Generator feature is now ready for integration into your Whysper application!