# Whysper Web2 Frontend

A modern React frontend providing an intuitive interface for AI-powered code analysis, diagram generation, and conversation management.

## 🚀 Features

### Core Functionality
- **AI Chat Interface**: Real-time conversations with multiple AI providers
- **Code Analysis**: Intelligent code extraction and analysis from AI responses
- **Diagram Rendering**: Support for Mermaid, D2, and C4 architecture diagrams
- **File Context Management**: Select and manage files for AI context
- **Multi-tab Conversations**: Organize and switch between different conversations

### UI/UX Features
- **Modern Design**: Built with Ant Design components for professional appearance
- **Theme Support**: Light, dark, and auto themes with system preference detection
- **Responsive Layout**: Optimized for desktop and mobile devices
- **Real-time Updates**: Streaming responses with live content updates
- **Rich Media Support**: Code highlighting, markdown rendering, and interactive diagrams

### Advanced Features
- **MCP Integration**: Model Context Protocol support for external tool integration
- **History Management**: Persistent conversation history with search and export
- **Settings Management**: Comprehensive configuration interface
- **File Operations**: Upload, download, and manage project files
- **Agent Prompts**: Specialized AI agents for different tasks

## 🛠️ Technology Stack

- **Framework**: React 18 with TypeScript
- **Build Tool**: Vite for fast development and optimized builds
- **UI Library**: Ant Design for consistent, professional components
- **State Management**: React hooks and context API
- **Styling**: Tailwind CSS with custom theme support
- **Code Editor**: Monaco Editor (VS Code editor) with syntax highlighting
- **Diagram Rendering**: Mermaid.js, D2, and custom C4-to-D2 converter
- **HTTP Client**: Axios for API communication
- **Markdown**: ReactMarkdown with syntax highlighting

## 📦 Project Structure

```
frontend/
├── public/                     # Static assets
│   ├── render-diagram.html     # Standalone diagram renderer
│   └── vite.svg                # Vite logo
├── src/                        # Source code
│   ├── components/             # React components
│   │   ├── chat/               # Chat-related components
│   │   │   ├── ChatView.tsx    # Main chat interface
│   │   │   ├── InputPanel.tsx  # Message input component
│   │   │   ├── MermaidDiagram.tsx # Mermaid diagram renderer
│   │   │   ├── D2Diagram.tsx   # D2 diagram renderer
│   │   │   └── C4Diagram.tsx   # C4 diagram renderer
│   │   ├── editor/             # Code editor components
│   │   │   ├── FileEditorView.tsx # File editor interface
│   │   │   └── MonacoEditor.tsx # Monaco editor wrapper
│   │   ├── layout/             # Layout components
│   │   │   ├── Header.tsx      # Application header
│   │   │   ├── StatusBar.tsx   # Status bar component
│   │   │   └── TabManager.tsx  # Tab management
│   │   ├── modals/             # Modal dialogs
│   │   │   ├── AboutModal.tsx  # About dialog
│   │   │   ├── SettingsModal.tsx # Settings dialog
│   │   │   └── FileSelectionModal.tsx # File selection
│   │   ├── terminal/           # Terminal components
│   │   │   ├── ShellView.tsx   # Shell interface
│   │   │   └── TerminalComponent.tsx # Terminal wrapper
│   │   └── common/             # Common components
│   │       └── Modal.tsx       # Base modal component
│   ├── pages/                  # Page components
│   │   └── DiagramRenderer.tsx # Standalone diagram renderer page
│   ├── services/               # API and business logic
│   │   └── api.ts              # API client configuration
│   ├── themes/                 # Theme management
│   │   ├── ThemeProvider.tsx   # Theme context provider
│   │   ├── ThemeContext.tsx    # Theme context
│   │   ├── useTheme.ts         # Theme hook
│   │   └── index.ts            # Theme exports
│   ├── types/                  # TypeScript type definitions
│   │   └── index.ts            # Type exports
│   ├── utils/                  # Utility functions
│   │   ├── c4ToD2.ts           # C4 to D2 converter
│   │   ├── mermaidUtils.ts     # Mermaid utilities
│   │   └── index.ts            # Utility exports
│   ├── App.css                 # Application styles
│   ├── App.tsx                 # Root application component
│   ├── index.css               # Global styles
│   ├── main.tsx                # Application entry point
│   └── vite-env.d.ts           # Vite type definitions
├── index.html                  # HTML template
├── package.json                # Dependencies and scripts
├── tsconfig.json               # TypeScript configuration
├── tsconfig.node.json          # Node.js TypeScript config
├── vite.config.ts              # Vite configuration
├── tailwind.config.js          # Tailwind CSS configuration
├── postcss.config.js           # PostCSS configuration
└── eslint.config.js            # ESLint configuration
```

## 🚀 Getting Started

### Prerequisites
- Node.js 16+ and npm
- Backend server running on port 8003

### Installation

1. **Install dependencies**:
   ```bash
   npm install
   ```

2. **Configure environment**:
   ```bash
   # Copy environment template
   cp .envTemplate .env
   
   # Edit .env with your configuration
   # VITE_API_BASE_URL=http://localhost:8003/api/v1
   ```

3. **Start development server**:
   ```bash
   npm run dev
   ```

4. **Access the application**:
   - Frontend: http://localhost:5173
   - Backend API: http://localhost:8003/docs

