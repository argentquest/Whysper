"""
Service layer for GitHub repository context management.

This module provides the high-level service interface for importing public GitHub
repositories into the Whysper Set Context system. It orchestrates the fetch, cache,
and scan operations to make repository files available for AI conversation context.

The service integrates with:
    - fetch module: Downloads and caches GitHub repository tarballs
    - ingest module: Scans repository files using the existing FileService
    - Set Context UI: Provides file/tree data in the expected format
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Optional

from common.env_manager import env_manager
from common.logger import get_logger

from .fetch import RepoSpec, GitHubFetchError, download_and_extract_repo, parse_repository
from .ingest import ScanResult, build_scan_result

logger = get_logger(__name__)


@dataclass
class GitHubImportResult:
    """
    Result of a successful GitHub repository import operation.

    This data structure contains all information needed to present the imported
    repository to the Set Context UI, including file listings and directory trees
    in the format expected by the frontend.

    Attributes:
        repository: Repository identifier in "owner/name" format.
        ref: Git reference (branch/tag/commit) that was fetched.
        root_path: Local filesystem path to the repository root.
        scan_path: Path that was scanned (may be a subdirectory if subpath was specified).
        files: List of file metadata dictionaries compatible with FileTreeModal.
        tree: Hierarchical tree structure compatible with FileTreeModal.
        message: User-friendly success message for display.

    Example:
        >>> result = GitHubImportResult(
        ...     repository="python/cpython",
        ...     ref="main",
        ...     root_path=Path("/cache/python/cpython/main"),
        ...     scan_path=Path("/cache/python/cpython/main/Lib"),
        ...     files=[{"path": "Lib/os.py", "name": "os.py", "size": 1234}],
        ...     tree={"name": "Lib", "children": [...]},
        ...     message="Loaded python/cpython@main from GitHub"
        ... )
    """
    repository: str
    ref: str
    root_path: Path
    scan_path: Path
    files: list
    tree: dict
    message: str


class GitHubContextService:
    """
    Service for importing public GitHub repositories into Set Context.

    This service manages the complete workflow of downloading, caching, and scanning
    GitHub repositories so their files can be used as conversation context. It reuses
    the existing FileService infrastructure for scanning and tree building.

    The cache directory structure is:
        cache_dir/
            owner/
                repo_name/
                    ref/
                        .whysper_ready  (marker file)
                        [repository files...]

    Configuration:
        Cache directory can be set via:
        1. Constructor parameter
        2. GITHUB_CONTEXT_CACHE environment variable
        3. Default: backend/app/github_context/cache

    Thread Safety:
        This service is not thread-safe for concurrent imports to the same repo@ref.
        However, concurrent imports of different repositories are safe due to the
        isolated cache directory structure.
    """

    def __init__(self, cache_dir: Optional[str] = None) -> None:
        """
        Initialize the GitHub context service.

        Args:
            cache_dir: Optional custom cache directory path. If not provided,
                uses GITHUB_CONTEXT_CACHE env var or default location.

        Example:
            >>> service = GitHubContextService()  # Uses default cache
            >>> service = GitHubContextService("/custom/cache")  # Custom location
        """
        env_vars = env_manager.load_env_file()
        default_cache = Path(__file__).parent / "cache"
        self.cache_dir = Path(cache_dir or env_vars.get("GITHUB_CONTEXT_CACHE", default_cache)).resolve()
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        logger.info(f"GitHubContextService cache directory: {self.cache_dir}")

    def import_repository(
        self,
        repository: str,
        ref: Optional[str] = None,
        subpath: Optional[str] = None,
        session_id: Optional[str] = None,
    ) -> GitHubImportResult:
        """
        Import a public GitHub repository and prepare it for Set Context.

        This method orchestrates the complete import workflow:
        1. Parse the repository identifier (handles multiple formats)
        2. Download and extract the tarball (or use cached copy)
        3. Validate and resolve the subpath (if specified)
        4. Scan files using FileService infrastructure
        5. Return results in Set Context-compatible format

        The imported repository files remain cached for future use. Subsequent
        imports of the same repo@ref will reuse the cached version.

        Args:
            repository: Repository identifier in one of these formats:
                - "owner/repo" (e.g., "python/cpython")
                - "https://github.com/owner/repo"
                - "https://github.com/owner/repo.git"
            ref: Git reference to fetch (branch, tag, or commit SHA).
                Defaults to "main" if not specified.
            subpath: Optional subdirectory path to limit the scan scope.
                For example, "src/lib" would only scan that subdirectory.
                The path must exist and stay within the repository root.

        Returns:
            GitHubImportResult containing:
                - Repository and ref identifiers
                - Local filesystem paths (root and scan)
                - File list and directory tree for the UI
                - Success message

        Raises:
            ValueError: If repository format is invalid.
            GitHubFetchError: If download fails, repo not found, or subpath invalid.

        Example:
            >>> service = GitHubContextService()
            >>> result = service.import_repository(
            ...     "facebook/react",
            ...     ref="v18.2.0",
            ...     subpath="packages/react"
            ... )
            >>> print(result.message)
            'Loaded facebook/react@v18.2.0 from GitHub'
            >>> len(result.files)
            42
        """
        # Parse repository identifier (handles multiple formats)
        spec: RepoSpec = parse_repository(repository, ref)

        # Download and extract (or use cached version)
        repo_dir = download_and_extract_repo(spec, self.cache_dir, session_id)

        # Determine scan path (full repo or subpath)
        scan_path = repo_dir / subpath if subpath else repo_dir
        scan_path = scan_path.resolve()

        # Validate subpath exists and stays within repo boundaries
        if not scan_path.exists():
            raise GitHubFetchError(f"Requested subpath does not exist: {subpath}")
        if not str(scan_path).startswith(str(repo_dir.resolve())):
            raise GitHubFetchError("Subpath must stay within the repository root")

        # Scan files using existing FileService infrastructure
        scan: ScanResult = build_scan_result(repo_dir, scan_path)

        # Return results in Set Context-compatible format
        return GitHubImportResult(
            repository=f"{spec.owner}/{spec.name}",
            ref=spec.ref,
            root_path=repo_dir,
            scan_path=scan.scan_path,
            files=scan.files,
            tree=scan.tree,
            message=f"Loaded {spec.repo_id} from GitHub",
        )


github_context_service = GitHubContextService()
