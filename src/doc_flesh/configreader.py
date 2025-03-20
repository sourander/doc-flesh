import yaml

from pathlib import Path
from doc_flesh.models import MyToolConfig

CONFIG = Path("~/.config/doc-flesh/config.yaml").expanduser()

def validate_all_exists(repoconfigs: MyToolConfig) -> bool:
    """Check if all local paths in the configuration exist."""
    all_exist = True
    for repoconfig in repoconfigs.ManagedRepos:
        if not repoconfig.local_path.exists():
            print(f"❌ ERROR: Local path {repoconfig.local_path} does not exist.")
            all_exist = False
    return all_exist

def validate_each_has_siteinfo(repoconfigs: MyToolConfig) -> bool:
    """Check if all local paths in the configuration have a siteinfo.json."""
    all_have_siteinfo = True
    for repoconfig in repoconfigs.ManagedRepos:
        siteinfo = repoconfig.local_path / "siteinfo.json"
        if not siteinfo.exists():
            print(f"❌ ERROR: Local path {repoconfig.local_path} does not have siteinfo.json.")
            all_have_siteinfo = False
    return all_have_siteinfo

def load_config(yaml_path: Path=CONFIG) -> MyToolConfig:
    """Load the configuration from a YAML file into a Pydantic model."""
    # Check that it exists
    if not yaml_path.exists():
        raise FileNotFoundError(f"Config file not found: {yaml_path}")
    
    # Load the YAML file
    managed_repos =  MyToolConfig(**yaml.safe_load(yaml_path.read_text()))

    if not validate_all_exists(managed_repos):
        raise FileNotFoundError("Some local paths do not exist. Please clone the repositories or check config.")
    if not validate_each_has_siteinfo(managed_repos):
        raise FileNotFoundError("Some local paths do not have siteinfo.json. Please create it or check config.")
    
    return managed_repos
