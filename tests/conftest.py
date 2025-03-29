import pytest

from pathlib import Path
from git import Repo
from dataclasses import dataclass
from typing import Generator

from doc_flesh.models import RepoConfig, MyToolConfig, SiteInfo

@dataclass
class SetupRepoYield:
    temp_dir: Path
    remote_path: Path
    local_path: Path
    local_repo: Repo
    remote_repo: Repo
    repo_config: RepoConfig


@pytest.fixture
def setup_repos(tmp_path: Path) -> Generator[SetupRepoYield, None, None]:
    """Create temporary directory with both remote and local Git repositories.

    Note! The tmp_path is a built-in fixture provided by pytest.
          Read more at: https://docs.pytest.org/en/stable/how-to/tmp_path.html
    """

    # Use pytest's tmp_path instead of tempfile
    temp_dir = tmp_path.resolve()
    print(f"Created temp dir: {temp_dir}")

    # Create "remote" bare repository
    remote_path = temp_dir / "remote.git"
    remote_repo = Repo.init(remote_path, bare=True)

    # Create "local" repository
    local_path = temp_dir / "local"
    local_repo = Repo.init(str(local_path), mkdir=True)

    # Create main branch
    local_repo.git.checkout("-b", "main")

    # Add remote to local repo
    _ = local_repo.create_remote("origin", str(remote_path))

    # Create a test file and commit it
    test_file = local_path / "test.txt"
    test_file.write_text("Test content")
    local_repo.index.add([str(test_file)])
    local_repo.index.commit("Initial commit")

    # Push to remote
    local_repo.git.push("origin", "main", set_upstream=True)

    yield SetupRepoYield(
        temp_dir=temp_dir,
        remote_path=remote_path,
        local_path=local_path,
        local_repo=local_repo,
        remote_repo=remote_repo,
        repo_config=RepoConfig(local_path=local_path),
    )

    # No manual cleanup needed—pytest's tmp_path handles it
    print(f"Test complete, temp dir will be auto-removed: {temp_dir}")


@pytest.fixture
def mock_mytoolconfig(tmp_path: Path) -> MyToolConfig:
    """Fixture to create a mock MyToolConfig with temporary directories."""

    repo1_siteinfo = SiteInfo(
        site_name="Defined in conftest 1",
        site_name_slug="defined-in-conftest-1",
        category="Learning tools", 
        related_repo="[Something](https://example.com)"
    )
    repo1_path = tmp_path / "repo1"
    repo1_path.mkdir()
    (repo1_path / "siteinfo.json").write_text(repo1_siteinfo.model_dump_json())

    repo2_siteinfo = SiteInfo(
        site_name="Defined in conftest 2",
        site_name_slug="defined-in-conftest-2",
        category="Learning tools",
    )
    repo2_path = tmp_path / "repo2"
    repo2_path.mkdir()
    (repo2_path / "siteinfo.json").write_text(repo2_siteinfo.model_dump_json())

    return MyToolConfig(
        ManagedRepos=[
            RepoConfig(
                local_path=repo1_path,
                name="repo1",
                # jinja_files="mkdocs.yml",  <= Not tested here
                # static_files="docs/foo.md" <= Not tested here
                ),
            RepoConfig(
                local_path=repo2_path,
                name="repo2",
            ),
        ]
    )


@pytest.fixture
def mock_subprocess_run(monkeypatch):
    """Fixture to mock subprocess.run for testing UV dependency updates."""
    class MockSubprocessRun:
        def __init__(self):
            self.called_with_args = []
            self.should_fail = False
            self.command_not_found = False

        def __call__(self, *args, **kwargs):
            self.called_with_args.append((args, kwargs))
            
            if self.command_not_found:
                raise FileNotFoundError("Mock 'uv' command not found")
            
            if self.should_fail:
                raise subprocess.CalledProcessError(1, args[0], b"Mock error output")
            
            return subprocess.CompletedProcess(args=args, returncode=0, stdout=b"", stderr=b"")

        def reset(self):
            self.called_with_args = []
            self.should_fail = False
            self.command_not_found = False

    mock = MockSubprocessRun()
    import subprocess
    monkeypatch.setattr(subprocess, "run", mock)
    return mock
