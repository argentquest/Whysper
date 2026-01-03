# Backend Test Rebuild Report (2026)

## Overview
This document details the complete rebuild of the backend test suite, ensuring full coverage across all major components. The new suite uses `pytest` and is located in `backend/tests_2026/`.

## Structure
- **`backend/tests_2026/unit/`**: Fast, isolated unit tests using `unittest.mock`.
- **`backend/tests_2026/integration/`**: Integration tests that perform real external calls (e.g., OpenRouter).
- **`backend/tests_2026/conftest.py`**: Global test configuration, environment loading, and markers.
- **`backend/.env.test`**: Configuration for integration tests (API keys, models).

## Test Coverage

### 1. Common Utilities (`unit/test_common.py`)
- **Components:** `BaseAIProvider` (Abstract Logic), `common.logger`.
- **Verify:** Initialization, header preparation, error handling, and logging.

### 2. AI Providers (`unit/test_openrouter_provider.py`)
- **Components:** `OpenRouterProvider`.
- **Verify:** Configuration parsing, request payload construction, response extraction (including Grok reasoning), and error mapping.

### 3. Diagram System (`unit/test_diagram_system.py`)
- **Components:** `ProviderRegistry`, `D2V1Provider`, `D2Renderer`.
- **Verify:** Provider auto-discovery, registration logic, and D2 rendering flow (mocking subprocess and validation).

### 4. Service Layer (`unit/test_services.py`)
- **Components:** `DiagramFactoryService`, `AsyncImageService`.
- **Verify:** Service orchestration, provider selection, and image generation logic.

### 5. Diagram Wizard (`unit/test_diagram_wizard_nodes.py`)
- **Components:** `llm_helpers` (used by nodes).
- **Verify:** LLM call wrapping and JSON parsing from LLM responses (handling Markdown blocks).

### 6. Form Processor (`unit/test_forms.py`)
- **Components:** `FormService`, `FormProcessor` logic.
- **Verify:** Form publishing, submission processing, and file handling (mocked).

### 7. API Routers (`unit/test_routers.py`)
- **Components:** FastAPI Routes (`forms.py`).
- **Verify:** Endpoint accessibility (Health/Root) and Logic (Publish/Submit) using `TestClient` and mocked services.

### 8. Integration Tests (`integration/test_openrouter_real.py`)
- **Target:** OpenRouter API.
- **Action:** Real network call using credentials from `.env.test`.
- **Verify:** Actual connectivity and response format from the AI model.

## Running Tests

### Run All Unit Tests
```bash
export PYTHONPATH=$PYTHONPATH:$(pwd)/backend
pytest backend/tests_2026/unit
```

### Run Integration Tests
*Note: Requires valid `API_KEY` in `backend/.env.test`.*
```bash
export PYTHONPATH=$PYTHONPATH:$(pwd)/backend
pytest -m integration backend/tests_2026/integration
```

### Run All Tests
```bash
export PYTHONPATH=$PYTHONPATH:$(pwd)/backend
pytest backend/tests_2026
```
