import yaml
import click

from tempfile import TemporaryDirectory
from pathlib import Path
from doc_flesh.models import MyToolConfig, RepoConfig, SiteInfo
from pydantic import ValidationError

CONFIG = Path("~/.config/doc-flesh/config.yaml").expanduser()


def validate_all_exists(mytoolconfig: MyToolConfig) -> bool:
    """Check if all local paths in the configuration exist."""
    all_exist = True
    for repoconfig in mytoolconfig.ManagedRepos:
        if not repoconfig.local_path.exists():
            print(f"❌ ERROR: Local path {repoconfig.local_path} does not exist.")
            all_exist = False
    return all_exist


def append_siteinfo(mytoolconfig: MyToolConfig) -> MyToolConfig:
    """Load siteinfo.json from each repository and add it to RepoConfig.siteinfo."""
    
    all_valid = True

    for repoconfig in mytoolconfig.ManagedRepos:
        
        siteinfo_path = repoconfig.local_path / "siteinfo.json"
        if siteinfo_path.exists():
            try:
                repoconfig.siteinfo = SiteInfo.model_validate_json(
                    siteinfo_path.read_text()
                )
            except ValidationError as e:
                print(
                    f"❌ ERROR: Invalid siteinfo.json in {repoconfig.local_path}"
                )
                all_valid = False
                continue
        else:
            print(f"⚠️ WARNING: siteinfo.json not found in {repoconfig.local_path}.")
            all_valid = False

    # assert (all_valid), "Aborting. Some repositories do not have a valid siteinfo.json. Read above."
    if not all_valid:
        raise SystemExit("Aborting. Some repositories do not have a valid siteinfo.json. Read above.")
    return mytoolconfig


def load_config(yaml_path: Path = CONFIG) -> MyToolConfig:
    """Load the configuration from a YAML file into a Pydantic model."""
    # Check that it exists
    if not yaml_path.exists():
        raise FileNotFoundError(f"Config file not found: {yaml_path}")

    # Load
    mytoolconfig = MyToolConfig(**yaml.safe_load(yaml_path.read_text()))

    if not validate_all_exists(mytoolconfig):
        raise FileNotFoundError(
            "Some local paths do not exist. Please clone the repositories or check config."
        )

    mytoolconfig = append_siteinfo(mytoolconfig)

    return mytoolconfig


def repo_local_paths_to_tmp(repoconfigs: list[RepoConfig]) -> list[RepoConfig]:
    """Replace the local paths with temporary directories."""

    # Create a Temporary Directory. It should be persistent so that users can inspect the files.
    tmpdir = TemporaryDirectory(delete=False)
    tmpdir = Path(tmpdir.name).resolve()
    print(
        f"🔧 All files will be written to {tmpdir} under directories with the same name as each repository."
    )
    for repoconfig in repoconfigs:
        this_repo_dir = tmpdir / repoconfig.name
        this_repo_dir.mkdir(parents=True, exist_ok=True)
        repoconfig.local_path = this_repo_dir

    return repoconfigs
