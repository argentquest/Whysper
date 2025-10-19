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

1.  In the `backend` directory, create a new file named `.env`.
2.  Open the `.env` file in a text editor and add the following content:
    ```
    # .env file for Whysper backend

    # AI Provider Configuration
    # You can use 'openrouter', 'anthropic', or 'openai'
    PROVIDER=openrouter

    # API Key for the selected provider
    API_KEY=your_api_key_here

    # Default AI model to use
    DEFAULT_MODEL=google/gemini-2.5-flash-preview-09-2025

    # Path to the codebase to be analyzed. Replace this with the full path to the project's root directory.
    CODE_PATH=.
    ```
    **Note:** Replace `your_api_key_here` with your actual API key from the selected provider.

### Run the Backend Server

1.  From the `backend` directory, run the following command to start the backend server:
    ```bash
    uvicorn app.main:app --host 0.0.0.0 --port 8003 --reload
    ```
2.  The backend server should now be running on `http://localhost:8003`.

## 4. Frontend Setup

### Install Node.js Dependencies

1.  Open a **new** Command Prompt or PowerShell window.
2.  Navigate to the `frontend` directory:
    ```bash
    cd C:\Whysper\frontend
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

Congratulations! The Whysper application should now be up and running on your new Windows 11 server.

## 6. Running the Application with PowerShell Script

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
