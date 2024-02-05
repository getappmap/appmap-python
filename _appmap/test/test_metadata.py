"""Test Metadata"""

# pylint: disable=protected-access, missing-function-docstring

from _appmap.metadata import Metadata

from ..test.helpers import DictIncluding


def test_missing_git(git, monkeypatch):
    monkeypatch.setenv("PATH", "")
    try:
        metadata = Metadata(root_dir=git.cwd)
        assert "git" not in metadata
    except FileNotFoundError:
        assert False, "_git_available didn't handle missing git"


def test_git_metadata(git):
    metadata = Metadata(root_dir=git.cwd)
    assert "git" in metadata
    git_md = metadata["git"]
    assert git_md == DictIncluding(
        {
            "repository": "https://www.example.test/repo.git",
            "branch": "main",
        }
    )


def test_tags(git):
    git("add new_file")
    git('commit -m "added new file"')
    git("rm README.metadata")
    git('commit -m "Removed readme"')

    metadata = Metadata(root_dir=git.cwd)
    git_md = metadata["git"]

    assert git_md == DictIncluding(
        {
            "repository": "https://www.example.test/repo.git",
            "branch": "main",
        }
    )


def test_add_framework():
    Metadata.add_framework("foo", "3.4")
    Metadata.add_framework("foo", "3.4")
    assert Metadata()["frameworks"] == [{"name": "foo", "version": "3.4"}]

    Metadata.add_framework("bar")
    Metadata.add_framework("baz", "4.2")
    assert Metadata()["frameworks"] == [
        {"name": "bar"},
        {"name": "baz", "version": "4.2"},
    ]
