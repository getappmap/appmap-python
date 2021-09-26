"""Test Configuration"""
# pylint: disable=missing-function-docstring

from distutils.dir_util import copy_tree
from pathlib import Path
import sys

import pytest

import appmap
import appmap._implementation
import appmap._implementation.env as impl_env
from appmap._implementation.configuration import Config, ConfigFilter
from appmap._implementation.env import Env
from appmap._implementation.recording import NullFilter, Filterable


def test_can_be_enabled():
    """
    Test that recording is enabled when APPMAP=true.
    """
    Env.current.set("APPMAP", "true")

    assert appmap.enabled()

@pytest.mark.appmap_enabled
def test_can_be_configured():
    """
    Test the happy path: APPMAP is true, appmap.yml is found, and the
    YAML is valid.
    """
    assert appmap.enabled()

    c = Config()
    assert c.file_present
    assert c.file_valid

@pytest.mark.appmap_enabled(config="appmap-broken.yml")
def test_reports_invalid():
    """
    Test that a parse error keeps recording from being enabled, and
    indicates that the config is not valid.
    """
    assert not appmap.enabled()
    assert not Config().file_valid

def test_is_disabled_when_unset():
    """Test that recording is disabled when APPMAP is unset"""
    assert Env.current.get('APPMAP', None) is None

    assert not appmap.enabled()

def test_is_disabled_when_false():
    """Test that recording is disabled when APPMAP=false"""
    Env.current.set("APPMAP", "false")
    assert not appmap.enabled()


def test_config_not_found(caplog):
    appmap._implementation.initialize(env={  # pylint: disable=protected-access
        'APPMAP': 'true', 'APPMAP_CONFIG': 'notfound.yml'
    })
    assert Config().name is None
    assert not Config().file_present
    assert not Config().file_valid

    assert not appmap.enabled()
    not_found = Path('notfound.yml').resolve()
    assert not not_found.exists()
    assert f'"{not_found}" is missing' in caplog.text

def test_config_no_message(caplog):
    """
    Messages about a missing config should only be logged when
    recording is enabled
    """

    assert Config().name is None
    assert not appmap.enabled()
    assert caplog.text is ""

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


class TestDefaultConfig:
    def check_default_config(self, expected_name):
        assert appmap.enabled()

        default_config = Config()
        assert default_config.name == expected_name
        assert len(default_config.packages) == 2
        assert sorted(default_config.packages, key=lambda p: p['path']) == [
            { 'path': 'package'},
            { 'path': 'test' }
        ]

    def test_created(self, git, data_dir, monkeypatch):
        repo_root = git.cwd
        copy_tree(data_dir / 'config', str(repo_root))
        monkeypatch.chdir(repo_root)

        # pylint: disable=protected-access
        appmap._implementation.initialize(cwd=repo_root,
                                          env={
                                              'APPMAP': 'true'
                                          })

        self.check_default_config(repo_root.name)

    def test_created_outside_repo(self, data_dir, tmpdir, monkeypatch):
        copy_tree(data_dir / 'config', str(tmpdir))
        monkeypatch.chdir(tmpdir)

        # pylint: disable=protected-access
        appmap._implementation.initialize(cwd=tmpdir,
                                          env={
                                              'APPMAP': 'true'
                                          })
        self.check_default_config(Path(tmpdir).name)

    def test_skipped_when_overridden(self):
        appmap._implementation.initialize(env={  # pylint: disable=protected-access
            'APPMAP': 'true',
            'APPMAP_CONFIG': '/tmp/appmap.yml'
        })
        assert not Config().name
        assert not appmap.enabled()

    def test_exclusions(self, data_dir, tmpdir, mocker, monkeypatch):
        copy_tree(data_dir / 'config-exclude', str(tmpdir))
        monkeypatch.chdir(tmpdir)
        mocker.patch('appmap._implementation.configuration._get_sys_prefix', return_value=str(tmpdir / 'venv'))

        # pylint: disable=protected-access
        appmap._implementation.initialize(cwd=tmpdir,
                                          env={
                                              'APPMAP': 'true'
                                          })
        self.check_default_config(Path(tmpdir).name)
