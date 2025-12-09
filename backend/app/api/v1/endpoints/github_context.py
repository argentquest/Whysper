"""
FastAPI endpoints for importing public GitHub repositories into Set Context.

This module provides REST API endpoints that allow the frontend to:
    - Import public GitHub repositories
    - Scan and explore repository contents
    - Integrate GitHub code with the existing file selection UI

The endpoint reuses the existing FileService infrastructure for consistency,
so GitHub imports behave identically to local directory scanning.

API Versioning:
    These endpoints are part of API v1 and mounted at /api/v1/github/*
"""

from fastapi import APIRouter, HTTPException

from app.github_context.fetch import GitHubFetchError
from app.github_context.service import github_context_service
from common.logger import get_logger
from common.logging_decorator import log_method_call
from schemas import GitHubImportRequest, GitHubImportResponse

logger = get_logger(__name__)
router = APIRouter()


@router.post(
    "/import",
    response_model=GitHubImportResponse,
    summary="Import a public GitHub repository",
    description=(
        "Download a public GitHub repository tarball via the GitHub codeload service, "
        "cache it locally, and return file listings compatible with the Set Context UI. "
        "Subsequent imports of the same repository@ref reuse the cached version for speed."
    ),
    responses={
        200: {
            "description": "Repository successfully imported",
            "content": {
                "application/json": {
                    "example": {
                        "repository": "facebook/react",
                        "ref": "main",
                        "rootPath": "/cache/facebook/react/main",
                        "scanPath": "/cache/facebook/react/main/packages/react",
                        "files": [{"path": "packages/react/index.js", "name": "index.js", "size": 1024}],
                        "tree": {"name": "react", "children": []},
                        "message": "Loaded facebook/react@main from GitHub"
                    }
                }
            }
        },
        400: {
            "description": "Invalid repository format, ref not found, or subpath doesn't exist"
        },
        500: {
            "description": "Unexpected server error during import"
        }
    },
    tags=["GitHub Context"]
)
@log_method_call
def import_github_repository(request: GitHubImportRequest):
    """
    Import a public GitHub repository and prepare it for Set Context selection.

    This endpoint handles the complete workflow of:
    1. Validating the repository identifier format
    2. Downloading the repository tarball (or using cache)
    3. Extracting and validating the subpath (if specified)
    4. Scanning files using FileService
    5. Returning results in Set Context UI format

    The cached repositories persist across server restarts for performance.

    Request Body:
        - repository: Repository identifier (owner/repo or full GitHub URL)
        - ref: Optional git reference (default: "main")
        - subpath: Optional subdirectory to limit scan scope

    Response:
        - repository: Normalized "owner/name" identifier
        - ref: Git reference that was fetched
        - rootPath: Local path to repository root
        - scanPath: Local path that was scanned
        - files: List of file metadata dictionaries
        - tree: Hierarchical directory tree
        - message: Success message

    Errors:
        - 400: Invalid request (bad format, ref not found, invalid subpath)
        - 500: Unexpected server error

    Example Request:
        POST /api/v1/github/import
        {
            "repository": "python/cpython",
            "ref": "3.11",
            "subpath": "Lib/collections"
        }

    Example Response:
        {
            "repository": "python/cpython",
            "ref": "3.11",
            "rootPath": "/cache/python/cpython/3.11",
            "scanPath": "/cache/python/cpython/3.11/Lib/collections",
            "files": [...],
            "tree": {...},
            "message": "Loaded python/cpython@3.11 from GitHub"
        }
    """
    try:
        # Delegate to service layer for business logic
        result = github_context_service.import_repository(
            repository=request.repository,
            ref=request.ref,
            subpath=request.subpath,
        )
    except (ValueError, GitHubFetchError) as exc:
        # Handle expected errors (validation, not found, etc.)
        logger.info(f"GitHub import failed: {exc}")
        raise HTTPException(status_code=400, detail=str(exc))
    except Exception as exc:  # pragma: no cover - safeguard
        # Handle unexpected errors with generic message
        logger.info(f"Unexpected error importing GitHub repo: {exc}")
        raise HTTPException(status_code=500, detail="Failed to import repository")

    # Convert service result to API response model
    return GitHubImportResponse(
        repository=result.repository,
        ref=result.ref,
        rootPath=str(result.root_path),
        scanPath=str(result.scan_path),
        files=result.files,
        tree=result.tree,
        message=result.message,
    )
