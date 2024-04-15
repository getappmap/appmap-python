#!/usr/bin/env bash

set -ex
pip -q install -U pip pytest "flask>=2,<3" python-decouple
pip -q install /dist/appmap-*-py3-none-any.whl

cp -R /_appmap/test/data/unittest/simple ./.

python -m appmap.command.appmap_agent_init |\
  python -c 'import json,sys; print(json.load(sys.stdin)["configuration"]["contents"])' > /tmp/appmap.yml
cat /tmp/appmap.yml

python -m appmap.command.appmap_agent_validate

$RUNNER appmap-python pytest -k test_hello_world

if [[ -f tmp/appmap/pytest/simple_test_simple_UnitTestTest_test_hello_world.appmap.json ]]; then
  echo 'Success'
else
  echo 'No appmap generated?'
  find $PWD
  exit 1
fi
