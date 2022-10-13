"""Test Metadata"""
# pylint: disable=protected-access, missing-function-docstring

import pytest

from appmap._implementation.metadata import Metadata
from appmap.test.helpers import DictIncluding


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
            "status": ["?? new_file"],
        }
    )
    for key in (
        "tag",
        "annotated_tag",
        "commits_since_tag",
        "commits_since_annotated_tag",
    ):
        assert key not in git_md


def test_tags(git):
    atag = "new_annotated_tag"
    git(f'tag -a "{atag}" -m "add annotated tag"')

    git("add new_file")
    git('commit -m "added new file"')

    tag = "new_tag"
    git(f"tag {tag}")

    git("rm README.metadata")
    git('commit -m "Removed readme"')

    metadata = Metadata(root_dir=git.cwd)
    git_md = metadata["git"]

    assert git_md == DictIncluding(
        {
            "repository": "https://www.example.test/repo.git",
            "branch": "main",
            "tag": tag,
            "annotated_tag": atag,
            "commits_since_tag": 1,
            "commits_since_annotated_tag": 2,
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
