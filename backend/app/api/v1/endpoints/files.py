"""
File and directory management endpoints.

This module handles file operations including:
- Directory scanning and validation
- File content reading
- Directory tree building
- File count statistics
"""
from fastapi import APIRouter, HTTPException
from app.services.conversation_service import conversation_manager
from app.services.file_service import file_service
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
    FileSaveRequest,
    FileSaveResponse,
    FileReadResponse,
    FileCreateRequest,
    FileCreateResponse,
)
from common.logger import get_logger
from app.utils.session_utils import session_summary_model

logger = get_logger(__name__)
router = APIRouter()




@router.post("/conversations/{conversation_id}/directory", response_model=SetDirectoryResponse)
def set_directory(conversation_id: str, request: SetDirectoryRequest):
    logger.debug(f"set_directory endpoint started for conversation_id: {conversation_id}")
    """Set the working directory for a conversation."""
    try:
        session = conversation_manager.get_session(conversation_id)
    except KeyError as exc:
        raise HTTPException(status_code=404, detail=str(exc))

    success, message, tracked_files = session.set_directory(request.path)
    if not success:
        raise HTTPException(status_code=400, detail=message)

    metadata = file_service.scan_directory(request.path)
    summary_model = session_summary_model(session)
    return SetDirectoryResponse(
        directory=request.path,
        files=metadata,
        message=message,
        summary=summary_model,
    )
    logger.info(f"Set directory to {request.path} completed for conversation: {conversation_id}")
    
@router.post("/conversations/{conversation_id}/files", response_model=ConversationSummaryModel)
def update_files(conversation_id: str, request: UpdateFilesRequest):
    logger.debug(f"update_files endpoint started for conversation_id: {conversation_id}")
    """Update selected files for a conversation."""
    try:
        session = conversation_manager.get_session(conversation_id)
    except KeyError as exc:
        raise HTTPException(status_code=404, detail=str(exc))

    session.update_selected_files(
        request.selected_files,
        make_persistent=request.persistent,
    )
    return session_summary_model(session)


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
    logger.debug("get_file_content endpoint started")
    """
    Read and combine content from multiple files.
    
    This endpoint reads the specified files and returns their
    combined content for AI processing.
    """
    try:
        combined = file_service.read_files(request.files)
    except Exception as exc:
        logger.error(f"Error reading files: {exc}", files=request.files)
        raise HTTPException(status_code=400, detail=str(exc))
    
    logger.info(f"Successfully read and combined {len(request.files)} files.")
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


