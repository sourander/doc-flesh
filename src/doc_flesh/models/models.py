from pydantic import BaseModel, field_validator, Field
from typing import List
from pathlib import Path
from enum import Enum

class SiteCategory(str, Enum):
    """The SiteInfo.category field is only allowed to be one of these values. 
    These are used by the index site for grouping the sites.
    """
    learning_tools = "Learning tools"
    study_materials = "Study materials"
    templates = "Templates"

class SiteInfo(BaseModel):
    """Each repository should have a site info file in the project root."""

    # MkDocs
    site_name: str
    site_name_slug: str

    # sourander.github.io
    category: SiteCategory
    related_repo: str = ""

    @field_validator('related_repo', mode='after')
    @classmethod
    def validate_related_repo(cls, value:str):
        if not value:
            return value
        if not value.startswith("["):
            raise ValueError("Related repo should be a markdown link.")
        return value

class RepoConfigFlags(BaseModel):
    """Boolean flags for RepoConfig."""
    site_uses_mathjax: bool = False
    site_uses_precommit: bool = False


class RepoConfig(BaseModel):
    """Each entitty in list called ManagedRepos in the configuration file."""
    local_path: Path
    jinja_files: List[Path] = []
    static_files: List[Path] = []
    siteinfo: SiteInfo = None

    # Boolean flags
    flags: RepoConfigFlags = Field(default_factory=RepoConfigFlags)

class MyToolConfig(BaseModel):
    """The ~/.config/doc-flesh/config.yaml configuration file model.

    Note: 
        We are only keepint the top-level ManagedRepos list in this model.
        The rest are used for YAML anchoring (&something and *something).
    """
    ManagedRepos: List[RepoConfig]


class JinjaVariables(BaseModel):
    """Model for Jinja template variables."""
    site_name: str
    site_name_slug: str
    category: SiteCategory
    related_repo: str
    site_uses_mathjax: bool
    site_uses_precommit: bool

