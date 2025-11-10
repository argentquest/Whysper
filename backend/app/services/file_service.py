"""File scanning utilities for the web backend."""
from __future__ import annotations

import os
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional

from common.lazy_file_scanner import LazyCodebaseScanner, FileInfo
from common.logger import get_logger
from common.env_manager import env_manager
from common.logging_decorator import log_method_call
from security_utils import SecurityUtils

logger = get_logger(__name__)


class FileService:
    """Wraps the existing scanners to expose REST-friendly helpers with support for external directories."""

    @log_method_call
    def __init__(self, base_directory: Optional[str] = None) -> None:
        logger.info("Initializing FileService")
        self._scanner = LazyCodebaseScanner()
        # Support for custom base directory - uses CODE_PATH from env or provided parameter
        # This allows scanning external folders (frontend, other projects, etc.)
        if base_directory:
            self._base_directory = base_directory
        else:
            # Try to load from environment variable CODE_PATH
            env_vars = env_manager.load_env_file()
            self._base_directory = env_vars.get("CODE_PATH", None)
        logger.info(f"FileService initialized with scanner, base_directory={self._base_directory}")

    # ------------------------------------------------------------------
    # Directory helpers
    # ------------------------------------------------------------------
    @log_method_call
    def set_base_directory(self, directory: str) -> Dict[str, Any]:
        """
        Safely set a new base directory for file scanning.

        This allows scanning external folders (frontend, other projects, etc.)
        while maintaining path traversal protection.

        Args:
            directory: The new base directory path

        Returns:
            Dict with validation result
        """
        # Validate the directory exists and is accessible
        validation = self.validate_directory(directory)

        if validation["is_valid"]:
            self._base_directory = directory
            logger.info(f"Base directory changed to: {directory}")
            return {
                "success": True,
                "message": f"Base directory set to {directory}",
                "directory": directory
            }
        else:
            logger.warning(f"Failed to set base directory: {validation['error']}")
            return {
                "success": False,
                "message": validation["error"],
                "error": validation["error"]
            }

    @log_method_call
    def get_base_directory(self) -> str:
        """Get the current base directory."""
        return self._base_directory or os.getcwd()

    @log_method_call
    def validate_directory(self, directory: str) -> Dict[str, Any]:
        """
        Validate if a given directory path is safe and accessible.
        
        Uses the internal scanner's logic to check for security vulnerabilities
        (e.g., path traversal) and accessibility.
        
        Args:
            directory: The path to validate.
        
        Returns:
            Dict[str, Any]: A dict containing {"is_valid": bool, "error": str}
        """
        is_valid, error_message = self._scanner.validate_directory(directory)
        return {
            "is_valid": is_valid,
            "error": error_message,
        }

    @log_method_call
    def scan_directory(self, directory: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Return metadata for all supported files under a directory.

        Args:
            directory: Directory to scan. If None, uses base directory.

        Returns:
            List of file metadata dictionaries
        """
        scan_dir = directory or self.get_base_directory()
        logger.info(f"Scanning directory: {scan_dir}")
        files: List[Dict[str, Any]] = []
        for batch in self._scanner.scan_directory_lazy(scan_dir):
            for info in batch:
                files.append(self._serialize_file_info(info, scan_dir))
        logger.info(f"Scan complete for {scan_dir}: {len(files)} files")
        return files

    @log_method_call
    def build_directory_tree(self, directory: str) -> Dict[str, Any]:
        """Return a nested tree of directories and supported files."""
        root_path = Path(directory)
        tree = {
            "name": root_path.name,
            "path": str(root_path),
            "type": "directory",
            "children": [],
        }
        children_map: Dict[Path, Dict[str, Any]] = {root_path: tree}

        for batch in self._scanner.scan_directory_lazy(directory):
            for info in batch:
                file_path = Path(info.path)
                parent = file_path.parent
                node = self._ensure_directory(children_map, parent, root_path)
                node.setdefault("children", []).append(
                    {
                        "name": file_path.name,
                        "path": str(file_path),
                        "relativePath": os.path.relpath(info.path, directory),
                        "type": "file",
                        "size": info.size,
                        "modifiedTime": info.modified_time,
                        "extension": info.extension,
                        "isSpecial": info.is_special,
                    }
                )
        return tree

    # ------------------------------------------------------------------
    # File content helpers
    # ------------------------------------------------------------------
    @log_method_call
    def read_file(self, file_path: str) -> str:
        return self._scanner.read_file_content(file_path)

    @log_method_call
    def read_files(self, file_paths: Iterable[str]) -> str:
        return self._scanner.get_codebase_content(list(file_paths))

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------
    @log_method_call
    def _ensure_directory(
        self,
        children_map: Dict[Path, Dict[str, Any]],
        directory: Path,
        root_path: Path,
    ) -> Dict[str, Any]:
        if directory in children_map:
            return children_map[directory]
        if directory == root_path:
            return children_map[root_path]

        parent_node = self._ensure_directory(
            children_map, directory.parent, root_path
        )
        node = {
            "name": directory.name,
            "path": str(directory),
            "type": "directory",
            "children": [],
        }
        parent_node.setdefault("children", []).append(node)
        children_map[directory] = node
        return node

    @log_method_call
    def _serialize_file_info(
        self, info: FileInfo, base_directory: str
    ) -> Dict[str, Any]:
        return {
            "path": info.path,
            "relativePath": os.path.relpath(info.path, base_directory),
            "size": info.size,
            "modifiedTime": info.modified_time,
            "extension": info.extension,
            "isSpecial": info.is_special,
        }

    @log_method_call
    def get_folder_file_counts(self, directory: str) -> List[Dict[str, Any]]:
        """Return recursive subfolders with file counts."""

        root = Path(directory).resolve()
        results = []
        for root_dir, dirs, files in os.walk(root):
            rel_path = os.path.relpath(root_dir, root)
            folder_path = "." if rel_path == "." else rel_path
            file_count = len(files)
            results.append({
                "path": folder_path,
                "fileCount": file_count
            })
        results.sort(key=lambda x: x["path"])
        return results


file_service = FileService()