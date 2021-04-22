import os.path
import sys

import pytest

collect_ignore = [os.path.join('appmap', 'test', 'data')]
pytest_plugins = ['pytester']
