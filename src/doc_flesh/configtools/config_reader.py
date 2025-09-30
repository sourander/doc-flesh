import yaml
import click

from tempfile import TemporaryDirectory
from pathlib import Path
from doc_flesh.models import RepoConfig, SiteInfo, EmptySiteInfo, FeatureConfig, RepoConfigFlags, ConfigEntries, ConfigEntry
from pydantic import ValidationError

CONFIG = Path("~/.config/doc-flesh/config.yaml").expanduser()

def validate_all_exists(config_entries: ConfigEntries) -> bool:
    """Check if all local paths in the configuration exist."""
    all_exist = True
    for entry in config_entries.ManagedRepos:
        if not entry.local_path.exists():
            print(f"❌ ERROR: Local path {entry.local_path} does not exist.")
            all_exist = False
    return all_exist


def get_siteinfo(siteinfo_dir: Path) -> SiteInfo:
    """Load siteinfo.json from each repository and add it to RepoConfig.siteinfo.
    
    If siteinfo.json doesn't exist, returns EmptySiteInfo with sensible defaults.
    """
    siteinfo_path = siteinfo_dir / "siteinfo.json"
    if not siteinfo_path.exists():
        print(f"⚠️  No siteinfo.json found in {siteinfo_dir}, using defaults")
        return EmptySiteInfo()

    siteinfo_data = yaml.safe_load(siteinfo_path.read_text())
    return SiteInfo(**siteinfo_data)


def load_feature_config(feature_name: str, yaml_path: Path) -> FeatureConfig:
    """Load a feature configuration from a YAML file (e.g. ~/.config/doc-flesh/features/feature_name.yaml).
    """
    feature_path = yaml_path.parent / "features" / f"{feature_name}.yaml"
    if not feature_path.exists():
        raise FileNotFoundError(f"Feature configuration not found: {feature_path}")

    feature_data = yaml.safe_load(feature_path.read_text())
    return FeatureConfig(**feature_data)


def convert_to_repo_config(entry: ConfigEntry, yaml_path: Path) -> RepoConfig:
    """Add a feature configuration and the siteinfo to the RepoConfig."""
    
    # Load the feature configuration
    feature_configs:list[FeatureConfig] = []
    for feature_name in entry.features:
        try:
            feature_config = load_feature_config(feature_name, yaml_path)
            feature_configs.append(feature_config)
        except FileNotFoundError as e:
            print(f"❌ You are trying to use a feature that does not exist: {feature_name}")
            raise e

    # Combine all features into a single RepoConfig
    combined_jinja_files = []
    combined_static_files = []
    combined_flags = RepoConfigFlags()

    for feature in feature_configs:
        combined_jinja_files.extend(feature.jinja_files)
        combined_static_files.extend(feature.static_files)
        
        # Merge flags properly: combine individual flag values instead of replacing entire object
        # Get current flag values as dict
        current_flags = combined_flags.model_dump()
        feature_flags = feature.flags.model_dump()
        
        # Merge individual flag values (OR operation for boolean flags)
        for flag_name, flag_value in feature_flags.items():
            if flag_value:  # Only set to True if the feature sets it to True
                current_flags[flag_name] = True
        
        # Create new combined_flags object with merged values
        combined_flags = RepoConfigFlags(**current_flags)

    # Remove duplicates
    combined_jinja_files = list(set(combined_jinja_files))
    combined_static_files = list(set(combined_static_files))

    # Create the RepoConfig object
    return RepoConfig(
        local_path=entry.local_path,
        jinja_files=combined_jinja_files,
        static_files=combined_static_files,
        flags=combined_flags,
        siteinfo=get_siteinfo(entry.local_path),
    )


def load_config(yaml_path: Path = CONFIG) -> list[RepoConfig]:
    """Load the configuration from a YAML file into a Pydantic model."""
    # Check that it exists
    if not yaml_path.exists():
        raise FileNotFoundError(f"Config file not found: {yaml_path}")

    # Load
    config_data = yaml.safe_load(yaml_path.read_text())
    config_entries = ConfigEntries(**config_data)
    
    if not validate_all_exists(config_entries):
        raise FileNotFoundError("One or more local paths do not exist. Read above.")
    
    # Convert ConfigEntries objects to RepoConfig objects
    repo_configs = []
    for entry in config_entries.ManagedRepos:
        repo_config = convert_to_repo_config(entry, yaml_path)
        repo_configs.append(repo_config)

    return repo_configs


def repo_local_paths_to_tmp(repoconfigs: list[RepoConfig]) -> list[RepoConfig]:
    """Replace the local paths with temporary directories."""

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
