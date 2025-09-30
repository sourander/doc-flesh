from doc_flesh.configtools.config_reader import load_config, repo_local_paths_to_tmp, get_siteinfo
from pathlib import Path
import yaml

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


def test_multiple_features_flags_merge(setup_config_file):
    """Test that flags from multiple features are properly merged, not overridden.
    
    This reproduces the bug where only the last feature's flags are kept
    instead of merging all flags from all features.
    """
    
    # Load the config
    repo_configs = load_config(setup_config_file)
    
    # repo_1 has features: ["default", "feature1"] 
    # feature1 has site_uses_mathjax: True
    repo1_config = repo_configs[0]
    
    # repo_2 has features: ["default", "feature2"]
    # feature2 has site_uses_precommit: True  
    repo2_config = repo_configs[1]
    
    # Test that repo1 has the mathjax flag from feature1
    assert repo1_config.flags.site_uses_mathjax == True
    assert repo1_config.flags.site_uses_precommit == False
    
    # Test that repo2 has the precommit flag from feature2
    assert repo2_config.flags.site_uses_mathjax == False
    assert repo2_config.flags.site_uses_precommit == True


def test_multiple_features_with_overlapping_flags(tmp_path: Path):
    """Test a scenario where multiple features both set flags - they should all be merged.
    This is to ensure that flags from multiple features are combined correctly.
    """
    
    # Create the features directory
    config_dir = tmp_path / "config_dir"
    config_dir.mkdir(parents=True, exist_ok=True)
    features_dir = config_dir / "features"
    features_dir.mkdir(parents=True, exist_ok=True)
    
    # Create the default feature file (no flags)
    feature_default_path = features_dir / "default.yaml"
    feature_default = {
        'jinja_files': ['mkdocs.yaml'],
        'static_files': ['.github/workflows/mkdocs-merge.yaml'],
        'flags': {}
    }
    feature_default_path.write_text(yaml.dump(feature_default))

    # Create mathjax feature (sets site_uses_mathjax: true)
    mathjax_feature_path = features_dir / "mathjax.yaml"
    mathjax_feature = {
        'static_files': ['docs/javascripts/mathjax.js'],
        'flags': {'site_uses_mathjax': True}
    }
    mathjax_feature_path.write_text(yaml.dump(mathjax_feature))
    
    # Create extract_exercise_list feature (sets site_uses_precommit: true)
    exercise_feature_path = features_dir / "extract_exercise_list.yaml"
    exercise_feature = {
        'static_files': ['.pre-commit-config.yaml', '.pre-commit-guide.md'],
        'flags': {'site_uses_precommit': True}
    }
    exercise_feature_path.write_text(yaml.dump(exercise_feature))

    # Create the config.yaml file with a repo using both features
    config_path = config_dir / "config.yaml"
    config_data = {
        'ManagedRepos': [{
            'local_path': str(tmp_path / "test_repo"),
            'features': ['default', 'mathjax', 'extract_exercise_list']
        }]
    }
    config_path.write_text(yaml.dump(config_data))

    # Create the test repo with siteinfo.json
    test_repo_path = tmp_path / "test_repo"
    test_repo_path.mkdir(parents=True, exist_ok=True)
    siteinfo = {
        'site_name': 'Test Repo',
        'site_name_slug': 'test-repo',
        'category': 'Learning tools'
    }
    siteinfo_path = test_repo_path / "siteinfo.json"
    siteinfo_path.write_text(yaml.dump(siteinfo))

    # Load the config and test
    repo_configs = load_config(config_path)
    
    assert len(repo_configs) == 1
    repo_config = repo_configs[0]
    
    # Both flags should be True (this is the bug we're testing for)
    assert repo_config.flags.site_uses_mathjax == True
    assert repo_config.flags.site_uses_precommit == True
    
    # Check that files from all features are included
    static_files = [str(f) for f in repo_config.static_files]
    assert 'docs/javascripts/mathjax.js' in static_files
    assert '.pre-commit-config.yaml' in static_files
    assert '.pre-commit-guide.md' in static_files
