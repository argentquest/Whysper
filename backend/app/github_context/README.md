# GitHub Context (public repos)

This package contains the backend pieces for importing **public** GitHub repositories into the Set Context flow. It reuses the existing file scanning infrastructure, so the UI can browse and select files exactly as it does for local folders.

Implemented modules:
- `fetch.py`: Parse repo identifiers, download tarballs from GitHub, and safely extract them into a cache directory.
- `ingest.py`: Build file lists and directory trees using the shared `FileService` for Set Context.
- `service.py`: High-level service that orchestrates fetch + ingest and exposes a cached `github_context_service` instance.

Assumptions:
- Only public repos (unauthenticated tarball URLs).
- No submodules or LFS handling on the first pass.
- Basic size guard (80MB archive limit); otherwise defers to existing file filters.
