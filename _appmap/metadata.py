"""Shared metadata gathering"""

import logging
import platform
import re
from functools import lru_cache

from . import utils
from .env import Env
from .utils import compact_dict

logger = logging.getLogger(__name__)


def _lines(text):
    """Split text into lines, stripping and returning just the nonempty ones.

    Returns None if the result would be empty."""

    lines = [x for x in map(lambda x: x.strip(), text.split("\n")) if len(x) > 0]
    if len(lines) == 0:
        return None
    return lines


class Metadata(dict):
    """A dict that self-initializes to reflect platform and git metadata."""

    def __init__(self, root_dir=None):
        super().__init__(self.base(root_dir or Env.current.root_dir))

        if any(self.__class__.frameworks):
            self["frameworks"] = self.__class__.frameworks
            self.reset()

    frameworks = []

    @classmethod
    def add_framework(cls, name, version=None):
        """Add a framework that will end up (only) in the next Metadata() created.

        Duplicate entries are ignored.
        """
        if not any(f["name"] == name for f in cls.frameworks):
            cls.frameworks.append(compact_dict({"name": name, "version": version}))

    @classmethod
    def reset(cls):
        """Resets stored framework metadata."""
        cls.frameworks = []

    @staticmethod
    @lru_cache()
    def base(root_dir):
        """Gathers git and platform metadata given the project root directory path."""
        metadata = {
            "language": {
                "name": "python",
                "engine": platform.python_implementation(),
                "version": platform.python_version(),
            },
            "client": {
                "name": "appmap",
                "url": "https://github.com/applandinc/appmap-python",
            },
        }

        if Metadata._git_available(root_dir):
            metadata.update({"git": Metadata._git_metadata(root_dir)})

        return metadata

    @staticmethod
    @lru_cache()
    def _git_available(root_dir):
        try:
            ret = utils.subprocess_run(["git", "status"], cwd=root_dir)
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

    @staticmethod
    @lru_cache()
    def _git_metadata(root_dir):
        git = utils.git(cwd=root_dir)
        repository = git("config --get remote.origin.url")
        branch = git("rev-parse --abbrev-ref HEAD")
        commit = git("rev-parse HEAD")
        status = _lines(git("status -s"))
        annotated_tag = git("describe --abbrev=0") or None
        tag = git("describe --abbrev=0 --tags") or None

        pattern = re.compile(r".*-(\d+)-\w+$")

        commits_since_annotated_tag = None
        if annotated_tag:
            result = pattern.search(git("describe"))
            if result:
                commits_since_annotated_tag = int(result.group(1))

        commits_since_tag = None
        if tag:
            result = pattern.search(git("describe --tags"))
            if result:
                commits_since_tag = int(result.group(1))

        return compact_dict(
            {
                "repository": repository,
                "branch": branch,
                "commit": commit,
                "status": status,
                "tag": tag,
                "annotated_tag": annotated_tag,
                "commits_since_tag": commits_since_tag,
                "commits_since_annotated_tag": commits_since_annotated_tag,
            }
        )


def initialize():
    Metadata.reset()
