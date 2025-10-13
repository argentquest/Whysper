# MCP History Service Documentation

## Overview

The MCP History Service (`mcp_history_service.py`) provides persistent logging functionality for MCP (Model Context Protocol) server requests and responses. It maintains a complete history of all MCP interactions with unique session tracking and file-based storage.

## Features

### 🗂️ Session Management
- **Unique GUID Generation**: Each MCP session gets a unique UUID for identification
- **Timestamp Tracking**: Records session start and last update times
- **File-based Storage**: Each session stored in separate JSON files
- **Automatic Directory Creation**: Creates `history/mcp/` directory structure as needed

### 📝 Request/Response Logging
- **Complete Data Capture**: Stores full request and response structures
- **Tool Name Tracking**: Records which MCP tool was called
- **Metadata Support**: Allows additional context information
- **Append-only Updates**: Files are updated, not overwritten

### 🔍 History Retrieval
- **Session Loading**: Load complete history for a specific session
- **Session Listing**: List all available MCP sessions with metadata
- **Sorted Results**: Sessions sorted by last updated time

## Architecture

```
history/
└── mcp/
    ├── 20250113-143022_550e8d9a-1234-5678-9abc-1234567890ab.json
    ├── 20250113-143045_550e8d9a-1234-5678-9abc-1234567890cd.json
    └── 20250113-143102_550e8d9a-1234-5678-9abc-1234567890ef.json
```

### File Naming Convention
- **Format**: `YYYYMMDD-HHMMSS_GUID.json`
- **Example**: `20250113-143022_550e8d9a-1234-5678-9abc-1234567890ab.json`
- **Components**:
  - `YYYYMMDD-HHMMSS`: Session start timestamp
  - `GUID`: Unique session identifier

## API Reference

### Class: `MCPHistoryService`

#### Constructor
```python
def __init__(self, history_dir: str = None)
```
- **Parameters**:
  - `history_dir`: Optional custom directory for history files
  - **Default**: `history/mcp/` in project root

#### Core Methods

##### `get_or_create_session_guid(session_id: str) -> str`
Get existing GUID for session or create new one.
- **Parameters**:
  - `session_id`: WebSocket connection ID or request identifier
- **Returns**: GUID string for the session

##### `log_request_response(
    session_id: str,
    request_data: Dict[str, Any],
    response_data: Dict[str, Any],
    tool_name: str = None,
    metadata: Dict[str, Any] = None
) -> bool`
Log a request/response pair to session history.
- **Parameters**:
  - `session_id`: Session identifier
  - `request_data`: Complete request dictionary
  - `response_data`: Complete response dictionary
  - `tool_name`: Optional name of called tool
  - `metadata`: Optional additional context
- **Returns**: `True` if logged successfully

##### `load_session_history(session_id: str) -> Optional[Dict[str, Any]]`
Load complete session history from file.
- **Parameters**:
  - `session_id`: Session identifier
- **Returns**: Session data dictionary or `None` if not found

##### `list_session_histories() -> List[Dict[str, Any]]`
List all available MCP sessions.
- **Returns**: List of session metadata dictionaries

## Data Structure

### Session File Format
```json
{
  "session_guid": "550e8d9a-1234-5678-9abc-1234567890ab",
  "session_id": "ws_connection_123",
  "created_at": "2025-01-13T14:30:22.123456",
  "last_updated": "2025-01-13T14:35:45.654321",
  "request_count": 5,
  "metadata": {
    "client_type": "claude_desktop",
    "user_agent": "Claude/1.0"
  },
  "requests": [
    {
      "timestamp": "2025-01-13T14:30:22.123456",
      "tool_name": "generate_diagram",
      "request": {
        "method": "tools/call",
        "params": {
          "name": "generate_diagram",
          "arguments": {
            "prompt": "Simple flowchart",
            "diagram_type": "mermaid"
          }
        }
      },
      "response": {
        "content": [
          {
            "type": "text",
            "text": "flowchart TD\n    A[Start] --> B[End]"
          }
        ],
        "isError": false
      },
      "metadata": {
        "processing_time_ms": 1250
      }
    }
  ]
}
```

## Usage Examples

### Basic Usage
```python
from mcp_server.mcp_history_service import mcp_history_service

# Log a request/response pair
success = mcp_history_service.log_request_response(
    session_id="ws_connection_123",
    request_data={"method": "tools/call", "params": {...}},
    response_data={"content": [...], "isError": False},
    tool_name="generate_diagram",
    metadata={"processing_time_ms": 1250}
)

# Load session history
history = mcp_history_service.load_session_history("ws_connection_123")
print(f"Session has {history['request_count']} requests")

