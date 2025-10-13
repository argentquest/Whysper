# API Documentation

## Overview

This document provides comprehensive API documentation for the Code Chat with AI FastAPI backend. The application exposes a REST API that serves the React frontend and provides programmatic access to AI-powered code analysis capabilities.

## Base URL
```
http://localhost:8003/api/v1
```

## Authentication
API keys are managed through environment variables and are not required in API requests. Authentication is handled server-side using the configured API keys.

## API Endpoints

### Health & Status

#### GET /api/v1/
Root endpoint with service information.

**Response:**
```json
{
  "status": "healthy",
  "timestamp": "2025-01-13T14:30:22.123456",
  "version": "2.0.0"
}
```

#### GET /api/v1/health
Health check with status details.

**Response:**
```json
{
  "status": "healthy",
  "timestamp": "2025-01-13T14:30:22.123456",
  "version": "2.0.0"
}
```

### Chat & Conversation Management

#### POST /api/v1/chat/
Send chat messages to AI providers.

**Request Body:**
```json
{
  "message": "What does this code do?",
  "conversationId": "conv_123456",
  "contextFiles": ["main.py", "utils.py"],
  "settings": {
    "model": "openai/gpt-4",
    "provider": "openrouter"
  }
}
```

**Response:**
```json
{
  "message": {
    "id": "msg_1642098622_abc12345",
    "role": "assistant",
    "content": "This code implements...",
    "timestamp": "2025-01-13T14:30:22",
    "metadata": {
      "model": "openai/gpt-4",
      "provider": "openrouter",
      "tokens": 150,
      "elapsedTime": 2.34
    }
  },
  "conversationId": "conv_123456"
}
```

#### POST /api/v1/chat/conversations
Create a new conversation session.

**Request Body:**
```json
{
  "provider": "openrouter",
  "model": "openai/gpt-4",
  "apiKey": "sk-your-api-key"
}
```

**Response:**
```json
{
  "conversationId": "conv_123456",
  "provider": "openrouter",
  "model": "openai/gpt-4",
  "availableModels": ["openai/gpt-4", "openai/gpt-3.5-turbo"],
  "summary": {
    "conversation_id": "conv_123456",
    "provider": "openrouter",
    "selected_model": "openai/gpt-4",
    "selected_files": [],
    "persistent_files": []
  }
}
```

#### GET /api/v1/chat/conversations/{conversation_id}/summary
Retrieve conversation summary.

**Response:**
```json
{
  "conversation_id": "conv_123456",
  "provider": "openrouter",
  "selected_model": "openai/gpt-4",
  "selected_directory": "/path/to/project",
  "selected_files": ["main.py", "utils.py"],
  "persistent_files": ["main.py"]
}
```

#### PUT /api/v1/chat/conversations/{conversation_id}/model
Update AI model for conversation.

**Request Body:**
```json
{
  "model": "anthropic/claude-3-sonnet"
}
```

**Response:**
```json
{
  "conversationId": "conv_123456",
  "provider": "openrouter",
  "model": "anthropic/claude-3-sonnet",
  "availableModels": ["openai/gpt-4", "anthropic/claude-3-sonnet"]
}
```

#### PUT /api/v1/chat/conversations/{conversation_id}/api-key
Update API key for conversation.

**Request Body:**
```json
{
  "api_key": "sk-new-api-key"
}
```

**Response:**
```json
{
  "conversationId": "conv_123456",
  "provider": "openrouter",
  "model": "openai/gpt-4",
  "availableModels": ["openai/gpt-4", "openai/gpt-3.5-turbo"]
}
```

#### GET /api/v1/chat/conversations/{conversation_id}/export
Export conversation data.

**Response:**
```json
{
  "summary": {
    "conversation_id": "conv_123456",
    "provider": "openrouter",
    "selected_model": "openai/gpt-4",
    "selected_files": ["main.py"],
    "persistent_files": ["main.py"]
  }
}
```

#### POST /api/v1/chat/conversations/import
Import conversation data.

**Request Body:**
```json
{
  "provider": "openrouter",
  "model": "openai/gpt-4",
  "api_key": "sk-api-key",
  "conversation_history": [
    {"role": "user", "content": "What does this code do?"},
    {"role": "assistant", "content": "This code implements..."}
  ]
}
```

**Response:**
```json
{
  "conversationId": "conv_789012",
  "provider": "openrouter",
  "model": "openai/gpt-4",
  "availableModels": ["openai/gpt-4", "openai/gpt-3.5-turbo"]
}
```

### Conversation History

#### GET /api/v1/chat/conversations/history
List all conversation history files.

