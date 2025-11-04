# Architecture Gen Studio

A web-based tool for generating and editing architectural diagrams using AI-powered natural language processing. Built with React, TypeScript, and Ant Design.

## Features

### 🎯 Core Features
- **Multi-Format Diagram Support**
  - Mermaid diagrams
  - D2 language
  - Structurizr format
  - PlantUML diagrams

- **AI-Powered Generation**
  - Natural language to diagram conversion
  - Agent-based diagram generation
  - Real-time streaming updates via SSE
  - Custom agent options and templates

- **Code Editing & Validation**
  - Syntax highlighting for multiple diagram languages
  - Real-time code validation
  - Error detection and reporting
  - Line-number based error locations

- **Interactive Visualization**
  - Live diagram rendering
  - Zoom in/out with keyboard shortcuts
  - SVG-based rendering
  - Smooth animations

- **Export & Sharing**
  - Export to SVG format
  - Export to PDF (8.5" x 11" standard)
  - Export diagram code
  - Share diagrams via URL

- **Responsive Layout**
  - Three-column layout (Prompts, Diagrams, Code)
  - Resizable columns with drag dividers
  - Collapse/expand columns
  - Persistent layout preferences

- **Accessibility**
  - WCAG 2.1 Level AA compliant
  - Full keyboard navigation
  - Screen reader support
  - High contrast mode ready

## Getting Started

### Prerequisites
- Node.js 16+ or higher
- npm 8+ or yarn
- Modern web browser

### Installation

```bash
# Clone repository
git clone https://github.com/yourorg/whysper.git
cd whysper

# Install dependencies
npm install

# Configure environment
cp .env.example .env
# Edit .env to set:
# REACT_APP_API_URL=http://localhost:8000/api/v1
# REACT_APP_THEME=light (or dark)
```

### Development

```bash
# Start development server
npm start

# Navigate to the studio
# http://localhost:3000/studio

# Run tests
npm test

# Build for production
npm run build
```

### Configuration

#### Environment Variables
```env
# API Configuration
REACT_APP_API_URL=http://localhost:8000/api/v1

# Theme (light, dark, or custom)
REACT_APP_THEME=light

# Feature Flags
REACT_APP_ENABLE_PDF_EXPORT=true
REACT_APP_ENABLE_SSE_STREAMING=true
REACT_APP_ENABLE_CODE_HIGHLIGHTING=true
```

#### Theme Customization
The application uses Whysper's ThemeProvider for theming. All Ant Design color tokens are available:

```typescript
import { ThemeProvider } from './themes';

// Wrap application with ThemeProvider
<ThemeProvider>
  <App />
</ThemeProvider>
```

## User Guide

### Workflow: Generate a New Diagram

1. **Select Agent**
   - Click agent dropdown in header
   - Choose diagram type (C4, Sequence, ER, etc.)

2. **Choose Template**
   - Select agent option from left column
   - Template auto-populates in prompt editor

3. **Edit Prompt**
   - Customize the template text
   - View character count (max 5000)
   - Click "Submit" to generate

4. **Monitor Generation**
   - Watch SSE messages in footer
   - See progress updates in real-time
   - Click "Cancel" to stop generation

5. **View Diagram**
   - Diagram renders in center column
   - Use zoom controls to adjust view
   - Click "Export" to save

6. **Fine-Tune Code**
   - Edit diagram code in right column
   - Click "Validate" to check syntax
   - Click "Render" to preview changes

### Keyboard Shortcuts

| Shortcut | Action |
|----------|--------|
| `Ctrl++` | Zoom in |
| `Ctrl+-` | Zoom out |
| `Ctrl+0` | Reset zoom to 100% |
| `Escape` | Close dialogs |
| `Tab` | Next interactive element |
| `Shift+Tab` | Previous interactive element |
| `Enter` | Activate focused button |

### Diagram Types

#### Mermaid
UML and flowchart diagrams. Supports:
- Flowcharts
- Sequence diagrams
- Class diagrams
- State diagrams
- Gantt charts

