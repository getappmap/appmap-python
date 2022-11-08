#!/usr/bin/env bash

set -x
t=$([ -t 0 ] && echo 't')
docker run -i${t} --rm\
  -v $PWD/dist:/dist -v $PWD/_appmap/test/data/unittest:/_appmap/test/data/unittest\
  -v $PWD/ci:/ci\
  -w /tmp\
  python:3.9 bash -ce "${@:-/ci/smoketest.sh; /ci/test_pipenv.sh}"
