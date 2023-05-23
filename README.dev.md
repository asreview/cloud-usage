# Developer documentation

## Linting and pre-commit

We lint using the `pre-commit` package, using `black` for Python files, `shellcheck` for bash files, and `markdownlint` for Markdown files.
You don't need to install these packages in your system, though you might find helpful to install an editor integration.

To install pre-commit:

```bash
python -m venv env
. env/bin/activate
pip install --upgrade pip setuptools
pip install pre-commit
pre-commit install
```

To run the linter:

```bash
pre-commit run -a
```
