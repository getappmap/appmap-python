import platform
import re

from .utils import subprocess_run


class Metadata:
    @staticmethod
    def to_dict():
        metadata = {
            'language': {
                'name': 'python',
                'engine': platform.python_implementation(),
                'version': platform.python_version()
            },
            'client': {
                'name': 'appmap',
                'url': 'https://github.com/applandinc/appmap-python'
            }
        }

        if Metadata._git_available():
            metadata.update({'git': Metadata._git_metadata()})

        return metadata

    @staticmethod
    def _git_available():
        ret = subprocess_run(['git', 'status'])
        if not ret.returncode:
            return True

        return False

    @staticmethod
    def _git_metadata():
        git_repo = subprocess_run(['git', 'config', '--get', 'remote.origin.url']).stdout.strip()
        git_branch = subprocess_run(['git', 'rev-parse', '--abbrev-ref', 'HEAD']).stdout.strip()
        git_sha = subprocess_run(['git', 'rev-parse', 'HEAD']).stdout.strip()
        git_status = list(map(lambda x: x.strip(), subprocess_run(['git', 'status', '-s']).stdout.strip().split('\n')))
        git_last_annotated_tag = subprocess_run(['git', 'describe', '--abbrev=0']).stdout.strip() or None
        git_last_tag = subprocess_run(['git', 'describe', '--abbrev=0', '--tags']).stdout.strip() or None

        pattern = re.compile(r'.*-(\d+)-\w+$')

        git_commits_since_last_annotated_tag = 0
        if git_last_annotated_tag:
            result = pattern.search(subprocess_run(['git', 'describe']).stdout.strip())
            if result:
                git_commits_since_last_annotated_tag = int(result[1])

        git_commits_since_last_tag = 0
        if git_last_tag:
            result = pattern.search(subprocess_run(['git', 'describe', '--tags']).stdout.strip())
            if result:
                git_commits_since_last_tag = int(result[1])

        return {
            'repository': git_repo,
            'branch': git_branch,
            'commit': git_sha,
            'status': git_status,
            'git_last_annotated_tag': git_last_annotated_tag,
            'git_last_tag': git_last_tag,
            'git_commits_since_last_annotated_tag': git_commits_since_last_annotated_tag,
            'git_commits_since_last_tag': git_commits_since_last_tag
        }
