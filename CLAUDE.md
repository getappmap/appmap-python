# appmap-python

Python agent for AppMap. Records function calls, HTTP requests, SQL queries, parameters, return values, and exceptions into `.appmap.json` files.

## Running tests

Tests must be run via `tox` or the `appmap-python` wrapper, not bare `pytest`. The wrapper sets `APPMAP=true`, which is required for conditional imports in `appmap/__init__.py` (e.g. `generation`). Subprocess-based tests also need the `appmap-python` script in PATH.

```sh
# Correct - via tox (how CI runs them)
tox

# Correct - via appmap-python wrapper
appmap-python pytest

# Also works for quick local iteration on non-subprocess tests
APPMAP=true .venv/bin/python -m pytest _appmap/test/test_events.py

# WRONG - will fail on subprocess tests
pytest
```

## Project structure

- `appmap/` - Public package entry point (conditional imports based on APPMAP env var)
- `_appmap/` - Internal implementation (event recording, instrumentation, web framework integration)
- `_appmap/test/` - Test suite
- `_appmap/test/data/` - Test fixtures and expected appmap JSON files