@router.get("/read/{file_path:path}", response_model=FileReadResponse)
def read_single_file(file_path: str):
    """
    Read content from a single file for editing.
    
    This endpoint reads the content of a specific file and returns it
    for the file editor interface.
    
    Args:
        file_path: Relative path to the file to read
    """
    try:
        import os
        from common.env_manager import env_manager
        
        # Get the base directory from CODE_PATH
        env_vars = env_manager.load_env_file()
        base_directory = env_vars.get("CODE_PATH", ".")
        
        # Construct full file path
        full_path = os.path.normpath(os.path.join(base_directory, file_path))
        
        # Security check: ensure file is within the base directory
        if not full_path.startswith(os.path.normpath(base_directory)):
            raise HTTPException(
                status_code=403,
                detail="Access denied: File path outside allowed directory"
            )
        
        # Check if file exists
        if not os.path.exists(full_path):
            raise HTTPException(
                status_code=404,
                detail=f"File not found: {file_path}"
            )
        
        if not os.path.isfile(full_path):
            raise HTTPException(
                status_code=400,
                detail=f"Path is not a file: {file_path}"
            )
        
        # Read file content
        try:
            with open(full_path, 'r', encoding='utf-8') as f:
                content = f.read()
        except UnicodeDecodeError:
            # Try with different encoding for binary files
            try:
                with open(full_path, 'r', encoding='latin-1') as f:
                    content = f.read()
            except Exception:
                raise HTTPException(
                    status_code=400,
                    detail="Unable to read file: unsupported encoding or binary file"
                )
        except PermissionError:
            raise HTTPException(
                status_code=403,
                detail="Permission denied: cannot read file"
            )
        
        return FileReadResponse(
            success=True,
            data={
                "path": file_path,
                "content": content,
                "size": len(content)
            }
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/save", response_model=FileSaveResponse)
def save_file(request: FileSaveRequest):
    """
    Save content to a file.
    
    This endpoint saves the provided content to the specified file path,
    creating directories if necessary.
    
    Expected request body:
    {
        "path": "relative/file/path.py",
        "content": "file content here"
    }
    """
    try:
        import os
        from common.env_manager import env_manager
        
        file_path = request.path
        content = request.content
        
        # Get the base directory from CODE_PATH
        env_vars = env_manager.load_env_file()
        base_directory = env_vars.get("CODE_PATH", ".")
        
        # Construct full file path
        full_path = os.path.normpath(os.path.join(base_directory, file_path))
        
        # Security check: ensure file is within the base directory
        if not full_path.startswith(os.path.normpath(base_directory)):
            raise HTTPException(
                status_code=403,
                detail="Access denied: File path outside allowed directory"
            )
        
        # Create directory if it doesn't exist
        directory = os.path.dirname(full_path)
        if directory and not os.path.exists(directory):
            os.makedirs(directory, exist_ok=True)
        
        # Write file content
        try:
            with open(full_path, 'w', encoding='utf-8') as f:
                f.write(content)
        except PermissionError:
            raise HTTPException(
                status_code=403,
                detail="Permission denied: cannot write to file"
            )
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Error writing file: {str(e)}"
            )
        
        logger.info(f"Successfully saved file: {file_path}")
        return FileSaveResponse(
            success=True,
            message=f"File saved successfully: {file_path}",
            data={
                "path": file_path,
                "size": len(content)
            }
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/create", response_model=FileCreateResponse)
def create_new_file(request: FileCreateRequest):
    """
    Create a new file with optional initial content.
    
    This endpoint creates a new file at the specified path with optional
    initial content. It will create directories if they don't exist.
    
    Expected request body:
    {
        "path": "relative/file/path.py",
        "content": "optional initial content"
    }
    """
    try:
        import os
        from common.env_manager import env_manager
        
        file_path = request.path
        content = request.content
        
        # Get the base directory from CODE_PATH
        env_vars = env_manager.load_env_file()
        base_directory = env_vars.get("CODE_PATH", ".")
        
        # Construct full file path
        full_path = os.path.normpath(os.path.join(base_directory, file_path))
        
        # Security check: ensure file is within the base directory
        if not full_path.startswith(os.path.normpath(base_directory)):
            raise HTTPException(
                status_code=403,
                detail="Access denied: File path outside allowed directory"
            )
        
        # Check if file already exists
        if os.path.exists(full_path):
            raise HTTPException(
                status_code=409,
                detail=f"File already exists: {file_path}"
            )
        
        # Create directory if it doesn't exist
        directory = os.path.dirname(full_path)
        if directory and not os.path.exists(directory):
            os.makedirs(directory, exist_ok=True)
        
        # Create the new file
        try:
            with open(full_path, 'w', encoding='utf-8') as f:
                f.write(content)
        except PermissionError:
            raise HTTPException(
                status_code=403,
                detail="Permission denied: cannot create file"
            )
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Error creating file: {str(e)}"
            )
        
        logger.info(f"Successfully created file: {file_path}")
        return FileCreateResponse(
            success=True,
            message=f"File created successfully: {file_path}",
            data={
                "path": file_path,
                "size": len(content)
            }
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/")
def get_files(directory: str = None, recursive: bool = True):
    """
    Get files from a directory for frontend compatibility.
    
    This endpoint provides a simple GET interface for the frontend
    to retrieve files from a directory, with optional recursive scanning.
    
    Args:
        directory: Directory path to scan (defaults to CODE_PATH)
        recursive: Whether to recursively scan subdirectories (default: True)
    """
    try:
        import os
        from typing import List
        
        # Default to current directory if none specified
        if not directory:
            env_vars = env_manager.load_env_file()
            directory = env_vars.get("CODE_PATH", ".")
        
        # Normalize the path for Windows compatibility
        directory = os.path.normpath(os.path.abspath(directory))
        
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
        
        def scan_directory_recursive(dir_path: str, base_path: str = None) -> List[dict]:
            """Recursively scan directory and return all files and subdirectories."""
            if base_path is None:
                base_path = dir_path
                
            files = []
            
            try:
                for item in os.listdir(dir_path):
                    # Skip hidden files and common ignore patterns
                    if item.startswith('.') or item in ['__pycache__', 'node_modules', '.git', '.venv', 'venv']:
                        continue
                        
                    item_path = os.path.join(dir_path, item)
                    
                    # Create relative path for display
                    if dir_path == base_path:
                        relative_path = item
                    else:
                        try:
                            relative_path = os.path.relpath(item_path, base_path).replace('\\', '/')
                        except ValueError:
                            # Fallback if relpath fails on Windows
                            relative_path = item_path.replace(base_path, '').lstrip('\\').lstrip('/').replace('\\', '/')
                    
                    if os.path.isfile(item_path):
                        try:
                            stat = os.stat(item_path)
                            files.append({
                                "path": relative_path,
                                "name": item,
                                "size": stat.st_size,
                                "isSelected": False,
                                "type": "file"
                            })
                        except (OSError, PermissionError):
                            # Skip files we can't access
                            continue
                            
                    elif os.path.isdir(item_path) and recursive:
                        # Add directory entry
                        files.append({
                            "path": relative_path,
                            "name": item,
                            "size": 0,
                            "isSelected": False,
                            "type": "directory"
                        })
                        
                        # Recursively scan subdirectory
                        try:
                            sub_files = scan_directory_recursive(item_path, base_path)
                            files.extend(sub_files)
                        except (OSError, PermissionError):
                            # Skip directories we can't access
                            continue
                            
            except (OSError, PermissionError):
                # Skip if we can't read the directory
                pass
                
            return files
        
        # Get files from the directory (recursively or not)
        if recursive:
            files = scan_directory_recursive(directory)
        else:
            # Non-recursive scan (original behavior)
            files = []
            for item in os.listdir(directory):
                item_path = os.path.join(directory, item)
                if os.path.isfile(item_path):
                    stat = os.stat(item_path)
                    files.append({
                        "path": item,
                        "name": item,
                        "size": stat.st_size,
                        "isSelected": False,
                        "type": "file"
                    })
                elif os.path.isdir(item_path):
                    files.append({
                        "path": item,
                        "name": item,
                        "size": 0,
                        "isSelected": False,
                        "type": "directory"
                    })
        
        # Sort files: directories first, then files, both alphabetically
        files.sort(key=lambda x: (x["type"] != "directory", x["name"].lower()))
        
        return {
            "success": True,
            "data": files
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
