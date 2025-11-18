```python
"""Utility helpers for applying include/exclude file pattern filters."""
from __future__ import annotations

import os
from fnmatch import fnmatch
from typing import Iterable, List, Optional, Sequence, Union
from .logging_decorator import log_method_call

PatternInput = Optional[Union[str, Sequence[str]]]


@log_method_call
def _normalize_patterns(patterns: PatternInput) -> List[str]:
    # Convert input patterns to a clean, consistent list of patterns
    # Handles single string or sequence of patterns, removes None/empty values
    if not patterns:
        return []

    # Split comma-separated string or use as-is for sequence
    if isinstance(patterns, str):
        raw_patterns = patterns.split(',')
    else:
        raw_patterns = patterns

    # Clean up patterns by stripping whitespace and removing empty entries
    normalized: List[str] = []
    for pattern in raw_patterns:
        if pattern is None:
            continue
        trimmed = pattern.strip()
        if trimmed:
            normalized.append(trimmed)
    return normalized


@log_method_call
def _matches_any(patterns: Sequence[str], file_path: str) -> bool:
    # Check if file path matches any of the given glob patterns
    # Matches against both full path and filename
    if not patterns:
        return False

    # Extract just the filename for additional matching
    filename = os.path.basename(file_path)
    return any(
        fnmatch(filename, pattern) or fnmatch(file_path, pattern)
        for pattern in patterns
    )


@log_method_call
def filter_files(
    files: Iterable[str],
    include: PatternInput = None,
    exclude: PatternInput = None,
) -> List[str]:
    # Apply include and exclude filters to a list of file paths
    # Supports glob-style pattern matching for file filtering
    files_list = list(files)
    
    # Normalize include and exclude patterns
    include_patterns = _normalize_patterns(include)
    exclude_patterns = _normalize_patterns(exclude)

    filtered = files_list

    # Apply include filtering if patterns exist
    if include_patterns:
        included: List[str] = []
        for pattern in include_patterns:
            for file_path in files_list:
                # Collect files that match any include pattern
                if _matches_any([pattern], file_path):
                    included.append(file_path)
        
        # Remove duplicates while preserving original order
        seen = dict.fromkeys(included)
        filtered = list(seen.keys())

    # Apply exclude filtering to remaining files
    if exclude_patterns:
        filtered = [
            file_path for file_path in filtered
            if not _matches_any(exclude_patterns, file_path)
        ]

    return filtered
```

The comments explain the key logic in each function, focusing on:
- What each function does
- How patterns are processed
- The filtering mechanism
- Handling of include/exclude patterns