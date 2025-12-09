"""
Utilities to fetch and unpack public GitHub repositories.

This module provides functionality to download GitHub repository archives
(tarballs) via the GitHub codeload service, extract them safely, and cache
them locally for reuse. It supports various repository identifier formats
and includes security measures against path traversal attacks.

Key Features:
    - Repository parsing from multiple formats (owner/repo, URLs)
    - Tarball downloading with size limits (80MB max)
    - Safe extraction with path traversal protection
    - Local caching to avoid redundant downloads
    - Support for branches, tags, and commit refs
"""

from __future__ import annotations

import os
import re
import shutil
import tarfile
import tempfile
from dataclasses import dataclass
from pathlib import Path
from typing import Optional, Tuple

import requests

from common.logger import get_logger

logger = get_logger(__name__)


class GitHubFetchError(Exception):
    """
    Raised when a GitHub archive cannot be fetched or unpacked.

    This exception is used for all errors related to:
    - Repository not found (404 errors)
    - Network failures during download
    - Archive size exceeding limits
    - Extraction failures
    - Path traversal attempts
    """


@dataclass
class RepoSpec:
    """
    Specification for a GitHub repository to fetch.

    Attributes:
        owner: GitHub repository owner (username or organization)
        name: Repository name
        ref: Git reference (branch, tag, or commit SHA)

    Example:
        >>> spec = RepoSpec(owner="python", name="cpython", ref="main")
        >>> spec.repo_id
        'python/cpython@main'
    """
    owner: str
    name: str
    ref: str

    @property
    def repo_id(self) -> str:
        """
        Return a unique identifier for this repository specification.

        Returns:
            String in format "owner/name@ref" for logging and caching.
        """
        return f"{self.owner}/{self.name}@{self.ref}"


def parse_repository(value: str, ref: Optional[str] = None) -> RepoSpec:
    """
    Parse repository identifiers from various formats into a standardized RepoSpec.

    Accepts and normalizes the following formats:
        - Short form: "owner/repo"
        - HTTPS URL: "https://github.com/owner/repo" or "https://github.com/owner/repo.git"
        - SSH URL: "git@github.com:owner/repo" or "git@github.com:owner/repo.git"

    Validation is strict to ensure safe filesystem paths in the cache directory.
    Special characters in owner/repo names are sanitized to prevent directory
    traversal or filesystem issues.

    Args:
        value: Repository identifier in one of the supported formats.
        ref: Optional git reference (branch, tag, or SHA). Defaults to "main".

    Returns:
        RepoSpec with sanitized owner, name, and ref.

    Raises:
        ValueError: If the repository format is not recognized or valid.

    Examples:
        >>> parse_repository("python/cpython", "3.11")
        RepoSpec(owner='python', name='cpython', ref='3.11')

        >>> parse_repository("https://github.com/facebook/react.git")
        RepoSpec(owner='facebook', name='react', ref='main')
    """
    repo_ref = ref or "main"
    normalized = value.strip()

    # Remove .git suffix if present
    if normalized.endswith(".git"):
        normalized = normalized[:-4]

    # Try matching against supported patterns
    patterns = [
        r"^https?://github\.com/(?P<owner>[^/]+)/(?P<repo>[^/#]+)$",
        r"^git@github\.com:(?P<owner>[^/]+)/(?P<repo>[^/#]+)$",
        r"^(?P<owner>[^/]+)/(?P<repo>[^/#]+)$",
    ]
    for pattern in patterns:
        match = re.match(pattern, normalized)
        if match:
            owner = _sanitize_segment(match.group("owner"))
            name = _sanitize_segment(match.group("repo"))
            return RepoSpec(owner=owner, name=name, ref=repo_ref)

    raise ValueError("Repository must be in the form owner/repo or a GitHub URL")


