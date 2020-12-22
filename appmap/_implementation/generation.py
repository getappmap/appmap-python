"""Generate an AppMap"""
import json
from collections.abc import MutableMapping

from . import metadata

from .event import Event, serialize_event


class ClassMapSet(MutableMapping):
    def __init__(self):
        self.dict = dict()

    def __delitem__(self, k):
        del self[k]

    def __getitem__(self, k):
        return self.dict[k]

    def __setitem__(self, k, v):
        self.dict[k] = v

    def __iter__(self):
        return self.dict.__iter__()

    def __len__(self):
        return len(self.dict)


class ClassMapEntry:
    def __init__(self, key, name, entry_type):
        self.key = key
        self.name = name
        self.type = entry_type

    def __eq__(self, other):
        return self.key == other.key

    def __hash__(self):
        return hash(self.key)


class PackageEntry(ClassMapEntry):
    def __init__(self, name):
        super().__init__(name, name, 'package')
        self.children = ClassMapSet()


class ClassEntry(ClassMapEntry):
    def __init__(self, name):
        super().__init__(name, name, 'class')
        self.children = ClassMapSet()


class FuncEntry(ClassMapEntry):
    def __init__(self, e, loc):
        super().__init__(loc, e.method_id, 'function')
        self.path = e.path
        self.lineno = e.lineno
        self.static = e.static


def classmap(recording):
    ret = ClassMapSet()
    for e in recording.events:
        if e.event != 'call':
            continue
        packages, class_ = e.defined_class.rsplit('.', 1)
        children = ret
        for p in packages.split('.'):
            entry = children.setdefault(p, PackageEntry(p))
            children = entry.children

        entry = children.setdefault(class_, ClassEntry(class_))
        children = entry.children

        loc = f'{e.path}:{e.lineno}'
        children.setdefault(loc, FuncEntry(e, loc))

    return ret


def appmap(recording):
    return {
        'version': '1.4',
        'metadata': metadata.Metadata.dump(),
        'events': recording.events,
        'classMap': list(classmap(recording).values())
    }


class AppMapEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, Event):
            return serialize_event(o)
        elif isinstance(o, ClassMapSet):
            return list(o.values())
        elif isinstance(o, ClassMapEntry):
            return AppMapEncoder.asdict(o)
        return json.JSONEncoder.default(self, o)

    @staticmethod
    def asdict(s):
        ret = vars(s)
        del ret['key']
        return ret



def dump(recording):
    a = appmap(recording)
    return json.dumps(a, cls=AppMapEncoder)
