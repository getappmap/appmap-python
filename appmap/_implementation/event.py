from functools import partial
import inspect
from inspect import Parameter, Signature
from itertools import chain
import logging
import threading

from .env import Env
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


def display_string(val):
    # Make a best-effort attempt to get a string value for the
    # parameter. If str() and repr() raise, formulate a value from
    # the class and id.
    try:
        value = str(val)
    except Exception:  # pylint: disable=broad-except
        try:
            value = repr(val)
        except Exception:  # pylint: disable=broad-except
            class_name = fqname(type(val))
            object_id = id(val)
            value = '<%s object at %#02x>' % (class_name, object_id)

    return value


def describe_value(val):
    return {
        "class": fqname(type(val)),
        "object_id": id(val),
        "value": display_string(val)
    }

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


class Param:
    __slots__ = ['name', 'kind', 'default', 'default_class']

    def __init__(self, sigp):
        self.name = sigp.name
        has_default = sigp.default is not Signature.empty
        if (sigp.kind == Parameter.POSITIONAL_ONLY
            or sigp.kind == Parameter.POSITIONAL_OR_KEYWORD):  # noqa: E129
            self.kind = 'opt' if has_default else 'req'
        elif sigp.kind == Parameter.VAR_POSITIONAL:
            self.kind = 'rest'
        elif sigp.kind == Parameter.KEYWORD_ONLY:
            self.kind = 'key' if has_default else 'keyreq'
        elif sigp.kind == Parameter.VAR_KEYWORD:
            self.kind = 'keyrest'
        if has_default:
            self.default = sigp.default
            self.default_class = fqname(type(self.default))

    def __repr__(self):
        return '<Param name: %s kind: %s>' % (self.name, self.kind)

    def to_dict(self, value):
        ret = {
            "name": self.name,
            "kind": self.kind
        }
        ret.update(describe_value(value))
        return ret


class CallEvent(Event):
    __slots__ = ['defined_class', 'method_id', 'path', 'lineno',
                 'static', 'receiver', 'parameters', 'labels']

    @staticmethod
    def make(fn, fntype):
        """
        Return a factory for creating new CallEvents based on
        introspecting the given function.
        """
        defined_class, method_id = split_function_name(fn)
        try:
            path = inspect.getsourcefile(fn)
            if path.startswith(Env.current.root_dir):
                path = path[Env.current.root_dir_len:]
        except TypeError:
            path = '<builtin>'

        try:
            __, lineno = inspect.getsourcelines(fn)
        except OSError:
            lineno = 0

        # Delete the labels so the app doesn't see them.
        labels = getattr(fn, '_appmap_labels', None)
        if labels:
            del fn._appmap_labels

        return partial(CallEvent, defined_class,
                       method_id, path, lineno, fntype, labels=labels)

    @staticmethod
    def make_params(fn):
        sig = inspect.signature(fn)
        return [Param(p) for p in sig.parameters.values()]

    @staticmethod
    def set_params(params, args, kwargs):
        # Note that set_params expects args and kwargs as a tuple and
        # dict, respectively. It operates on them as collections, so
        # it doesn't unpack them.
        ret = []
        for p in params:
            if p.kind == 'req':
                # A 'req' argument can be either keyword or
                # positional.
                if p.name in kwargs:
                    value = kwargs[p.name]
                else:
                    value = args[0]
                    args = args[1:]
            elif p.kind == 'keyreq':
                value = kwargs[p.name]
            elif p.kind == 'opt' or p.kind == 'key':
                value = kwargs.get(p.name, p.default)
            elif p.kind == 'rest':
                value = args
            elif p.kind == 'keyrest':
                value = kwargs
            else:
                # If all the parameter types are handled, this
                # shouldn't ever happen...
                raise RuntimeError('Unknown parameter with desc %s' % (repr(p)))
            ret.append(p.to_dict(value))
        return ret

    def __init__(self, defined_class, method_id, path, lineno,
                 fntype, parameters, labels):
        super().__init__('call')
        self.defined_class = defined_class
        self.method_id = method_id
        self.path = path
        self.lineno = lineno
        self.static = fntype in FnType.STATIC | FnType.CLASS
        self.receiver = None
        if fntype in FnType.CLASS | FnType.INSTANCE:
            self.receiver = parameters[0]
            parameters = parameters[1:]
        self.parameters = parameters
        self.labels = labels

class SqlEvent(Event):
    __slots__ = ['sql_query']

    def __init__(self, sql):
        super().__init__('call')
        self.sql_query = {
            'sql': sql
        }


class HttpRequestEvent(Event):
    __slots__ = ['http_server_request']

    def __init__(self, request_method, path_info,
                 normalized_path_info=None, protocol=None):
        super().__init__('call')
        http_server_request = {
            'request_method': request_method,
            'path_info': path_info
        }
        if normalized_path_info:
            http_server_request['normalized_path_info'] = normalized_path_info
        if protocol:
            http_server_request['protocol'] = protocol

        self.http_server_request = http_server_request

class ReturnEvent(Event):
    __slots__ = ['parent_id', 'elapsed']

    def __init__(self, parent_id, elapsed):
        super().__init__('return')
        self.parent_id = parent_id
        self.elapsed = elapsed


class FuncReturnEvent(ReturnEvent):
    __slots__ = ['return_value']

    def __init__(self, parent_id, elapsed, return_value):
        super().__init__(parent_id, elapsed)
        self.return_value = describe_value(return_value)


class HttpResponseEvent(ReturnEvent):
    __slots__ = ['http_server_response']

    def __init__(self, status_code, mime_type, **kwargs):
        super().__init__(**kwargs)
        self.http_server_response = {
            'status_code': status_code,
            'mime_type': mime_type
        }


class ExceptionEvent(ReturnEvent):
    __slots__ = ['exceptions']

    def __init__(self, parent_id, elapsed, exc_info):
        super().__init__(parent_id, elapsed)
        class_, exc, __ = exc_info
        self.exceptions = [{
            'class': fqname(class_),
            'message': str(exc),
            'object_id': id(exc)
        }]


def initialize():
    appmap_tls().pop('thread_id', None)
    _EventIds.reset()
