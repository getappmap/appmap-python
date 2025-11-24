#!/bin/bash

set -e
set -o pipefail

if [ -z "$DISTRIBUTION_NAME" ] || [ "$DISTRIBUTION_NAME" = "appmap" ] ; then
  exec poetry build $*
fi

echo "Altering distribution name to $DISTRIBUTION_NAME" 

cp -v pyproject.toml /tmp/pyproject.bak
sed -i -e "s/^name = \".*\"/name = \"${DISTRIBUTION_NAME}\"/" pyproject.toml
grep -n 'name = "' pyproject.toml

poetry build $*

echo "Not patching artifacts with Provides-Dist, they won't work anyway (this flow is solely for publishing test)"
cp -v /tmp/pyproject.bak pyproject.toml
