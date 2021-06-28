from distutils.dir_util import copy_tree
import os
import json
from pathlib import Path

import appmap._implementation
from appmap.command import appmap_agent_init

def test_agent_init(git, capsys, data_dir, monkeypatch):
    repo_root = git.cwd
    copy_tree(data_dir / 'config', str(repo_root))
    monkeypatch.chdir(repo_root)

    # pylint: disable=protected-access
    appmap._implementation.initialize(cwd=repo_root,
                                      env={
                                          'APPMAP': 'true'
                                      })

    rc = appmap_agent_init._run()
    assert rc == 0
    output = capsys.readouterr()
    config = json.loads(output.out)

    # Make sure the JSON has the correct form, and contains the
    # expected filename. The contents of the default appmap.yml are
    # verified by other tests
    assert config['configuration']['filename'] == 'appmap.yml'
    assert config['configuration']['contents'] is not None
