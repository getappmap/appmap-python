"""Test Configuration"""
# pylint: disable=missing-function-docstring

from pathlib import Path
import pytest

import appmap
import appmap._implementation
from appmap._implementation.configuration import Config, ConfigFilter
from appmap._implementation.env import Env
from appmap._implementation.recording import NullFilter, Filterable


def test_can_be_enabled():
    """Test that recording is enabled when APPMAP=true"""
    Env.current.set("APPMAP", "true")

    assert appmap.enabled()

def test_is_disabled_when_unset():
    """Test that recording is disabled when APPMAP is unset"""
    assert Env.current.get('APPMAP', None) is None

    assert not appmap.enabled()

def test_is_disabled_when_false():
    """Test that recording is disabled when APPMAP=false"""
    Env.current.set("APPMAP", "false")
    assert not appmap.enabled()


def test_config_not_found(caplog):
    appmap._implementation.initialize({  # pylint: disable=protected-access
        'APPMAP': 'true', 'APPMAP_CONFIG': 'notfound.yml'
    })
    assert Config().name is None
    assert not appmap.enabled()
    not_found = Path('notfound.yml').resolve()
    assert f'"{not_found}" is missing' in caplog.text


cf = lambda: ConfigFilter(NullFilter())

@pytest.mark.appmap_enabled(config='appmap-class.yml')
def test_class_included():
    f = Filterable('package1.package2.Mod1Class', None)
    assert cf().filter(f) is True

@pytest.mark.appmap_enabled(config='appmap-func.yml')
def test_function_included():
    f = Filterable('package1.package2.Mod1Class.func', None)
    assert cf().filter(f) is True

@pytest.mark.appmap_enabled(config='appmap-class.yml')
def test_function_included_by_class():
    f = Filterable('package1.package2.Mod1Class.func', None)
    assert cf().filter(f) is True


@pytest.mark.appmap_enabled
class TestConfiguration:
    def test_package_included(self):
        f = Filterable('package1.cls', None)
        assert cf().filter(f) is True

    def test_function_included_by_package(self):
        f = Filterable('package1.package2.Mod1Class.func', None)
        assert cf().filter(f) is True

    def test_class_prefix_doesnt_match(self):
        f = Filterable('package1_prefix.cls', None)
        assert cf().filter(f) is False
