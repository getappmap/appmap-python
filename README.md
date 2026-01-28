- [About](#about)
- [Usage](#usage)
- [Development](#development)
  - [Getting the code](#getting-the-code)
  - [Python version support](#python-version-support)
  - [Dependency management](#dependency-management)
    - [wrapt](#wrapt)
  - [Linting](#linting)
  - [Testing](#testing)
    - [pytest](#pytest)
    - [tox](#tox)
  - [Code Coverage](#code-coverage)

# About
`appmap-python` is a Python package for recording
[AppMaps](https://github.com/applandinc/appmap) of your code. "AppMap" is a data format
which records code structure (modules, classes, and methods), code execution events
(function calls and returns), and code metadata (repo name, repo URL, commit SHA, labels,
etc). It's more granular than a performance profile, but it's less granular than a full
debug trace. It's designed to be optimal for understanding the design intent and structure
of code and key data flows.

# Usage

Visit the [AppMap for Python](https://appland.com/docs/reference/appmap-python.html) reference page on AppLand.com for a complete reference guide.

# Development

[![Build Status](https://travis-ci.com/getappmap/appmap-python.svg?branch=master)](https://travis-ci.com/getappmap/appmap-python)

## Getting the code
Clone the repo to begin development.

```shell
% git clone https://github.com/applandinc/appmap-python.git
Cloning into 'appmap-python'...
remote: Enumerating objects: 167, done.
remote: Counting objects: 100% (167/167), done.
remote: Compressing objects: 100% (100/100), done.
remote: Total 962 (delta 95), reused 116 (delta 61), pack-reused 795
Receiving objects: 100% (962/962), 217.31 KiB | 4.62 MiB/s, done.
Resolving deltas: 100% (653/653), done.
```

## Python version support
As a package intended to be installed in as many environments as possible, `appmap-python`
needs to avoid using features of Python or the standard library that were added after the
oldest version currently supported (see the
[supported versions](https://appland.com/docs/reference/appmap-python.html#supported-versions)).

## Dependency management

[uv](https://docs.astral.sh/uv/) is used for dependency management and provides fast package installation:

```bash
# Install uv (macOS/Linux)
curl -LsSf https://astral.sh/uv/install.sh | sh

# Install dependencies
cd appmap-python
uv sync --all-extras
```

### wrapt
The one dependency that is not managed using `uv` is `wrapt`. Because it's possible that
projects that use `appmap` may also need an unmodified version of `wrapt` (e.g. `pylint` depends on
`astroid`, which in turn depends on `wrapt`), we use
[vendoring](https://github.com/pradyunsg/vendoring) to vendor `wrapt`.

To update `wrapt`, use `tox` (described below) to run the `vendoring` environment.

## Linting
[pylint](https://www.pylint.org/) for linting:

```bash
cd appmap-python
uv run tox -e lint

# Or run pylint directly
uv run pylint appmap

--------------------------------------------------------------------
Your code has been rated at 10.00/10 (previous run: 10.00/10, +0.00)
```


## Testing
### pytest

[pytest](https://docs.pytest.org/en/stable/) for testing:

```bash
cd appmap-python

# Run all tests
APPMAP_DISPLAY_PARAMS=true uv run appmap-python pytest

# Run tests with a specific Python version
APPMAP_DISPLAY_PARAMS=true uv run --python 3.9 appmap-python pytest

# Run tests in parallel
APPMAP_DISPLAY_PARAMS=true uv run appmap-python pytest -n auto
```

### tox
The `tox` configuration provides the ability to run the tests for all supported versions of Python and web frameworks (Django, Flask, SQLAlchemy).

With `uv`, you don't need to pre-install Python versions - `uv` will automatically download and manage them:

```bash
cd appmap-python

# Run full test matrix (all Python versions and frameworks)
uv run tox

# Run tests for a specific Python version
uv run tox -e py312-web

# Run tests for specific framework
uv run tox -e py312-django5

# Update vendored wrapt dependency
uv run tox -e vendoring sync
```

## Code Coverage
[coverage](https://coverage.readthedocs.io/) for coverage:

```bash
cd appmap-python
uv run coverage run -m pytest
uv run coverage html
open htmlcov/index.html
```
