import importlib
from distutils.dir_util import copy_tree
from functools import partialmethod

import pytest
import yaml

import _appmap
import appmap
from appmap import generation

from .. import utils
from ..recorder import Recorder


def _data_dir(pytestconfig):
    return pytestconfig.rootpath / "_appmap" / "test" / "data"


@pytest.fixture(name="data_dir")
def fixture_data_dir(pytestconfig):
    return _data_dir(pytestconfig)


@pytest.fixture(name="with_data_dir")
def fixture_with_data_dir(data_dir, monkeypatch):
    monkeypatch.syspath_prepend(data_dir)
    return data_dir


@pytest.fixture
def events():
    rec = Recorder.get_current()
    rec.clear()
    rec._enabled = True
    yield rec.events
    rec._enabled = False
    rec.clear()


@pytest.hookimpl
def pytest_runtest_setup(item):
    mark = item.get_closest_marker("appmap_enabled")
    env = {}

    if mark:
        env = mark.kwargs.get("env", {})

        appmap_yml = mark.kwargs.get("config", "appmap.yml")
        d = _data_dir(item.config)
        config = d / appmap_yml
        env["APPMAP_CONFIG"] = config

        appmap_enabled = mark.kwargs.get("appmap_enabled", None)
        if isinstance(appmap_enabled, str):
            env["APPMAP"] = appmap_enabled
        elif appmap_enabled is False:
            env["APPMAP"] = "false"
        elif appmap_enabled is None:
            env.pop("APPMAP", None)

    _appmap.initialize(env=env)  # pylint: disable=protected-access

    # Some tests want yaml instrumented, others don't.
    # Reload it to make sure it's instrumented, or not, as set in appmap.yml.
    importlib.reload(yaml)


@pytest.fixture(scope="session", name="git_directory")
def git_directory_fixture(tmp_path_factory):
    git_dir = tmp_path_factory.mktemp("test_project")
    (git_dir / "README.metadata").write_text("Read me")
    (git_dir / "new_file").write_text("new_file")

    git = utils.git(cwd=git_dir)
    git("init --initial-branch main")
    git("config --local user.email test@test")
    git("config --local user.name Test")
    git("add README.metadata")
    git('commit -m "initial commit"')
    git("remote add origin https://www.example.test/repo.git")

    return git_dir


@pytest.fixture(name="git")
def tmp_git(git_directory, tmp_path):
    copy_tree(git_directory, str(tmp_path))
    return utils.git(cwd=tmp_path)


# fix the following error:
# AttributeError: module 'django.core.mail' has no attribute 'outbox'
# https://github.com/pytest-dev/pytest-django/issues/993#issue-1147362573
@pytest.fixture(scope="function", autouse=True)
def _dj_autoclear_mailbox() -> None:
    # Override the `_dj_autoclear_mailbox` test fixture in `pytest_django`.
    pass


@pytest.fixture(name="verify_example_appmap")
def fixture_verify_appmap(monkeypatch):
    def _generate(check_fn, method_name):
        monkeypatch.setattr(
            generation.FuncEntry,
            "to_dict",
            partialmethod(check_fn, generation.FuncEntry.to_dict),
        )

        rec = appmap.Recording()
        with rec:
            # pylint: disable=import-outside-toplevel, import-error
            from example_class import ExampleClass

            # pylint: enable=import-outside-toplevel, import-error

            m = getattr(ExampleClass(), method_name)
            m()

        return generation.dump(rec)

    return _generate
