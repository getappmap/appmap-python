from itertools import chain
import threading


class _EventIds:
    id = 1
    lock = threading.Lock()

    @classmethod
    def next_id(cls):
        with cls.lock:
            cls.id += 1
            return cls.id

    # The identifiers returned by threading.get_ident() aren't
    # guaranteed to be unique: they may be recycled after the thread
    # exits. We need a unique id, so we'll manage it ourselves.
    next_thread_id = 0
    next_thread_id_lock = threading.Lock()
    tls = threading.local()

    @classmethod
    def get_thread_id(cls):
        thread_id = getattr(cls.tls, 'thread_id', None)
        if thread_id is None:
            with cls.next_thread_id_lock:
                cls.next_thread_id += 1
                thread_id = cls.tls.thread_id = cls.next_thread_id
        return thread_id


class Event:
    __slots__ = ['id', 'event', 'thread_id']

    def __init__(self, event):
        self.id = _EventIds.next_id()
        self.event = event
        self.thread_id = _EventIds.get_thread_id()

    def to_dict(self):
        return {
            k: getattr(self, k, None)
            for k in chain.from_iterable(getattr(cls, '__slots__', []) for cls in type(self).__mro__)
        }


class CallEvent(Event):
    __slots__ = ['defined_class', 'method_id', 'path', 'lineno',
                 'static']  # ,'receiver', 'parameters'

    def __init__(self, defined_class, method_id, path, lineno, static):
        super().__init__('call')
        self.defined_class = defined_class
        self.method_id = method_id
        self.path = path
        self.lineno = lineno
        self.static = static


class ReturnEvent(Event):
    __slots__ = ['parent_id']

    def __init__(self, parent_id):
        super().__init__('return')
        self.parent_id = parent_id


class ExceptionEvent(ReturnEvent):
    __slots__ = ['exceptions']

    def __init__(self, parent_id, exc_info):
        super().__init__(parent_id)
        class_, exc, __ = exc_info
        self.exceptions = [{
            'exceptions': {
                'class': class_,
                'message': str(exc),
                'object_id': exc.id(),
            }
        }]


def serialize_event(event):
    if isinstance(event, Event):
        return event.to_dict()
    raise TypeError
