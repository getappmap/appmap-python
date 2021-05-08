import json
import pytest

from .normalize import normalize_appmap

@pytest.fixture(autouse=True)
def setup(pytester, monkeypatch):
    pytester.copy_example('pytest')
    monkeypatch.setenv('APPMAP', 'true')

    pytester.appmap_json = pytester.path / 'tmp' / 'appmap' / 'pytest' / 'test_hello_world.appmap.json'


def test_basic_integration(data_dir, pytester, monkeypatch):
    pytester.copy_example('pytest')
    monkeypatch.setenv('APPMAP', 'true')

    result = pytester.runpytest('-vv')
    result.assert_outcomes(passed=1, failed=1, xpassed=1, xfailed=1)

    appmap_json = pytester.appmap_json

    assert len(list(appmap_json.parent.iterdir())) == 4

    generated_appmap = normalize_appmap(appmap_json.read_text())

    expected_json = data_dir / 'pytest' / 'expected.appmap.json'
    expected_appmap = json.loads(expected_json.read_text())

    assert generated_appmap == expected_appmap


def test_overwrites_existing(pytester):
    appmap_json = pytester.appmap_json
    appmap_json.parent.mkdir(parents=True, exist_ok=True)
    appmap_json.touch()

    result = pytester.runpytest('-vv', '-k', 'test_hello_world')
    result.assert_outcomes(passed=1)
