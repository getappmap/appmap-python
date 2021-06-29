#!/usr/bin/env bash

set -e
pip install -U pip pytest
pip install /dist/appmap-0.0.0-py3-none-any.whl

cp -R /appmap/test/data/unittest/simple ./.

appmap-agent-init |\
  python -c 'import json,sys; print(json.load(sys.stdin)["configuration"]["contents"])' > /tmp/appmap.yml
cat /tmp/appmap.yml

APPMAP=true pytest -v -k test_hello_world

if [[ -f tmp/appmap/pytest/simple_test_simple_UnitTestTest_test_hello_world.appmap.json ]]; then
  echo 'Success'
else
  echo 'No appmap generated?'
  find $PWD
  exit 1
fi