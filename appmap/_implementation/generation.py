"""Generate an AppMap"""
import json

from .metadata import Metadata
from .event import Event


# ClassMapDict needs to quack a little like a dict. If it's actually a
# subclass of dict, though, json tries to process it without calling
# our encoder. So, just implement the methods we need.
class ClassMapDict:
    def __init__(self):
        self._dict = dict()

    def setdefault(self, k, default):
        return self._dict.setdefault(k, default)

    def values(self):
        return self._dict.values()


class ClassMapEntry:
    # pylint: disable=redefined-builtin
    def __init__(self, name, type):
        self.name = name
        # `type` is a builtin, but the appmap attribute is named
        # `type`. So, ignore this warning, unless it turns out to
        # actually be a problem, of course.
        self.type = type

class PackageEntry(ClassMapEntry):
    def __init__(self, name):
        super().__init__(name, 'package')
        self.children = ClassMapDict()

class ClassEntry(ClassMapEntry):
    def __init__(self, name):
        super().__init__(name, 'class')
        self.children = ClassMapDict()

class FuncEntry(ClassMapEntry):
    def __init__(self, e):
        super().__init__(e.method_id, 'function')
        self.location = '%s:%s' % (e.path, e.lineno)
        self.static = e.static


def classmap(recording):
    ret = ClassMapDict()
    for e in recording.events:
        try:
            if e.event != 'call':
                continue
            packages, class_ = e.defined_class.rsplit('.', 1)
            children = ret
            for p in packages.split('.'):
                entry = children.setdefault(p, PackageEntry(p))
                children = entry.children

            entry = children.setdefault(class_, ClassEntry(class_))
            children = entry.children

            loc = '%s:%s' % (e.path, e.lineno)
            children.setdefault(loc, FuncEntry(e))
        except AttributeError:
            # Event might not have a defined_class attribute;
            # SQL events for example are calls without it.
            # Ignore them when building the class map.
            continue

    return ret


def appmap(recording, metadata):
    appmap_metadata = Metadata().to_dict()
    if metadata:
        appmap_metadata.update(metadata)

    return {
        'version': '1.4',
        'metadata': appmap_metadata,
        'events': recording.events,
        'classMap': list(classmap(recording).values())
    }


class AppMapEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, Event):
            return o.to_dict()
        elif isinstance(o, ClassMapDict):
            return list(o.values())
        elif isinstance(o, ClassMapEntry):
            return vars(o)

        return json.JSONEncoder.default(self, o)


def dump(recording, metadata=None):
    a = appmap(recording, metadata)
    return json.dumps(a, cls=AppMapEncoder)
