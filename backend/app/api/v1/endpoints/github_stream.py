"""
Server-Sent Events (SSE) streaming endpoint for GitHub repository import.

This module provides real-time progress updates during GitHub repository downloads,
allowing the frontend to display progress information to users during long-running
import operations.

SSE Flow:
1. Client sends POST to /api/v1/stream/github-import
2. Server opens SSE connection
3. Server sends progress events during download/extraction
4. Server sends final 'complete' event with results
5. Server closes connection

Event Types:
- progress: Download/extraction progress updates
- complete: Final results with file listings
- error: Error information if import fails
"""

import asyncio
import json
from fastapi import APIRouter
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from typing import Optional

from app.github_context.fetch import GitHubFetchError
from app.github_context.service import github_context_service
from common.logger import get_logger
from common.logging_decorator import log_method_call

logger = get_logger(__name__)
router = APIRouter()


class GitHubImportStreamRequest(BaseModel):
    """Request model for streaming GitHub import"""
    repository: str
    ref: Optional[str] = "main"
    subpath: Optional[str] = None
    session_id: Optional[str] = None


async def generate_import_events(request: GitHubImportStreamRequest):
    """
    Generator function that yields Server-Sent Events during GitHub import.

    Yields SSE-formatted events with progress updates and final results.
    """
    try:
        # Send initial progress event
        yield f"event: progress\n"
        yield f"data: {json.dumps({'stage': 'Starting', 'message': 'Preparing to import repository...'})}\n\n"

        # Allow event loop to process
        await asyncio.sleep(0.1)

        # Send fetching progress
        yield f"event: progress\n"
        yield f"data: {json.dumps({'stage': 'Fetching', 'message': f'Downloading {request.repository}@{request.ref}...'})}\n\n"

        await asyncio.sleep(0.1)

        # Perform the actual import (blocking operation, but quick enough)
        # Note: For truly large repos, this should be made async or use a task queue
        result = await asyncio.to_thread(
            github_context_service.import_repository,
            repository=request.repository,
            ref=request.ref,
            subpath=request.subpath,
            session_id=request.session_id,
        )

        # Send extraction progress
        yield f"event: progress\n"
        yield f"data: {json.dumps({'stage': 'Extracting', 'message': 'Extracting repository contents...'})}\n\n"

        await asyncio.sleep(0.1)

        # Send scanning progress
        yield f"event: progress\n"
        yield f"data: {json.dumps({'stage': 'Scanning', 'message': f'Scanning {len(result.files)} files...'})}\n\n"

        await asyncio.sleep(0.1)

        # Send completion event with full results
        complete_data = {
            'repository': result.repository,
            'ref': result.ref,
            'rootPath': str(result.root_path),
            'scanPath': str(result.scan_path),
            'files': result.files,
            'tree': result.tree,
            'message': result.message,
        }

        yield f"event: complete\n"
        yield f"data: {json.dumps(complete_data)}\n\n"

        logger.info(f"GitHub import streaming completed successfully for {request.repository}@{request.ref}")

    except (ValueError, GitHubFetchError) as exc:
        # Send error event for expected errors
        logger.warning(f"GitHub import failed: {exc}")
        error_data = {
            'error': str(exc),
            'repository': request.repository,
            'ref': request.ref,
        }
        yield f"event: error\n"
        yield f"data: {json.dumps(error_data)}\n\n"

    except Exception as exc:
        # Send error event for unexpected errors
        logger.error(f"Unexpected error during GitHub import: {exc}", exc_info=True)
        error_data = {
            'error': 'Failed to import repository. Please check the repository name and try again.',
            'repository': request.repository,
            'ref': request.ref,
        }
        yield f"event: error\n"
        yield f"data: {json.dumps(error_data)}\n\n"


@router.post(
    "/github-import",
    summary="Import GitHub repository with SSE progress",
    description=(
        "Stream real-time progress updates while importing a GitHub repository. "
        "Uses Server-Sent Events (SSE) to provide feedback during download and extraction. "
        "Frontend should connect with EventSource or fetch() and read the stream."
    ),
    tags=["GitHub Context", "Streaming"],
)
@log_method_call
async def stream_github_import(request: GitHubImportStreamRequest):
    """
    Stream GitHub repository import with real-time progress updates.

    This endpoint provides Server-Sent Events (SSE) to show progress during:
    1. Repository download
    2. Content extraction
    3. File scanning
    4. Final results

    Event Types:
        - progress: Updates during import (stage, message)
        - complete: Final results with file listings
        - error: Error information if import fails

    Request Body:
        - repository: GitHub repository (owner/repo or URL)
        - ref: Git reference (default: "main")
        - subpath: Optional subdirectory path
        - session_id: Optional session identifier

    Response:
        Server-Sent Events stream with progress and completion events

    Example:
        POST /api/v1/stream/github-import
        {
            "repository": "facebook/react",
            "ref": "main",
            "subpath": "packages/react"
        }

        Receives SSE events:
        event: progress
        data: {"stage": "Fetching", "message": "Downloading facebook/react@main..."}

        event: complete
        data: {"repository": "facebook/react", "files": [...], ...}
    """
    logger.info(f"Starting GitHub import stream for {request.repository}@{request.ref}")

    return StreamingResponse(
        generate_import_events(request),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",  # Disable nginx buffering
        }
    )
