#!/usr/bin/env bash

set -ex

git clean -fd
poetry publish --build