**Response:**
```json
{
  "success": true,
  "data": [
    {
      "conversation_id": "conv_123456",
      "created_at": "2025-01-13T14:30:22",
      "last_updated": "2025-01-13T14:45:10",
      "message_count": 5
    }
  ],
  "count": 1
}
```

#### GET /api/v1/chat/conversations/{conversation_id}/history
Get conversation history for a specific conversation.

**Response:**
```json
{
  "success": true,
  "data": {
    "conversation_id": "conv_123456",
    "created_at": "2025-01-13T14:30:22",
    "messages": [
      {
        "id": "msg_1642098622_abc12345",
        "role": "user",
        "content": "What does this code do?",
        "timestamp": "2025-01-13T14:30:22"
      },
      {
        "id": "msg_1642098625_def67890",
        "role": "assistant",
        "content": "This code implements...",
        "timestamp": "2025-01-13T14:30:25"
      }
    ]
  }
}
```

#### DELETE /api/v1/chat/conversations/{conversation_id}/history
Delete conversation history for a specific conversation.

**Response:**
```json
{
  "success": true,
  "message": "Conversation history deleted successfully"
}
```

### Diagram Events

#### POST /api/v1/diagram-events/log-diagram-event
Log diagram detection and rendering events from frontend.

**Request Body:**
```json
{
  "event_type": "detection",
  "diagram_type": "mermaid",
  "code_length": 245,
  "detection_method": "language_marker",
  "conversation_id": "conv_123456"
}
```

**Response:**
```json
{
  "status": "logged",
  "event_type": "detection",
  "diagram_type": "mermaid"
}
```

#### GET /api/v1/diagram-events/health
Health check endpoint for diagram event logging service.

**Response:**
```json
{
  "status": "healthy",
  "service": "diagram_events"
}
```

### MCP (Model Context Protocol)

#### GET /api/v1/mcp/tools
List available MCP tools.

**Response:**
```json
{
  "tools": [
    {
      "name": "generate_diagram",
      "description": "Generate diagram code from a natural language prompt.",
      "inputSchema": {
        "type": "object",
        "properties": {
          "prompt": {"type": "string"},
          "diagram_type": {"type": "string", "enum": ["mermaid", "d2", "c4"]}
        }
      }
    }
  ]
}
```

#### POST /api/v1/mcp/tools/generate_diagram
Generate diagram code from a prompt.

**Request Body:**
```json
{
  "prompt": "Simple flowchart showing a login process",
  "diagram_type": "mermaid"
}
```

**Response:**
```json
{
  "content": [
    {
      "type": "text",
      "text": "{\"diagram_code\": \"flowchart TD\\n    A[Start] --> B[Login]\", \"diagram_type\": \"mermaid\"}"
    }
  ],
  "isError": false
}
```

#### POST /api/v1/mcp/tools/render_diagram
Render diagram code to SVG or PNG.

**Request Body:**
```json
{
  "code": "flowchart TD\n    A[Start] --> B[End]",
  "diagram_type": "mermaid",
  "output_format": "svg"
}
```

**Response:**
```json
{
  "content": [
    {
      "type": "text",
      "text": "{\"image_data\": \"<svg>...</svg>\", \"output_format\": \"svg\"}"
    }
  ],
  "isError": false
}
```

#### POST /api/v1/mcp/tools/generate_and_render
Generate and render a diagram in one step.

**Request Body:**
```json
{
  "prompt": "User authentication flow",
  "diagram_type": "mermaid",
  "output_format": "svg"
}
```

**Response:**
```json
{
  "content": [
    {
      "type": "text",
      "text": "{\"diagram_code\": \"flowchart TD...\", \"image_data\": \"<svg>...</svg>\"}"
    }
  ],
  "isError": false
}
```

#### POST /api/v1/mcp/call_tool
Generic MCP tool call endpoint.

**Request Body:**
```json
{
  "name": "generate_diagram",
  "arguments": {
    "prompt": "Simple flowchart",
    "diagram_type": "mermaid"
  }
}
```

**Response:**
```json
{
  "content": [
    {
      "type": "text",
      "text": "{\"diagram_code\": \"flowchart TD...\"}"
    }
  ],
  "isError": false
}
```

#### WebSocket /api/v1/mcp/ws
WebSocket endpoint for real-time MCP communication.

**Connection:** Establish WebSocket connection for JSON-RPC 2.0 protocol

**Message Format:**
```json
{
  "jsonrpc": "2.0",
  "id": 1,
  "method": "tools/call",
  "params": {
    "name": "generate_diagram",
    "arguments": {
      "prompt": "Simple flowchart",
      "diagram_type": "mermaid"
    }
  }
}
```

### Settings & Configuration

#### GET /api/v1/settings/
Retrieves current application settings.

