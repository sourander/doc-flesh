import subprocess
from pathlib import Path
from typing import Optional
from doc_flesh.models import RepoConfig

def update_uv_dependencies(repoconfigs: list[RepoConfig]) -> bool:
    """
    Update UV dependencies by running 'uv lock --upgrade' in each repository.
    """

    all_safe = True

    for repoconfig in repoconfigs:

        repo = Path(repoconfig.local_path)

        try:
            subprocess.run(["uv", "lock", "--upgrade"], cwd=str(repo), check=True)
        except subprocess.CalledProcessError as e:
            print(f"❌ ERROR: Failed to update dependencies in {repo}. Error: {e}")
            all_safe = False
            break
        except FileNotFoundError:
            print(f"❌ ERROR: 'uv' command not found. Please install it.")
            all_safe = False
            break

    return all_safe