import click

from doc_flesh.git_utils import add_to_staging, commit_and_push, check_all, add_uv_lock_to_staging
from doc_flesh.configtools.config_reader import load_config, repo_local_paths_to_tmp
from doc_flesh.configtools.siteinfo_generator import generate_and_write_siteinfo
from doc_flesh.target_file_writer import apply_jinja_template, copy_static_files
from doc_flesh.uv_utils import update_uv_dependencies
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
def version():
    """Show the version of doc-flesh (hardcoded for now)."""
    print(f"doc-flesh is 0.1.2")

@cli.command()
def check():
    """Check if the local repotories are safe to sync. The dirtiness is defined in the README."""

    # Read the configuration file
    repoconfigs = load_config()
    run_all_checks(repoconfigs)

    print()
    print("✅ All repos are clean and safe for automation.")

@cli.command()
@click.option("--dry-run", is_flag=True, help="Write in tempdir. Don't touch Git.")
@click.option("--no-commit", is_flag=True, help="Add files but don't commit.")
def sync(dry_run: bool, no_commit: bool):
    """Deploy the configured Jinja/Static files to production."""
    # Step 1: Check if all repos are safe to sync and have a valid siteinfo.json file.
    repoconfigs = load_config()
    run_all_checks(repoconfigs)

    # Step 2: Overwrite the local paths with temporary directories if dry-run is enabled.
    #        This is to prevent any accidental changes to the repositories.
    if dry_run:
        repoconfigs = repo_local_paths_to_tmp(repoconfigs)
    
    # Step 3: Write the files based on JinjaFiles and StaticFiles and push to the remote.
    #         If any step fails, we should abort immediately.
    for repoconfig in repoconfigs:

        apply_jinja_template(repoconfig)
        copy_static_files(repoconfig)
        
        if not dry_run:
            add_to_staging(repoconfig)
            if not no_commit:
                commit_and_push(repoconfig)
    
    print("🎉 Sync complete.")

@cli.command() # Add a positional parameter to specify the path.
@click.argument("siteinfo_dir", default=".", type=click.Path(exists=True))
def generate_siteinfo(siteinfo_dir: str):
    """Generate the siteinfo.json file to given path. Default: pwd"""
    
    generate_and_write_siteinfo(siteinfo_dir)

@cli.command()
def uv_upgrade():
    """Run `uv lock --upgrade` in all managed repositories."""
    # Read the configuration file
    repoconfigs = load_config()

    # Step 1: Check all repos for cleanliness.
    all_safe = check_all(repoconfigs)
    if not all_safe:
        raise click.Abort()

    # Step 2: Run `uv sync -upgrade` in each repository.
    all_safe = update_uv_dependencies(repoconfigs)
    if not all_safe:
        raise click.Abort()
    print("✅ All uv.lock files are up to date.")

    # Step 3: Write the files based on JinjaFiles and StaticFiles and push to the remote.
    #         If any step fails, we should abort immediately.
    for repoconfig in repoconfigs:
        add_uv_lock_to_staging(repoconfig)
        commit_and_push(repoconfig)