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
    FileUploadRequest,
    FileUploadResponse,
    UploadedFileItem,
)
from common.logger import get_logger
from app.utils.session_utils import session_summary_model
from common.logging_decorator import log_method_call

logger = get_logger(__name__)
router = APIRouter()




@router.post("/conversations/{conversation_id}/directory", response_model=SetDirectoryResponse)
@log_method_call
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
@log_method_call
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
@log_method_call
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
@log_method_call
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
@log_method_call
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
@log_method_call
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
@log_method_call
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
@log_method_call
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
@log_method_call
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
@log_method_call
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


@router.post("/upload", response_model=FileUploadResponse)
@log_method_call
def upload_files(request: FileUploadRequest):
    """
    Upload files directly to the server, bypassing the local file system.
    
    This endpoint allows users to upload files directly to the server memory
    without writing them to the local file system. Files are stored in memory
    and can be used as context for AI conversations.
    
    Expected request body:
    {
        "files": [
            {
                "name": "example.py",
                "content": "print('hello world')",
                "size": 25
            }
        ],
        "target_directory": "uploads"  # Optional
    }
    """
    try:
        import os
        import tempfile
        import uuid
        from common.env_manager import env_manager
        from common.logger import get_logger
        
        logger = get_logger(__name__)
        
        # Get the base directory from CODE_PATH
        env_vars = env_manager.load_env_file()
        base_directory = env_vars.get("CODE_PATH", ".")
        
        # Create a temporary directory for uploaded files if it doesn't exist
        upload_dir = os.path.join(base_directory, request.target_directory or "uploads")
        if not os.path.exists(upload_dir):
            os.makedirs(upload_dir, exist_ok=True)
        
        uploaded_files = []
        total_size = 0
        
        for file_data in request.files:
            try:
                # Validate file data
                if not all(key in file_data for key in ['name', 'content']):
                    logger.warning(f"Skipping invalid file data: missing required fields")
                    continue
                
                file_name = file_data['name']
                file_content = file_data['content']
                file_size = len(file_content.encode('utf-8'))
                
                # Security check: validate file name
                if not file_name or '/' in file_name or '\\' in file_name:
                    logger.warning(f"Skipping invalid file name: {file_name}")
                    continue
                
                # Generate a unique filename to avoid conflicts
                name, ext = os.path.splitext(file_name)
                unique_id = str(uuid.uuid4())[:8]
                unique_filename = f"{name}_{unique_id}{ext}"
                
                # Create file path
                file_path = os.path.join(request.target_directory or "uploads", unique_filename)
                
                # Write file to disk (for persistence across sessions)
                full_path = os.path.join(upload_dir, unique_filename)
                with open(full_path, 'w', encoding='utf-8') as f:
                    f.write(file_content)
                
                # Create uploaded file item
                uploaded_file = UploadedFileItem(
                    path=file_path,
                    name=file_name,
                    size=file_size,
                    content=file_content,
                    type="file",
                    is_uploaded=True
                )
                
                uploaded_files.append(uploaded_file)
                total_size += file_size
                
                logger.info(f"Successfully uploaded file: {file_name} ({file_size} bytes)")
                
            except Exception as e:
                logger.error(f"Error processing file upload: {str(e)}")
                continue
        
        if not uploaded_files:
            raise HTTPException(
                status_code=400,
                detail="No valid files were uploaded"
            )
        
        logger.info(f"File upload completed: {len(uploaded_files)} files, {total_size} bytes total")
        
        return FileUploadResponse(
            success=True,
            message=f"Successfully uploaded {len(uploaded_files)} files",
            data={
                "files": [file.dict() for file in uploaded_files],
                "total_files": len(uploaded_files),
                "total_size": total_size,
                "upload_directory": request.target_directory or "uploads"
            }
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in file upload: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/uploaded")
@log_method_call
def get_uploaded_files():
    """
    Get list of uploaded files that can be used as context.
    
    This endpoint returns a list of files that have been uploaded
    and are available for use in AI conversations.
    """
    try:
        import os
        import json
        from common.env_manager import env_manager
        from common.logger import get_logger
        
        logger = get_logger(__name__)
        
        # Get the base directory from CODE_PATH
        env_vars = env_manager.load_env_file()
        base_directory = env_vars.get("CODE_PATH", ".")
        
        # Check for uploaded files directory
        upload_dir = os.path.join(base_directory, "uploads")
        if not os.path.exists(upload_dir):
            return {
                "success": True,
                "data": []
            }
        
        uploaded_files = []
        
        try:
            for filename in os.listdir(upload_dir):
                file_path = os.path.join(upload_dir, filename)
                if os.path.isfile(file_path):
                    try:
                        # Read file content
                        with open(file_path, 'r', encoding='utf-8') as f:
                            content = f.read()
                        
                        # Extract original name from unique filename
                        # Format: original_name_uuid.ext
                        parts = filename.split('_')
                        if len(parts) >= 2:
                            uuid_part = parts[-1]
                            name_parts = parts[:-1]
                            original_name = '_'.join(name_parts)
                            
                            # Re-add the extension from the UUID part
                            if '.' in uuid_part:
                                ext = uuid_part.split('.', 1)[1]
                                original_name += f'.{ext}'
                        else:
                            original_name = filename
                        
                        stat = os.stat(file_path)
                        
                        uploaded_file = {
                            "path": os.path.join("uploads", filename),
                            "name": original_name,
                            "size": stat.st_size,
                            "content": content,
                            "type": "file",
                            "is_uploaded": True
                        }
                        
                        uploaded_files.append(uploaded_file)
                        
                    except (UnicodeDecodeError, PermissionError) as e:
                        logger.warning(f"Could not read uploaded file {filename}: {str(e)}")
                        continue
                        
        except (OSError, PermissionError) as e:
            logger.error(f"Error accessing upload directory: {str(e)}")
        
        return {
            "success": True,
            "data": uploaded_files
        }
        
    except Exception as e:
        logger.error(f"Error getting uploaded files: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
