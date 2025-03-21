import click

from git import Repo

from doc_flesh.git_utils import commit_and_push, check_all
from doc_flesh.configreader import load_config, repo_local_paths_to_tmp
from doc_flesh.writer import apply_jinja_template, copy_static_files
from doc_flesh.models import RepoConfig

@click.group()
def cli():
    """CLI for doc_flesh."""
    pass

def run_all_checks(repoconfigs: list[RepoConfig]) -> bool:
    """Check if all repos are safe to sync and have a valid siteinfo.json file.
    """
    # Step 1: Check all repos for cleanliness.
    all_safe = check_all(repoconfigs)
    if not all_safe:
        raise click.Abort()
    
    return True

@cli.command()
def check():
    """Check if the local repotories are safe to sync. The dirtiness is defined in the README."""

    # Read the configuration file
    repoconfigs = load_config().ManagedRepos
    run_all_checks(repoconfigs)

    print()
    print("✅ All repos are clean and safe for automation.")

@cli.command()
@click.option("--dry-run", is_flag=True, help="Write in tempdir. Don't touch Git.")
def sync(dry_run: bool):
    """Deploy the configured Jinja/Static files to production."""
    # Step 1: Check if all repos are safe to sync and have a valid siteinfo.json file.
    repoconfigs = load_config().ManagedRepos
    run_all_checks(repoconfigs)

    # DEBUG! Setting the dry-run flag to True while the code is in development.
    # TODO: Remove before production.
    dry_run = True

    # Step 2: Overwrite the local paths with temporary directories if dry-run is enabled.
    #        This is to prevent any accidental changes to the repositories.
    if dry_run:
        repoconfigs = repo_local_paths_to_tmp(repoconfigs)
    
    # Step 3: Write the files based on JinjaFiles and StaticFiles and push to the remote.
    #         If any step fails, we should abort immediately.
    for repoconfig in repoconfigs:

        apply_jinja_template(repoconfig)
        copy_static_files(repoconfig)
        

        if dry_run:
            print(f"🔧 Dry-run: skipping the Git operations.")
        else:
            remote_url = Repo(repoconfig.local_path).remotes.origin.url
            # commit_and_push(repoconfig)
            print(f"✅ Successfully pushed changes to {remote_url}.")
    
    print("🎉 Sync complete.")