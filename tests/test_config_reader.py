from doc_flesh.configtools.config_reader import load_config, repo_local_paths_to_tmp, get_siteinfo
from pathlib import Path

def test_load_config(setup_config_file):
    """Test the load_config wrapper function."""

    repo_configs = load_config(setup_config_file)

    # Test that most of the attributes are correct
    assert len(repo_configs) == 2
    assert repo_configs[0].local_path == (setup_config_file.parent.parent / "repo_1").resolve()
    assert repo_configs[1].local_path == (setup_config_file.parent.parent / "repo_2").resolve()
    
    # Jinja files
    assert len(repo_configs[0].jinja_files) == 4
    assert len(repo_configs[1].jinja_files) == 4
    assert Path("mkdocs.yaml") in repo_configs[0].jinja_files
    assert Path("feature_1_specific_file.toml") in repo_configs[0].jinja_files
    assert Path("feature_1_specific_file.toml") not in repo_configs[1].jinja_files
    assert Path("feature_2_specific_file.md") in repo_configs[1].jinja_files
    assert Path("feature_2_specific_file.md") not in repo_configs[0].jinja_files

    # Static files
    assert len(repo_configs[0].static_files) == 2
    assert len(repo_configs[1].static_files) == 2
    assert Path("feature_1_specific_static_file.yaml") in repo_configs[0].static_files
    assert Path("feature_2_specific_static_file.yaml") not in repo_configs[0].static_files

    # Check that siteinfo is there
    assert repo_configs[0].siteinfo.site_name == "Test Repo 1"
    assert repo_configs[1].siteinfo.site_name == "Test Repo 2"


"""
def repo_local_paths_to_tmp(repoconfigs: list[RepoConfig]) -> list[RepoConfig]:

    # Create a Temporary Directory. It should be persistent so that users can inspect the files.
    tmpdir = TemporaryDirectory(delete=False)
    tmpdir = Path(tmpdir.name).resolve()
    print(
        f"🔧 All files will be written to {tmpdir} under directories with the same name as each repository."
    )

    # We will build a new list to avoid potential issues
    updated_repoconfigs = []

    for repoconfig in repoconfigs:
        # Use only the repository's name for the temporary directory
        this_repo_dir = tmpdir / repoconfig.local_path.name
        this_repo_dir.mkdir(parents=True, exist_ok=True)
        updated_repo = repoconfig.model_copy(update={"local_path": this_repo_dir})
        updated_repoconfigs.append(updated_repo)

    return updated_repoconfigs
    """

def test_repo_local_paths_to_tmp(setup_config_file):
    """Test the repo_local_paths_to_tmp function."""

    # Load the config
    repo_configs = load_config(setup_config_file)

    orig_path_1 = repo_configs[0].local_path.resolve()
    orig_path_2 = repo_configs[1].local_path.resolve()

    # Convert to temporary paths
    updated_repo_configs = repo_local_paths_to_tmp(repo_configs)

    # Check that they are still directories
    for repo_config in updated_repo_configs:
        assert repo_config.local_path.is_dir()

    # Check that the original paths are not the same as the updated paths
    assert updated_repo_configs[0].local_path != orig_path_1
    assert updated_repo_configs[1].local_path != orig_path_2


"""
def get_siteinfo(siteinfo_dir: Path) -> SiteInfo:

    siteinfo_path = siteinfo_dir / "siteinfo.json"
    if not siteinfo_path.exists():
        raise FileNotFoundError(f"Site info file not found: {siteinfo_path}")

    siteinfo_data = yaml.safe_load(siteinfo_path.read_text())
    return SiteInfo(**siteinfo_data)
    """

def test_get_siteinfo(setup_config_file):
    """Test the get_siteinfo function."""

    # Load the config
    repo_configs = load_config(setup_config_file)

    # Get the siteinfo for the first repo
    siteinfo = get_siteinfo(repo_configs[0].local_path)

    # Check that the siteinfo is correct
    assert siteinfo.site_name == "Test Repo 1"
