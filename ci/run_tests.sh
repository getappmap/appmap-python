#!/usr/bin/env bash

set -x
docker run -i --rm\
  -v $PWD/dist:/dist -v $PWD/appmap/test/data/unittest:/appmap/test/data/unittest\
  -v $PWD/ci:/ci\
  -w /tmp\
  python:3.9 bash -ce '/ci/smoketest.sh; /ci/test_pipenv.sh'