**Response:**
```json
{
  "values": {
    "API_KEY": "sk-your-key",
    "UI_THEME": "light",
    "MODEL": "openai/gpt-4"
  },
  "masked": {
    "API_KEY": "sk-***key",
    "UI_THEME": "light",
    "MODEL": "openai/gpt-4"
  },
  "theme": "light",
  "availableThemes": ["light", "dark", "auto"]
}
```

#### PUT /api/v1/settings/env
Updates environment variables.

**Request Body:**
```json
{
  "updates": {
    "UI_THEME": "dark",
    "MODEL": "anthropic/claude-3-sonnet"
  }
}
```

**Response:**
```json
{
  "API_KEY": true,
  "UI_THEME": true,
  "MODEL": false
}
```

#### PUT /api/v1/settings/theme
Sets the application theme.

**Request Body:**
```json
{
  "theme": "dark"
}
```

**Response:**
```json
{
  "theme": "dark",
  "message": "Theme updated"
}
```

#### POST /api/v1/settings/theme/toggle
Toggles between light and dark theme.

**Response:**
```json
{
  "theme": "dark",
  "message": "Theme updated"
}
```


## Error Handling

All API endpoints return appropriate HTTP status codes and error messages:

### Common Error Responses

#### 400 Bad Request
```json
{
  "detail": "Message cannot be empty"
}
```

#### 404 Not Found
```json
{
  "detail": "Conversation not found"
}
```

#### 500 Internal Server Error
```json
{
  "detail": "Internal server error: AI processing failed"
}
```

## Rate Limiting

- API requests are subject to the rate limits of the underlying AI providers
- Implement exponential backoff for retry logic
- Monitor token usage through response metadata

## Data Types

### ConversationSummary
```typescript
interface ConversationSummary {
  conversation_id: string;
  provider: string;
  selected_model: string;
  selected_directory?: string;
  selected_files: string[];
  persistent_files: string[];
}
```

### ChatMessage
```typescript
interface ChatMessage {
  id: string;
  role: 'user' | 'assistant';
  content: string;
  timestamp: string;
  metadata?: {
    model: string;
    provider: string;
    tokens: number;
    elapsedTime: number;
  };
}
```

### MCPToolResponse
```typescript
interface MCPToolResponse {
  content: Array<{
    type: string;
    text: string;
  }>;
  isError: boolean;
}
```

## SDK Examples

### JavaScript/TypeScript
```javascript
// Create conversation
const response = await fetch('/api/v1/chat/conversations', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    provider: 'openrouter',
    model: 'openai/gpt-4',
    apiKey: 'sk-your-key'
  })
});

// Send chat message
const chatResponse = await fetch('/api/v1/chat/', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    message: 'What does this code do?',
    conversationId: conversationId,
    contextFiles: ['main.py']
  })
});

// Call MCP tool
const mcpResponse = await fetch('/api/v1/mcp/tools/generate_diagram', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    prompt: 'Simple flowchart',
    diagram_type: 'mermaid'
  })
});
```

### Python
```python
import requests

# Create conversation
response = requests.post('http://localhost:8003/api/v1/chat/conversations', json={
    'provider': 'openrouter',
    'model': 'openai/gpt-4',
    'apiKey': 'sk-your-key'
})
conversation_id = response.json()['conversationId']

# Send chat message
chat_response = requests.post(
    'http://localhost:8003/api/v1/chat/',
    json={
        'message': 'What does this code do?',
        'conversationId': conversation_id,
        'contextFiles': ['main.py']
    }
)

# Call MCP tool
mcp_response = requests.post(
    'http://localhost:8003/api/v1/mcp/tools/generate_diagram',
    json={
        'prompt': 'Simple flowchart',
        'diagram_type': 'mermaid'
    }
)
```

## WebSocket Connection (MCP)

### JavaScript Example
```javascript
// Connect to MCP WebSocket
const ws = new WebSocket('ws://localhost:8003/api/v1/mcp/ws');

ws.onopen = () => {
  // List available tools
  ws.send(JSON.stringify({
    jsonrpc: "2.0",
    id: 1,
    method: "tools/list"
  }));
};

ws.onmessage = (event) => {
  const response = JSON.parse(event.data);
  console.log('MCP Response:', response);
};

// Call a tool
ws.send(JSON.stringify({
  jsonrpc: "2.0",
  id: 2,
  method: "tools/call",
  params: {
    name: "generate_diagram",
    arguments: {
      prompt: "Simple flowchart",
      diagram_type: "mermaid"
    }
  }
}));
```

This API documentation covers the complete FastAPI backend interface used by the Whysper Web2 application. For implementation details, refer to the source code in the `backend/` directory.