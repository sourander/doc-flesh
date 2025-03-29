import pytest
from pathlib import Path
import subprocess

from doc_flesh.models import RepoConfig
from doc_flesh.uv_utils import update_uv_dependencies


def test_update_uv_dependencies_success(tmp_path, mock_subprocess_run):
    """Test successful update of UV dependencies."""
    # Setup test repositories
    repo1_path = tmp_path / "repo1"
    repo1_path.mkdir()
    repo2_path = tmp_path / "repo2"
    repo2_path.mkdir()
    
    repos = [
        RepoConfig(local_path=repo1_path),
        RepoConfig(local_path=repo2_path)
    ]
    
    # Run the function
    result = update_uv_dependencies(repos)
    
    # Assertions
    assert result is True
    assert len(mock_subprocess_run.called_with_args) == 2
    
    # Check first call
    args1, kwargs1 = mock_subprocess_run.called_with_args[0]
    assert args1[0] == ["uv", "lock", "--upgrade"]
    assert kwargs1["cwd"] == str(repo1_path)
    assert kwargs1["check"] is True
    
    # Check second call
    args2, kwargs2 = mock_subprocess_run.called_with_args[1]
    assert args2[0] == ["uv", "lock", "--upgrade"]
    assert kwargs2["cwd"] == str(repo2_path)
    assert kwargs2["check"] is True


def test_update_uv_dependencies_command_error(tmp_path, mock_subprocess_run):
    """Test handling of command execution error."""
    repo_path = tmp_path / "repo"
    repo_path.mkdir()
    repos = [RepoConfig(local_path=repo_path)]
    
    # Set mock to fail
    mock_subprocess_run.should_fail = True
    
    # Run the function
    result = update_uv_dependencies(repos)
    
    # Assertions
    assert result is False
    assert len(mock_subprocess_run.called_with_args) == 1


def test_update_uv_dependencies_command_not_found(tmp_path, mock_subprocess_run):
    """Test handling of UV command not found."""
    repo_path = tmp_path / "repo"
    repo_path.mkdir()
    repos = [RepoConfig(local_path=repo_path)]
    
    # Set mock to simulate command not found
    mock_subprocess_run.command_not_found = True
    
    # Run the function
    result = update_uv_dependencies(repos)
    
    # Assertions
    assert result is False
    assert len(mock_subprocess_run.called_with_args) == 1
