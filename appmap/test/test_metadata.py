"""Test Metadata"""
# pylint: disable=protected-access, missing-function-docstring

from distutils.dir_util import copy_tree
import pytest

from appmap._implementation import utils
from appmap._implementation.metadata import Metadata


@pytest.fixture(scope='session', name='git_directory')
def git_directory_fixture(tmp_path_factory):
    git_dir = tmp_path_factory.mktemp('test-project')
    (git_dir / 'README.metadata').write_text('Read me')
    (git_dir / 'new_file').write_text('new_file')

    git = utils.git(cwd=git_dir)
    git('init')
    git('config --local user.email test@test')
    git('config --local user.name Test')
    git('add README.metadata')
    git('commit -m "initial commit"')
    git('remote add origin https://www.example.test/repo.git')

    return git_dir


@pytest.fixture(name='git')
def tmp_git(git_directory, tmp_path):
    copy_tree(git_directory, str(tmp_path))
    return utils.git(cwd=tmp_path)


def test_missing_git(git, monkeypatch):
    monkeypatch.setenv('PATH', '')
    try:
        metadata = Metadata(cwd=git.cwd)
        assert not metadata._git_available()
    except FileNotFoundError:
        assert False, "_git_available didn't handle missing git"


def test_git_metadata(git):
    metadata = Metadata(cwd=git.cwd)
    assert metadata._git_available()  # sanity check
    git_md = metadata._git_metadata()
    expected = {
        'repository': 'https://www.example.test/repo.git',
        'branch': 'master',
        'status': [
            '?? new_file'
        ]
    }
    for key, val in expected.items():
        assert git_md[key] == val
    for key in (
        'tag', 'annotated_tag', 'commits_since_tag', 'commits_since_annotated_tag'
    ):
        assert key not in git_md


def test_tags(git):
    atag = 'new_annotated_tag'
    git(f'tag -a "{atag}" -m "add annotated tag"')

    git('add new_file')
    git('commit -m "added new file"')

    tag = 'new_tag'
    git(f'tag {tag}')

    git('rm README.metadata')
    git('commit -m "Removed readme"')

    metadata = Metadata(cwd=git.cwd)
    git_md = metadata._git_metadata()

    assert git_md == {
        'repository': 'https://www.example.test/repo.git',
        'branch': 'master',
        'commit': git_md['commit'],
        'tag': tag,
        'annotated_tag': atag,
        'commits_since_tag': 1,
        'commits_since_annotated_tag': 2
    }
