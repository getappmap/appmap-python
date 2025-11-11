#!/usr/bin/env bash

SMOKETEST_DOCKER_IMAGE=${SMOKETEST_DOCKER_IMAGE:-"python:3.11"}
DISTRIBUTION_NAME=${DISTRIBUTION_NAME:-appmap}

set -x
t=$([ -t 0 ] && echo 't')
docker run -q -i${t} --rm \
  -v $PWD/dist:/dist \
  -v $PWD/_appmap/test/data/unittest:/_appmap/test/data/unittest\
  -v $PWD/ci/tests:/ci/tests\
  -v $PWD/.git:/tmp/.git:ro\
  -v $PWD/ci/tests/data/readonly-mount-appmap.log:/tmp/appmap.log:ro\
  -w /tmp\
  -e DISTRIBUTION_NAME \
  $SMOKETEST_DOCKER_IMAGE bash -ce "${@:-/ci/tests/smoketest.sh; /ci/tests/test_pipenv.sh; /ci/tests/test_poetry.sh}"
