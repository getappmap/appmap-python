"""Generate an AppMap"""
import json
from collections.abc import MutableMapping

from . import metadata

from .event import Event, serialize_event


class ClassMapSet(MutableMapping):
    def __init__(self):
        self.dict = dict()

    def __delitem__(self, k):
        import pdb; pdb.set_trace()
        self.dict.discard(k)

    def __getitem__(self, k):
        return self.dict[k]

    def __setitem__(self, k, v):
        self.dict[k] = v

    def __iter__(self):
        return self.dict.__iter__()

    def __len__(self):
        return len(self.dict)

class ClassMapEntry:
    def __init__(self, key, name, type):
        self.key = key
        self.name = name
        self.type = type

    def __eq__(self, other):
        return self.key == other.key

    def __hash__(self):
        return hash(self.key)


class PackageEntry(ClassMapEntry):
    def __init__(self, name):
        super().__init__(key=name, name=name, type='package')
        self.children = ClassMapSet()

    __hash__ = ClassMapEntry.__hash__


class ClassEntry(ClassMapEntry):
    def __init__(self, name):
        super().__init__(key=name, name=name, type='class')
        self.children = ClassMapSet()

    __hash__ = ClassMapEntry.__hash__


class FuncEntry(ClassMapEntry):
    def __init__(self, e, loc):
        super().__init__(key=loc, name=e.method_id, type='function')
        self.path = e.path
        self.lineno = e.lineno
        self.static = e.static

    __hash__ = ClassMapEntry.__hash__


def asdict(s):
    ret = vars(s)
    del ret['key']
    return ret


def classmap(recording):
    classmap = ClassMapSet()
    for e in recording.events:
        if e.event != 'call':
            continue
        packages, class_ = e.defined_class.rsplit('.', 1)
        children = classmap
        for p in packages.split('.'):
            entry = children.setdefault(p, PackageEntry(p))
            children = entry.children

        entry = children.setdefault(class_, ClassEntry(class_))
        children = entry.children

        loc = f'{e.path}:{e.lineno}'
        children.setdefault(loc, FuncEntry(e, loc))

    return classmap


def appmap(recording):
    return {
        'version': '1.4',
        'metadata': metadata.Metadata.dump(),
        'events': recording.events,
        'classMap': list(classmap(recording).values())
    }


class AppMapEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, Event):
            return serialize_event(obj)
        elif isinstance(obj, ClassMapSet):
            return list(obj.values())
        elif isinstance(obj, ClassMapEntry):
            return asdict(obj)
        return json.JSONEncoder.default(self, obj)


def dump(recording):
    a = appmap(recording)
    return json.dumps(a, cls=AppMapEncoder)
