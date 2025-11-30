# Whysper Web2 - Full Stack AI Chat Application

A modern, full-stack web application that provides AI-powered chat functionality with code analysis, file management, and multi-provider AI integration.

## 🎉 Recent Updates (November 29, 2025)

**Critical Bug Fixes & Performance Enhancements:**

- ✅ Fixed diagram type selection not proceeding to code generation
- ✅ Fixed SVG not displaying in Preview tab
- ✅ Made provider system async to support long-running LLM operations (30-90s) without blocking
- ✅ Added real-time progress updates during diagram rendering

📖 **See:** [Bug Fixes Documentation](DOCUMENTATION/3-DIAGRAM_SYSTEM/DIAGRAM_WIZARD/BUGFIXES_2025_11_29.md)

## 📚 Documentation

For detailed documentation, please refer to the `DOCUMENTATION/` directory:
-   [Getting Started](DOCUMENTATION/1-GETTING_STARTED/)
-   [Architecture](DOCUMENTATION/2-ARCHITECTURE/)
-   [Diagram System](DOCUMENTATION/3-DIAGRAM_SYSTEM/)
-   [Frontend Guide](DOCUMENTATION/4-FRONTEND/)
-   [Backend Guide](DOCUMENTATION/5-BACKEND/)
-   [API Reference](DOCUMENTATION/6-API/)

## 🚀 Installation & Setup

### Prerequisites
-   **Python 3.8+**
-   **Node.js 16+** and **npm**

### 1. Backend Setup (FastAPI)

1.  **Create a Virtual Environment**:
    It is recommended to use a virtual environment to isolate dependencies.
    ```bash
    # Windows
    python -m venv venv
    venv\Scripts\activate

    # Linux/macOS
    python3 -m venv venv
    source venv/bin/activate
    ```

2.  **Install Dependencies**:
    With the virtual environment activated, install the requirements from the **project root**:
    ```bash
    pip install -r requirements.txt
    ```

3.  **Configure Environment**:
    -   Navigate to the `backend` directory:
        ```bash
        cd backend
        ```
    -   Create a `.env` file by copying the template from the root:
        ```bash
        # Windows
        copy ..\.envTemplate .env
        # Linux/macOS
        cp ../.envTemplate .env
        ```
    -   **Edit `.env`**: Open the file and set your `API_KEY` (e.g., OpenRouter key).
    -   *Note*: The `.env` file **must** be located in the `backend/` directory.

4.  **Run the Backend**:
    ```bash
    # Ensure you are in the 'backend' directory
    python main.py
    ```
    The backend will start at **http://localhost:8003**.

### 2. Frontend Setup (React + Vite)
The frontend requires Node.js dependencies.

1.  **Install Dependencies**:
    Open a new terminal (keep the backend running in the first one), navigate to the `frontend` directory, and install:
    ```bash
    cd frontend
    npm install
    ```

2.  **Run the Frontend**:
    ```bash
    npm run dev
    ```
    The frontend will start at **http://localhost:5173**.

---

## 💻 Frontend Details

The frontend is a React application built with TypeScript and Vite, located in the `frontend/` directory.

### Configuration
-   **Default Connection**: The frontend is pre-configured to connect to the backend at `http://localhost:8003`.
-   **Custom Port**: To connect to a different backend port, create a `.env` file in `frontend/` (copy from `frontend/.envTemplate`) and update `VITE_BACKEND_PORT`.

### Available Commands
| Command | Description |
|---------|-------------|
| `npm run dev` | Start development server with hot-reload |
| `npm run build` | Build the application for production |
| `npm run lint` | Run ESLint to check code quality |
| `npm test` | Run Vitest tests |

---

## ⚙️ Backend Details

The backend is a FastAPI application handling AI logic, file management, and diagram generation, located in the `backend/` directory.

### Configuration (`backend/.env`)
The application requires a `.env` file in the `backend/` directory. Key settings include:
-   **API_KEY**: Your AI Provider API Key (Required).
-   **PROVIDER**: `openrouter` (default) or `custom`.
-   **PORT**: `8003` (default).
-   **DEFAULT_MODEL**: Model to use (e.g., `google/gemini-2.5-flash-preview-09-2025`).

### Available Commands
| Command | Description |
|---------|-------------|
| `python main.py` | Start the server (Development mode) |
| `pytest` | Run the test suite |
| `ruff check .` | Run linting (if installed) |

---

## 📱 Access the Application

