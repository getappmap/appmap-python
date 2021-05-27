"""SQL statement capture for SQLAlchemy."""

import time

import sqlalchemy
from sqlalchemy import event
from sqlalchemy.engine import Engine

from appmap._implementation.event import SqlEvent, ReturnEvent
from appmap._implementation.instrument import is_instrumentation_disabled
from ._implementation.metadata import Metadata
from appmap._implementation.recording import Recorder


@event.listens_for(Engine, 'before_cursor_execute')
# pylint: disable=too-many-arguments,unused-argument
def capture_sql_call(conn, cursor, statement, parameters, context, executemany):
    """Capture SQL query callinto appmap."""
    recorder = Recorder()
    if is_instrumentation_disabled():
        # We must be in the middle of fetching object representation.
        # Don't record this query in the appmap.
        pass
    elif recorder.enabled:
        Metadata.add_framework('SQLAlchemy', sqlalchemy.__version__)
        if executemany:
            # Sometimes the same query is executed with different parameter sets.
            # Instead of substituting them all, just say how many times it was run.
            try:
                times = len(parameters)
            except TypeError:
                times = '?'
            sql = '-- %s times\n%s' % (times, statement)
        else:
            sql = statement
        dialect = conn.dialect
        call_event = SqlEvent(sql, vendor=dialect.name, version=dialect.server_version_info)
        recorder.add_event(call_event)
        setattr(
            context, 'appmap',
            { 'start_time': time.monotonic(), 'call_event_id': call_event.id }
        )


@event.listens_for(Engine, 'after_cursor_execute')
# pylint: disable=too-many-arguments,unused-argument
def capture_sql(conn, cursor, statement, parameters, context, executemany):
    """Capture SQL query return into appmap."""
    recorder = Recorder()
    if is_instrumentation_disabled():
        # We must be in the middle of fetching object representation.
        # Don't record this query in the appmap.
        pass
    elif recorder.enabled:
        stop = time.monotonic()
        duration = stop - context.appmap['start_time']
        return_event = ReturnEvent(parent_id=context.appmap['call_event_id'], elapsed=duration)
        del context.appmap
        recorder.add_event(return_event)
