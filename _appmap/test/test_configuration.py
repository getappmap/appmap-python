"""Test Configuration"""
# pylint: disable=missing-function-docstring

from contextlib import contextmanager
from distutils.dir_util import copy_tree
from pathlib import Path
from textwrap import dedent

import pytest
import yaml

import _appmap
import appmap
from _appmap.configuration import Config, ConfigFilter
from _appmap.env import Env
from _appmap.importer import Filterable, NullFilter


@pytest.mark.appmap_enabled
def test_can_be_configured():
    """
    Test the happy path: recording is enabled, appmap.yml is found, and the YAML is valid.
    """
    assert appmap.enabled()

    c = Config.current
    assert c.file_present
    assert c.file_valid


@pytest.mark.appmap_enabled(config="appmap-broken.yml")
def test_reports_invalid():
    """
    Test that a parse error keeps recording from being enabled, and
    indicates that the config is not valid.
    """
    assert not appmap.enabled()
    assert not Config.current.file_valid


@pytest.mark.appmap_enabled(config="appmap-broken.yml")
def test_is_disabled_when_unset():
    """Test that recording is disabled when APPMAP is unset but the config is broken"""
    assert not appmap.enabled()


@pytest.mark.appmap_enabled(config="appmap-broken.yml", appmap_enabled="false")
def test_is_disabled_when_false():
    """Test that recording is disabled when _APPMAP=false"""
    Env.current.set("_APPMAP", "false")
    assert not appmap.enabled()


def test_config_not_found(caplog):
    _appmap.initialize(
        env={  # pylint: disable=protected-access
            "APPMAP_CONFIG": "notfound.yml",
        }
    )
    assert Config.current.name is None
    assert not Config.current.file_present
    assert not Config.current.file_valid

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
    assert Config.current.name is None
    assert caplog.text == ""


def cf():
    return ConfigFilter(NullFilter())


@pytest.mark.appmap_enabled(config="appmap-class.yml")
def test_class_included():
    f = Filterable(None, "package1.package2.Mod1Class", None)
    assert cf().filter(f) is True


@pytest.mark.appmap_enabled(config="appmap-func.yml")
def test_function_included():
    f = Filterable(None, "package1.package2.Mod1Class.func", None)
    assert cf().filter(f) is True


@pytest.mark.appmap_enabled(config="appmap-class.yml")
def test_function_included_by_class():
    f = Filterable(None, "package1.package2.Mod1Class.func", None)
    assert cf().filter(f) is True


@pytest.mark.appmap_enabled
class TestConfiguration:
    def test_package_included(self):
        f = Filterable(None, "package1.cls", None)
        assert cf().filter(f) is True

    def test_function_included_by_package(self):
        f = Filterable(None, "package1.package2.Mod1Class.func", None)
        assert cf().filter(f) is True

    def test_class_prefix_doesnt_match(self):
        f = Filterable(None, "package1_prefix.cls", None)
        assert cf().filter(f) is False

    def test_malformed_path(self, data_dir, caplog):
        _appmap.initialize(env={"APPMAP_CONFIG": "appmap-malformed-path.yml"}, cwd=data_dir)
        Config.current._load_config(show_warnings=True)  # pylint: disable=protected-access
        assert (
            "Malformed path value 'package1/package2/Mod1Class' in configuration file. "
            "Path entries must be module names not directory paths."
            in caplog.text
        )

    def test_all_paths_malformed(self, data_dir):
        _appmap.initialize(env={"APPMAP_CONFIG": "appmap-all-paths-malformed.yml"}, cwd=data_dir)
        assert len(Config().packages) == 0

    def test_empty_path(self, data_dir, caplog):
        _appmap.initialize(env={"APPMAP_CONFIG": "appmap-empty-path.yml"}, cwd=data_dir)
        Config.current._load_config(show_warnings=True)  # pylint: disable=protected-access
        assert (
            "Missing path value in configuration file."
            in caplog.text
        )


class DefaultHelpers:
    def check_default_packages(self, actual_packages):
        pkgs = [p["path"] for p in actual_packages if p["path"] in ("package", "test")]
        assert ["package", "test"] == sorted(pkgs)

    def check_default_config(self, expected_name):
        assert appmap.enabled()

        default_config = Config.current
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
        assert not Config.current.name
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

        Config.current  # pylint: disable=pointless-statement
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
        _appmap.initialize(cwd=repo_root, env={"_APPMAP": "false"})

        Config.current  # pylint: disable=pointless-statement
        assert not path.is_file()


class TestEmpty(DefaultHelpers):
    @pytest.fixture(autouse=True)
    def setup_config(self, data_dir, monkeypatch, tmpdir):
        copy_tree(data_dir / "config", str(tmpdir))
        monkeypatch.chdir(tmpdir)

    @contextmanager
    def incomplete_config(self):
        # pylint: disable=protected-access
        with open("appmap-incomplete.yml", mode="w", buffering=1, encoding="utf-8") as f:
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

class TestSearchConfig:
    # pylint: disable=too-many-arguments

    def test_config_in_parent_folder(self, data_dir, tmpdir, monkeypatch):
        copy_tree(data_dir / "config-up", str(tmpdir))
        wd = tmpdir / "project" / "p1"
        monkeypatch.chdir(wd)

        # pylint: disable=protected-access
        _appmap.initialize(cwd=wd)
        assert Config.current.name == "config-up-name"
        assert str(Env.current.output_dir).endswith(str(tmpdir / "tmp" / "appmap"))

    def _init_repo(self, data_dir, tmpdir, git_directory, repo_root, appmapdir):
        copy_tree(data_dir / "config-up", str(tmpdir))
        copy_tree(git_directory, str(repo_root))
        with open(appmapdir / "appmap.yml", "w+", encoding="utf-8") as f:
            f.writelines(
                dedent("""
                name: project
                packages: []
                """)
            )

    @pytest.mark.parametrize("subdir", [Path("p1"), Path("p2", "sub1")])
    def test_config_in_repo_root(self, data_dir, tmpdir, git_directory, monkeypatch, subdir):
        repo_root = tmpdir / "project"
        self._init_repo(data_dir, tmpdir, git_directory, repo_root, repo_root)

        wd = repo_root / subdir
        monkeypatch.chdir(wd)

        # pylint: disable=protected-access
        _appmap.initialize(cwd=wd)

        # There's a config in the repo root. It should have been found, and have
        # the correct contents.
        assert Config.current.file_present
        assert Config.current.name == "project"

        assert Env.current.enabled

    @pytest.mark.parametrize("subdir", [Path("p1"), Path("p2", "sub1")])
    def test_config_above_repo_root(self, data_dir, tmpdir, git_directory, monkeypatch, subdir):
        repo_root = tmpdir / "project"
        self._init_repo(data_dir, tmpdir, git_directory, repo_root, tmpdir)

        wd = repo_root / subdir
        monkeypatch.chdir(wd)

        # pylint: disable=protected-access
        _appmap.initialize(cwd=wd)

        # We should have stopped at the repo root without finding a config.
        assert not Config.current.file_present

        # It should go on with default config
        assert Env.current.enabled

    def test_config_not_found_in_path_hierarchy(self, data_dir, tmpdir, monkeypatch):
        copy_tree(data_dir / "config-up", str(tmpdir))
        wd = tmpdir / "project" / "p1"
        monkeypatch.chdir(wd)

        # pylint: disable=protected-access
        _appmap.initialize(
            cwd=wd,
            env={"APPMAP_CONFIG": "notfound.yml"},
        )
        Config.current  # pylint: disable=pointless-statement
        # No default config since we specified APPMAP_CONFIG
        assert not Env.current.enabled
