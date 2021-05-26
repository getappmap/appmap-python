"""Shared infrastructure for testing framework integration."""

from hashlib import sha256
import inflection
import os
import re
from tempfile import NamedTemporaryFile

from contextlib import contextmanager

from appmap._implementation import configuration, env, generation, recording
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
        if test_name.startswith('Test'):
            test_name = test_name[4:]
        return inflection.humanize(inflection.titleize(test_name))

    @property
    def feature(self):
        return inflection.humanize(self.test_name)

    @property
    def scenario_name(self):
        name = '%s%s' % (self.feature[0].lower(), self.feature[1:])
        if self.has_feature_group():
            name = ' '.join([self.feature_group, name])
        return name

    @property
    def test_name(self):
        ret = self.name
        return re.sub('^test.?_', '', ret)

    @property
    def filename(self):
        fname = self.name
        if self.cls:
            fname = '%s_%s' % (self.defined_class, fname)
        fname = re.sub('[^a-zA-Z0-9-_]', '_', fname)
        if fname.endswith('_'):
            fname = fname[:-1]
        return fname

    @property
    def metadata(self):
        ret = {}
        if self.is_in_class():
            ret['feature_group'] = self.feature_group
            ret['recording'] = {
                'defined_class': self.defined_class,
                'method_id': self.method_id
            }
        if self.location:
            ret.setdefault('recording', {}).update({
                'source_location': '%s:%d' % self.location[0:2]
            })
        ret.update({
            'name': self.scenario_name,
            'feature': self.feature
        })
        return ret


NAME_MAX = 255  # true for most filesystems
HASH_LEN = 7  # arbitrary, but git proves it's a reasonable value
APPMAP_SUFFIX = '.appmap.json'


def name_hash(namepart):
    """Returns the hex digits of the sha256 of the os.fsencode()d namepart."""
    return sha256(os.fsencode(namepart)).hexdigest()


def write_appmap(basedir, basename, contents):
    """Write an appmap file into basedir.

    Adds APPMAP_SUFFIX to basename; shortens the name if necessary.
    Atomically replaces existing files. Creates the basedir if required.
    """

    if len(basename) > NAME_MAX - len(APPMAP_SUFFIX):
        part = NAME_MAX - len(APPMAP_SUFFIX) - 1 - HASH_LEN
        basename = basename[:part] + '-' + name_hash(basename[part:])[:HASH_LEN]
    filename = basename + APPMAP_SUFFIX

    if not basedir.exists():
        basedir.mkdir(parents=True, exist_ok=True)

    with NamedTemporaryFile(mode='w', dir=basedir, delete=False) as tmp:
        tmp.write(contents)
    os.replace(tmp.name, basedir / filename)


class session:
    def __init__(self, name, version=None):
        self.name = name
        self.version = version
        self.metadata = None

    @contextmanager
    def record(self, klass, method, **kwds):
        if not env.Env.current.enabled:
            yield
            return

        Metadata.add_framework(self.name, self.version)

        item = FuncItem(klass, method, **kwds)

        metadata = item.metadata
        metadata.update({
            'app': configuration.Config().name,
            'recorder': {
                'name': self.name
            }
        })

        rec = recording.Recording()
        try:
            with rec:
                yield metadata
        finally:
            basedir = env.Env.current.output_dir / self.name
            write_appmap(basedir, item.filename, generation.dump(rec, metadata))


@contextmanager
def collect_result_metadata(metadata):
    """Collect test case result metadata.

    Sets test_status and exception information.
    """
    try:
        yield
        metadata['test_status'] = 'succeeded'
    except Exception as exn:
        metadata['test_status'] = 'failed'
        metadata['exception'] = {
            'class': exn.__class__.__name__,
            'message': str(exn)
        }
        raise
