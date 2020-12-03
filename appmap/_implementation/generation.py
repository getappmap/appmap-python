"""Generate an AppMap"""
import orjson

from . import metadata

from .event import serialize_event


def appmap(recording):
    return {
        'metadata': metadata.Metadata.dump(),
        'events': recording.events
    }


def dump(recording):
    return orjson.dumps(appmap(recording), default=serialize_event)