#### D2
Declarative diagram syntax. Supports:
- Flowcharts
- Database schemas
- Network diagrams
- Mindmaps

#### Structurizr
Architecture diagrams using C4 model:
- System Context diagrams
- Container diagrams
- Component diagrams
- Code diagrams

#### PlantUML
Rich diagram language. Supports:
- Sequence diagrams
- Use case diagrams
- Class diagrams
- Component diagrams

## API Reference

### Endpoints

#### Get Agents
```
GET /api/v1/agents

Response:
[
  {
    "id": "agent-1",
    "name": "C4 Diagram Agent",
    "description": "Generates C4 architecture diagrams"
  }
]
```

#### Get Agent Options
```
GET /api/v1/agents/{agentId}/options

Response:
[
  {
    "id": "option-1",
    "agentId": "agent-1",
    "name": "System Context Diagram",
    "description": "High-level overview",
    "template": "Create a C4 system context...",
    "validationRules": ["Must include system boundary"],
    "outputFormat": "SVG",
    "enabled": true
  }
]
```

#### Generate Diagram
```
POST /api/v1/diagrams/v2/generate

Request:
{
  "agentId": "agent-1",
  "prompt": "Create a system context diagram for...",
  "diagramType": "mermaid"
}

Response:
{
  "requestId": "req-1234567890",
  "diagram": {
    "svg": "<svg>...</svg>",
    "provider": "mermaid",
    "code": "graph TD...",
    "metadata": {...},
    "status": "success",
    "timestamp": "2024-01-01T12:00:00Z"
  }
}
```

#### Validate Code
```
POST /api/v1/diagrams/v2/validate

Request:
{
  "code": "graph TD\n  A --> B",
  "diagramType": "mermaid"
}

Response:
{
  "isValid": true,
  "errors": [],
  "warnings": []
}
```

#### Render Diagram
```
POST /api/v1/diagrams/v2/render

Request:
{
  "code": "graph TD\n  A --> B",
  "diagramType": "mermaid"
}

Response:
{
  "svg": "<svg>...</svg>",
  "provider": "mermaid",
  "code": "graph TD\n  A --> B",
  "metadata": {...},
  "status": "success",
  "timestamp": "2024-01-01T12:00:00Z"
}
```

#### Cancel Request
```
POST /api/v1/diagrams/v2/cancel

Request:
{
  "requestId": "req-1234567890"
}

Response:
{
  "status": "cancelled"
}
```

#### Stream Updates (SSE)
```
GET /api/v1/diagrams/v2/stream?requestId={requestId}

Events:
event: message
data: {"type":"progress","message":"Generating..."}

event: diagram
data: {"svg":"...","provider":"mermaid"}
```

## Architecture

### Component Structure
```
ArchitectureGenStudio
├── Header
│   ├── BrandingSection
│   ├── AgentSelector
│   ├── NavigationMenu
│   ├── UserAccountMenu
│   └── NotificationBadge
├── Layout
│   ├── LeftColumn (Prompts)
│   │   ├── AgentOptionList
│   │   ├── PromptEditor
│   │   └── SubmitButton
│   ├── CenterColumn (Diagrams)
│   │   ├── DiagramRenderingArea
│   │   └── ZoomControls
│   └── RightColumn (Code)
│       ├── CodeEditor
│       ├── ValidateButton
│       ├── RenderButton
│       └── ErrorPanel
└── Footer
    ├── StatusColumn
    ├── SSEMessagesColumn
    └── LinksColumn
```

### State Management
- **useArchitectureStudioState**: Main state hook with 30+ handlers
- **useAPIClient**: API integration hook
- **useSSE**: Server-Sent Events streaming hook
- **useLocalStorage**: localStorage persistence

### Type Safety
- Full TypeScript coverage (0 `any` types)
- 26+ interfaces for complete type safety
- Strict null checking enabled

## Development

