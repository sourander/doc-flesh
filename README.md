# doc-flesh

Ah, some flesh for [doc-skeleton](https://github.com/sourander/doc-skeleton) template's bones This tool allows hosting canonical config files in HOME directory and syncing those to ALL repositories based on doc-skeleton locally.

The affected repositories are listed at [sourander.github.io](https://sourander.github.io/) site, which is the index of all doc-skeleton based repositories. All these repositories share the same upstream, which could be handled using forking or subtree merging, but instead, I chose to use this tool for syncing the config files. The tool allows the repositories to be more independent. Each might have their own flavor of the config files, but the canonical ones are always available in the HOME directory.

## How it Works

To add local repositories to be managed by doc-flesh, add the repository names to the configuration file: `~/.config/doc-flesh/config.yaml`

There are two sorts of files:

* **JinjaFiles**: The files are expected to have a key for each value in the `siteinfo.json` file that is also used for updating the `sourander.github.io` site every night.
* **StaticFiles**: These files are copied from the HOME directory to the repository as is.

## Configuration

The configuration file is a YAML file located at `~/.config/doc-flesh/config.yaml`. The file should contain a list of repositories to be managed. Each repository should have a `local_path` and a `name` key. The `local_path` should point to the local repository's root directory. The `name` key is used for logging purposes.

```yaml
Files: &defaults
  jinja_files:
    - mkdocs.yml
  static_files:
    - .github/workflows/mkdocs-merge.yaml
    - docs/javascripts/mathjax.js

ManagedRepos:
  # A repository using only the default Files
  - local_path: /Users/me/Code/me/oat/
    name: Oppimispäiväkirja 101
    <<: *defaults

  # A repository using files that are not common to all repos
  - local_path: /Users/me/Code/me/repo-b/
    name: Repo B
    <<: *defaults
    jinja_files:
      - some/dynamic/config.yml
    static_files:
      - some/static/file/used/by/many/but/not/all.js

```

## Installation and Usage

The tool can be run from GitHub. I will not be hosting it to PyPi, as it is a very specific tool. I may consider adding a self-hosted Python package index (e.g. devpi) later.

```bash
# Install and run
uvx --from git+https://github.com/sourander/doc-flesh doc-flesh --help

# Or run locally cloned repository
uv run doc-flesh --help
```

### Commands

It is assumed that all commands below are prefixed with `uv run` or `uvx --from git+...` as shown above.

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
doc-flesh sync
```

## Development notes

* Add `siteinfo.json` Pydantic model to `src/models/`. This tool than also centrally check that each repo has a valid `siteinfo.json` file.
* Add a `--dry-run` flag to the `sync` command to show what would be done without actually doing it. 
    * The files could be written to `output/repoconfig.name/../../file.txt` for inspection.
    * This is trickier with GitPython. It does not really have a dry-run mode. Maybe simple print the Python statements that would be executed?
* I need to make sure this works with both HTTPS and GIT authentication. 

Obvious stuff:

* The tool is not yet fully functional. 
    * The `check` command is mostly done, but the `sync` command is still in the works.
