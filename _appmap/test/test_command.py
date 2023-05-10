import json
import re
from distutils.dir_util import copy_tree

import pytest
from importlib_metadata import version

import _appmap
from appmap.command import appmap_agent_init, appmap_agent_status, appmap_agent_validate

from .helpers import DictIncluding


@pytest.fixture(name="cmd_setup")
def _cmd_setup(request, git, data_dir, monkeypatch):
    repo_root = git.cwd
    copy_tree(data_dir / request.param, str(repo_root))
    monkeypatch.chdir(repo_root)

    # pylint: disable=protected-access
    _appmap.initialize(cwd=repo_root)

    return monkeypatch


@pytest.mark.parametrize("cmd_setup", ["config"], indirect=True)
def test_agent_init(cmd_setup, capsys):
    rc = appmap_agent_init._run()  # pylint: disable=protected-access

    assert rc == 0
    output = capsys.readouterr()
    config = json.loads(output.out)

    # Make sure the JSON has the correct form, and contains the
    # expected filename. The contents of the default appmap.yml are
    # verified by other tests
    assert config["configuration"]["filename"] == "appmap.yml"
    assert config["configuration"]["contents"] is not None


class TestAgentStatus:
    @pytest.mark.parametrize("cmd_setup", ["pytest"], indirect=True)
    @pytest.mark.parametrize("do_discovery", [True, False])
    def test_test_discovery_control(self, cmd_setup, do_discovery, mocker):
        mocker.patch("appmap.command.appmap_agent_status.discover_pytest_tests")
        rc = appmap_agent_status._run(  # pylint: disable=protected-access
            discover_tests=do_discovery
        )
        assert rc == 0
        call_count = 1 if do_discovery else 0
        assert appmap_agent_status.discover_pytest_tests.call_count == call_count

    @pytest.mark.parametrize("cmd_setup", ["pytest"], indirect=True)
    def test_agent_status(self, cmd_setup, capsys):
        rc = appmap_agent_status._run(discover_tests=True)  # pylint: disable=protected-access

        assert rc == 0
        output = capsys.readouterr()
        status = json.loads(output.out)
        # XXX This will detect pytest as the test framework, because
        # appmap-python uses it. We need a better mechanism to handle
        # testing more broadly.
        props = status["properties"]
        config = props["config"]
        assert config == DictIncluding({"app": "Simple", "present": True, "valid": True})
        project = props["project"]
        assert project == DictIncluding(
            {
                "language": "python",
                "remoteRecordingCapable": True,
                "integrationTests": True,
            }
        )
        assert "agentVersion" in project
        test_commands = status["test_commands"]
        assert test_commands[0] == DictIncluding(
            {"args": [], "framework": "pytest", "command": "pytest"}
        )

    @pytest.mark.parametrize("cmd_setup", ["package1"], indirect=True)
    def test_agent_status_no_commands(self, cmd_setup, capsys):
        rc = appmap_agent_status._run(discover_tests=True)  # pylint: disable=protected-access

        assert rc == 0
        output = capsys.readouterr()
        status = json.loads(output.out)

        assert "test_commands" not in status


class TestAgentValidate:
    def check_errors(self, capsys, status, count, msg):
        rc = appmap_agent_validate._run()  # pylint: disable=protected-access

        assert rc == status

        output = capsys.readouterr()
        errors = json.loads(output.out)

        assert len(errors) == count
        if count > 0:
            err = errors[0]
            assert err["level"] == "error"
            assert re.match(msg, err["message"]) is not None

    def test_no_errors(self, capsys, mocker):
        # Both Django and flask are installed in a dev environment, so
        # validation will succeed.
        self.check_errors(capsys, 0, 0, None)

    def test_python_version(self, capsys, mocker):
        mocker.patch(
            "_appmap.py_version_check._get_py_version",
            return_value=(3, 5),
        )
        mocker.patch(
            "_appmap.py_version_check._get_platform_version",
            return_value="3.5",
        )

        self.check_errors(capsys, 1, 1, r"Minimum Python version supported is \d\.\d, found")

    def test_django_version(self, capsys, mocker):
        mocker.patch(
            "appmap.command.appmap_agent_validate.version",
            side_effect=lambda d: "3.1" if d == "django" else version(d),
        )

        self.check_errors(capsys, 1, 1, "django must have version >= 3.2, found 3.1")

    def test_flask_version(self, capsys, mocker):
        mocker.patch(
            "appmap.command.appmap_agent_validate.version",
            side_effect=lambda d: "1.0" if d == "flask" else version(d),
        )

        self.check_errors(capsys, 1, 1, "flask must have version >= 1.1, found 1.0")