### Project Structure
```
frontend/src/components/architectureGenStudio/
├── index.tsx                    # Main component
├── types/
│   └── architectureStudio.ts   # All TypeScript interfaces
├── hooks/
│   ├── useArchitectureStudioState.ts
│   ├── useAPIClient.ts
│   ├── useSSE.ts
│   └── useLocalStorage.ts
├── components/
│   ├── Header/
│   ├── LeftColumn/
│   ├── CenterColumn/
│   ├── RightColumn/
│   └── Footer/
├── styles/
│   └── architectureStudio.module.css
├── __tests__/
│   ├── integration.test.ts
│   ├── stateSynchronization.test.ts
│   ├── errorHandling.test.ts
│   ├── componentTesting.guide.md
│   ├── workflowTesting.guide.md
│   └── accessibility.audit.md
├── README.md
├── DEPLOYMENT_GUIDE.md
└── CHANGELOG.md
```

### Running Tests

```bash
# Unit tests
npm test

# Integration tests
npm test -- integration.test.ts

# State synchronization tests
npm test -- stateSynchronization.test.ts

# Error handling tests
npm test -- errorHandling.test.ts

# Coverage report
npm test -- --coverage
```

### Code Style

```bash
# Lint code
npm run lint

# Format code
npm run format

# Type check
npm run type-check
```

## Performance

### Metrics
- First Contentful Paint (FCP): < 1.8s
- Largest Contentful Paint (LCP): < 2.5s
- Cumulative Layout Shift (CLS): < 0.1
- Time to Interactive (TTI): < 3.5s

### Optimization
- Code splitting for lazy loading
- Memoization for expensive operations
- SSE connection pooling
- localStorage caching
- Gzip compression

## Accessibility

### Compliance
- WCAG 2.1 Level AA certified
- Keyboard navigation fully supported
- Screen reader compatible
- High contrast mode ready

### Features
- Skip to main content link
- Focus visible indicators
- ARIA labels and descriptions
- Live regions for updates
- Semantic HTML structure

## Browser Support

| Browser | Support | Version |
|---------|---------|---------|
| Chrome | ✅ | 90+ |
| Firefox | ✅ | 88+ |
| Safari | ✅ | 14+ |
| Edge | ✅ | 90+ |
| Opera | ⚠️ | 76+ (partial) |
| IE11 | ❌ | Not supported |

## Troubleshooting

### Issue: Diagram not rendering
**Solution:**
1. Verify backend is running
2. Check API URL in .env
3. Validate diagram syntax
4. Check browser console for errors

### Issue: SSE connection fails
**Solution:**
1. Check network connectivity
2. Verify backend SSE endpoint
3. Check CORS headers
4. Try reconnecting

### Issue: Slow performance
**Solution:**
1. Check browser DevTools performance tab
2. Reduce diagram complexity
3. Clear browser cache
4. Restart backend service

### Issue: Layout issues
**Solution:**
1. Clear localStorage
2. Refresh page
3. Check browser zoom level
4. Try different browser

## FAQ

**Q: Can I use my own agents?**
A: Yes, customize agents in the backend configuration.

**Q: How do I extend diagram types?**
A: Add new types to the `DIAGRAM_TYPES` constant and create corresponding components.

**Q: Can I customize the UI colors?**
A: Yes, via Whysper's ThemeProvider.

**Q: Is there an API for programmatic access?**
A: Yes, all features available via REST API endpoints.

**Q: How do I scale for multiple users?**
A: See deployment guide for scaling recommendations.

## Contributing

Please follow the project's contribution guidelines:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/new-feature`)
3. Commit your changes (`git commit -am 'Add new feature'`)
4. Push to the branch (`git push origin feature/new-feature`)
5. Create a Pull Request

## License

Copyright (c) 2024 Wells Fargo. All rights reserved.

## Support

For issues and questions:
- Email: support@example.com
- Documentation: https://docs.example.com
- Issues: https://github.com/yourorg/whysper/issues

## Changelog

See [CHANGELOG.md](./CHANGELOG.md) for detailed version history.

## Deployment

See [DEPLOYMENT_GUIDE.md](./DEPLOYMENT_GUIDE.md) for production deployment instructions.

---

**Last Updated:** January 2024
**Version:** 1.0.0
**Status:** Production Ready ✅
