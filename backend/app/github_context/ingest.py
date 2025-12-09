"""
Helpers to transform fetched GitHub repositories into Set Context-compatible data structures.

This module acts as an adapter between the GitHub fetch layer and the existing
FileService infrastructure. It reuses the FileService's scan_directory and
build_directory_tree methods to ensure consistency with local file scanning.

Integration Points:
    - FileService.scan_directory: Scans files and produces metadata
    - FileService.build_directory_tree: Builds hierarchical tree structure
    - Set Context UI: Consumes the files and tree data
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List

from app.services.file_service import file_service


@dataclass
class ScanResult:
    """
    Container for repository scan results compatible with Set Context UI.

    This structure bundles the file listing and directory tree in the format
    expected by the FileTreeModal and ContextModal components. It mirrors the
    results from scanning local directories to ensure a consistent UX.

    Attributes:
        repo_path: Local filesystem path to the repository root.
        scan_path: Path that was scanned (may be repo_path or a subdirectory).
        files: List of file metadata dictionaries, each containing:
            - path: Relative or absolute file path
            - name: File name
            - size: File size in bytes
            - Other metadata from FileService.scan_directory
        tree: Hierarchical directory tree dictionary with structure:
            - name: Node name
            - type: "file" or "directory"
            - children: List of child nodes (for directories)
            - Other metadata from FileService.build_directory_tree

    Example:
        >>> result = ScanResult(
        ...     repo_path=Path("/cache/owner/repo/main"),
        ...     scan_path=Path("/cache/owner/repo/main/src"),
        ...     files=[
        ...         {"path": "src/main.py", "name": "main.py", "size": 1024},
        ...         {"path": "src/utils.py", "name": "utils.py", "size": 512}
        ...     ],
        ...     tree={
        ...         "name": "src",
        ...         "type": "directory",
        ...         "children": [
        ...             {"name": "main.py", "type": "file"},
        ...             {"name": "utils.py", "type": "file"}
        ...         ]
        ...     }
        ... )
    """
    repo_path: Path
    scan_path: Path
    files: List[Dict]
    tree: Dict


def build_scan_result(repo_path: Path, scan_path: Path) -> ScanResult:
    """
    Scan a repository path and build Set Context-compatible data structures.

    This function delegates to the existing FileService infrastructure to ensure
    consistent behavior between GitHub imports and local directory scanning. It
    applies the same file filtering, tree building, and metadata extraction logic.

    The FileService automatically:
        - Filters out binary files and build artifacts
        - Respects .gitignore patterns
        - Extracts file metadata (size, type, etc.)
        - Builds a hierarchical tree structure

    Args:
        repo_path: Root path of the repository (used for reference).
        scan_path: Path to scan (can be repo_path or a subdirectory).

    Returns:
        ScanResult containing files list and tree structure ready for the UI.

    Example:
        >>> repo = Path("/cache/python/cpython/main")
        >>> scan = Path("/cache/python/cpython/main/Lib")
        >>> result = build_scan_result(repo, scan)
        >>> len(result.files)
        523
        >>> result.tree["name"]
        'Lib'

    Note:
        This function is intentionally thin to maximize reuse of FileService logic.
        Any changes to file scanning behavior should be made in FileService to
        ensure consistency across both local and GitHub context sources.
    """
    # Use FileService to scan directory and build tree (same as local files)
    files = file_service.scan_directory(str(scan_path))
    tree = file_service.build_directory_tree(str(scan_path))

    return ScanResult(repo_path=repo_path, scan_path=scan_path, files=files, tree=tree)
