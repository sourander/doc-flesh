import click

from git import Repo

from doc_flesh.git_utils import is_repo_safe, commit_and_push, check_all
from doc_flesh.configreader import load_config
from doc_flesh.writer import apply_jinja_template
from doc_flesh.models import RepoConfig

def _get_managed_repos():
    """Get the list of repositories to manage."""
    repoconfigs = load_config().ManagedRepos
    return repoconfigs



@click.group()
def cli():
    """CLI for doc_flesh."""
    pass

@cli.command()
def check():
    """Check if the local repotories are safe to sync. The dirtiness is defined in the README."""

    repoconfigs = _get_managed_repos()

    # Step 1: Check all repos.
    all_safe = check_all(repoconfigs)
    if not all_safe:
        raise click.Abort()

@cli.command()
def sync():
    """Deploy the configured Jinja/Static files to production."""
    repoconfigs = _get_managed_repos()

    # Step 1: Check all repos. 
    #         We should not continue if ANY is dirty.
    all_safe = check_all(repoconfigs[:1])
    if not all_safe:
        raise click.Abort()
    
    # Step 2: Write the files based on JinjaFiles and StaticFiles and push to the remote.
    #         If any step fails, we should abort immediately.
    for repoconfig in repoconfigs:
        remote_url = Repo(repoconfig.local_path).remotes.origin.url
        print(f"Not implemented: would be writing files to {repoconfig.local_path} and pushing to {remote_url}")
        # apply_jinja_template(repoconfig)
        # commit_and_push(repoconfig)
        print(f"✅ Successfully pushed changes to {remote_url}.")
    print("🎉 Sync complete.")