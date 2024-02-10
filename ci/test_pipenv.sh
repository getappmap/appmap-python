#!/usr/bin/env bash

set -e
pip -q install pipenv

mkdir /pipenv || true
cd /pipenv

pipenv run /ci/smoketest.sh
