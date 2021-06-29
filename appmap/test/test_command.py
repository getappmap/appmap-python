from distutils.dir_util import copy_tree
import os
import json
from pathlib import Path

import pytest

import appmap._implementation
from appmap.command import appmap_agent_init, appmap_agent_status
from .helpers import DictIncluding

@pytest.fixture
def cmd_setup(request, git, data_dir, monkeypatch):
    repo_root = git.cwd
    copy_tree(data_dir / request.param, str(repo_root))
    monkeypatch.chdir(repo_root)

    # pylint: disable=protected-access
    appmap._implementation.initialize(cwd=repo_root)

    return monkeypatch

@pytest.mark.parametrize("cmd_setup", ["config"], indirect=True)
def test_agent_init(cmd_setup, capsys):
    rc = appmap_agent_init._run()
    assert rc == 0
    output = capsys.readouterr()
    config = json.loads(output.out)

    # Make sure the JSON has the correct form, and contains the
    # expected filename. The contents of the default appmap.yml are
    # verified by other tests
    assert config['configuration']['filename'] == 'appmap.yml'
    assert config['configuration']['contents'] is not None

class TestAgentStatus:
    @pytest.mark.parametrize("cmd_setup", ["pytest"], indirect=True)
    @pytest.mark.parametrize("do_discovery", [True, False])
    def test_test_discovery_control(self, cmd_setup, do_discovery, mocker):
        mocker.patch("appmap.command.appmap_agent_status.discover_pytest_tests")
        rc = appmap_agent_status._run(discover_tests=do_discovery)
        assert rc == 0
        call_count = 1 if do_discovery else 0
        assert appmap_agent_status.discover_pytest_tests.call_count == call_count


    @pytest.mark.parametrize("cmd_setup", ["pytest"], indirect=True)
    def test_agent_status(self, cmd_setup, capsys):
        rc = appmap_agent_status._run(discover_tests=True)
        assert rc == 0
        output = capsys.readouterr()
        status = json.loads(output.out)
        # XXX This will detect pytest as the test framework, because
        # appmap-python uses it. We need a better mechanism to handle
        # testing more broadly.
        assert status == DictIncluding({
            "properties": {
                "config": {
                    "app": "Simple",
                    "present": True,
                    "valid": True
                },
            "project": {
                "agentVersion": "0.0.0",
                "language": "python",
                "remoteRecordingCapable": True,
                "integrationTests": True
            }
            },
            "test_commands": [{
                "args": [],
                "framework": "pytest",
                "command": "pytest",
                "environment": {
                    "APPMAP": "true"
                }
            }]})

    @pytest.mark.parametrize("cmd_setup", ["package1"], indirect=True)
    def test_agent_status(self, cmd_setup, capsys):
        rc = appmap_agent_status._run(discover_tests=True)
        assert rc == 0
        output = capsys.readouterr()
        status = json.loads(output.out)

        assert 'test_commands' not in status
