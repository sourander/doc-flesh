import os
import json

from jinja2 import Template, Environment, FileSystemLoader
from pathlib import Path
from doc_flesh.models import RepoConfig

def apply_jinja_template(repoconfig: RepoConfig):
    """This function is currenlty work in progress. It will apply the Jinja template to the
    source files and write the output to the destination files. StaticFiles will not require templating. They are simply copied over.
    
    Here is my thought process:

    repo.config.local_path will look like this: `/Users/janisou1/Code/sourander/oat/`. It is an absolute path to the local git repository.
    repo.config.JinjaFiles will look like this: ["mkdocs.yml"]
    repo.config.StaticFiles will look like this: [".github/workflows/mkdocs-merge.yaml", "docs/javascripts/mathjax.js"]

    The variables used in the Jinja template will be defined in a mandatory `siteinfo.json` file in the root of the repository.
    It needs to include all keys used in any Jinja template within that repository. If not, we need to raise an error. The schema of the file
    will be documented later into a models/ directory.

    Thus, for each Jinja file, we need to:
    0. Setup the Jinja environment.
    1. Load the siteinfo.json file. (`repo.config.local_path + siteinfo.json`)
    2. (loop) Load the Jinja file. (`~/.configs/doc_flesh/ + relative path`)
    3. (loop) Apply the Jinja template.
    4. (loop) Write the output to the destination file. (`repo.config.local_path + relative path`)

    For each StaticFile, we need to:
    * Copy the StaticFiles to the destination. (`repo.config.local_path + relative path`)
    """

    print(f"Applying Jinja template to {repoconfig.name}...")

    # TODO: Implement dry-run functionality. It should write the files to a temporary directory instead of the actual one.

    # Step 0: Setup the Jinja environment.
    environment = Environment(loader=FileSystemLoader("~/.configs/doc_flesh"))
    
    # Step 1: Load the siteinfo.json file.
    siteinfo_path = Path(repoconfig.local_path) / "siteinfo.json"

    # TODO: Use /models/ Pydantic model instead of dict.
    siteinfo:dict = json.loads(siteinfo_path.read_text())

    # Step 2: Load the Jinja file.
    for jinjafile in repoconfig.JinjaFiles:
        
        # Get templare allows the input to be a relative path, but it needs to be resolved into a string.
        jinja_template = environment.get_template(str(jinjafile))
        
        # Step 3: Apply the Jinja template.
        output = jinja_template.render(siteinfo)
        
        # Step 4: We will simply display the output for now.
        print(f" ==== {jinjafile} OUTPUT ====")
        print(output)
        print(" ==== END ====")
        print()

    # TODO: Use Path instead of os.path.join.
    # # Only step: Copy the StaticFiles to the destination.
    # for staticfile in repoconfig.StaticFiles:
    #     staticfile_path = os.path.join(repoconfig.local_path, staticfile)
    #     output_path = os.path.join(repoconfig.local_path, "templates", staticfile)
    #     os.makedirs(os.path.dirname(output_path), exist_ok=True)
    #     os.system(f"cp {staticfile_path} {output_path}")

    print(f"Jinja template applied to {repoconfig.name}.")