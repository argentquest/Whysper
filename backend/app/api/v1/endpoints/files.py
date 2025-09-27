"""
File and directory management endpoints.

This module handles file operations including:
- Directory scanning and validation
- File content reading
- Directory tree building
- File count statistics
"""
from fastapi import APIRouter, HTTPException
from web_backend.services.conversation_service import conversation_manager
from web_backend.services.file_service import file_service
from common.env_manager import env_manager
from schemas import (
    SetDirectoryRequest,
    SetDirectoryResponse,
    DirectoryScanRequest,
    DirectoryScanResponse,
    FileContentRequest,
    FileContentResponse,
    FolderFileCountRequest,
    FolderFileCountResponse,
    FolderInfo,
    TopFoldersResponse,
    UpdateFilesRequest,
    ConversationSummaryModel,
)
from common.logger import get_logger

logger = get_logger(__name__)
router = APIRouter()


def _session_summary_model(session) -> ConversationSummaryModel:
    """Convert session summary to response model."""
    summary = session.get_summary()
    return ConversationSummaryModel(
        conversation_id=summary.conversation_id,
        provider=summary.provider,
        selected_model=summary.selected_model,
        selected_directory=summary.selected_directory,
        selected_files=summary.selected_files,
        persistent_files=summary.persistent_files,
        question_history=summary.question_history,
        conversation_history=summary.conversation_history,
    )


@router.post("/conversations/{conversation_id}/directory", response_model=SetDirectoryResponse)
def set_directory(conversation_id: str, request: SetDirectoryRequest):
    """Set the working directory for a conversation."""
    try:
        session = conversation_manager.get_session(conversation_id)
    except KeyError as exc:
        raise HTTPException(status_code=404, detail=str(exc))

    success, message, tracked_files = session.set_directory(request.path)
    if not success:
        raise HTTPException(status_code=400, detail=message)

    metadata = file_service.scan_directory(request.path)
    summary_model = _session_summary_model(session)
    return SetDirectoryResponse(
        directory=request.path,
        files=metadata,
        message=message,
        summary=summary_model,
    )


@router.post("/conversations/{conversation_id}/files", response_model=ConversationSummaryModel)
def update_files(conversation_id: str, request: UpdateFilesRequest):
    """Update selected files for a conversation."""
    try:
        session = conversation_manager.get_session(conversation_id)
    except KeyError as exc:
        raise HTTPException(status_code=404, detail=str(exc))

    session.clear_files()
    for file_path in request.files:
        session.add_file(file_path)

    return _session_summary_model(session)


@router.post("/scan", response_model=DirectoryScanResponse)
def scan_directory(request: DirectoryScanRequest):
    """
    Scan a directory for files and build a file tree.
    
    This endpoint validates the directory path and returns:
    - List of files with metadata
    - Directory tree structure
    """
    logger.info(f"Scanning directory: {request.path}")
    validation = file_service.validate_directory(request.path)
    if not validation["is_valid"]:
        raise HTTPException(status_code=400, detail=validation["error"])

    files = file_service.scan_directory(request.path)
    logger.info(f"Scan complete: {len(files)} files found")
    tree = file_service.build_directory_tree(request.path)
    return DirectoryScanResponse(
        directory=request.path,
        files=files,
        tree=tree,
    )


@router.post("/content", response_model=FileContentResponse)
def get_file_content(request: FileContentRequest):
    """
    Read and combine content from multiple files.
    
    This endpoint reads the specified files and returns their
    combined content for AI processing.
    """
    try:
        combined = file_service.read_files(request.files)
    except Exception as exc:
        raise HTTPException(status_code=400, detail=str(exc))
    return FileContentResponse(combinedContent=combined)


@router.post("/folder-counts", response_model=FolderFileCountResponse)
def get_folder_file_counts(request: FolderFileCountRequest):
    """
    Get file counts for subdirectories.
    
    This endpoint returns the number of files in each subdirectory
    of the specified path, useful for directory browsing UIs.
    """
    validation = file_service.validate_directory(request.path)
    if not validation["is_valid"]:
        raise HTTPException(status_code=400, detail=validation["error"])

    counts = file_service.get_folder_file_counts(request.path)
    folder_infos = [
        FolderInfo(
            path=item["path"],
            fileCount=item["fileCount"]
        ) for item in counts
    ]
    return FolderFileCountResponse(folders=folder_infos)


@router.get("/top-folders", response_model=TopFoldersResponse)
def get_top_folders():
    """
    Get top-level folders from the configured CODE_PATH.
    
    This endpoint returns a list of directories from the CODE_PATH
    environment variable, useful for project browsing.
    """
    env_vars = env_manager.load_env_file()
    code_path = env_vars.get("CODE_PATH", ".")
    try:
        import os
        if os.path.exists(code_path):
            folders = [
                d for d in os.listdir(code_path)
                if os.path.isdir(os.path.join(code_path, d))
            ]
            return TopFoldersResponse(folders=folders)
        else:
            raise HTTPException(
                status_code=404,
                detail=f"CODE_PATH directory not found: {code_path}",
            )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/")
def get_files(directory: str = None):
    """
    Get files from a directory for frontend compatibility.
    
    This endpoint provides a simple GET interface for the frontend
    to retrieve files from a directory.
    """
    try:
        import os
        from typing import List
        
        # Default to current directory if none specified
        if not directory:
            env_vars = env_manager.load_env_file()
            directory = env_vars.get("CODE_PATH", ".")
        
        # Validate directory exists
        if not os.path.exists(directory):
            raise HTTPException(
                status_code=404,
                detail=f"Directory not found: {directory}"
            )
        
        if not os.path.isdir(directory):
            raise HTTPException(
                status_code=400,
                detail=f"Path is not a directory: {directory}"
            )
        
        # Get files from the directory
        files = []
        for item in os.listdir(directory):
            item_path = os.path.join(directory, item)
            if os.path.isfile(item_path):
                stat = os.stat(item_path)
                files.append({
                    "path": item_path,
                    "name": item,
                    "size": stat.st_size,
                    "isSelected": False,
                    "type": "file"
                })
            elif os.path.isdir(item_path):
                files.append({
                    "path": item_path,
                    "name": item,
                    "size": 0,
                    "isSelected": False,
                    "type": "directory"
                })
        
        return {
            "success": True,
            "data": files
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))