def download_and_extract_repo(spec: RepoSpec, cache_dir: Path) -> Path:
    """
    Download a GitHub repository tarball and extract it to the local cache.

    This function handles the complete workflow of:
    1. Checking if the repo@ref already exists in cache
    2. Downloading the tarball from GitHub's codeload service
    3. Validating the archive size (80MB limit)
    4. Safely extracting with path traversal protection
    5. Moving to the final cache location
    6. Creating a marker file to indicate successful extraction

    The cache directory structure is: cache_dir / owner / name / ref /
    A .whysper_ready marker file indicates the extraction is complete and valid.

    Args:
        spec: Repository specification with owner, name, and ref.
        cache_dir: Base directory for caching downloaded repositories.

    Returns:
        Path to the extracted repository root directory.

    Raises:
        GitHubFetchError: If the repository cannot be found (404), download fails,
            archive exceeds size limit, or extraction fails.

    Example:
        >>> spec = RepoSpec(owner="python", name="cpython", ref="main")
        >>> cache = Path("/tmp/github_cache")
        >>> repo_path = download_and_extract_repo(spec, cache)
        >>> repo_path
        Path('/tmp/github_cache/python/cpython/main')
    """
    cache_dir.mkdir(parents=True, exist_ok=True)
    target_dir = cache_dir / spec.owner / spec.name / spec.ref
    marker_file = target_dir / ".whysper_ready"

    # Check if repository is already cached and valid
    if marker_file.exists() and target_dir.is_dir():
        logger.info(f"Using cached GitHub repo {spec.repo_id} at {target_dir}")
        return target_dir

    # Construct GitHub codeload URL for tarball download
    url = f"https://codeload.github.com/{spec.owner}/{spec.name}/tar.gz/{spec.ref}"
    logger.info(f"Fetching GitHub repo {spec.repo_id}", url=url)

    with requests.get(url, stream=True, timeout=30) as response:
        # Handle 404 errors explicitly (repo or ref not found)
        if response.status_code == 404:
            raise GitHubFetchError(f"Repository or ref not found: {spec.repo_id}")
        try:
            response.raise_for_status()
        except Exception as exc:
            raise GitHubFetchError(f"Failed to fetch {spec.repo_id}: {exc}") from exc

        # Check archive size before downloading (80MB limit for public repos)
        content_length = response.headers.get("Content-Length")
        if content_length and int(content_length) > 80 * 1024 * 1024:
            raise GitHubFetchError("Repository archive is larger than 80MB, aborting download")

        # Stream download to a temporary file
        with tempfile.NamedTemporaryFile(delete=False, suffix=".tar.gz") as tmp_file:
            for chunk in response.iter_content(chunk_size=8192):
                if chunk:
                    tmp_file.write(chunk)
            tmp_path = Path(tmp_file.name)

    # Create temporary directory for extraction
    temp_extract_dir = Path(tempfile.mkdtemp(prefix="gh_repo_"))

    try:
        # Extract with path traversal protection
        with tarfile.open(tmp_path, "r:gz") as tar:
            _safe_extract(tar, temp_extract_dir)
    except Exception as exc:
        raise GitHubFetchError(f"Failed to extract archive for {spec.repo_id}: {exc}") from exc
    finally:
        # Clean up downloaded tarball
        tmp_path.unlink(missing_ok=True)

    # GitHub tarballs typically extract to a single directory named "{repo}-{ref}"
    # Find the actual repo root (usually the only subdirectory)
    extracted_children = [p for p in temp_extract_dir.iterdir() if p.is_dir()]
    repo_root = extracted_children[0] if len(extracted_children) == 1 else temp_extract_dir

    # Move extracted repo to final cache location
    target_dir.parent.mkdir(parents=True, exist_ok=True)
    if target_dir.exists():
        # Reuse existing if it looks complete
        if marker_file.exists():
            shutil.rmtree(temp_extract_dir, ignore_errors=True)
            return target_dir
        # Otherwise remove incomplete cache
        shutil.rmtree(target_dir, ignore_errors=True)

    shutil.move(str(repo_root), str(target_dir))
    shutil.rmtree(temp_extract_dir, ignore_errors=True)

    # Create marker file to indicate successful extraction
    marker_file.touch()
    logger.info(f"Repository extracted to {target_dir}")
    return target_dir


def _safe_extract(tar: tarfile.TarFile, path: Path) -> None:
    """
    Safely extract a tarfile while preventing path traversal attacks.

    Validates that all members in the archive extract to paths within the target
    directory. This prevents malicious archives from writing files outside the
    intended extraction directory (e.g., using "../../../etc/passwd" paths).

    Args:
        tar: Open tarfile.TarFile object to extract.
        path: Target directory for extraction.

    Raises:
        GitHubFetchError: If any archive member attempts path traversal.

    Note:
        This implements the security recommendations from:
        https://docs.python.org/3/library/tarfile.html#tarfile-extraction-filter
    """
    for member in tar.getmembers():
        member_path = path / member.name
        if not _is_within_directory(path, member_path):
            raise GitHubFetchError(f"Blocked path traversal in archive member: {member.name}")
    tar.extractall(path=path)


def _is_within_directory(directory: Path, target: Path) -> bool:
    """
    Check if target path is within directory (no parent traversal).

    Uses os.path.commonpath to verify that the target resolves to a location
    inside the directory, preventing "../" style attacks.

    Args:
        directory: The allowed parent directory.
        target: The path to validate.

    Returns:
        True if target is within directory, False otherwise.

    Example:
        >>> _is_within_directory(Path("/tmp/safe"), Path("/tmp/safe/file.txt"))
        True
        >>> _is_within_directory(Path("/tmp/safe"), Path("/tmp/safe/../etc/passwd"))
        False
    """
    abs_directory = os.path.abspath(directory)
    abs_target = os.path.abspath(target)
    return os.path.commonpath([abs_directory]) == os.path.commonpath([abs_directory, abs_target])


def _sanitize_segment(value: str) -> str:
    """
    Sanitize a path segment for safe filesystem use.

    Replaces any characters that might cause issues on filesystems (especially
    Windows) with hyphens. Allows only alphanumerics, underscores, dots, and hyphens.

    Args:
        value: Raw path segment (e.g., repository owner or name).

    Returns:
        Sanitized string safe for use as a directory name.

    Example:
        >>> _sanitize_segment("user/name")
        'user-name'
        >>> _sanitize_segment("my-repo")
        'my-repo'
        >>> _sanitize_segment("special@chars#here")
        'special-chars-here'
    """
    return re.sub(r"[^A-Za-z0-9_.-]+", "-", value)
