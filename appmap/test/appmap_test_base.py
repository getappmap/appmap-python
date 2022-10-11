import json
import platform
import re
from operator import itemgetter

import pytest

import appmap._implementation
from appmap._implementation.recorder import Recorder


def normalize_path(path):
    """
    Normalize absolute path to a file in a package down to a package path.
    Not foolproof, but good enough for the tests.
    """
    return re.sub(r"^.*site-packages/", "", path)


class AppMapTestBase:
    def setup_method(self, _):
        appmap._implementation.initialize()  # pylint: disable=protected-access

    @staticmethod
    @pytest.fixture
    def events():
        rec = Recorder.get_current()
        rec.clear()
        rec._enabled = True
        return rec.events

    @staticmethod
    def normalize_git(git):
        git.pop("repository")
        git.pop("branch")
        git.pop("commit")
        status = git.pop("status")
        assert isinstance(status, list)
        tag = git.pop("tag", None)
        if tag:
            assert isinstance(tag, str)
        commits_since_tag = git.pop("commits_since_tag", None)
        if commits_since_tag:
            assert isinstance(commits_since_tag, int)
        git.pop("annotated_tag", None)

        commits_since_annotated_tag = git.pop("commits_since_annotated_tag", None)
        if commits_since_annotated_tag:
            assert isinstance(commits_since_annotated_tag, int)

    @staticmethod
    def normalize_metadata(metadata):
        engine = metadata["language"].pop("engine")
        assert engine == platform.python_implementation()
        version = metadata["language"].pop("version")
        assert version == platform.python_version()

        if "frameworks" in metadata:
            frameworks = metadata["frameworks"]
            for f in frameworks:
                if f["name"] == "pytest":
                    v = f.pop("version")
                    assert v == pytest.__version__

    def normalize_appmap(self, generated_appmap):
        """
        Normalize the data in generated_appmap, removing any
        environment-specific values.

        Note that attempts to access required keys will raise
        KeyError, causing the test to fail.
        """

        def normalize(dct):
            if "classMap" in dct:
                dct["classMap"].sort(key=itemgetter("name"))
            if "children" in dct:
                dct["children"].sort(key=itemgetter("name"))
            if "elapsed" in dct:
                elapsed = dct.pop("elapsed")
                assert isinstance(elapsed, float)
            if "git" in dct:
                self.normalize_git(dct.pop("git"))
            if "location" in dct:
                dct["location"] = normalize_path(dct["location"])
            if "path" in dct:
                dct["path"] = normalize_path(dct["path"])
            if "metadata" in dct:
                self.normalize_metadata(dct["metadata"])
            if "object_id" in dct:
                object_id = dct.pop("object_id")
                assert isinstance(object_id, int)
            if "value" in dct:
                # This maps all object references to the same
                # location. We don't actually need to verify that the
                # locations are correct -- if they weren't, the
                # instrumented code would be broken, right?
                v = dct["value"]
                dct["value"] = re.sub(
                    r"<(.*) object at 0x.*>", r"<\1 object at 0xabcdef>", v
                )
            return dct

        return json.loads(generated_appmap, object_hook=normalize)
