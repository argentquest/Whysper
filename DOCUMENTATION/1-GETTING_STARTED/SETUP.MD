# Whysper Application Setup Guide for Windows 11

This guide provides detailed instructions for setting up and running the Whysper application on a fresh installation of Windows 11.

## 1. Prerequisites

Before you begin, you need to install the following software:

### Git

Git is a version control system used to manage and clone the application repository.

- **Download Git:** [https://git-scm.com/download/win](https://git-scm.com/download/win)
- **Installation:** Run the downloaded installer and follow the on-screen instructions. It is recommended to use the default settings.

### Python

Python is required to run the backend server.

- **Download Python:** [https://www.python.org/downloads/windows/](https://www.python.org/downloads/windows/)
- **Installation:**
    1.  Run the downloaded installer.
    2.  **Important:** On the first screen of the installer, make sure to check the box that says **"Add Python to PATH"**.
    3.  Click on **"Install Now"** and follow the on-screen instructions.

### Node.js and npm

Node.js and npm (Node Package Manager) are required to run the frontend application.

- **Download Node.js:** [https://nodejs.org/en/download/](https://nodejs.org/en/download/)
- **Installation:** Run the downloaded installer and follow the on-screen instructions. It is recommended to use the default settings. npm is included with the Node.js installation.

## 2. Clone the Repository

Once the prerequisites are installed, you can clone the application repository.

1.  Open a new **Command Prompt** or **PowerShell** window.
2.  Clone the repository to a directory of your choice:
    ```bash
    git clone <repository_url>
    ```
    (Replace `<repository_url>` with the actual URL of the repository.)
3.  Navigate into the cloned repository's directory. If you cloned the repository with the default name, you can use:
    ```bash
    cd Whysper
    ```

## 3. Backend Setup

### Create and Activate Virtual Environment

A virtual environment is used to isolate the Python dependencies for the application.

1.  Create a virtual environment named `.venv`:
    ```bash
    python -m venv .venv
    ```
2.  Activate the virtual environment:
    ```bash
    .venv\Scripts\activate.bat
    ```
    Your command prompt should now be prefixed with `(.venv)`.

### Install Python Dependencies

1.  Navigate to the `backend` directory:
    ```bash
    cd backend
    ```
2.  Install the required Python packages using pip:
    ```bash
    pip install -r requirements.txt
    ```

### Configure Environment Variables

1.  In the `backend` directory, you'll find a `.env` file. If it doesn't exist, copy the `.envTemplate` file from the project root:
    ```bash
    copy ..\\.envTemplate .env
    ```
2.  Open the `.env` file in a text editor and configure the following **required** settings:

    **Required Configuration:**
    ```bash
    # Access Key for the application
    ACCESS_KEY="your_secret_key"

    # API Key - REQUIRED for all AI operations
    # Get your OpenRouter key from: https://openrouter.ai/keys
    API_KEY="your_api_key_here"

    # AI Provider (openrouter recommended)
    PROVIDER="openrouter"

    # Default AI model to use
    DEFAULT_MODEL="google/gemini-2.5-flash-preview-09-2025"

    # Available models list (comma-separated)
    MODELS="x-ai/grok-code-fast-1,google/gemini-2.5-flash-preview-09-2025,deepseek/deepseek-coder-v2,anthropic/claude-3.5-haiku"
    ```

    **Optional Configuration (can be left as defaults):**
    ```bash
    # Path to the codebase (use "." for current directory)
    CODE_PATH="."

    # Backend and Frontend URLs
    API_PORT="8003"
    FASTAPI_URL="http://localhost:8003"
    FRONTEND_URL="http://localhost:5173"

    # Path Configuration (leave empty for auto-detection)
    STATIC_DIR=""          # Auto-detects backend/static
    PROMPTS_DIR=""         # Auto-detects project root
    D2_EXECUTABLE_PATH=""  # Auto-detects bin/d2.exe
    ```

    **Note:**
    - Replace `your_api_key_here` with your actual API key from OpenRouter
    - Replace `your_secret_key` with a secure access key of your choice
    - For a complete list of all configuration options, see `.envTemplate` in the project root

### Run the Backend Server

1.  From the `backend` directory, run the following command to start the backend server:
    ```bash
    uvicorn app.main:app --host 0.0.0.0 --port 8003 --reload
    ```
2.  The backend server should now be running on `http://localhost:8003`.

## 4. Frontend Setup

### Install Node.js Dependencies

1.  Open a **new** Command Prompt or PowerShell window.
2.  Navigate to the `frontend` directory from the project root:
    ```bash
    cd frontend
    ```
    Or use the full path:
    ```bash
    cd C:\Code2025\Whysper\frontend
    ```
3.  Install the required Node.js packages using npm:
    ```bash
    npm install
    ```

### Run the Frontend Development Server

1.  From the `frontend` directory, run the following command to start the frontend development server:
    ```bash
    npm run dev
    ```
2.  The frontend development server should now be running on `http://localhost:5173` (or another port if 5173 is in use).

## 5. Running the Application

Once both the backend and frontend servers are running, you can access the application in your web browser:

1.  Open your web browser (e.g., Chrome, Firefox, Edge).
2.  Navigate to the frontend URL, which is typically `http://localhost:5173`.

## 6. Project Structure

Understanding the project structure will help you navigate and configure the application:

```
C:\Code2025\Whysper\          (Project Root)
├── backend\                  (Backend Python/FastAPI application)
│   ├── app\                  (Main application code)
│   ├── static\               (Static files served by FastAPI)
│   ├── .env                  (Backend configuration - create from .envTemplate)
│   └── requirements.txt      (Python dependencies)
├── frontend\                 (Frontend React/TypeScript application)
│   ├── src\                  (Frontend source code)
│   ├── package.json          (Node.js dependencies)
│   └── .env                  (Frontend configuration)
├── bin\                      (Binary executables)
│   └── d2.exe                (D2 diagram renderer for Windows)
├── prompts\                  (AI prompt templates)
│   └── coding\
│       └── agent\            (Agent-specific prompts)
├── .envTemplate              (Template for environment configuration)
└── PATH_CONFIGURATION.md     (Guide for deployment path configuration)
```

**Key Files:**
- **`.envTemplate`**: Template with all available configuration options
- **`backend/.env`**: Backend-specific configuration (copy from .envTemplate)
- **`frontend/.env`**: Frontend-specific configuration
- **`PATH_CONFIGURATION.md`**: Detailed guide for configuring paths in production

## 7. Running the Application with PowerShell Script

A PowerShell script is provided to automate the process of starting both the backend and frontend servers.

1.  **Navigate to the root directory of the project** in your terminal or file explorer:
    ```bash
    cd C:\Code2025\Whysper
    ```
2.  **Run the script:**
    *   **From File Explorer:** Right-click on the `Start-App.ps1` file and select "Run with PowerShell".
    *   **From a PowerShell window:**
        ```powershell
        .\Start-App.ps1
        ```
    **Note:** If you get an error about running scripts being disabled on your system, you may need to change the execution policy. You can do this by running the following command in a PowerShell window with administrator privileges:
    ```powershell
    Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
    ```
    Then, try running the script again.

3.  The script will open two new PowerShell windows, one for the backend and one for the frontend. The application will be accessible at `http://localhost:5173`.

## 8. Troubleshooting

### Backend Issues

**Problem:** Backend fails to start with "D2 CLI not found" error
- **Solution:** The D2 executable is included in `bin/d2.exe`. If auto-detection fails, set the path explicitly in `backend/.env`:
  ```bash
  D2_EXECUTABLE_PATH="bin/d2.exe"
  ```

**Problem:** Backend can't find prompt files
- **Solution:** Ensure you're running the backend from the project root directory, or set the prompts directory in `backend/.env`:
  ```bash
  PROMPTS_DIR="C:/Code2025/Whysper"
  ```

**Problem:** Static files not loading
- **Solution:** The static directory should auto-detect. If it fails, set it explicitly in `backend/.env`:
  ```bash
  STATIC_DIR="backend/static"
  ```

### Frontend Issues

**Problem:** Frontend can't connect to backend
- **Solution:** Verify the backend is running on port 8003 and update `frontend/.env` if needed:
  ```bash
  VITE_API_URL=http://localhost:8003
  ```

**Problem:** Port 5173 is already in use
- **Solution:** Vite will automatically use the next available port (5174, 5175, etc.). Check the terminal output for the actual port.

### API Key Issues

**Problem:** "API key not found" or authentication errors
- **Solution:**
  1. Verify your API key is correctly set in `backend/.env`
  2. Make sure there are no extra spaces or quotes
  3. Restart the backend server after changing the `.env` file

For more configuration options and deployment scenarios, see:
- **`.envTemplate`** - Complete list of all configuration options
- **`PATH_CONFIGURATION.md`** - Guide for production deployment with custom paths
