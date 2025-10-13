# Server Rendering Architecture - MVP Diagram Generator and MCP Server

## Overview

This document provides a comprehensive technical architecture overview of the server-side diagram rendering system, including the MVP diagram generator and MCP (Model Context Protocol) server implementations.

## System Architecture

### High-Level Components

```
┌─────────────────────────────────────────────────────────────────┐
│                        Client Layer                              │
├─────────────────────────────────────────────────────────────────┤
│  Frontend (React)  │  MCP Clients  │  Direct API Consumers      │
└─────────────────────────────────────────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────────┐
│                      API Gateway Layer                          │
├─────────────────────────────────────────────────────────────────┤
│  FastAPI Router  │  MCP Server  │  WebSocket Endpoints          │
└─────────────────────────────────────────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────────┐
│                    Business Logic Layer                         │
├─────────────────────────────────────────────────────────────────┤
│  Diagram Generation  │  Validation  │  Rendering Pipeline       │
└─────────────────────────────────────────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────────┐
│                    Infrastructure Layer                         │
├─────────────────────────────────────────────────────────────────┤
│  AI Services  │  Playwright  │  File System  │  Cache Layer     │
└─────────────────────────────────────────────────────────────────┘
```

## Core Modules

### 1. MVP Diagram Generator (`backend/mvp_diagram_generator/`)

#### 1.1 Renderer V2 (`renderer_v2.py`)
**Purpose**: Primary diagram rendering engine with fallback mechanisms

**Key Features**:
- Browserless rendering using Playwright
- Support for React dev server and static HTML fallback
- Multiple diagram types: Mermaid, D2, C4
- Output formats: SVG, PNG
- Comprehensive error handling and logging

**Architecture**:
```python
async def render_diagram(
    diagram_code: str,
    diagram_type: str,
    output_format: str = "svg",
    frontend_url: str = "http://localhost:5173",
    timeout: int = 30000
) -> str
```

**Rendering Pipeline**:
1. URL-encode diagram code
2. Launch headless browser with Playwright
3. Try React dev server first (frontend_url/render)
4. Fallback to static HTML with embedded libraries
5. Wait for rendering completion (CSS class detection)
6. Extract SVG or capture PNG screenshot
7. Clean up resources

**Dependencies**:
- Playwright (browser automation)
- Frontend render-diagram.html page
- Mermaid.js and D2 libraries (CDN or static)

#### 1.2 Legacy Renderer (`renderer.py`)
**Purpose**: Basic rendering implementation (deprecated)

**Issues**:
- Requires local static files
- No fallback mechanism
- Limited error handling
- Uses file:// protocol (security restrictions)

**Status**: Superseded by `renderer_v2.py`

#### 1.3 Diagram Validators (`diagram_validators.py`)
**Purpose**: Syntax validation for different diagram types

**Supported Types**:
- **Mermaid**: Keyword matching in first 3 lines
- **D2**: Pattern matching across all lines
- **C4**: Keyword matching for diagram declarations

**Validation Patterns**:
```python
# Mermaid keywords
MERMAID_KEYWORDS = [
    "classDiagram", "sequenceDiagram", "graph", "flowchart",
    "stateDiagram", "erDiagram", "gantt", "pie", "journey",
    "gitGraph", "mindmap", "timeline", "quadrantChart"
]

# D2 regex patterns
D2_PATTERNS = [
    re.compile(r"^[a-zA-Z0-9_]+\s*-+>", re.IGNORECASE),  # Arrows
    re.compile(r"\.shape\s*:", re.IGNORECASE),          # Shapes
    re.compile(r"\.style\.", re.IGNORECASE),            # Styles
    re.compile(r"direction\s*:", re.IGNORECASE)         # Direction
]
```

#### 1.4 C4 to D2 Converter (`c4_to_d2.py`)
**Purpose**: Convert C4 model diagrams to D2 syntax

**Current Implementation**: Basic conversion of diagram declarations to comments

**Missing Features** (Critical):
- Entity definition parsing (Person, System, Container, Component)
- Relationship parsing (Rel, Rel_U, Rel_Back, etc.)
- Proper D2 syntax generation with shapes and connections
- Layout and styling preservation

#### 1.5 Rendering API (`rendering_api.py`)
**Purpose**: FastAPI endpoints for diagram generation

