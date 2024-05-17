import importlib
import os
import socket
import sys
from distutils.dir_util import copy_tree
from functools import partial, partialmethod
from pathlib import Path
from typing import Any

import pytest
import yaml
from attr import dataclass
from xprocess import ProcessStarter

import _appmap
import appmap
from _appmap.test.web_framework import TEST_HOST, TEST_PORT
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
    # pylint: disable=protected-access
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
            env["_APPMAP"] = appmap_enabled
        elif appmap_enabled is False:
            env["_APPMAP"] = "false"
        elif appmap_enabled is None:
            env.pop("_APPMAP", None)

    _appmap.initialize(env=env)  # pylint: disable=protected-access

    # Some tests want yaml instrumented, others don't.
    # Reload it to make sure it's instrumented, or not, as set in appmap.yml.
    importlib.reload(yaml)

    # Remove the example_class module, so it will get reinstrumented the next time it's needed. We
    # should find a way to do this more generically, i.e. for any modules loaded by a test case.
    sys.modules.pop("example_class", None)


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
            from example_class import (  # pyright: ignore[reportMissingImports]
                ExampleClass,
            )

            # pylint: enable=import-outside-toplevel, import-error

            m = getattr(ExampleClass(), method_name)
            m()

        return generation.dump(rec)

    return _generate


@dataclass
class ServerInfo:
    name: str = ""
    debug: bool = False
    host: str = ""
    port: int = 0
    cmd: str = ""
    pattern: str = ""
    env: dict = {}
    factory: Any = None


class _ServerStarter(ProcessStarter):
    @property
    def args(self):
        return self._args

    @property
    def pattern(self):
        return self._pattern

    def startup_check(self):
        try:
            s = socket.socket()
            s.connect((self._host, self._port))
            return True
        except ConnectionRefusedError:
            pass
        return False

    def __init__(self, info: ServerInfo, controldir, xprocess):
        super().__init__(controldir, xprocess)
        self._host = info.host
        self._port = info.port
        # Can't set popen_kwargs["cwd"] on a ProcessStarter until
        # https://github.com/pytest-dev/pytest-xprocess/issues/89 is fixed.
        #
        # In the meantime, pass the desired directory to server_runner, which
        # will handle changing the working directory.
        self._args = [
            (Path(__file__).parent / "bin" / "server_runner").as_posix(),
            (Path(__file__).parent / "data" / info.name).as_posix(),
            f"{Path(sys.executable).as_posix()} {info.cmd}",
        ]
        self._pattern = info.pattern
        self.env = {**info.env}
        self.terminate_on_interrupt = True


def server_starter(info, name, cmd, pattern, env=None):
    def _starter(controldir, xprocess):
        info.name = name
        info.cmd = cmd
        if env is not None:
            info.env = {**env, **info.env}
        info.pattern = pattern
        return _ServerStarter(info, controldir, xprocess)

    return _starter


@pytest.fixture(name="server_base")
def server_base_fixture(request):
    marker = request.node.get_closest_marker("server")
    debug = marker.kwargs.get("debug", False)
    server_env = os.environ.copy()
    server_env.update(marker.kwargs.get("env", {}))

    info = ServerInfo(debug=debug, host=TEST_HOST, port=TEST_PORT, env=server_env)
    info.factory = partial(server_starter, info)
    return info
