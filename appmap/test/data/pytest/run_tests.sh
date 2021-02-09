#!/usr/bin/env bash

set -ex

# Have poetry install into the system site-packages, rather than
# create a virtualenv.
poetry config virtualenvs.create false

# Install appmap-python from the current directory into site-packages.
poetry install --no-dev

# Make sure pip sees appmap-python, too
pip show appmap

# Run a simple test to create an AppMap
cd appmap/test/data/pytest
pip install pytest
APPMAP=true APPMAP_LOG_LEVEL=info pytest
