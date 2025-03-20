"""Why this file is required?

Uv/Hatch does not support namespace packages (PEP 420).
Alternatively, one could define the pyproject.toml like:

    [tool.hatch.build.targets.wheel]
    packages = ["src/doc_flesh"]
"""