**Endpoints**:
- `POST /generate` - Generate diagram from prompt
- Request/Response models with Pydantic validation
- Integration with AI services
- Comprehensive error handling

**Generation Pipeline**:
1. Load appropriate agent prompt based on diagram type
2. Construct conversation with system message
3. Call AI processor with prompt and context
4. Extract diagram code from response
5. Validate diagram syntax
6. Render diagram to image format
7. Return structured response

### 2. MCP Server (`backend/mcp_server/`)

#### 2.1 Standard MCP Server (`diagram_server.py`)
**Purpose**: stdio-based MCP server for diagram generation

**Communication**: stdio transport protocol
**Tools Provided**:
- `generate_diagram` - Generate diagram code from prompt
- `render_diagram` - Render diagram code to image
- `generate_and_render` - Combined operation

**Architecture**:
```python
@app.list_tools()
async def list_tools() -> list[Tool]

@app.call_tool()
async def call_tool(name: str, arguments: Any) -> list[TextContent]
```

**Issues**:
- Placeholder AI generation (returns hardcoded response)
- Missing import for `generate_diagram_code`
- Import resolution problems

#### 2.2 FastMCP Server (`fastmcp_server.py`)
**Purpose**: FastAPI-integrated MCP server

**Features**:
- HTTP/WebSocket communication instead of stdio
- FastAPI router integration
- Real-time communication support
- Same tool set as standard MCP server

**Endpoints**:
- `POST /mcp/tools/generate_diagram`
- `POST /mcp/tools/render_diagram`
- `POST /mcp/tools/generate_and_render`
- `GET /mcp/tools` - List available tools
- `POST /mcp/call_tool` - Generic tool call
- `WS /mcp/ws` - WebSocket endpoint

## Data Flow

### Diagram Generation Flow

```
User Prompt
     │
     ▼
Load Agent Prompt (based on diagram type)
     │
     ▼
Construct Conversation (system + user messages)
     │
     ▼
Call AI Service (OpenRouter/OpenAI)
     │
     ▼
Extract Code Blocks (from AI response)
     │
     ▼
Validate Syntax (Mermaid/D2/C4 validators)
     │
     ▼
Convert if Needed (C4 → D2)
     │
     ▼
Render Diagram (Playwright + browser)
     │
     ▼
Return Response (image + metadata)
```

### MCP Server Flow

```
MCP Client Request
     │
     ▼
Tool Dispatch (call_tool handler)
     │
     ▼
Argument Validation
     │
     ▼
Execute Tool Logic
     │
     ▼
Format Response (TextContent)
     │
     ▼
Return to Client
```

## Security Considerations

### Current Issues
1. **No Input Validation**: User inputs not sanitized
2. **No Rate Limiting**: Potential for abuse
3. **No Authentication**: Open access to endpoints
4. **File System Access**: Temporary file creation risks
5. **Browser Security**: Headless browser attack surface

### Recommended Security Measures
1. Input validation and sanitization
2. Rate limiting implementation
3. Authentication/authorization layer
4. Secure temporary file handling
5. Browser sandboxing
6. Content Security Policy for rendered HTML

## Performance Considerations

### Current Bottlenecks
1. **Browser Launch**: Each render creates new browser instance
2. **AI API Calls**: External service latency
3. **Temporary Files**: File I/O overhead
4. **No Caching**: Repeated renders of same diagrams

### Optimization Opportunities
1. **Browser Pooling**: Reuse browser instances
2. **Result Caching**: Cache rendered diagrams
3. **Async Processing**: Background rendering for large diagrams
4. **Connection Pooling**: Reuse HTTP connections
5. **Lazy Loading**: Load libraries on demand

## Configuration Management

### Current State
- Hard-coded paths and URLs
- No centralized configuration
- Environment variables not consistently used

### Recommended Configuration
```python
class RenderingConfig:
    # Browser settings
    browser_timeout: int = 30000
    viewport_width: int = 1920
    viewport_height: int = 1080
    
    # Frontend settings
    frontend_url: str = "http://localhost:5173"
    static_fallback_enabled: bool = True
    
    # AI settings
    ai_provider: str = "openrouter"
    default_model: str = "gpt-4"
    
    # Security settings
    max_diagram_size: int = 10000
    allowed_formats: List[str] = ["svg", "png"]
    
    # Performance settings
    browser_pool_size: int = 5
    cache_ttl: int = 3600
```

