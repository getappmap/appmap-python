import pytest

from appmap._implementation import utils

@pytest.fixture
def tmp_git(tmp_path):
    g = utils.git(cwd=tmp_path)
    g('init')
    utils.subprocess_run(['touch', 'README.md'], cwd=tmp_path)
    g('add README.md')
    g('commit -m "initial commit"')
    g('remote add origin https://www.example.com/repo.git')
    utils.subprocess_run(['touch', 'new_file'], cwd=tmp_path)
    return g
