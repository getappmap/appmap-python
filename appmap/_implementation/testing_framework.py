"""Shared infrastructure for testing framework integration."""

import os
import re
from contextlib import contextmanager

import inflection

from appmap._implementation import configuration, env, generation, web_framework
from appmap._implementation.env import Env
from appmap._implementation.recording import Recording
from appmap._implementation.utils import fqname

from .metadata import Metadata

try:
    # Make sure we have hooks installed if we're testing a django app.
    # pylint: disable=unused-import
    import appmap.django  # noqa: F401
except ImportError:
    pass  # probably no django


class FuncItem:
    def __init__(self, cls, name, method_id=None, location=None):
        self.cls = cls
        self.name = name
        self.method_id = method_id or name
        self.location = location

    @property
    def class_name(self):
        return self.cls.__name__

    @property
    def defined_class(self):
        return fqname(self.cls)

    def is_in_class(self):
        return self.cls is not None

    has_feature_group = is_in_class

    @property
    def feature_group(self):
        test_name = self.class_name
        if test_name.startswith("Test"):
            test_name = test_name[4:]
        return inflection.humanize(inflection.titleize(test_name))

    @property
    def feature(self):
        return inflection.humanize(self.test_name)

    @property
    def scenario_name(self):
        name = "%s%s" % (self.feature[0].lower(), self.feature[1:])
        if self.has_feature_group():
            name = " ".join([self.feature_group, name])
        return name

    @property
    def test_name(self):
        ret = self.name
        return re.sub("^test.?_", "", ret)

    @property
    def filename(self):
        fname = self.name
        if self.cls:
            fname = "%s_%s" % (self.defined_class, fname)
        fname = re.sub("[^a-zA-Z0-9-_]", "_", fname)
        if fname.endswith("_"):
            fname = fname[:-1]
        return fname

    @property
    def metadata(self):
        ret = {}
        if self.is_in_class():
            ret["feature_group"] = self.feature_group
            ret["recording"] = {
                "defined_class": self.defined_class,
                "method_id": self.method_id,
            }
        if self.location:
            ret.setdefault("recording", {}).update(
                {"source_location": "%s:%d" % self.location[0:2]}
            )
        ret.update({"name": self.scenario_name, "feature": self.feature})
        return ret


class session:
    def __init__(self, name, recorder_type, version=None):
        self.name = name
        self.recorder_type = recorder_type
        self.version = version
        self.metadata = None

    @contextmanager
    def record(self, klass, method, **kwds):
        Metadata.add_framework(self.name, self.version)

        item = FuncItem(klass, method, **kwds)

        metadata = item.metadata
        metadata.update(
            {
                "app": configuration.Config().name,
                "recorder": {
                    "name": self.name,
                    "type": self.recorder_type,
                },
            }
        )

        rec = Recording()
        try:
            with rec:
                yield metadata
        finally:
            basedir = env.Env.current.output_dir / self.name
            web_framework.write_appmap(
                basedir, item.filename, generation.dump(rec, metadata)
            )


@contextmanager
def collect_result_metadata(metadata):
    """Collect test case result metadata.

    Sets test_status and exception information.
    """
    try:
        yield
        metadata["test_status"] = "succeeded"
    except Exception as exn:
        metadata["test_status"] = "failed"
        metadata["exception"] = {"class": exn.__class__.__name__, "message": str(exn)}
        raise


def file_delete(filename):
    try:
        os.remove(filename)
    except FileNotFoundError:
        pass
