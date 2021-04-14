"""Test Configuration"""
import pytest

import appmap
from .appmap_test_base import AppMapTestBase
from appmap._implementation.configuration import ConfigFilter
from appmap._implementation.recording import NullFilter, Filterable


class TestConfigurationFromEnv(AppMapTestBase):
    def test_can_be_enabled(self, monkeypatch):
        """Test that recording is enabled when APPMAP=true"""
        monkeypatch.setenv("APPMAP", "true")
        assert appmap.enabled()

    def test_is_disabled_when_unset(self, monkeypatch):
        """Test that recording is disabled when APPMAP is unset"""
        monkeypatch.delenv("APPMAP", raising=False)
        assert not appmap.enabled()

    def test_is_disabled_when_false(self, monkeypatch):
        """Test that recording is disabled when APPMAP=false"""
        monkeypatch.setenv("APPMAP", "false")
        assert not appmap.enabled()


def nf():
    return ConfigFilter(NullFilter())


@pytest.mark.usefixtures('appmap_enabled')
class TestConfiguration(AppMapTestBase):
    def test_package_included(self):
        f = Filterable('package1.cls', None)
        assert nf().filter(f) is True

    @pytest.mark.appmap_config('appmap-class.yml')
    def test_class_included(self):
        f = Filterable('package1.package2.Mod1Class', None)
        assert nf().filter(f) is True

    @pytest.mark.appmap_config('appmap-func.yml')
    def test_function_included(self):
        f = Filterable('package1.package2.Mod1Class.func', None)
        assert nf().filter(f) is True

    def test_function_included_by_package(self):
        f = Filterable('package1.package2.Mod1Class.func', None)
        assert nf().filter(f) is True

    @pytest.mark.appmap_config('appmap-class.yml')
    def test_function_included_by_class(self):
        f = Filterable('package1.package2.Mod1Class.func', None)
        assert nf().filter(f) is True

    def test_class_prefix_doesnt_match(self):
        f = Filterable('package1_prefix.cls', None)
        assert nf().filter(f) is False