### Available Scripts

| Script | Description |
|--------|-------------|
| `npm run dev` | Start development server with hot reload |
| `npm run build` | Build for production |
| `npm run preview` | Preview production build locally |
| `npm run deploy` | Build and deploy to backend |
| `npm run build:deploy` | Build and deploy in one command |
| `npm run lint` | Run ESLint |
| `npm run type-check` | Run TypeScript type checking |

## 🔧 Configuration

### Environment Variables

Create a `.env` file in the frontend root:

```bash
# API Configuration
VITE_API_BASE_URL=http://localhost:8003/api/v1

# Application Settings
VITE_APP_TITLE="Whysper Web2"
VITE_APP_VERSION="2.0.0"

# Feature Flags
VITE_ENABLE_MCP=true
VITE_ENABLE_DIAGRAMS=true
VITE_ENABLE_FILE_OPERATIONS=true

# Development Settings
VITE_DEBUG=false
VITE_LOG_LEVEL=info
```

### Backend Integration

The frontend communicates with the backend through REST API:

```typescript
// API configuration in src/services/api.ts
const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || '/api/v1';

// Example API call
const response = await axios.post(`${API_BASE_URL}/chat/`, {
  message: userMessage,
  conversationId: currentConversationId,
  contextFiles: selectedFiles
});
```

## 🎨 Diagram Support

### Mermaid Diagrams
- Automatic detection in AI responses
- 21+ diagram types supported
- Interactive features (zoom, pan, export)
- Code preview and copy functionality

### D2 Diagrams
- Modern diagram scripting language
- Client-side rendering
- Custom shapes and styles
- Architecture-focused diagrams

### C4 Architecture Diagrams
- Automatic translation to D2
- Professional architectural visualizations
- Support for boundaries and nesting
- Technology stack annotations

## 🧩 Component Architecture

### Chat System
- **ChatView**: Main chat interface with message history
- **InputPanel**: Rich text input with file attachment support
- **Diagram Components**: Specialized renderers for different diagram types

### File Management
- **FileEditorView**: Integrated code editor with syntax highlighting
- **MonacoEditor**: VS Code-compatible editor with IntelliSense
- **FileSelectionModal**: File browser with search and filtering

### Theme System
- **ThemeProvider**: Global theme context
- **ThemeContext**: Theme state and methods
- **useTheme**: Hook for theme consumption

## 🔌 API Integration

### Authentication
- API key management through settings
- Secure storage of credentials
- Automatic token refresh

### Real-time Features
- WebSocket connection for live updates
- Streaming responses with chunked transfer
- Progress indicators for long operations

### Error Handling
- Global error boundary
- User-friendly error messages
- Automatic retry with exponential backoff

## 📱 Responsive Design

### Breakpoints
- Mobile: < 768px
- Tablet: 768px - 1024px
- Desktop: > 1024px

### Adaptive UI
- Collapsible sidebars on mobile
- Touch-friendly controls
- Optimized layouts for different screen sizes

## 🎯 Performance Optimization

### Code Splitting
- Lazy loading of components
- Route-based code splitting
- Dynamic imports for heavy dependencies

### Caching Strategy
- API response caching
- Component memoization
- Static asset optimization

### Bundle Optimization
- Tree shaking for unused code
- Minification and compression
- Source maps for debugging

## 🧪 Testing

### Unit Testing
```bash
# Run unit tests
npm run test

# Run with coverage
npm run test:coverage
```

### Integration Testing
```bash
# Run integration tests
npm run test:integration

# Run E2E tests
npm run test:e2e
```

## 📚 Development Guidelines

### Code Style
- TypeScript strict mode enabled
- ESLint with React rules
- Prettier for code formatting
- Conventional commits for version control

### Component Patterns
- Functional components with hooks
- Props interfaces for type safety
- Custom hooks for reusable logic
- Context API for state management

### Best Practices
- Accessibility (WCAG 2.1) compliance
- Performance monitoring
- Error boundary implementation
- Progressive enhancement

## 🔍 Debugging

### Browser DevTools
- React Developer Tools
- Redux DevTools (if applicable)
- Network tab for API debugging
- Console for error tracking

### VS Code Integration
- TypeScript debugging
- Breakpoint support
- Hot module replacement
- Intellisense for imports

## 🚀 Deployment

### Production Build
```bash
# Build for production
npm run build

# Deploy to backend
npm run deploy
```

### Static Hosting
The built frontend can be deployed to any static hosting service:
- Netlify
- Vercel
- GitHub Pages
- AWS S3 + CloudFront

### Docker Deployment
```dockerfile
FROM node:18-alpine as builder
WORKDIR /app
COPY package*.json ./
RUN npm ci
COPY . .
RUN npm run build

FROM nginx:alpine
COPY --from=builder /app/dist /usr/share/nginx/html
EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Submit a pull request

## 📄 License

This project is part of Whysper Web2 and provided as-is for educational and development purposes.

## 🔗 Related Projects

- [Backend API](../backend/README.md)
- [MCP Server](../backend/mcp_server/README.md)
- [Deployment Guide](../DEPLOYMENT.md)
- [API Documentation](../API_DOCUMENTATION.md)

---

**Last Updated**: 2025-01-13  
**Version**: 2.0.0  
**Maintainer**: Whysper Development Team
