"""Test Configuration"""
# pylint: disable=missing-function-docstring

from contextlib import contextmanager
from distutils.dir_util import copy_tree
from pathlib import Path

import pytest

import appmap
import appmap._implementation
from appmap._implementation.configuration import Config, ConfigFilter
from appmap._implementation.env import Env
from appmap._implementation.importer import Filterable, NullFilter


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


@pytest.mark.appmap_enabled(config="appmap-broken.yml", appmap_enabled=None)
def test_is_disabled_when_unset():
    """Test that recording is disabled when APPMAP is unset"""
    assert Env.current.get("APPMAP", None) is None

    assert not appmap.enabled()


@pytest.mark.appmap_enabled(config="appmap-broken.yml", appmap_enabled="false")
def test_is_disabled_when_false():
    """Test that recording is disabled when APPMAP=false"""
    Env.current.set("APPMAP", "false")
    assert not appmap.enabled()


def test_config_not_found(caplog):
    appmap._implementation.initialize(
        env={  # pylint: disable=protected-access
            "APPMAP": "true",
            "APPMAP_CONFIG": "notfound.yml",
        }
    )
    assert Config().name is None
    assert not Config().file_present
    assert not Config().file_valid

    assert not appmap.enabled()
    not_found = Path("notfound.yml").resolve()
    assert not not_found.exists()
    assert f'"{not_found}" is missing' in caplog.text


@pytest.mark.appmap_enabled(appmap_enabled="false", config="notfound.yml")
def test_config_no_message(caplog):
    """
    Messages about a missing config should only be logged when
    recording is enabled
    """

    assert not appmap.enabled()
    assert Config().name is None
    assert caplog.text == ""


cf = lambda: ConfigFilter(NullFilter())


@pytest.mark.appmap_enabled(config="appmap-class.yml")
def test_class_included():
    f = Filterable("package1.package2.Mod1Class", None)
    assert cf().filter(f) is True


@pytest.mark.appmap_enabled(config="appmap-func.yml")
def test_function_included():
    f = Filterable("package1.package2.Mod1Class.func", None)
    assert cf().filter(f) is True


@pytest.mark.appmap_enabled(config="appmap-class.yml")
def test_function_included_by_class():
    f = Filterable("package1.package2.Mod1Class.func", None)
    assert cf().filter(f) is True


@pytest.mark.appmap_enabled
class TestConfiguration:
    def test_package_included(self):
        f = Filterable("package1.cls", None)
        assert cf().filter(f) is True

    def test_function_included_by_package(self):
        f = Filterable("package1.package2.Mod1Class.func", None)
        assert cf().filter(f) is True

    def test_class_prefix_doesnt_match(self):
        f = Filterable("package1_prefix.cls", None)
        assert cf().filter(f) is False


class DefaultHelpers:
    def check_default_config(self, expected_name):
        assert appmap.enabled()

        default_config = Config()
        assert default_config.name == expected_name
        assert len(default_config.packages) == 2
        assert sorted(default_config.packages, key=lambda p: p["path"]) == [
            {"path": "package"},
            {"path": "test"},
        ]


class TestDefaultConfig(DefaultHelpers):
    def test_created(self, git, data_dir, monkeypatch):
        repo_root = git.cwd
        copy_tree(data_dir / "config", str(repo_root))
        monkeypatch.chdir(repo_root)

        # pylint: disable=protected-access
        appmap._implementation.initialize(cwd=repo_root, env={"APPMAP": "true"})

        self.check_default_config(repo_root.name)

    def test_created_outside_repo(self, data_dir, tmpdir, monkeypatch):
        copy_tree(data_dir / "config", str(tmpdir))
        monkeypatch.chdir(tmpdir)

        # pylint: disable=protected-access
        appmap._implementation.initialize(cwd=tmpdir, env={"APPMAP": "true"})
        self.check_default_config(Path(tmpdir).name)

    def test_skipped_when_overridden(self):
        appmap._implementation.initialize(
            env={  # pylint: disable=protected-access
                "APPMAP": "true",
                "APPMAP_CONFIG": "/tmp/appmap.yml",
            }
        )
        assert not Config().name
        assert not appmap.enabled()

    def test_exclusions(self, data_dir, tmpdir, mocker, monkeypatch):
        copy_tree(data_dir / "config-exclude", str(tmpdir))
        monkeypatch.chdir(tmpdir)
        mocker.patch(
            "appmap._implementation.configuration._get_sys_prefix",
            return_value=str(tmpdir / "venv"),
        )

        # pylint: disable=protected-access
        appmap._implementation.initialize(cwd=tmpdir, env={"APPMAP": "true"})
        self.check_default_config(Path(tmpdir).name)

    def test_created_if_missing_and_enabled(self, git, data_dir, monkeypatch):
        repo_root = git.cwd
        copy_tree(data_dir / "config", str(repo_root))
        monkeypatch.chdir(repo_root)

        path = Path(repo_root / "appmap.yml")
        assert not path.is_file()

        # pylint: disable=protected-access
        appmap._implementation.initialize(cwd=repo_root, env={"APPMAP": "true"})

        c = Config()
        assert path.is_file()

    def test_not_created_if_missing_and_not_enabled(self, git, data_dir, monkeypatch):
        monkeypatch.setenv("APPMAP", "false")
        repo_root = git.cwd
        copy_tree(data_dir / "config", str(repo_root))
        monkeypatch.chdir(repo_root)

        path = Path(repo_root / "appmap.yml")
        assert not path.is_file()

        # pylint: disable=protected-access
        appmap._implementation.initialize(cwd=repo_root)

        c = Config()
        assert not path.is_file()


class TestEmpty(DefaultHelpers):
    @pytest.fixture(autouse=True)
    def setup_config(self, data_dir, monkeypatch, tmpdir):
        copy_tree(data_dir / "config", str(tmpdir))
        monkeypatch.chdir(tmpdir)

    @contextmanager
    def incomplete_config(self):
        # pylint: disable=protected-access
        with open("appmap-incomplete.yml", mode="w", buffering=1) as f:
            print("# Incomplete file", file=f)
            yield f

    def test_empty(self, tmpdir):
        with self.incomplete_config():
            appmap._implementation.initialize(
                cwd=tmpdir,
                env={"APPMAP": "true", "APPMAP_CONFIG": "appmap-incomplete.yml"},
            )
            self.check_default_config(Path(tmpdir).name)

    def test_missing_name(self, tmpdir):
        with self.incomplete_config() as f:
            print('packages: [{"path": "package"}, {"path": "test"}]', file=f)
            appmap._implementation.initialize(
                cwd=tmpdir,
                env={"APPMAP": "true", "APPMAP_CONFIG": "appmap-incomplete.yml"},
            )
            self.check_default_config(Path(tmpdir).name)

    def test_missing_packages(self, tmpdir):
        with self.incomplete_config() as f:
            print(f"name: {Path(tmpdir).name}", file=f)
            appmap._implementation.initialize(
                cwd=tmpdir,
                env={"APPMAP": "true", "APPMAP_CONFIG": "appmap-incomplete.yml"},
            )
            self.check_default_config(Path(tmpdir).name)
