#!/usr/bin/env bash

test_recording_when_appmap_not_true()
{
  cat <<EOF > test_client.py
from appmap import Recording

with Recording():
  print("Hello from appmap library client")
EOF

  python test_client.py

  if [[ $? -eq 0 ]]; then
    echo 'Script executed successfully'
  else
    echo 'Script execution failed'
    exit 1
  fi
}

test_log_file_not_writable()
{
  cat <<EOF > test_log_file_not_writable.py
import appmap
EOF

  python test_log_file_not_writable.py

  if [[ $? -eq 0 ]]; then
    echo 'Script executed successfully'
  else
    echo 'Script execution failed'
    exit 1
  fi
}

set -ex

# now appmap requires git
apt-get update -qq \
 && apt-get install -y --no-install-recommends git

pip -q install -U pip pytest "flask>=2,<3" python-decouple
pip -q install /dist/appmap-*-py3-none-any.whl

cp -R /_appmap/test/data/unittest/simple ./.

# Before we enable, run a command that tries to load the config
python -m appmap.command.appmap_agent_status

# Ensure that client code using appmap.Recording does not fail when not APPMAP=true
test_recording_when_appmap_not_true

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

test_log_file_not_writable
