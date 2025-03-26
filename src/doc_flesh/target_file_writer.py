import shutil
import os

from jinja2 import Environment, FileSystemLoader, Template
from pathlib import Path
from doc_flesh.models import RepoConfig
from doc_flesh.models.transformations import transform_to_jinja_variables

def make_file_readonly(file_path: Path):
    os.chmod(file_path, 0o444)

def make_file_writable(file_path: Path):
    os.chmod(file_path, 0o644)

def render_jinja_to_file(jinja_template: Template, output_path: Path, jinja_variables: dict):
    # Make sure we can write
    if output_path.exists():
        make_file_writable(output_path)

    # Generate content
    output = jinja_template.render(jinja_variables)

    # Write and make read-only
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(output)
    make_file_readonly(output_path)

def apply_jinja_template(repoconfig: RepoConfig):
    """Apply Jinja template to the Template file and write it to the destination."""

    print(f"\n📄 Applying Jinja template to {repoconfig.siteinfo.site_name}...")

    # Step 0: Setup the Jinja environment.
    template_dir = Path("~/.config/doc-flesh/templates").expanduser()
    environment = Environment(
        loader=FileSystemLoader(template_dir), extensions=["jinja2_time.TimeExtension"]
    )

    jinja_variables = transform_to_jinja_variables(repoconfig).model_dump()

    for jinjafile in repoconfig.jinja_files:
        jinja_template = environment.get_template(str(jinjafile))
        output_path = Path(repoconfig.local_path) / jinjafile

        render_jinja_to_file(jinja_template, output_path, jinja_variables)

    print(f"Jinja template applied to {repoconfig.siteinfo.site_name}.")

def render_static_to_file(static_file: Path, output_path: Path):
    # Make sure we can write
    if output_path.exists():
        make_file_writable(output_path)

    # Copy the file
    shutil.copy(static_file, output_path)
    make_file_readonly(output_path)

def copy_static_files(repoconfig: RepoConfig):
    """Copy the static files to the destination."""

    base_dir = Path("~/.config/doc-flesh/static").expanduser()

    for static_file in repoconfig.static_files:
        src = base_dir / static_file
        dst = Path(repoconfig.local_path) / static_file
        dst.parent.mkdir(parents=True, exist_ok=True)
        
        render_static_to_file(src, dst)
