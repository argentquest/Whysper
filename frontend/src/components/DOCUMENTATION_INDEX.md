# Frontend Documentation Index & Navigation

## Overview

This comprehensive documentation system provides detailed JSDoc comments, type definitions, and inline documentation for all frontend components in the Whysper application. The documentation follows established standards and provides clear guidance for developers working with the codebase.

## Documentation Categories

### 🏗️ **Architecture Documentation**
- **[ARCHITECTURE.md](architectureGenStudio/ARCHITECTURE.md)** - Detailed technical documentation covering component hierarchy, custom hooks, data flow, state management, and API integration
- **[ARCHITECTURE_DIAGRAM.md](architectureGenStudio/ARCHITECTURE_DIAGRAM.md)** - Mermaid diagrams showing component relationships, data flow sequences, and system architecture
- **[ARCHITECTURE_SUMMARY.md](architectureGenStudio/ARCHITECTURE_SUMMARY.md)** - ASCII visual diagrams providing quick reference for component layout and technology stack

### 📋 **Core Application Files**
- **[App.tsx](App.tsx)** - Main application component with routing, layout, theme management, and conversation state
- **[DOCUMENTATION_GUIDE.md](DOCUMENTATION_GUIDE.md)** - Comprehensive documentation standards and JSDoc templates

### 🔧 **Services & API**
- **[api.ts](../services/api.ts)** - REST API client with comprehensive request/response type documentation
- **[diagramProviderService.ts](../services/diagramProviderService.ts)** - Diagram provider management with validation and rendering services

### 🎨 **ArchitectureGenStudio Components**
#### Main Layout Components
- **[Header.tsx](architectureGenStudio/Header.tsx)** - Navigation header with logo, controls, and user interface elements
- **[LeftColumn.tsx](architectureGenStudio/LeftColumn.tsx)** - Left sidebar with prompt management and context selection
- **[CenterColumn.tsx](architectureGenStudio/CenterColumn.tsx)** - Central area for diagram generation and display
- **[RightColumn.tsx](architectureGenStudio/RightColumn.tsx)** - Right panel for generated code display and management
- **[Footer.tsx](architectureGenStudio/Footer.tsx)** - Application footer with status information and controls

#### Core Components
- **[TabManager.tsx](architectureGenStudio/TabManager.tsx)** - Tab management system for multiple conversations and code display
- **[ContextManager.tsx](architectureGenStudio/ContextManager.tsx)** - File selection and context management interface

### 🛠️ **Utility Functions**
- **[mermaidUtils.ts](../utils/mermaidUtils.ts)** - Mermaid diagram utilities with syntax validation and processing functions
- **[c4ToD2.ts](../utils/c4ToD2.ts)** - C4 model to D2 diagram conversion utilities

### 🎨 **Theme & Layout**
- **[ThemeProvider.tsx](themes/ThemeProvider.tsx)** - Theme management with light/dark mode support and custom CSS variables
- **[ThemePickerModal.tsx](modals/ThemePickerModal.tsx)** - Theme selection interface with real-time preview

### 📱 **Modal Components**
#### Settings & Configuration
- **[SettingsModal.tsx](modals/SettingsModal.tsx)** - Comprehensive settings modal with API configuration, model parameters, UI preferences, file system settings, system prompts, server configuration, and advanced options
- **[SystemMessageModal.tsx](modals/SystemMessageModal.tsx)** - System prompt editing interface with file management
- **[NewFileModal.tsx](modals/NewFileModal.tsx)** - New file creation interface with directory selection

#### File Management
- **[ContextModal.tsx](modals/ContextModal.tsx)** - Multi-view file selection modal with list, tree, and uploaded file views
- **[FileTreeModal.tsx](modals/FileTreeModal.tsx)** - Hierarchical file tree selection with checkbox support and bulk operations
- **[FileSelectionModal.tsx](modals/FileSelectionModal.tsx)** - Simple file selection interface
- **[CodeFragmentsModal.tsx](modals/CodeFragmentsModal.tsx)** - Code extraction and management interface

#### Information & Help
- **[AboutModal.tsx](modals/AboutModal.tsx)** - Application information modal with features, technology stack, and navigation links
- **[HelpModal.tsx](modals/HelpModal.tsx)** - Quick start guide with markdown content loading

#### Testing & Debugging
- **[D2TesterModal.tsx](modals/D2TesterModal.tsx)** - D2 diagram testing interface
- **[MermaidTesterModal.tsx](modals/MermaidTesterModal.tsx)** - Mermaid diagram testing interface

## Documentation Standards

### JSDoc Template Structure
```typescript
/**
 * Component/Function Description
 * 
 * Detailed explanation of purpose, functionality, and usage
 * 
 * @param {Type} paramName - Parameter description
 * @returns {Type} Return description
 * @example
 * // Usage example
 * const result = functionName(param);
 */
```

### Props Interface Documentation
```typescript
/**
 * Props interface for the ComponentName component
 * 
 * @interface ComponentNameProps
 * @property {Type} propName - Property description
 * @property {Type} [optionalProp] - Optional property description
 */
```

### Method Documentation Standards
- **Async Functions**: Include `@async` tag and describe promise resolution
- **Event Handlers**: Document event parameters and side effects
- **Complex Logic**: Break down complex algorithms with step-by-step comments
- **Error Handling**: Document error scenarios and fallback behavior

