import pytest

from pathlib import Path
from doc_flesh.configtools.reader import append_siteinfo, validate_all_exists, repo_local_paths_to_tmp


def test_validate_all_exists(mock_mytoolconfig):
    """Test that validate_all_exists correctly identifies existing paths."""
    assert validate_all_exists(mock_mytoolconfig) is True


def test_validate_all_exists_missing(mock_mytoolconfig):
    """Test that validate_all_exists correctly identifies missing paths."""
    mock_mytoolconfig.ManagedRepos[0].local_path = Path("/nonexistent/path")
    # Note: ❌ ERROR: Local path /nonexistent/path does not exist.
    assert validate_all_exists(mock_mytoolconfig) is False


def test_append_siteinfo(mock_mytoolconfig):
    """Test that append_siteinfo correctly loads siteinfo.json."""
    c = append_siteinfo(mock_mytoolconfig)

    assert len(c.ManagedRepos) == 2

    assert c.ManagedRepos[0].siteinfo.site_name == "Defined in conftest 1"
    assert c.ManagedRepos[0].siteinfo.site_name_slug == "defined-in-conftest-1"
    assert c.ManagedRepos[0].siteinfo.category == "Learning tools"
    assert c.ManagedRepos[0].siteinfo.related_repo == "[Something](https://example.com)"
    
    assert c.ManagedRepos[1].siteinfo.site_name == "Defined in conftest 2"
    assert c.ManagedRepos[1].siteinfo.site_name_slug == "defined-in-conftest-2"
    assert c.ManagedRepos[1].siteinfo.category == "Learning tools"
    assert c.ManagedRepos[1].siteinfo.related_repo == ""

def test_append_siteinfo_missing(mock_mytoolconfig):
    """Test that append_siteinfo correctly handles missing siteinfo.json."""

    mock_mytoolconfig.ManagedRepos[0].local_path /= "wrong-path"

    # Test that this raises an AssertionError
    with pytest.raises(SystemExit):
        append_siteinfo(mock_mytoolconfig)


def test_repo_local_paths_to_tmp(mock_mytoolconfig):
    """Test that repo_local_paths_to_tmp updates local_path to temporary directories."""
    original_paths = [repo.local_path for repo in mock_mytoolconfig.ManagedRepos]

    updated_repos = repo_local_paths_to_tmp(mock_mytoolconfig.ManagedRepos)
    updated_paths = [repo.local_path for repo in updated_repos]

    # Ensure paths are updated and different from the original
    for original, updated in zip(original_paths, updated_paths):
        assert original != updated
        assert updated.exists()


