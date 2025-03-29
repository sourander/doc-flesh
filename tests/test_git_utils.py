from doc_flesh.git_utils import is_repo_safe, commit_and_push, add_to_staging, add_uv_lock_to_staging
from git import Repo


def test_repo_safe_clean_repo(setup_repos):
    """Test is_repo_safe returns True for clean repo."""
    # Clean repo should be safe
    assert is_repo_safe(setup_repos.repo_config) is True


def test_repo_safe_new_untracked_file(setup_repos):
    """Test is_repo_safe should be ok with new files that are NOT tracked."""
    # Create a file but don't commit it
    test_file = setup_repos.local_path / "dirty.txt"
    test_file.write_text("Making repo dirty")
    
    assert is_repo_safe(setup_repos.repo_config)

def test_repo_safe_new_tracked_file(setup_repos):
    """Test is_repo_safe should NOT be ok with new files that ARE tracked."""
    # Create a file and commit it
    test_file = setup_repos.local_path / "dirty.txt"
    test_file.write_text("Making repo dirty")
    setup_repos.local_repo.index.add([str(test_file)])
    
    # Note: ❌ ERROR: Repository is dirty. Aborting.
    assert is_repo_safe(setup_repos.repo_config) is False

def test_repo_safe_new_tracked__and_committed_file(setup_repos):
    """Test is_repo_safe should NOT be ok with new files that ARE tracked."""
    # Create a file and commit it
    test_file = setup_repos.local_path / "dirty.txt"
    test_file.write_text("Making repo dirty")
    setup_repos.local_repo.index.add([str(test_file)])
    setup_repos.local_repo.index.commit("Adding dirty file")
    
    # Note: ❌ ERROR: Local branch (hash) does not match remote (diffhash). Aborting.
    assert is_repo_safe(setup_repos.repo_config) is False

def test_repo_safe_wrong_branch(setup_repos):
    """Test is_repo_safe returns False when not on main branch."""
    # Create and checkout a new branch
    local_repo = setup_repos.local_repo
    local_repo.git.checkout("-b", "feature-branch")
    
    # Note: ❌ ERROR: Not on the 'main' branch. Aborting.
    assert is_repo_safe(setup_repos.repo_config) is False

def test_repo_safe_behind_remote(setup_repos):
    """Test is_repo_safe returns False when behind remote.
    
    Instead of modifying the bare remote directly, we'll:
    1. Create a second local clone
    2. Make a change in that clone
    3. Push to the remote
    4. Check if our original local repo is detected as behind
    """
    # Create a second local clone in a different directory
    second_local_path = setup_repos.temp_dir / "second-local"
    second_local = Repo.clone_from(str(setup_repos.remote_path), str(second_local_path))
    
    # Make a change in the second local repo
    test_file = second_local_path / "test.txt"
    test_file.write_text("Remote change")
    second_local.git.add("test.txt")
    second_local.git.commit("-m", "Change from second local")
    
    # Push to remote
    second_local.git.push("origin", "main")
    
    # Now our main local repo should be behind remote
    # Note: ❌ ERROR: Local branch (hash) does not match remote (diffhash). Aborting.
    assert is_repo_safe(setup_repos.repo_config) is False

def test_repo_safe_detached_head(setup_repos):
    """Test is_repo_safe returns False when in detached HEAD state.
    
    1. Create 3 commits and push to remote. This way we will actually have HEAD~1.
    2. Checkout HEAD~1
    3. Check if is_repo_safe returns False
    """
    
    # Create 3 commits and push to remote
    for i in range(3):
        test_file = setup_repos.local_path / f"test-{i}.txt"
        test_file.write_text(f"Test content {i}")
        setup_repos.local_repo.index.add([str(test_file.resolve())])
        setup_repos.local_repo.index.commit(f"Commit {i}")
    
    setup_repos.local_repo.git.push("origin", "main")
    
    # Checkout HEAD~1 to enter detached HEAD state
    setup_repos.local_repo.git.checkout("HEAD~1")
    
    # Note: ❌ ERROR: Repository is in detached HEAD state. Aborting.
    assert is_repo_safe(setup_repos.repo_config) is False

