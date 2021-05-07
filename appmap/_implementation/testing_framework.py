import inflection
import os
import re
from tempfile import NamedTemporaryFile

from contextlib import contextmanager
from pathlib import Path

from appmap._implementation import configuration, env, generation, recording
from appmap._implementation.utils import fqname


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


class session:
    def __init__(self, name, version=None):
        self.name = name
        self.version = version
        self.appmap_path = None
        self.metadata = None

    @contextmanager
    def record(self, klass, method, **kwds):
        if not env.Env.current.enabled:
            yield
            return

        self.appmap_path = Path(env.Env.current.output_dir) / self.name
        self.appmap_path.mkdir(parents=True, exist_ok=True)

        framework = {'name': self.name}
        if self.version is not None:
            framework['version'] = self.version

        self.metadata = {
            'app': configuration.Config().name,
            'frameworks': [framework],
            'recorder': {
                'name': self.name
            }
        }

        rec = recording.Recording()
        with rec:
            yield

        fi = FuncItem(klass, method, **kwds)
        filename = fi.filename + '.appmap.json'
        metadata = fi.metadata
        metadata.update(self.metadata)
        appmap_json = self.appmap_path / filename
        with NamedTemporaryFile(mode='w', dir=self.appmap_path, delete=False) as f:
            f.write(generation.dump(rec, metadata))
            try:
                os.remove(appmap_json)
            except FileNotFoundError:
                pass
            os.replace(f.name, appmap_json)
