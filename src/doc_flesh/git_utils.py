import sys

from git import Repo, GitCommandError
from doc_flesh.models import RepoConfig

def check_all(repoconfigs: list[RepoConfig]):
    """Check if repositories are safe."""
    all_safe = True
    for repoconfig in repoconfigs:
        print(f"Checking {repoconfig.local_path}...")

        if not is_repo_safe(repoconfig):
            print(f"Repository {repoconfig.local_path} is not safe.", file=sys.stderr)
            all_safe = False
    return all_safe

def is_repo_up_to_date(repo: Repo):
    """Check if a repo is up-to-date with the remote."""
    print("🔄 Fetching updates from remote...")
    origin = repo.remotes.origin
    origin.fetch()

    # Get local and remote branch references
    local_branch = repo.active_branch
    remote_branch_name = f"origin/{local_branch.name}"

    try:
        # Get commit hashes directly
        local_commit = local_branch.commit.hexsha
        remote_commit = repo.commit(remote_branch_name).hexsha

        if local_commit != remote_commit:
            print(
                f"❌ ERROR: Local branch ({local_commit[:7]}) does not match remote ({remote_commit[:7]}). Aborting."
            )
            return False

        print("✅ Repo is up-to-date with the remote.")
        return True

    except Exception as e:
        print(f"⚠️ ERROR: Could not determine remote branch state: {e}")
        return False


def is_git_operation_in_progress(repoconfig: RepoConfig) -> bool:
    """Check if a Git operation (rebase, merge, cherry-pick) is in progress."""
    git_dir = repoconfig.local_path / ".git"
    git_operations = {
        "Rebase": ["rebase-merge", "rebase-apply"],
        "Merge": ["MERGE_HEAD"],
        "Cherry-pick": ["CHERRY_PICK_HEAD"],
    }

    for operation, files in git_operations.items():

        if any((git_dir / file).exists() for file in files):
            print(
                f"❌ ERROR: Repository has a {operation.lower()} in progress. Aborting."
            )
            return True

    return False


def is_repo_safe(repoconfig: RepoConfig):
    """Check if a repo is safe for automated commits using GitPython."""
    print()
    print(f"🔍 Checking repo: {repoconfig.local_path}")

    if not repoconfig.local_path.exists():
        print("❌ ERROR: Repository does not exist. Aborting.")
        return False

    repo = Repo(repoconfig.local_path)

    if repo.head.is_detached:
        print(
            "❌ ERROR: Repository is in detached HEAD state. Aborting.", file=sys.stderr
        )
        return False

    if repo.active_branch.name != "main":
        print("❌ ERROR: Not on the 'main' branch. Aborting.", file=sys.stderr)
        return False

    if repo.bare:
        print("❌ ERROR: Repository is bare. Aborting.", file=sys.stderr)
        return False

    if repo.is_dirty():
        print("❌ ERROR: Repository is dirty. Aborting.", file=sys.stderr)
        return False

    if is_git_operation_in_progress(repoconfig):
        print("❌ ERROR: Git operation in progress. Aborting.", file=sys.stderr)
        return False

    if not is_repo_up_to_date(repo):
        return False

    print("✅ Repo is clean and safe for automation.", file=sys.stderr)
    return True

def list_repoconfig_files(repoconfig: RepoConfig):
    """Get the list of files to commit."""
    files = [str(repoconfig.local_path / file) for file in repoconfig.jinja_files]
    files += [str(repoconfig.local_path / file) for file in repoconfig.static_files]
    return files

def add_to_staging(repoconfig: RepoConfig):
    """Add files to the staging area using GitPython."""
    try:
        repo = Repo(repoconfig.local_path)

        # Get the list of files to commit
        files = list_repoconfig_files(repoconfig)
        repo.index.add(files)
        
        # Count how many were actually added
        added_files = len(repo.index.diff("HEAD"))
        print(f"✅ Added {added_files}/{len(files)} files to staging area (Rest have no changes).")
    except GitCommandError as e:
        print(f"❌ ERROR: Git command error: {e}", file=sys.stderr)

def commit_and_push(repo_config: RepoConfig):
    """Commit and push changes in a repo using GitPython."""
    try:
        repo = Repo(repo_config.local_path)

        # We should not commit if there are no staged files.
        if not repo.index.diff("HEAD"):
            print(f"🚫 No changes to commit for {repo_config.local_path}")
            return

        # Commit the changes
        commit_msg = "Auto-sync config files by doc-flesh"
        print(f"📝 Committing changes with message: '{commit_msg}'")
        repo.index.commit(commit_msg)

        # Push the changes to the remote repository
        print("🚀 Pushing changes to remote...")
        origin = repo.remotes.origin
        origin.push()
        print(f"✅ Successfully pushed changes to {origin.url}.")
    except GitCommandError as e:
        print(f"❌ ERROR: Git command error: {e}", file=sys.stderr)

