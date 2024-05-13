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

[poetry](https://https://python-poetry.org/) for dependency management:

```
% brew install poetry
% cd appmap-python
% poetry install
```

### wrapt
The one dependency that is not managed using `poetry` is `wrapt`. Because it's possible that
projects that use `appmap` may also need an unmodified version of `wrapt` (e.g. `pylint` depends on
`astroid`, which in turn depends on `wrapt`), we use
[vendoring](https://github.com/pradyunsg/vendoring) to vendor `wrapt`.

To update `wrapt`, use `tox` (described below) to run the `vendoring` environment.

## Linting
[pylint](https://www.pylint.org/) for linting:

```
% cd appmap-python
% poetry run pylint appmap

--------------------------------------------------------------------
Your code has been rated at 10.00/10 (previous run: 10.00/10, +0.00)

```

[Note that the current configuration has a threshold set which must be met for the Travis build to
pass. To make this easier to achieve, a number of checks have both been disabled. They should be
reenabled as soon as possible.]


## Testing
### pytest

Note that you must install the dependencies contained in
[requirements-dev.txt](requirements-dev.txt) before running tests. See the explanation in
[pyproject.toml](pyproject.toml) for details.

Additionally, the tests currently require that you set `APPMAP=true`. You can
either run `pytest` with `appmap-python` (see [tox.ini](tox.ini)), or you can explicitly
set the environment variable.

[pytest](https://docs.pytest.org/en/stable/) for testing:

```
% cd appmap-python
% pip install -r requirements-test.txt
% poetry run pytest
```

### tox
Additionally, the `tox` configuration provides the ability to run the tests for all
supported versions of Python and Django.

`tox` requires that all the correct versions of Python to be available to create
the test environments. [pyenv](https://github.com/pyenv/pyenv) is an easy way to manage
multiple versions of Python, and the [xxenv-latest
plugin](https://github.com/momo-lab/xxenv-latest) can help get all the latest versions.



```sh
% brew install pyenv
% git clone https://github.com/momo-lab/xxenv-latest.git "$(pyenv root)"/plugins/xxenv-latest
% cd appmap-python
% pyenv latest local 3.{9,6,7,8}
% for v in 3.{9,6,7,8}; do pyenv latest install $v; done
% poetry run tox
```

## Code Coverage
[coverage](https://coverage.readthedocs.io/) for coverage:

```
% cd appmap-python
% poetry run coverage run -m pytest
% poetry run coverage html
% open htmlcov/index.html
```
