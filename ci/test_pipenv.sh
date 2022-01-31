#!/usr/bin/env bash

set -e
pip install pipenv

mkdir /pipenv || true
cd /pipenv

pipenv run /ci/smoketest.sh
