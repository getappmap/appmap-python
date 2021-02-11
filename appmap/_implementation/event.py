import inspect
import logging
import threading
from itertools import chain
from functools import partial

from .utils import appmap_tls, split_function_name, fqname, FnType

logger = logging.getLogger(__name__)


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
    _next_thread_id = 0
    _next_thread_id_lock = threading.Lock()

    @classmethod
    def next_thread_id(cls):
        with cls._next_thread_id_lock:
            cls._next_thread_id += 1
            return cls._next_thread_id

    @classmethod
    def get_thread_id(cls):
        tls = appmap_tls()
        return (tls.get('thread_id')
                or tls.setdefault('thread_id', cls.next_thread_id()))

    @classmethod
    def reset(cls):
        cls.id = 1
        cls._next_thread_id = 0


class Event:
    __slots__ = ['id', 'event', 'thread_id']

    def __init__(self, event):
        self.id = _EventIds.next_id()
        self.event = event
        self.thread_id = _EventIds.get_thread_id()

    def to_dict(self):
        ret = {}
        for k in chain.from_iterable(getattr(cls, '__slots__', [])
                                     for cls in type(self).__mro__):
            a = getattr(self, k, None)
            if a is not None:
                ret[k] = a
        return ret

    def __repr__(self):
        return repr(self.to_dict())


class CallEvent(Event):
    __slots__ = ['defined_class', 'method_id', 'path', 'lineno',
                 'static', 'receiver', 'parameters']

    @staticmethod
    def make(fn, fntype):
        """
        Return a factory for creating new CallEvents based on
        introspecting the given function.
        """
        defined_class, method_id = split_function_name(fn)

        try:
            path = inspect.getsourcefile(fn)
        except TypeError:
            path = '<builtin>'

        try:
            __, lineno = inspect.getsourcelines(fn)
        except OSError:
            lineno = 0

        return partial(CallEvent, defined_class,
                       method_id, path, lineno, fntype)

    @staticmethod
    def make_param(name, kind, class_name, val):
        # Make a best-effort attempt to get a string value for the
        # parameter. If str() and repr() raise, formulate a value from
        # the class and id.
        object_id = id(val)
        try:
            value = str(val)
        except Exception:  # pylint: disable=broad-except
            try:
                value = repr(val)
            except Exception:  # pylint: disable=broad-except
                value = f'<{class_name} object at {object_id:#02x}>'
        return {
            "name": name,
            "class": class_name,
            "value": value,
            "object_id": object_id,
            "kind": kind
        }

    @staticmethod
    def make_param_defs(fn):
        sig = inspect.signature(fn)
        ret = []
        for p in sig.parameters.values():
            no_default = p.default is p.empty
            if (p.kind == p.POSITIONAL_ONLY
                or p.kind == p.POSITIONAL_OR_KEYWORD):  # noqa: E129
                kind = 'req' if no_default else 'opt'
            elif p.kind == p.VAR_POSITIONAL:
                kind = 'rest'
            elif p.kind == p.KEYWORD_ONLY:
                kind = 'keyreq' if no_default else 'key'
            elif p.kind == p.VAR_KEYWORD:
                kind = 'keyrest'
            ret.append(partial(CallEvent.make_param, p.name, kind))
        return ret

    @staticmethod
    def make_params(defs):
        def make(defs, args, kwargs):
            logger.debug('kwargs %s', kwargs)
            ret = []
            for i, p in enumerate(defs):
                class_name = fqname(type(args[i]))
                value = args[i]
                ret.append(p(class_name, value))
            return ret
        return partial(make, defs)

    def __init__(self, defined_class, method_id, path, lineno,
                 fntype, parameters):
        super().__init__('call')
        self.defined_class = defined_class
        self.method_id = method_id
        self.path = path
        self.lineno = lineno
        self.static = fntype in FnType.STATIC | FnType.CLASS
        if fntype in FnType.CLASS | FnType.INSTANCE:
            self.receiver = parameters[0]
            parameters = parameters[1:]
        self.parameters = parameters


class ReturnEvent(Event):
    __slots__ = ['parent_id', 'elapsed']

    def __init__(self, parent_id, elapsed):
        super().__init__('return')
        self.parent_id = parent_id
        self.elapsed = elapsed


class ExceptionEvent(ReturnEvent):
    __slots__ = ['exceptions']

    def __init__(self, parent_id, elapsed, exc_info):
        super().__init__(parent_id, elapsed)
        class_, exc, __ = exc_info
        self.exceptions = [{
            'exceptions': {
                'class': fqname(class_),
                'message': str(exc),
                'object_id': id(exc),
            }
        }]


def initialize():
    appmap_tls().pop('thread_id', None)
    _EventIds.reset()
