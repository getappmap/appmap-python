import inflection
import re

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
    def __init__(self, cls, name, method_id=None):
        self.cls = cls
        self.name = name
        self.method_id = method_id or name

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
        ret.update({
            'name': self.scenario_name,
            'feature': self.feature
        })
        return ret


class session:
    def __init__(self, name, version=None):
        if not env.enabled():
            return

        self.appmap_path = Path(configuration.Config().output_dir) / name
        self.appmap_path.mkdir(parents=True, exist_ok=True)

        framework = {'name': name}
        if version is not None:
            framework['version'] = version

        self.metadata = {
            'app': configuration.Config().name,
            'frameworks': [framework],
            'recorder': {
                'name': name
            }
        }

    @contextmanager
    def record(self, klass, method, **kwds):
        if not env.enabled():
            yield
            return

        rec = recording.Recording()
        with rec:
            yield

        fi = FuncItem(klass, method, **kwds)
        filename = fi.filename + '.appmap.json'
        metadata = fi.metadata
        metadata.update(self.metadata)
        (self.appmap_path / filename).write_text(generation.dump(rec, metadata))
