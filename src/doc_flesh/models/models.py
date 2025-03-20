from pydantic import BaseModel
from typing import List, Dict
from pathlib import Path

class RepoConfig(BaseModel):
    """Each entitty in list called ManagedRepos in the configuration file."""
    local_path: Path
    name: str
    jinja_files: List[Path] = []
    static_files: List[Path] = []

class MyToolConfig(BaseModel):
    """The ~/.config/doc-flesh/config.yaml configuration file model.

    Note: 
        We are not keeping the top-level Files key. It is only used for YAML anchoring.
    """
    ManagedRepos: List[RepoConfig]
    # Files: ...