#!/usr/bin/env bash

set -ex

git clean -f -x -d -e /.tox -e /dist
poetry publish --build
