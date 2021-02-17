from appmap._implementation.event import SqlEvent, ReturnEvent
from appmap._implementation.recording import Recorder

from django.db.backends.signals import connection_created
from django.dispatch import receiver

import time


class ExecuteWrapper:
    def __init__(self):
        self.recorder = Recorder()

    def __call__(self, execute, sql, params, many, context):
        start = time.monotonic()
        try:
            return execute(sql, params, many, context)
        finally:
            if self.recorder.enabled:
                stop = time.monotonic()
                duration = stop - start
                # Note this logic is based on django.db.backends.utils.CursorDebugWrapper.
                if many:
                    # Sometimes the same query is executed with different parameter sets.
                    # Instead of substituting them all, just say how many times it was run.
                    try:
                        times = len(params)
                    except TypeError:
                        times = '?'
                    sql = f'{times} times {sql}'
                else:
                    db = context['connection']
                    cursor = context['cursor']
                    sql = db.ops.last_executed_query(cursor, sql, params)
                call_event = SqlEvent(sql)
                self.recorder.add_event(call_event)
                return_event = ReturnEvent(parent_id=call_event.id, elapsed=duration)
                self.recorder.add_event(return_event)


@receiver(connection_created)
def connected(sender, connection, **_):
    # pylint: disable=unused-argument
    wrappers = connection.execute_wrappers
    if not any(isinstance(x, ExecuteWrapper) for x in wrappers):
        wrappers.append(ExecuteWrapper())
