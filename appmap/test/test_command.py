from distutils.dir_util import copy_tree
import os
import json
from pathlib import Path

import yaml
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
def test_agent_init_config(cmd_setup, capsys):
    rc = appmap_agent_init._run()
    assert rc == 0
    output = capsys.readouterr()
    config = json.loads(output.out)

    # Make sure the JSON has the correct form, and contains the
    # expected filename. The contents of the default appmap.yml are
    # verified by other tests
    assert config['configuration']['filename'] == 'appmap.yml'
    assert config['configuration']['contents'] is not None

class TestAgentInit:
    # @pytest.mark.parametrize("cmd_setup", ["pytest"], indirect=True)
    def test_with_pytest_tests(self, data_dir, virtualenv):
        virtualenv.run(f'cd {os.getcwd()}; poetry install --no-dev') # install appmap in the virtual env
        virtualenv.run('pip install pytest')
        copy_tree(data_dir / 'pytest', str(virtualenv.workspace))
        out = virtualenv.run("python -c 'from appmap.command import appmap_agent_init as cmd; cmd._run()'", capture=True)
        config = yaml.safe_load(json.loads(out)["configuration"]["contents"])
        assert config["test_commands"][0] == DictIncluding({
            "framework": "pytest",
            "command": {
                "program": "pytest",
                "environment": {
                    "APPMAP": "true"
                }
            }
        })

    @pytest.mark.parametrize("cmd_setup", ["package1"], indirect=True)
    def test_no_tests(self, cmd_setup, capsys):
        rc = appmap_agent_init._run()
        assert rc == 0
        output = capsys.readouterr()
        config = yaml.safe_load(json.loads(output.out)["configuration"]["contents"])

        assert 'test_commands' not in config

@pytest.mark.parametrize("cmd_setup", ["agent_status"], indirect=True)
def test_agent_status(cmd_setup, capsys):
    rc = appmap_agent_status._run()
    assert rc == 0
    output = capsys.readouterr()
    status = json.loads(output.out)

    assert status == DictIncluding({
        "properties": {
            "config": {
                "app": "agent_status_test",
                "present": True,
                "valid": True
            },
            "project": {
                "agentVersion": "0.0.0",
                "language": "python",
                "remoteRecordingCapable": True,
            }},
        "test_commands": [{
            "framework": "pytest",
            "command": {
                "program": "pytest",
                "environment": {
                    "APPMAP": "true"
                }
            }
        }]
    })
