import os
from pathlib import Path

import pytest

from app.github_context.fetch import GitHubFetchError
from app.github_context.service import GitHubContextService


@pytest.mark.skipif(
    os.environ.get("CI_OFFLINE") == "1",
    reason="Requires network access to GitHub",
)
def test_import_public_github_repo(tmp_path):
    """
    Integration test that fetches a public GitHub repo and ensures files are available for Set Context.

    This exercises the full fetch + extract + scan flow for a known public repository.
    """
    cache_dir = tmp_path / "github_cache"
    service = GitHubContextService(cache_dir=str(cache_dir))

    try:
        result = service.import_repository("https://github.com/argentquest/LLMOneProvider", ref="main")
    except GitHubFetchError:
        # Fallback if default branch is not "main"
        result = service.import_repository("https://github.com/argentquest/LLMOneProvider", ref="master")

    assert result.repository.endswith("LLMOneProvider")
    assert result.root_path.exists()
    assert result.scan_path.exists()
    assert len(result.files) > 0
    assert isinstance(result.tree, dict)

    # Sanity check that a README or similar top-level file was fetched
    filenames = {Path(f["path"]).name.lower() for f in result.files if "path" in f}
    assert any(name.startswith("readme") for name in filenames)
