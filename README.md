# doc-flesh

Ah, some flesh for [doc-skeleton](https://github.com/sourander/doc-skeleton) template's bones! This tool allows hosting canonical config files in HOME directory and syncing those to ALL repositories based on doc-skeleton locally.

![alt](assets/template-flow.png)

**Diagram 1:** *The flow from `~/.config/.../` to X different repository directories explained as a diagram. The files are then committed and pushed to origin main.*

In the original creator's context, the affected repositories are listed at [sourander.github.io](https://sourander.github.io/) site. All these repositories share the same template Github project, called doc-skeleton. Syncing the changes could be done using Git submodules or clever forking and merges, but I chose to use this tool for syncing the config files. The tool allows the repositories to be more independent. Also, this allows clever tricks like running `uv lock --upgrade` in each repository to upgrade the dependencies in all repositories at once.

## Configuration

The configuration file is a YAML file located at `~/.config/doc-flesh/config.yaml`. The file should contain a list of repositories to be managed. Each repository should have an absolute `local_path` and a `name` key. The `local_path` should point to the local repository's root directory. The `name` key is used for logging purposes.

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

ExtractExerciseList: &extract_exercise_list
  static_files:
    - .pre-commit-config.yaml

ManagedRepos:
  - local_path: /absolute/path/to/oat/
    name: Oppimispäiväkirja 101
    <<: *defaults

  - local_path: /absolute/path/to/oat/linux-perusteet/
    name: Linux Perusteet
    <<: *defaults
    <<: *extract_exercise_list
  
  - local_path: /absolute/path/to/oat/ml-perusteet/
    name: Johdatus koneoppimiseen
    <<: *defaults
    <<: *mathjax
```

There are two sorts of files:

* **Jinja files**: The files are expected to have a key for each value in the `$REPO/siteinfo.json` file that is also used for updating the `sourander.github.io` site every night.
* **Static files**: These files are copied from the HOME directory to the repository as is.

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
