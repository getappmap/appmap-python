# pylint: disable=protected-access

"""Test Metadata"""
from appmap._implementation.metadata import Metadata

class TestMetadata:
    def test_fixture(self, tmp_git):
        md = Metadata(cwd=tmp_git.cwd)
        assert md._git_available() # sanity check

    def test_git_metadata(self, tmp_git):
        md = Metadata(cwd=tmp_git.cwd)

        git_md = md._git_metadata()
        expected = {
            'repository': 'https://www.example.com/repo.git',
            'branch': 'master',
            'status': [
                '?? new_file'
            ]
        }
        for k,v in expected.items():
            assert git_md[k] == v
        missing = ('tag', 'annotated_tag',
                   'commits_since_tag', 'commit_since_annotated_tag')
        for m in missing:
            assert m not in git_md

    def test_tag(self, tmp_git):
        tag = 'new_tag'
        tmp_git('tag %s' % (tag))
        md = Metadata(cwd=tmp_git.cwd)
        git_md = md._git_metadata()

        assert git_md['tag'] == tag
        assert 'commits_since_tag' not in git_md

    def test_annotated_tag(self, tmp_git):
        tag = 'new_annotated_tag'
        tmp_git('tag -a "%s" -m "add annotated tag"' % (tag))
        md = Metadata(cwd=tmp_git.cwd)
        git_md = md._git_metadata()

        assert git_md['annotated_tag'] == tag
        assert 'commits_since_annotated_tag' not in git_md

    def test_since_tag(self, tmp_git):
        tag = 'new_tag'
        tmp_git('tag %s' % (tag))
        tmp_git('add new_file')
        tmp_git('commit -m "added new file"')
        md = Metadata(cwd=tmp_git.cwd)
        git_md = md._git_metadata()

        assert git_md['commits_since_tag'] == 1

    def test_since_annotated_tag(self, tmp_git):
        tag = 'new_tag'
        tmp_git('tag -a "%s" -m "add annotated tag"' % (tag))
        tmp_git('add new_file')
        tmp_git('commit -m "added new file"')
        md = Metadata(cwd=tmp_git.cwd)
        git_md = md._git_metadata()

        assert git_md['commits_since_annotated_tag'] == 1
