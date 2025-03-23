import shutil

from jinja2 import Environment, FileSystemLoader
from pathlib import Path
from doc_flesh.models import RepoConfig
from doc_flesh.models.transformations import transform_to_jinja_variables


def apply_jinja_template(repoconfig: RepoConfig):
    """Apply Jinja template to the Template file and write it to the destination."""

    print(f"📄 Applying Jinja template to {repoconfig.siteinfo.site_name}...")

    # Step 0: Setup the Jinja environment.
    template_dir = Path("~/.config/doc-flesh/templates").expanduser()
    environment = Environment(
        loader=FileSystemLoader(template_dir), extensions=["jinja2_time.TimeExtension"]
    )

    # Step 1: Transform RepoConfig to JinjaVariables.
    jinja_variables = transform_to_jinja_variables(repoconfig).model_dump()

    # Step 2: Load the Jinja file.
    for jinjafile in repoconfig.jinja_files:
        jinja_template = environment.get_template(str(jinjafile))

        # Step 3: Apply the Jinja template.
        output = jinja_template.render(jinja_variables)

        # Step 4: Write the output file
        output_path = Path(repoconfig.local_path) / jinjafile
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(output)

    print(f"Jinja template applied to {repoconfig.siteinfo.site_name}.")


def copy_static_files(repoconfig: RepoConfig):
    """Copy the static files to the destination."""

    base_dir = Path("~/.config/doc-flesh/static").expanduser()

    for static_file in repoconfig.static_files:
        src = base_dir / static_file
        dst = Path(repoconfig.local_path) / static_file
        dst.parent.mkdir(parents=True, exist_ok=True)
        
        shutil.copy(src, dst)
