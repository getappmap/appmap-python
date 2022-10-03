#!/usr/bin/env bash

set -e
eval "$(pyenv init -)"
eval "$(pyenv init --path)"
eval "$(pyenv virtualenv-init -)"
semantic-release
