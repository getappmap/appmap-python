"""Test Configuration"""
import os

import pytest

import appmap
from .appmap_test_base import AppMapTestBase
from appmap._implementation.configuration import ConfigFilter
from appmap._implementation.recording import NullFilter
from .helpers import FIXTURE_DIR


class TestConfiguration(AppMapTestBase):
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

    @pytest.mark.datafiles(
        os.path.join(FIXTURE_DIR, 'appmap.yml')
    )
    def test_package_included(self, datafiles, mocker, monkeypatch):
        monkeypatch.setenv("APPMAP", "true")
        monkeypatch.setenv("APPMAP_CONFIG",
                           os.path.join(str(datafiles), 'appmap.yml'))
        monkeypatch.setenv("APPMAP_LOG_LEVEL", 'debug')

        f = ConfigFilter(NullFilter())
        c = mocker.Mock()
        c.__module__ = 'package1'
        c.__qualname__ = 'cls'
        assert f.filter(c) is True

    @pytest.mark.datafiles(
        os.path.join(FIXTURE_DIR, 'appmap-class.yml')
    )
    def test_class_included(self, datafiles, mocker, monkeypatch):
        monkeypatch.setenv("APPMAP", "true")
        monkeypatch.setenv("APPMAP_CONFIG",
                           os.path.join(str(datafiles), 'appmap-class.yml'))
        monkeypatch.setenv("APPMAP_LOG_LEVEL", 'debug')

        f = ConfigFilter(NullFilter())
        c = mocker.Mock()
        c.__module__ = 'package1.package2'
        c.__qualname__ = 'Mod1Class'
        assert f.filter(c) is True

    @pytest.mark.datafiles(
        os.path.join(FIXTURE_DIR, 'appmap-func.yml')
    )
    def test_function_included(self, datafiles, mocker, monkeypatch):
        monkeypatch.setenv("APPMAP", "true")
        monkeypatch.setenv("APPMAP_CONFIG",
                           os.path.join(str(datafiles), 'appmap-func.yml'))
        monkeypatch.setenv("APPMAP_LOG_LEVEL", 'debug')

        f = ConfigFilter(NullFilter())
        c = mocker.Mock()
        c.__module__ = 'package1.package2'
        c.__qualname__ = 'Mod1Class.func'
        assert f.filter(c) is True

    @pytest.mark.datafiles(
        os.path.join(FIXTURE_DIR, 'appmap.yml')
    )
    def test_function_included_by_package(self, datafiles, mocker, monkeypatch):
        monkeypatch.setenv("APPMAP", "true")
        monkeypatch.setenv("APPMAP_CONFIG",
                           os.path.join(str(datafiles), 'appmap.yml'))
        monkeypatch.setenv("APPMAP_LOG_LEVEL", 'debug')

        f = ConfigFilter(NullFilter())
        c = mocker.Mock()
        c.__module__ = 'package1.package2'
        c.__qualname__ = 'Mod1Class.func'
        assert f.filter(c) is True

    @pytest.mark.datafiles(
        os.path.join(FIXTURE_DIR, 'appmap-class.yml')
    )
    def test_function_included_by_class(self, datafiles, mocker, monkeypatch):
        monkeypatch.setenv("APPMAP", "true")
        monkeypatch.setenv("APPMAP_CONFIG",
                           os.path.join(str(datafiles), 'appmap-class.yml'))
        monkeypatch.setenv("APPMAP_LOG_LEVEL", 'debug')

        f = ConfigFilter(NullFilter())
        c = mocker.Mock()
        c.__module__ = 'package1.package2'
        c.__qualname__ = 'Mod1Class.func'
        assert f.filter(c) is True

    @pytest.mark.datafiles(
        os.path.join(FIXTURE_DIR, 'appmap.yml')
    )
    def test_class_prefix_doesnt_match(self, datafiles, mocker, monkeypatch):
        monkeypatch.setenv("APPMAP", "true")
        monkeypatch.setenv("APPMAP_CONFIG",
                           os.path.join(str(datafiles), 'appmap.yml'))
        monkeypatch.setenv("APPMAP_LOG_LEVEL", 'debug')

        f = ConfigFilter(NullFilter())
        c = mocker.Mock()
        c.__module__ = 'package1_prefix'
        c.__qualname__ = 'cls'
        assert f.filter(c) is False

    @pytest.mark.datafiles(
        os.path.join(FIXTURE_DIR, 'appmap.yml')
    )
    def test_fn_prefix_doesnt_match(self, datafiles, mocker, monkeypatch):
        monkeypatch.setenv("APPMAP", "true")
        monkeypatch.setenv("APPMAP_CONFIG",
                           os.path.join(str(datafiles), 'appmap.yml'))
        monkeypatch.setenv("APPMAP_LOG_LEVEL", 'debug')

        f = mocker.Mock()
        f.__module__ = 'package1_prefix'
        f.__qualname__ = 'cls.func'
        fltr = ConfigFilter(NullFilter())
        assert not fltr.included(f)
