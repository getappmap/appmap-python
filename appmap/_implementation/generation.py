"""Generate an AppMap"""
import orjson
from dataclasses import dataclass, field

from .metadata import Metadata
from .event import Event


class ClassMapDict(dict):
    pass


@dataclass
class ClassMapEntry:
    name: str
    type: str


@dataclass
class PackageEntry(ClassMapEntry):
    children: ClassMapDict = field(default_factory=ClassMapDict)
    type: str = 'package'


@dataclass
class ClassEntry(ClassMapEntry):
    children: ClassMapDict = field(default_factory=ClassMapDict)
    type: str = 'class'


@dataclass
class FuncEntry(ClassMapEntry):
    location: str
    static: bool

    def __init__(self, e):
        super().__init__(e.method_id, 'function')
        self.location = f'{e.path}:{e.lineno}'
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

            loc = f'{e.path}:{e.lineno}'
            children.setdefault(loc, FuncEntry(e))
        except AttributeError:
            # Event might not have a defined_class attribute;
            # SQL events for example are calls without it.
            # Ignore them when building the class map.
            continue

    return ret


def appmap(recording, metadata):
    appmap_metadata = Metadata.to_dict()
    if metadata:
        appmap_metadata.update(metadata)

    return {
        'version': '1.4',
        'metadata': appmap_metadata,
        'events': recording.events,
        'classMap': list(classmap(recording).values())
    }


class AppMapEncoder:
    @staticmethod
    def default(o):
        if isinstance(o, Event):
            return o.to_dict()
        elif isinstance(o, ClassMapDict):
            return list(o.values())
        elif isinstance(o, ClassMapEntry):
            return vars(o)
        raise TypeError


def dump(recording, metadata=None):
    a = appmap(recording, metadata)
    return orjson.dumps(a, default=AppMapEncoder.default,
                        option=(orjson.OPT_PASSTHROUGH_SUBCLASS |
                                orjson.OPT_PASSTHROUGH_DATACLASS))