Once both servers are running, access the application at:
-   **Frontend UI**: [http://localhost:5173](http://localhost:5173)
-   **Backend API**: [http://localhost:8003/api/v1](http://localhost:8003/api/v1)
-   **API Documentation**: [http://localhost:8003/docs](http://localhost:8003/docs) (Swagger UI)

## 🏗️ Architecture

```
MyApp/
├── backend/                 # FastAPI backend server
│   ├── app/                 # Application code
│   │   ├── api/v1/          # API version 1 endpoints
│   │   ├── core/            # Core configuration
│   │   ├── services/        # Business logic services
│   │   └── utils/           # Utility functions
│   ├── diagrams/            # Diagram provider system (Modular)
│   ├── mvp_diagram_generator/ # Legacy diagram generation logic
│   ├── providers/           # AI providers (OpenRouter, etc.)
│   ├── static/              # Built frontend files
│   └── main.py              # Simple entry point
├── frontend/                # React frontend
│   ├── src/
│   │   ├── components/      # UI components (DiagramWizard, etc.)
│   │   ├── services/        # API clients and services
│   │   └── hooks/           # Custom React hooks
├── setup/                   # Installation scripts (Legacy)
├── requirements.txt         # Python dependencies
└── README.md                # This file
```

### Diagram Generation System (DiagramWizard)

The diagram generation system is a core feature of Whysper, enabling users to generate architectural diagrams from natural language descriptions. It uses a sophisticated multi-stage pipeline:

1.  **Frontend (React + TypeScript)**:
    -   **DiagramWizard Component**: Orchestrates the user flow (Analysis -> Clarification -> Generation -> Rendering).
    -   **useDiagramSession Hook**: Manages the session lifecycle, SSE connection, and state transitions.
    -   **DiagramProviderService**: Handles communication with the backend provider system for validation and rendering.

2.  **Backend (FastAPI + Python)**:
    -   **DiagramFactoryService**: Manages the diagram generation workflow using LangGraph state machines.
    -   **LangGraph Workflow**:
        -   `analyze_request`: Deconstructs user prompt into key components.
        -   `clarify_prompt`: Generates clarification questions if information is ambiguous.
        -   `generate_json`: Creates a structured JSON representation of the system.
        -   `determine_diagram_type`: Selects the best diagram type (Mermaid, D2, PlantUML, C4).
        -   `generate_code`: Uses LLM to generate diagram code.
        -   `validate_code`: Validates syntax using specific validators.
        -   `render_diagram`: Renders the final SVG/PNG.
    -   **Provider System** (`backend/diagrams/`): Modular system for supporting different diagram tools (Mermaid, D2, etc.) with uniform interfaces for rendering and validation.

### AI Integration

Whysper uses a flexible AI provider system:
-   **BaseAIProvider**: Abstract base class for all AI providers.
-   **OpenRouter Provider**: Default implementation connecting to OpenRouter for access to GPT-4, Claude 3, Gemini, etc.
-   **Custom Provider**: Allows connection to any OpenAI-compatible endpoint.

### Real-time Updates

Communication between backend and frontend for long-running tasks (like diagram generation) is handled via **Server-Sent Events (SSE)**. This ensures the UI remains responsive and provides real-time feedback on the AI's progress.

## ✨ Features

### Frontend (React + TypeScript)
- 🎨 Modern UI with Ant Design components
- 🌓 Light/Dark theme support
- 📱 Responsive design
- 🗂️ Multi-tab conversation management
- 📁 File context selection
- 🎯 Quick command templates
- 🔧 Settings management

### Backend (FastAPI + Python)
- 🤖 Multi-provider AI integration (OpenRouter, OpenAI, Anthropic)
- 📊 Code extraction and analysis
- 🎨 LLM-powered diagram generation with 7 providers (Mermaid, D2, PlantUML, C4, Kroki)
- 📂 File system integration
- 🔄 Real-time chat processing with Server-Sent Events (SSE)
- 📝 Conversation persistence
- 🔐 API key management
- 🎯 Architecture diagram generation with agent system prompts

### Diagram Wizard (New!)
- 🧙‍♂️ Interactive, conversational AI for diagram creation
- 🎯 Intelligent clarification loop to ensure requirements are met
- 🔄 Multi-step workflow: Analysis -> Clarification -> Generation -> Rendering
- 📊 Real-time clarity scoring and architectural validation
- 🖼️ Supports Mermaid, D2, PlantUML, and C4 models
- 💾 Session persistence and export capabilities

## 🔧 AI Provider Configuration

Whysper supports multiple AI providers through a modular provider system.

### Available Providers

1. **OpenRouter Provider** (`openrouter`) - **Default & Recommended**
   - Unified API for multiple AI models.
   - Get API key: https://openrouter.ai/keys

2. **Custom Provider** (`custom`)
   - Configurable for any OpenAI-compatible API.

### Switching Providers

Update `backend/.env`:
```bash
# Set the provider name (openrouter or custom)
PROVIDER="openrouter"

# Provider-specific API key
API_KEY="your-provider-api-key-here"
```

## 🚀 Development (VS Code)

The project includes comprehensive VS Code configuration (`.vscode/launch.json`) for one-click development.

1.  **Launch Configurations**:
    -   **Integrated: Backend + Frontend Server**: Automatically builds and deploys frontend, then starts integrated server.
    -   **Development: Backend + Frontend Separate**: Runs backend and frontend on separate ports.

2.  **Quick Start**:
    -   Press `F5` and select **"🚀 Integrated: Backend + Frontend Server"**.

*Note*: Ensure your `.env` file is correctly configured in the `backend/` directory.

## 📚 API Endpoints

-   `GET /api/v1/` - API health check
-   `POST /api/v1/chat/` - Send chat messages
-   `GET /api/v1/files/` - Browse files
-   `GET /api/v1/settings/` - Get application settings
-   `GET /docs` - Interactive API documentation

## 🛠️ Troubleshooting

### Common Issues

1.  **Port 8003 in use**: Change the port in `backend/.env` or `backend/app/core/config.py`.
2.  **API key errors**: Set your AI provider API key in `backend/.env`.
3.  **Frontend not connecting**: Ensure `backend` is running and `VITE_BACKEND_PORT` in `frontend/.env` matches the backend port.

## 📄 License

This project is provided as-is for educational and development purposes.

## Change History

