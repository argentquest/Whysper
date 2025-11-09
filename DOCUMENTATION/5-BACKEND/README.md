# Diagram Generator MCP Server

An MCP (Model Context Protocol) server that provides AI-powered diagram generation and rendering capabilities.

## Features

- **AI-Powered Generation**: Generate diagram code from natural language prompts
- **Multi-Format Support**: Supports Mermaid, D2, and C4 diagram types
- **Headless Rendering**: Renders diagrams to SVG or PNG using Playwright
- **Easy Integration**: Standard MCP protocol for use with Claude Desktop and other MCP clients

## Installation

### Prerequisites

1. **Python 3.12+** with required packages:
```bash
pip install mcp playwright
playwright install chromium
```

2. **Frontend Server Running**:
```bash
cd frontend
npm run dev
```
The frontend must be running on `http://localhost:5173` for rendering to work.

3. **Backend Dependencies**:
```bash
cd backend
pip install -r requirements.txt
```

## Configuration

### For Claude Desktop

Add to your Claude Desktop configuration file:

**Windows**: `%APPDATA%\Claude\claude_desktop_config.json`
**macOS**: `~/Library/Application Support/Claude/claude_desktop_config.json`

```json
{
  "mcpServers": {
    "diagram-generator": {
      "command": "python",
      "args": [
        "-m",
        "mcp_server.fastmcp_server"
      ],
      "cwd": "C:\\Code2025\\Whysper\\backend"
    }
  }
}
```

**Note**: Adjust the paths to match your installation location.

## Usage

Once configured, Claude Desktop will have access to three tools:

### 1. `generate_diagram`
Generate diagram code from a natural language description.

**Example**:
```
Generate a mermaid flowchart showing a login process with user, frontend, and backend
```

### 2. `render_diagram`
Render existing diagram code to an image.

**Example**:
```
Render this mermaid code to SVG:
flowchart TD
    A[Start] --> B[End]
```

### 3. `generate_and_render`
Generate and render in one step (most convenient).

**Example**:
```
Create a D2 diagram showing a three-tier web architecture and render it as PNG
```

## Supported Diagram Types

### Mermaid
- Flowcharts
- Sequence diagrams
- Class diagrams
- State diagrams
- Entity-relationship diagrams
- Gantt charts
- And more...

### D2
- System architecture diagrams
- Network diagrams
- Container-based designs
- Custom shapes and styles

### C4
- Context diagrams (C1)
- Container diagrams (C2)
- Component diagrams (C3)
- Automatically converted to D2 for rendering

## Architecture

```
┌─────────────────────────────────────────┐
│  Claude Desktop / MCP Client            │
│  (User Interface)                       │
└─────────────────────────────────────────┘
                  │
                  │ MCP Protocol (HTTP/stdio)
                  ▼
┌─────────────────────────────────────────┐
│  fastmcp_server.py                      │
│  (MCP Server)                           │
│  ├─ generate_diagram                    │
│  ├─ render_diagram                      │
│  ├─ generate_and_render                 │
│  └─ history_management                  │
└─────────────────────────────────────────┘
                  │
                  ▼
┌─────────────────────────────────────────┐
│  renderer_v2.py                         │
│  (Playwright + Frontend)                │
│  └─ Headless browser rendering          │
└─────────────────────────────────────────┘
                  │
                  ▼
┌─────────────────────────────────────────┐
│  Frontend: /render (React)              │
│  ├─ Mermaid.js                          │
│  ├─ D2 Browser Library                  │
│  └─ C4 → D2 Converter                   │
└─────────────────────────────────────────┘
```

## Troubleshooting

### Server won't start
- Check that Python is in your PATH
- Verify all dependencies are installed
- Check the Claude Desktop logs for errors

### Rendering fails
- Ensure frontend server is running on port 5173
- Check that Playwright chromium is installed: `playwright install chromium`
- Verify backend/.env has required configuration

### Diagram generation produces invalid code
- Check that API_KEY is configured in backend/.env
- Verify the AI model is accessible
- Try simpler prompts first

## Development

### Running Tests
```bash
cd backend
pytest mvp_diagram_generator/tests/ -v
```

### Debugging
Set environment variable for verbose logging:
```bash
set LOG_LEVEL=DEBUG
cd backend
python -m mcp_server.fastmcp_server
```

## History Service

The MCP server includes a comprehensive history service for logging all requests and responses. See [MCP_HISTORY_SERVICE.md](MCP_HISTORY_SERVICE.md) for detailed documentation.

## License

Part of the Whysper Web2 project.