# List all sessions
sessions = mcp_history_service.list_session_histories()
for session in sessions:
    print(f"Session {session['guid']}: {session['request_count']} requests")
```

### Integration with MCP Server
```python
# In your MCP server request handler
async def handle_tool_call(session_id: str, request: dict):
    # Process the request
    response = await process_tool(request)
    
    # Log the interaction
    mcp_history_service.log_request_response(
        session_id=session_id,
        request_data=request,
        response_data=response,
        tool_name=request.get('params', {}).get('name'),
        metadata={
            'client_ip': client_ip,
            'user_agent': user_agent
        }
    )
    
    return response
```

## Configuration

### Environment Variables
The history service respects these environment variables:

- `LOG_LEVEL`: Controls logging verbosity (DEBUG, INFO, WARNING, ERROR)
- `HISTORY_DIR`: Custom directory for history files (overrides default)

### Directory Permissions
Ensure the application has write permissions to:
- `history/` directory (or custom history directory)
- Session files created within the history directory

## Monitoring and Debugging

### Logging
The service provides structured logging at different levels:

```python
# Enable debug logging
import logging
logging.getLogger('mcp_server.mcp_history_service').setLevel(logging.DEBUG)
```

**Log Messages**:
- `INFO`: Service initialization, new session creation
- `DEBUG`: Request/response logging, file operations
- `WARNING`: File read errors, missing data
- `ERROR`: Failed logging operations, critical errors

### File Monitoring
Monitor the `history/mcp/` directory for:
- **File Growth**: Watch for unusually large session files
- **File Count**: Monitor number of session files
- **Disk Usage**: Ensure adequate storage space

## Performance Considerations

### File I/O Optimization
- **Lazy Loading**: Session data loaded only when needed
- **Append Operations**: Files updated rather than rewritten
- **JSON Encoding**: UTF-8 encoding with ASCII fallback

### Memory Usage
- **Session Tracking**: In-memory GUID mapping for active sessions
- **File Handles**: Files opened/closed per operation
- **JSON Parsing**: Efficient parsing of session data

### Scalability
- **Session Isolation**: Each session in separate file
- **Concurrent Access**: Thread-safe file operations
- **Cleanup Strategy**: Implement session cleanup for long-running servers

## Security Considerations

### Data Privacy
- **Sensitive Data**: Review logged data for sensitive information
- **File Permissions**: Restrict access to history directory
- **Data Retention**: Implement cleanup policies as needed

### Access Control
```python
# Example: Restrict history directory access
import os
history_dir = "history/mcp"
os.chmod(history_dir, 0o700)  # Owner read/write/execute only
```

## Troubleshooting

### Common Issues

#### "History directory not accessible"
**Solution**: Check directory permissions and create directory if missing
```python
import os
os.makedirs("history/mcp", exist_ok=True)
```

#### "Session file corrupted"
**Solution**: Implement file validation and backup recovery
```python
try:
    with open(filepath, 'r') as f:
        data = json.load(f)
except json.JSONDecodeError:
    # Handle corrupted file
    logger.error(f"Corrupted session file: {filepath}")
```

#### "GUID collision"
**Solution**: UUID generation makes collisions extremely unlikely
- Verify session_id uniqueness
- Check for concurrent access issues

### Debug Information
Enable debug logging to trace operations:
```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

## Integration Points

### With FastMCP Server
The history service integrates seamlessly with the FastMCP server:

```python
# In fastmcp_server.py
from mcp_server.mcp_history_service import mcp_history_service

@mcp.tool()
async def generate_diagram(prompt: str, diagram_type: str):
    request_id = generate_request_id()
    
    # Log request
    mcp_history_service.log_request_response(
        session_id=get_session_id(),
        request_data={"prompt": prompt, "diagram_type": diagram_type},
        response_data={"result": diagram_result},
        tool_name="generate_diagram"
    )
    
    return diagram_result
```

### With Frontend History
Follows the same pattern as frontend history service for consistency:
- GUID-based session identification
- Timestamp-based file naming
- JSON-based storage format

## Future Enhancements

### Planned Features
- [ ] Session compression for long histories
- [ ] Automatic cleanup of old sessions
- [ ] Search functionality across sessions
- [ ] Export capabilities (CSV, JSON)
- [ ] Session analytics and metrics

### Performance Improvements
- [ ] Async file operations
- [ ] Batch logging for high-frequency requests
- [ ] Memory-mapped file access for large sessions
- [ ] Database backend option for enterprise use

## Version History

- **v1.0.0** (2025-01-13): Initial implementation
  - Basic session management
  - Request/response logging
  - File-based storage
  - GUID-based tracking

---

**Last Updated**: 2025-01-13  
**Version**: 1.0.0  
**Maintainer**: Whysper Development Team