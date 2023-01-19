"""Test Configuration"""
# pylint: disable=missing-function-docstring

from contextlib import contextmanager
from distutils.dir_util import copy_tree
from pathlib import Path

import pytest
import yaml

import _appmap
import appmap
from _appmap.configuration import Config, ConfigFilter
from _appmap.env import Env
from _appmap.importer import Filterable, NullFilter


def test_enabled_by_default():
    assert appmap.enabled()


@pytest.mark.appmap_enabled
def test_can_be_configured():
    """
    Test the happy path: recording is enabled, appmap.yml is found, and the YAML is valid.
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


@pytest.mark.appmap_enabled(config="appmap-broken.yml")
def test_is_disabled_when_unset():
    """Test that recording is disabled when APPMAP is unset but the config is broken"""
    assert Env.current.get("APPMAP", None) is None

    assert not appmap.enabled()


@pytest.mark.appmap_enabled(config="appmap-broken.yml", appmap_enabled="false")
def test_is_disabled_when_false():
    """Test that recording is disabled when APPMAP=false"""
    Env.current.set("APPMAP", "false")
    assert not appmap.enabled()


def test_config_not_found(caplog):
    _appmap.initialize(
        env={  # pylint: disable=protected-access
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
    def check_default_packages(self, actual_packages):
        pkgs = [p["path"] for p in actual_packages if p["path"] in ("package", "test")]
        assert ["package", "test"] == sorted(pkgs)

    def check_default_config(self, expected_name):
        assert appmap.enabled()

        default_config = Config()
        assert default_config.name == expected_name
        self.check_default_packages(default_config.packages)
        assert default_config.default["appmap_dir"] == "tmp/appmap"


class TestDefaultConfig(DefaultHelpers):
    def test_created(self, git, data_dir, monkeypatch):
        repo_root = git.cwd
        copy_tree(data_dir / "config", str(repo_root))
        monkeypatch.chdir(repo_root)

        # pylint: disable=protected-access
        _appmap.initialize(cwd=repo_root)

        self.check_default_config(repo_root.name)

    def test_created_outside_repo(self, data_dir, tmpdir, monkeypatch):
        copy_tree(data_dir / "config", str(tmpdir))
        monkeypatch.chdir(tmpdir)

        # pylint: disable=protected-access
        _appmap.initialize(cwd=tmpdir)
        self.check_default_config(Path(tmpdir).name)

    def test_skipped_when_overridden(self):
        _appmap.initialize(
            env={  # pylint: disable=protected-access
                "APPMAP_CONFIG": "/tmp/appmap.yml",
            }
        )
        assert not Config().name
        assert not appmap.enabled()

    def test_exclusions(self, data_dir, tmpdir, mocker, monkeypatch):
        copy_tree(data_dir / "config-exclude", str(tmpdir))
        monkeypatch.chdir(tmpdir)
        mocker.patch(
            "_appmap.configuration._get_sys_prefix",
            return_value=str(tmpdir / "venv"),
        )

        # pylint: disable=protected-access
        _appmap.initialize(cwd=tmpdir)
        self.check_default_config(Path(tmpdir).name)

    def test_created_if_missing_and_enabled(self, git, data_dir, monkeypatch, tmpdir):
        repo_root = git.cwd
        copy_tree(data_dir / "config", str(repo_root))
        monkeypatch.chdir(repo_root)

        path = Path(repo_root / "appmap.yml")
        assert not path.is_file()

        # pylint: disable=protected-access
        _appmap.initialize(cwd=repo_root)

        Config()  # write the file as a side-effect
        assert path.is_file()
        with open(path, encoding="utf-8") as cfg:
            actual_config = yaml.safe_load(cfg)
        assert Path(tmpdir).name == actual_config["name"]
        assert "tmp/appmap" == actual_config["appmap_dir"]
        assert "packages" in actual_config
        self.check_default_packages(actual_config["packages"])

    def test_not_created_if_missing_and_not_enabled(self, git, data_dir, monkeypatch):
        repo_root = git.cwd
        copy_tree(data_dir / "config", str(repo_root))
        monkeypatch.chdir(repo_root)

        path = Path(repo_root / "appmap.yml")
        assert not path.is_file()

        # pylint: disable=protected-access
        _appmap.initialize(cwd=repo_root, env={"APPMAP": "false"})

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
            _appmap.initialize(
                cwd=tmpdir,
                env={"APPMAP_CONFIG": "appmap-incomplete.yml"},
            )
            self.check_default_config(Path(tmpdir).name)

    def test_missing_name(self, tmpdir):
        with self.incomplete_config() as f:
            print('packages: [{"path": "package"}, {"path": "test"}]', file=f)
            _appmap.initialize(
                cwd=tmpdir,
                env={"APPMAP_CONFIG": "appmap-incomplete.yml"},
            )
            self.check_default_config(Path(tmpdir).name)

    def test_missing_packages(self, tmpdir):
        with self.incomplete_config() as f:
            print(f"name: {Path(tmpdir).name}", file=f)
            _appmap.initialize(
                cwd=tmpdir,
                env={"APPMAP_CONFIG": "appmap-incomplete.yml"},
            )
            self.check_default_config(Path(tmpdir).name)
