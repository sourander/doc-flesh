# doc-flesh

Ah, some flesh for [doc-skeleton](https://github.com/sourander/doc-skeleton) template's bones! This tool allows hosting canonical config files in HOME directory and syncing those to ALL repositories based on doc-skeleton locally.

![alt](assets/template-flow.png)

**Diagram 1:** *The flow from `~/.config/.../` to X different repository directories explained as a diagram. The files are then committed and pushed to origin main. The `siteinfo.json`, used by `sourander.github.io` index site, is borrowed for site name and slug. There are placed to e.g. `mkdocs.yml` and `pyproject.toml`.*

All affected repositories are listed at [sourander.github.io](https://sourander.github.io/) site. All these repositories have been originally created using the same Github project, called **doc-skeleton**. This tool will work as a master data that can push changes to all repositories at once. Updates include but are not limited to:

* Changes in the `mkdocs.yml` file caused by new plugins or themes.
* Changes in the `pyproject.toml` file caused by new dependencies.
* Changes in the `.pre-commit-config.yaml` file caused by new hooks.
* Changes in the `.github/workflows/mkdocs-merge.yaml` file caused by new workflows.
* Need to run `uv lock --upgrade` in all repositories.
* Need to render the `siteinfo.json` file for a new repository.


## Configuration

The configuration file is a YAML file located at `~/.config/doc-flesh/config.yaml`. The file should contain a list of repositories to be managed. The schema of this file is defined in `doc_flesh/models.py` as `ManagedRepo`. The file should look something like this:

```yaml
Basic: &defaults
  jinja_files:
    - mkdocs.yml
    - pyproject.toml
  static_files:
    - .github/workflows/mkdocs-merge.yaml

MathJax: &mathjax
  static_files:
    - docs/javascripts/mathjax.js
  flags:
    site_uses_mathjax: true

ExtractExerciseList: &extract_exercise_list
  static_files:
    - .pre-commit-config.yaml
  flags:
    site_uses_precommit: true

ManagedRepos:
  - local_path: /absolute/path/to/oat/
    name: Oppimispäiväkirja 101
    <<: *defaults

  - local_path: /absolute/path/to/linux-perusteet/
    name: Linux Perusteet
    <<: *defaults
    <<: *extract_exercise_list
  
  - local_path: /absolute/path/to/ml-perusteet/
    name: Johdatus koneoppimiseen
    <<: *defaults
    <<: *mathjax
```

The site info looks like this:

```json
{
  "site_name": "Linux Perusteet",
  "site_name_slug": "linux-perusteet",
  "category": "Study materials",
  "related_repo": ""
}
```

There are two sorts of files:

* **Jinja files**: The files are expected to have a key for each value in the `$REPO/siteinfo.json` file that is also used for updating the `sourander.github.io` site every night.
* **Static files**: These files are copied from the HOME directory to the repository as is.

### Jinja File Variables

The *facts* in the rendered files, based on `templates/**/*`, gather their facts from two sources. The rule for deciding where a fact goes is simple: if the fact is needed for building the `sourander.github.io` index site, it goes to the `siteinfo.json` file. Otherwise, it goes to the `~/.config/doc-flesh/config.yaml` file. Below is a (non-exhaustive) list of facts and where they are stored.

| Fact             | Site info | Config | Example                         |
| ---------------- | --------- | ------ | ------------------------------- |
| Site name        | X         |        | Linux Perusteet                 |
| Site name slug   | X         |        | linux-perusteet                 |
| Category         | X         |        | Study materials                 |
| Related repo     | X         |        | \[Example\](http://example.com) |
| Uses MathJax     |           | X      | true                            |
| Uses Precommit   |           | X      | false                           |
| Any Boolean Flag |           | X      | true/false                      |


## Installation and Usage

The tool is meant to be run locally using [uv](https://docs.astral.sh/uv/). It can be used in the clone location like this:

```bash
# Clone
git clone $url

# Run
uv run doc-flesh --help
```

You can also install it as a tool like this:

```bash
# Either from Github or from local path
uv tool install git+https://github.com/sourander/doc-flesh
uv tool install /path/to/doc-flesh

# Run
doc-flesh --help
```

If you need shell completions, check [Click: Shell Completion](https://click.palletsprojects.com/en/stable/shell-completion/).

### Commands

It is assumed that all commands below are prefixed with `uv run` as shown above.

#### Check

You can manually check the repositories for dirtiness using the `check` command. Note that the sync command also checks for dirtiness before proceeding for safety.

```bash
doc-flesh check
```

Before proceeding syncing ANY templates to ANY repository, the tool verifies that all repositories are in a non-dirty state.

**Currently Verified Non-Dirtyness:**

* ✅ Repository existence (path exists)
* ✅ Current branch is 'main'
* ✅ Repository is not bare
* ✅ Repository has no uncommitted changes (not dirty)
* ✅ Repository is not in detached HEAD state
* ✅ Local and remote branches point to the same commit (after fetching)
* ✅ Working copy is not in a rebase, merge, or cherry-pick state

**Assumed but Not Verified:**

* 🚧 Branch protection rules allow direct pushes to main
* 🚧 Repository has a properly configured remote named 'origin'
* 🚧 No hooks that might interfere with the commit or push operations
* ⁉️ And potentially some unknown unknowns


#### Sync

Running the sync runs the check command first and then proceeds to sync the files to the repositories.

```bash
doc-flesh sync [--dry-run]
```

The sync command does the following:

* Checks the repositories for dirtiness.
* Copies the Jinja files to the repositories (using variables from the `$REPO/siteinfo.json` file).
* Copies the static files to the repositories.
* Commits the changes to the repositories.
* Pushes the changes to the repositories.

The `--dry-run` flag can be used to show what would be done without actually doing it. It will instead write the files into a temporary directory for inspection. Example below.

```console
$ uv run doc-flesh sync --dry-run
🔍 Checking repo: /Users/janisou1/Code/sourander/oat
🔄 Fetching updates from remote...
✅ Repo is up-to-date with the remote.
✅ Repo is clean and safe for automation.
🔧 All files will be written to /private/var/folders/aa/hash/T/tmpe8u9pv9o under directories with the same name as each repository.
🔧 Dry-run: skipping the Git operations.
🎉 Sync complete.

$ ls /private/var/folders/aa/hash/T/tmpe8u9pv9o
/private/var/folders/6q/glcwrb855ss6mjvqhjzk4lbctxydll/T/tmpe8u9pv9o
└── Oppimispäiväkirja 101
    ├── docs
    │   └── javascripts
    │       └── mathjax.js
    └── mkdocs.yml

4 directories, 2 files
```

#### Generate Siteinfo

Running the `generate-siteinfo` command generates the `siteinfo.json` file for the repositories. The target directory default is `.` (current directory). The `siteinfo.json` file is **read from** and **generated to** that directory.

* IF FILE EXISTS: 
    * Existing values are displayed for all fields that already have a valid value in JSON.
    * Default values are displayed for all fields that do not have value in JSON.
* IF NOT EXISTS:
    * Default values are displayed for all fields.

```
doc-flesh generate-siteinfo [path-to-directory]
```

## Development notes

* Triple-check the sync-logic. It is the most dangerous part of the tool.
* Add an option to run `uv lock --upgrade` in each repository. 
    * This should be a separate command. Sync should not be omnipotent.
* Maybe the `~/.config/doc-flesh/config.yaml` should include information about required toggles, like:

    ```yaml
    MathJax: &mathjax
    static_files:
    - docs/javascripts/mathjax.js
    required_toggles:
    - site_uses_mathjax
    ```

    Note that the `reader.py::append_siteinfo` function already validates the Pydantic model. This could be extended to check the required toggles as well. This way, the user would need to go and run the `doc-flesh generate-siteinfo` command to update the `siteinfo.json` file before continuing.


### Obvious WIP notes

* The tool is not yet fully functional. 
    * `sync` command is currently forced to:
        *  `no-commit` for safety. Results will be manually validated, committed and pushed.
