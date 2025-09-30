import re

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
    inactive = "Inactive"

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
        
        # Pattern for: [Text here](url here) 
        pattern = r"^\[.*\]\(.*\)$"
        if not re.match(pattern, value):
            raise ValueError("Related repo should be a markdown link.")
        
        return value


class EmptySiteInfo(SiteInfo):
    """Default SiteInfo used when no siteinfo.json exists or when creating test instances."""
    
    def __init__(self, **data):
        # Provide sensible defaults
        defaults = {
            "site_name": "Unnamed Site",
            "site_name_slug": "unnamed-site",
            "category": SiteCategory.inactive,
            "related_repo": ""
        }
        # Allow overrides via **data
        defaults.update(data)
        super().__init__(**defaults)

class RepoConfigFlags(BaseModel):
    """Boolean flags for RepoConfig that are supported and tested by doc-flesh."""
    site_uses_mathjax: bool = False
    site_uses_precommit: bool = False


class RepoConfig(BaseModel):
    """This is the target data model that will be used by other modules in doc-flesh.
    """
    local_path: Path
    jinja_files: List[Path] = Field(default_factory=list)
    static_files: List[Path] = Field(default_factory=list)
    siteinfo: SiteInfo = Field(default_factory=EmptySiteInfo)

    # Boolean flags
    flags: RepoConfigFlags = Field(default_factory=RepoConfigFlags)

class FeatureConfig(BaseModel):
    """A feature activated in the configuration file. They are defined in files `~/.config/doc-flesh/features/*.yaml`.
    
    All these will be concatenated to form the final RepoConfig.
    """
    jinja_files: List[Path] = Field(default_factory=list)
    static_files: List[Path] = Field(default_factory=list)
    flags: RepoConfigFlags = Field(default_factory=RepoConfigFlags)

class ConfigEntry(BaseModel):
    """Each entry in the config.yml file. Features are activated by adding them here.
    """
    local_path: Path
    features: List[str] = Field(default_factory=list)

class ConfigEntries(BaseModel):
    """All entries in the config.yml file. This is the main entry point for doc-flesh.
    """
    ManagedRepos: List[ConfigEntry] = Field(default_factory=list)

class JinjaVariables(BaseModel):
    """Model for Jinja template variables."""
    site_name: str
    site_name_slug: str
    category: SiteCategory
    related_repo: str
    site_uses_mathjax: bool
    site_uses_precommit: bool

