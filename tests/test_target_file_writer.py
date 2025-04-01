import os
import shutil
from pathlib import Path
from jinja2 import Template
from doc_flesh.target_file_writer import render_jinja_to_file, make_file_readonly, render_static_to_file
from doc_flesh.models import RepoConfig

def test_render_jinja_to_file_with_existing_file(tmp_path):
    # Setup
    existing_file = tmp_path / "output.txt"
    existing_file.write_text("Old content")
    make_file_readonly(existing_file)

    jinja_template = Template("Hello, {{ name }}!")
    jinja_variables = {"name": "World"}

    # Act
    render_jinja_to_file(jinja_template, existing_file, jinja_variables)

    # Assert
    assert existing_file.read_text() == "Hello, World!"
    assert not os.access(existing_file, os.W_OK)  # File should be read-only

def test_render_jinja_to_file_with_nonexistent_file(tmp_path):
    # Setup
    output_file = tmp_path / "output.txt"
    jinja_template = Template("Hello, {{ name }}!")
    jinja_variables = {"name": "World"}

    # Act
    render_jinja_to_file(jinja_template, output_file, jinja_variables)

    # Assert
    assert output_file.read_text() == "Hello, World!"
    assert not os.access(output_file, os.W_OK)  # File should be read-only

def test_render_static_to_file_with_nonexistent_file(tmp_path):
    # Setup
    src_file = tmp_path / "source.txt"
    src_file.write_text("Static content")
    dest_file = tmp_path / "destination.txt"

    # Act
    render_static_to_file(src_file, dest_file)

    # Assert
    assert dest_file.read_text() == "Static content"
    assert not os.access(dest_file, os.W_OK)  # File should be read-only

def test_render_static_to_file_with_existing_readonly_file(tmp_path):
    # Setup
    src_file = tmp_path / "source.txt"
    src_file.write_text("Updated static content")
    dest_file = tmp_path / "destination.txt"
    dest_file.write_text("Old static content")
    os.chmod(dest_file, 0o444)  # Make destination file read-only

    # Act
    render_static_to_file(src_file, dest_file)

    # Assert
    assert dest_file.read_text() == "Updated static content"
    assert not os.access(dest_file, os.W_OK)  # File should be read-only
