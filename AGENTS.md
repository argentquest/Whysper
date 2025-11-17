# AGENTS.md

## Build/Lint/Test Commands

### Frontend (React/TypeScript)
- **Build**: `npm run build`
- **Dev server**: `npm run dev`
- **Lint**: `npm run lint` (ESLint)
- **Test**: `npm test` (Vitest) or `npm run test:ui`
- **Single test**: `npm test -- <test-file>` or `npx vitest run <test-file>`

### Backend (Python/FastAPI)
- **Install**: `pip install -r requirements.txt`
- **Run**: `python main.py` or `uvicorn backend.app.main:app --reload`
- **Lint**: `ruff check .` or `ruff format .`
- **Test**: `python -m pytest` or `pytest`
- **Single test**: `python -m pytest <test-file>`

## Code Style Guidelines

### TypeScript/JavaScript
- Use ES6+ features, strict TypeScript with `strict: true`
- Imports: Use ES6 imports, group by external/internal, sort alphabetically
- Naming: camelCase for variables/functions, PascalCase for components/classes
- Types: Define interfaces for objects, use union types, avoid `any`
- Error handling: Use try-catch with specific error types, async/await with proper error propagation

### Python
- PEP 8 compliant, use Black for formatting, Ruff for linting
- Imports: Standard library first, then third-party, then local; sort alphabetically
- Naming: snake_case for variables/functions, PascalCase for classes
- Types: Use type hints, mypy for type checking
- Error handling: Use try-except with specific exceptions, log errors appropriately

### General
- No comments unless necessary; code should be self-documenting
- Follow existing patterns in codebase
- Use existing libraries (React, FastAPI, etc.)