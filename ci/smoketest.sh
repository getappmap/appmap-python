#!/usr/bin/env bash

set -ex
pip -q install -U pip pytest "flask>=2,<3" python-decouple
pip -q install /dist/appmap-*-py3-none-any.whl

cp -R /_appmap/test/data/unittest/simple ./.

# Before we enable, run a command that tries to load the config
python -m appmap.command.appmap_agent_status

export APPMAP=true

python -m appmap.command.appmap_agent_init |\
  python -c 'import json,sys; print(json.load(sys.stdin)["configuration"]["contents"])' > /tmp/appmap.yml
cat /tmp/appmap.yml

python -m appmap.command.appmap_agent_validate

# Promote warnings to errors, so we'll fail if pytest warns it can't rewrite appmap
$RUNNER pytest -Werror -k test_hello_world

if [[ -f tmp/appmap/pytest/simple_test_simple_UnitTestTest_test_hello_world.appmap.json ]]; then
  echo 'Success'
else
  echo 'No appmap generated?'
  find $PWD
  exit 1
fi
