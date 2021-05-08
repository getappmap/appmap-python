#!/usr/bin/env bash

set -x
docker run -i --rm\
  -v $PWD/dist:/dist -v $PWD/appmap/test/data/pytest:/appmap/test/data/pytest\
  --entrypoint /bin/bash\
  -w /appmap/test/data/pytest\
  python:3.9 -c 'pip install pytest && pip install /dist/appmap-0.0.0-py3-none-any.whl && APPMAP=true pytest -k test_hello_world'
