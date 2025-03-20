import pytest
import tempfile
import shutil
from pathlib import Path
from git import Repo
from doc_flesh.models import RepoConfig
from dataclasses import dataclass
from typing import Generator

@dataclass
class SetupRepoYield:
    temp_dir: Path
    remote_path: Path
    local_path: Path
    local_repo: Repo
    remote_repo: Repo
    repo_config: RepoConfig

@pytest.fixture
def setup_repos() -> Generator[SetupRepoYield, None, None]:
    """Create temporary directory with both remote and local Git repositories.
    
    The three parts in Generator[SetupRepoYield, None, None] are:
    Generator[YIELD_TYPE, SEND_TYPE, RETURN_TYPE]
    """
    temp_dir = Path(tempfile.mkdtemp())
    temp_dir = temp_dir.resolve()
    print(f"Created temp dir: {temp_dir}")

    try:
        # Create "remote" bare repository
        remote_path = temp_dir / "remote.git"
        remote_repo = Repo.init(remote_path, bare=True)

        # Create "local" repository
        local_path = temp_dir / "local"
        local_repo = Repo.init(str(local_path), mkdir=True)

        # Create main branch
        # git checkout -b main
        local_repo.git.checkout("-b", "main")

        # Add remote to local repo
        origin = local_repo.create_remote("origin", str(remote_path))

        # Create a file and commit
        test_file = local_path / "test.txt"
        test_file.write_text("Test content")

        # $ git add <file>
        add_file = [str(test_file)]
        local_repo.index.add(add_file)

        # $ git commit -m <message>
        local_repo.index.commit("Initial commit")

        # git push origin main --set-upstream
        local_repo.git.push("origin", "main", set_upstream=True)
        

        yield SetupRepoYield(
            temp_dir=temp_dir,
            remote_path=remote_path,
            local_path=local_path,
            local_repo=local_repo,
            remote_repo=remote_repo,
            repo_config=RepoConfig(local_path=local_path, name="test-repo"),
        )

    finally:
        # Cleanup after test, ensuring temp directories are removed
        shutil.rmtree(temp_dir, ignore_errors=True)
        print(f"Removed temp dir: {temp_dir}")
