import logging
import platform
import re
import os

from . import utils

logger = logging.getLogger(__name__)


class Metadata:
    def __init__(self, cwd=None):
        self._cwd = cwd if cwd else os.getcwd()

    def to_dict(self):
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

        if self._git_available():
            metadata.update({'git': self._git_metadata()})

        return metadata

    def _git_available(self):
        try:
            ret = utils.subprocess_run(['git', 'status'], cwd=self._cwd)
            if not ret.returncode:
                return True
            logger.warning("Failed running 'git status', %s", ret.stderr)
        except FileNotFoundError as exc:
            msg = """
    Couldn't find git executable, repository information
    will not be included in the AppMap.

    Make sure git is installed and that your PATH is set
    correctly.

    Error: %s
    """
            logger.warning(msg, str(exc))

        return False

    def _git_metadata(self):
        git = utils.git(cwd=self._cwd)
        repository = git('config --get remote.origin.url')
        branch = git('rev-parse --abbrev-ref HEAD')
        commit = git('rev-parse HEAD')
        status = list(map(lambda x: x.strip(), git('status -s').split('\n')))
        annotated_tag = git('describe --abbrev=0') or None
        tag = git('describe --abbrev=0 --tags') or None

        pattern = re.compile(r'.*-(\d+)-\w+$')

        commits_since_annotated_tag = None
        if annotated_tag:
            result = pattern.search(git('describe'))
            if result:
                commits_since_annotated_tag = int(result.group(1))

        commits_since_tag = None
        if tag:
            result = pattern.search(git('describe --tags'))
            if result:
                commits_since_tag = int(result.group(1))

        ret = {
            'repository': repository,
            'branch': branch,
            'commit': commit,
            'status': status,
            'tag': tag,
            'annotated_tag': annotated_tag,
            'commits_since_tag': commits_since_tag,
            'commits_since_annotated_tag': commits_since_annotated_tag
        }
        return { k: v for k,v in ret.items() if v is not None }
