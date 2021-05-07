import os
import os.path
from pathlib import Path

import json
import pytest

from .normalize import normalize_appmap

@pytest.fixture(autouse=True)
def setup(testdir):
    testdir.copy_example('pytest')
    testdir.monkeypatch.setenv('APPMAP', 'true')

    testdir.appmap_json = (Path(str(testdir))
        / 'tmp' / 'appmap'/ 'pytest'/ 'test_hello_world.appmap.json')

def test_basic_integration(data_dir, testdir):
    result = testdir.runpytest('-vv', '-k', 'test_hello_world')
    result.assert_outcomes(passed=1)
    appmap_json = testdir.appmap_json
    with open(appmap_json) as appmap:
        generated_appmap = normalize_appmap(appmap.read())

    expected_json = os.path.join(data_dir, 'pytest', 'expected.appmap.json')
    with open(expected_json) as f:
        expected_appmap = json.load(f)

    assert generated_appmap == expected_appmap

def test_overwrites_existing(testdir):
    appmap_json = testdir.appmap_json
    appmap_json.parent.mkdir(parents=True, exist_ok=True)
    appmap_json.touch()

    result = testdir.runpytest('-vv', '-k', 'test_hello_world')
    result.assert_outcomes(passed=1)
