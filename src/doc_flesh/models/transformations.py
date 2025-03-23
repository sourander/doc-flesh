from doc_flesh.models import JinjaVariables, RepoConfig

def transform_to_jinja_variables(repoconfig: RepoConfig) -> JinjaVariables:
    """Transform RepoConfig into JinjaVariables."""
    return JinjaVariables(
        site_name=repoconfig.siteinfo.site_name,
        site_name_slug=repoconfig.siteinfo.site_name_slug,
        category=repoconfig.siteinfo.category,
        related_repo=repoconfig.siteinfo.related_repo,
        site_uses_mathjax=repoconfig.flags.site_uses_mathjax,
        site_uses_precommit=repoconfig.flags.site_uses_precommit,
)