def test_commit_and_push(setup_repos):
    """Commit files to origin main and check they actually get there.
    """

    repo_config = setup_repos.repo_config

    # Let's add some files to the RepoConfig pydantic object
    repo_config.jinja_files = ["test.txt"]
    repo_config.static_files = ["another_test.txt"]
    
    # Create both files
    test_file = setup_repos.local_path / "test.txt"
    test_file.write_text("Test content")
    another_test_file = setup_repos.local_path / "another_test.txt"
    another_test_file.write_text("Another test content")

    # Add files to staging
    add_to_staging(setup_repos.repo_config)

    # Call the tested function
    commit_and_push(setup_repos.repo_config)

    # git ls-tree -r --name-only HEAD
    remote_files = setup_repos.remote_repo.git.ls_tree("HEAD", r=True).splitlines()
    remote_files = [line.split()[-1] for line in remote_files]
    assert "test.txt" in remote_files
    assert "another_test.txt" in remote_files

def test_commit_no_changes(setup_repos):
    """Test commit_and_push does nothing when there are no changes to commit."""
    repo_config = setup_repos.repo_config

    # Add a file to the RepoConfig
    repo_config.jinja_files = ["test.txt"]

    # Rewrite the file with the same content (no actual changes)
    test_file = setup_repos.local_path / "test.txt"
    test_file.write_text("Test content")  # Same content as in the initial commit

    # Add files to staging
    add_to_staging(setup_repos.repo_config)

    # Call the tested function
    commit_and_push(setup_repos.repo_config)
    # Note: 🚫 No changes to commit for test-repo

    # Assert no new commits were made after the initial commit
    log = list(setup_repos.local_repo.iter_commits("main"))
    assert len(log) == 1  # Only the initial commit should exist

def test_add_uv_lock_to_staging(setup_repos):
    """Test that add_uv_lock_to_staging correctly adds uv.lock to the staging area."""
    repo_config = setup_repos.repo_config
    
    # Create a uv.lock file
    uv_lock_file = setup_repos.local_path / "uv.lock"
    uv_lock_file.write_text("Lock file content")
    
    # Call the function
    add_uv_lock_to_staging(repo_config)
    
    # Check that the file is in the staging area
    staged_files = setup_repos.local_repo.git.diff("--name-only", "--cached").splitlines()
    assert "uv.lock" in staged_files

def test_add_uv_lock_no_changes(setup_repos):
    """Test add_uv_lock_to_staging when the file exists but has no changes."""
    repo_config = setup_repos.repo_config
    
    # Create and commit the uv.lock file first
    uv_lock_file = setup_repos.local_path / "uv.lock"
    uv_lock_file.write_text("Original lock file")
    setup_repos.local_repo.git.add("uv.lock")
    setup_repos.local_repo.git.commit("-m", "Add uv.lock file")
    
    # Make sure the staging area is clean
    assert not setup_repos.local_repo.index.diff("HEAD")
    
    # Call the function with no changes to the file
    add_uv_lock_to_staging(repo_config)
    
    # Verify no new changes were staged
    assert not setup_repos.local_repo.index.diff("HEAD")

def test_add_uv_lock_with_changes(setup_repos):
    """Test add_uv_lock_to_staging when the file exists and has changes."""
    repo_config = setup_repos.repo_config
    
    # Create and commit the uv.lock file first
    uv_lock_file = setup_repos.local_path / "uv.lock"
    uv_lock_file.write_text("Original lock file")
    setup_repos.local_repo.git.add("uv.lock")
    setup_repos.local_repo.git.commit("-m", "Add uv.lock file")
    
    # Make a change to the file
    uv_lock_file.write_text("Updated lock file content")
    
    # Call the function
    add_uv_lock_to_staging(repo_config)
    
    # Verify the change was staged
    staged_files = setup_repos.local_repo.git.diff("--name-only", "--cached").splitlines()
    assert "uv.lock" in staged_files

def test_add_uv_lock_commit_and_push(setup_repos):
    """A tiny integration test that checks if add_uv_lock_to_staging and commit_and_push work together.
    
    This test:
    1. Creates a uv.lock file
    2. Uses add_uv_lock_to_staging to stage it
    3. Uses commit_and_push to commit and push it
    4. Verifies the file exists in the remote repository
    """
    repo_config = setup_repos.repo_config
    
    # Create a uv.lock file
    uv_lock_file = setup_repos.local_path / "uv.lock"
    uv_lock_file.write_text("Integration test lock file content")
    
    # Add the file to staging
    add_uv_lock_to_staging(repo_config)
    
    # Commit and push the changes
    commit_and_push(repo_config)
    
    # Verify that the file is now in the remote repository
    remote_files = setup_repos.remote_repo.git.ls_tree("HEAD", r=True).splitlines()
    remote_files = [line.split()[-1] for line in remote_files]

    assert "uv.lock" in remote_files