## Error Handling Strategy

### Current Approach
- Inconsistent error handling across modules
- Generic exception catching
- Limited error context

### Recommended Strategy
```python
class DiagramRenderingError(Exception):
    """Base exception for diagram rendering errors"""
    pass

class ValidationError(DiagramRenderingError):
    """Diagram syntax validation failed"""
    pass

class RenderingError(DiagramRenderingError):
    """Rendering process failed"""
    pass

class AIServiceError(DiagramRenderingError):
    """AI service unavailable or failed"""
    pass
```

## Testing Strategy

### Current Test Coverage
- Basic unit tests for some modules
- Limited integration testing
- No end-to-end testing

### Recommended Test Approach
1. **Unit Tests**: Test individual functions and classes
2. **Integration Tests**: Test module interactions
3. **End-to-End Tests**: Test complete workflows
4. **Performance Tests**: Load and stress testing
5. **Security Tests**: Vulnerability scanning

### Test Structure
```
tests/
├── unit/
│   ├── test_validators.py
│   ├── test_converters.py
│   └── test_renderers.py
├── integration/
│   ├── test_api_endpoints.py
│   ├── test_mcp_tools.py
│   └── test_ai_integration.py
├── e2e/
│   ├── test_complete_workflow.py
│   └── test_error_scenarios.py
└── performance/
    ├── test_rendering_performance.py
    └── test_concurrent_requests.py
```

## Monitoring and Logging

### Current Logging
- Basic logging with `common.logger`
- Inconsistent log levels
- Limited structured logging

### Recommended Monitoring
1. **Structured Logging**: JSON format with correlation IDs
2. **Metrics Collection**: Render times, success rates, error rates
3. **Health Checks**: Service availability and dependency health
4. **Alerting**: Error thresholds and performance issues

### Log Categories
```python
# Request logging
logger.info("Diagram generation request", extra={
    "request_id": request_id,
    "diagram_type": diagram_type,
    "prompt_length": len(prompt)
})

# Performance logging
logger.info("Diagram rendered", extra={
    "request_id": request_id,
    "render_time_ms": render_time,
    "output_format": output_format,
    "output_size": len(result)
})

# Error logging
logger.error("Rendering failed", extra={
    "request_id": request_id,
    "error_type": error_type,
    "error_message": str(error),
    "stack_trace": traceback.format_exc()
})
```

## Deployment Architecture

### Current Deployment
- Single-server deployment
- Manual configuration
- No containerization

### Recommended Deployment
```yaml
# Docker Compose example
version: '3.8'
services:
  diagram-api:
    build: .
    ports:
      - "8003:8003"
    environment:
      - AI_PROVIDER=openrouter
      - FRONTEND_URL=http://frontend:5173
    depends_on:
      - redis
      - playwright
  
  redis:
    image: redis:alpine
    ports:
      - "6379:6379"
  
  playwright:
    image: mcr.microsoft.com/playwright:v1.40.0
    volumes:
      - playwright-cache:/ms-playwright
```

## Future Enhancements

### Short Term (1-3 months)
1. Fix critical import and module resolution issues
2. Implement complete C4 to D2 conversion
3. Add comprehensive input validation
4. Implement basic rate limiting
5. Add configuration management

### Medium Term (3-6 months)
1. Consolidate renderer implementations
2. Add authentication and authorization
3. Implement caching layer
4. Add browser connection pooling
5. Expand test coverage

### Long Term (6-12 months)
1. Microservices architecture
2. Distributed rendering cluster
3. Advanced AI integration
4. Real-time collaboration features
5. Multi-tenant support

## Conclusion

The server rendering architecture provides a solid foundation for diagram generation and rendering, but requires significant improvements in reliability, security, and performance. The modular design allows for incremental enhancements, and the MCP server integration provides flexibility for different client types.

Key priorities should be:
1. Fixing critical import and functionality issues
2. Implementing proper security measures
3. Improving error handling and monitoring
4. Optimizing performance for production use
5. Expanding test coverage for reliability

The architecture is well-positioned for future enhancements and can scale to support enterprise-level diagram generation requirements.