## Key Concepts & Patterns

### 🎯 **State Management Pattern**
The application uses a centralized state management approach with React hooks:
- `useArchitectureStudioState` - Manages diagram generation state
- `useAPIClient` - Handles API communication and request state
- `useSSE` - Manages Server-Sent Events for real-time updates

### 🔄 **Data Flow Architecture**
1. **User Interaction** → Component Event Handlers
2. **State Updates** → Custom Hooks
3. **API Calls** → Service Layer
4. **Response Processing** → State Management
5. **UI Updates** → React Re-rendering

### 🎨 **Theme System**
- Global theme provider with CSS custom properties
- Ant Design theme integration
- Dynamic theme switching with persistence
- Dark/light mode support across all components

### 🔧 **Service Layer**
- **ApiService**: Centralized API communication
- **DiagramProviderService**: Diagram rendering and validation
- **Authentication**: Token management and security
- **Error Handling**: Global error boundaries and user feedback

## Usage Examples

### Working with Components
```typescript
// Importing with proper TypeScript types
import { SettingsModal, type SettingsModalProps } from './modals/SettingsModal';

// Using the component with proper props
const MyComponent = () => {
  const [settingsOpen, setSettingsOpen] = useState(false);
  
  const handleSettingsSave = (settings: AppSettings) => {
    console.log('Settings saved:', settings);
  };
  
  return (
    <SettingsModal
      open={settingsOpen}
      onCancel={() => setSettingsOpen(false)}
      onSave={handleSettingsSave}
    />
  );
};
```

### Working with Services
```typescript
// Using API service with proper error handling
const fetchData = async () => {
  try {
    const response = await ApiService.getFiles();
    if (response.success) {
      setFiles(response.data);
    } else {
      message.error(response.error || 'Failed to fetch files');
    }
  } catch (error) {
    console.error('API Error:', error);
    message.error('Network error occurred');
  }
};
```

### Working with Hooks
```typescript
// Using custom hooks for state management
const MyComponent = () => {
  const { diagram, isGenerating, generateDiagram } = useArchitectureStudioState();
  const { theme, setTheme } = useTheme();
  
  const handleGenerate = async () => {
    await generateDiagram('mermaid', 'graph TD; A-->B;');
  };
  
  return (
    <div className={theme === 'dark' ? 'dark' : 'light'}>
      {/* Component JSX */}
    </div>
  );
};
```

## Development Best Practices

### ✅ **Do's**
- Always document props interfaces with JSDoc
- Include usage examples for complex components
- Document async functions and their promise behavior
- Use TypeScript types for all props and state
- Follow the established naming conventions
- Include error handling documentation

### ❌ **Don'ts**
- Don't leave complex logic undocumented
- Don't skip documenting event handler parameters
- Don't omit error scenarios and edge cases
- Don't use `any` types without proper documentation
- Don't ignore accessibility considerations

## Quick Reference

### Common Import Patterns
```typescript
// Components
import { ComponentName } from './path/to/component';

// Services
import ApiService from '../services/api';

// Hooks
import { useCustomHook } from '../hooks/useCustomHook';

// Types
import type { ComponentProps, ServiceResponse } from '../types';
```

### Theme Classes
```css
/* Light theme classes */
.light {
  --bg-primary: #ffffff;
  --text-primary: #333333;
}

/* Dark theme classes */
.dark {
  --bg-primary: #1a1a1a;
  --text-primary: #ffffff;
}
```

### Modal Pattern
```typescript
// Standard modal structure with proper documentation
const MyModal: React.FC<MyModalProps> = ({ open, onCancel, onSave }) => {
  // State management
  const [loading, setLoading] = useState(false);
  
  // Event handlers with proper documentation
  const handleSave = async () => {
    setLoading(true);
    try {
      // Logic here
      onSave(data);
      onCancel();
    } finally {
      setLoading(false);
    }
  };
  
  return (
    <Modal
      title="Modal Title"
      open={open}
      onCancel={onCancel}
      onOk={handleSave}
      confirmLoading={loading}
    >
      {/* Modal content */}
    </Modal>
  );
};
```

## Testing & Validation

### Running Documentation Validation
```bash
# TypeScript type checking
npm run type-check

# Linting with documentation rules
npm run lint

# Running tests with coverage
npm run test:coverage
```

### Documentation Coverage
- **Components**: 100% JSDoc coverage for all public APIs
- **Services**: Complete API documentation with request/response types
- **Hooks**: Full documentation of state management and side effects
- **Utilities**: Comprehensive function documentation with examples

## Contributing

When adding new components or modifying existing ones:

1. **Follow the established documentation standards** from `DOCUMENTATION_GUIDE.md`
2. **Update this index** with new documentation entries
3. **Include TypeScript types** for all props and interfaces
4. **Add usage examples** for complex functionality
5. **Document error scenarios** and edge cases
6. **Test documentation** builds and validation

---

## Navigation Links

- [Architecture Overview](architectureGenStudio/ARCHITECTURE.md)
- [Documentation Standards](DOCUMENTATION_GUIDE.md)
- [API Documentation](../services/api.ts)
- [Component Library](architectureGenStudio/)
- [Modal Components](modals/)
- [Utility Functions](../utils/)

*Last updated: 2025-11-06*
*Maintained by: Frontend Development Team*