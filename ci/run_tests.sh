#!/usr/bin/env bash

SMOKETEST_DOCKER_IMAGE=${SMOKETEST_DOCKER_IMAGE:-"python:3.11"}
APPMAP_PACKAGE_NAME=${APPMAP_PACKAGE_NAME:-appmap}

set -x
t=$([ -t 0 ] && echo 't')
docker run -q -i${t} --rm\
  -v $PWD/dist:/dist -v $PWD/_appmap/test/data/unittest:/_appmap/test/data/unittest\
  -v $PWD/ci:/ci\
  -v $PWD/.git:/tmp/.git:ro\
  -v $PWD/ci/readonly-mount-appmap.log:/tmp/appmap.log:ro\
  -w /tmp\
  -e APPMAP_PACKAGE_NAME \
  $SMOKETEST_DOCKER_IMAGE bash -ce "${@:-/ci/smoketest.sh; /ci/test_pipenv.sh; /ci/test_poetry.sh}"
