import pytest
import yaml
import subprocess

from pathlib import Path
from git import Repo
from dataclasses import dataclass
from typing import Generator

from doc_flesh.models import (
    RepoConfig,
    SiteInfo,
    ConfigEntries,
    ConfigEntry,
    FeatureConfig,
    RepoConfigFlags,
)


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

    # Create siteinfo.json
    siteinfo = SiteInfo(
        site_name="Test Repo", site_name_slug="test-repo", category="Learning tools"
    )

    siteinfo_path = local_path / "siteinfo.json"
    siteinfo_path.write_text(siteinfo.model_dump_json())

    # Create a RepoConfig
    repo_config = RepoConfig(local_path=local_path, siteinfo=siteinfo)

    yield SetupRepoYield(
        temp_dir=temp_dir,
        remote_path=remote_path,
        local_path=local_path,
        local_repo=local_repo,
        remote_repo=remote_repo,
        repo_config=repo_config,
    )

    # No manual cleanup needed—pytest's tmp_path handles it
    print(f"Test complete, temp dir will be auto-removed: {temp_dir}")


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

            return subprocess.CompletedProcess(
                args=args, returncode=0, stdout=b"", stderr=b""
            )

        def reset(self):
            self.called_with_args = []
            self.should_fail = False
            self.command_not_found = False

    mock = MockSubprocessRun()
    import subprocess

    monkeypatch.setattr(subprocess, "run", mock)
    return mock

@pytest.fixture
def setup_config_file(tmp_path: Path) -> Path:
    """This fixture creates a temporary directory with config files 
    for testing the load_config() function.
    
    Created items mimicing the doc-flesh central configuration directory:
        - config_dir/config.yaml (should be ~/.config/doc-flesh/)
        - config_dir/features/default.yaml
        - config_dir/features/feature1.yaml
        - config_dir/features/feature2.yaml

    Created items mimicing what the repositories would have:
        - repo_1/siteinfo.json
        - repo_2/siteinfo.json
    
    We will create TWO separate repositories with different features enabled.
    """

    """
    jinja_files:
    - mkdocs.yaml
    - pyproject.toml
    - README.md
    static_files:
    - .github/workflows/mkdocs-merge.yaml

    Use the model to write the following data into features/default.yaml:
    """

    # Create the features directory
    config_dir = tmp_path / "config_dir"
    config_dir.mkdir(parents=True, exist_ok=True)
    features_dir = config_dir / "features"
    features_dir.mkdir(parents=True, exist_ok=True)
    
    # Create the default feature file
    feature_default_path = features_dir / "default.yaml"
    feature_default = FeatureConfig(
        jinja_files=["mkdocs.yaml", "pyproject.toml", "README.md"],
        static_files=[".github/workflows/mkdocs-merge.yaml"]
    )
    feature_default_path.write_text(yaml.dump(feature_default.model_dump(mode="json")))

    # Create the feature1 file
    feature1_path = features_dir / "feature1.yaml"
    feature1 = FeatureConfig(
        jinja_files=["feature_1_specific_file.toml"],
        static_files=["feature_1_specific_static_file.yaml"],
        flags=RepoConfigFlags(site_uses_mathjax=True)
    )
    feature1_path.write_text(yaml.dump(feature1.model_dump(mode="json")))

    # Create the feature2 file
    feature2_path = features_dir / "feature2.yaml"
    feature2 = FeatureConfig(
        jinja_files=["feature_2_specific_file.md"],
        static_files=["feature_2_specific_static_file.yaml"],
        flags=RepoConfigFlags(site_uses_precommit=True)
    )
    # save as YAML
    feature2_path.write_text(yaml.dump(feature2.model_dump(mode="json")))

    # Create the config.yaml file
    config_path = config_dir / "config.yaml"
    config_entries = ConfigEntries(
        ManagedRepos=[
            ConfigEntry(
                local_path=tmp_path / "repo_1",
                features=["default", "feature1"]
            ),
            ConfigEntry(
                local_path=tmp_path / "repo_2",
                features=["default", "feature2"]
            )
        ]
    )
    config_path.write_text(yaml.dump(config_entries.model_dump(mode="json")))

    # Create the siteinfo.json files for each repo
    siteinfo1 = SiteInfo(
        site_name="Test Repo 1",
        site_name_slug="test-repo-1",
        category="Learning tools"
    )
    siteinfo1_path = tmp_path / "repo_1" / "siteinfo.json"
    siteinfo1_path.parent.mkdir(parents=True, exist_ok=True)
    siteinfo1_path.write_text(yaml.dump(siteinfo1.model_dump(mode="json")))

    siteinfo2 = SiteInfo(
        site_name="Test Repo 2",
        site_name_slug="test-repo-2",
        category="Learning tools"
    )
    siteinfo2_path = tmp_path / "repo_2" / "siteinfo.json"
    siteinfo2_path.parent.mkdir(parents=True, exist_ok=True)
    siteinfo2_path.write_text(yaml.dump(siteinfo2.model_dump(mode="json")))

    return config_path
