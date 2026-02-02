#!/usr/bin/env bash

set -e
pip -q install poetry

mkdir /poetry || true
cd /poetry

poetry init -q

# Yes, we need to set RUNNER, and we need to "poetry run" the script.
RUNNER="poetry run" poetry run /ci/tests/smoketest.sh
