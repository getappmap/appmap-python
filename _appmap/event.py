# pylint: disable=missing-module-docstring,missing-class-docstring,missing-function-docstring
import inspect
import logging
import threading
from functools import lru_cache, partial
from inspect import Parameter, Signature
from itertools import chain

from .env import Env
from .recorder import Recorder
from .utils import (
    FnType,
    FqFnName,
    appmap_tls,
    compact_dict,
    fqname,
    get_function_location,
)

logger = Env.current.getLogger(__name__)


class _EventIds:
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
        return tls.get("thread_id") or tls.setdefault("thread_id", cls.next_thread_id())

    @classmethod
    def reset(cls):
        cls.id = 1
        cls._next_thread_id = 0


def display_string(val):
    # If we're asked to display parameters, make a best-effort attempt
    # to get a string value for the parameter using repr(). If parameter
    # display is disabled, or repr() has raised, just formulate a value
    # from the class and id.
    value = None
    if Env.current.display_params:
        try:
            value = repr(val)
        except Exception:  # pylint: disable=broad-except
            pass

    if value is None:
        class_name = fqname(type(val))
        object_id = id(val)
        value = "<%s object at %#02x>" % (class_name, object_id)

    return value


def _is_list_or_dict(val_type):
    # We cannot use isinstance here because it uses __class__
    # and val could be overloading it and calling it could cause side effects.
    #
    # For example lazy objects such as django.utils.functional.LazyObject
    # pretend to be the wrapped object, but they don't know its class
    # a priori, so __class__ attribute lookup has to force evaluation.
    # If the object hasn't been evaluated before it could change the
    # observed behavior by doing that prematurely (perhaps even before
    # the evaluation can even succeed).

    return issubclass(val_type, list), issubclass(val_type, dict)


def _describe_schema(name, val, depth, max_depth):

    val_type = type(val)

    ret = {}
    if name is not None:
        ret["name"] = name
    ret["class"] = fqname(val_type)

    islist, isdict = _is_list_or_dict(val_type)
    if not (islist or isdict) or (depth >= max_depth and isdict):
        return ret

    if islist:
        elts = [(None, v) for v in val]
        schema_key = "items"
    elif isdict:
        elts = val.items()
        schema_key = "properties"

    schema = [_describe_schema(k, v, depth + 1, max_depth) for k, v in elts]
    # schema will be [None] if depth is exceeded, don't use it
    if any(schema):
        ret[schema_key] = schema

    return ret


def describe_value(name, val, max_depth=5):
    ret = {
        "object_id": id(val),
        "value": display_string(val),
    }
    ret.update(_describe_schema(name, val, 0, max_depth))
    if any(_is_list_or_dict(type(val))):
        ret["size"] = len(val)

    return ret


class Event:
    __slots__ = ["id", "event", "thread_id"]

    def __init__(self, event):
        self.id = Recorder.next_event_id()
        self.event = event
        self.thread_id = _EventIds.get_thread_id()

    def to_dict(self, attrs=None):
        ret = {}
        if attrs is None:
            attrs = chain.from_iterable(
                getattr(cls, "__slots__", []) for cls in type(self).__mro__
            )
        for k in attrs:
            if k[0] == "_":  # skip internal attrs
                continue

            a = getattr(self, k, None)
            if a is not None:
                ret[k] = a
        return ret

    def __repr__(self):
        return repr(self.to_dict())


class Param:
    __slots__ = ["name", "kind", "default", "default_class"]

    def __init__(self, sigp):
        self.name = sigp.name
        has_default = sigp.default is not Signature.empty
        if sigp.kind in (Parameter.POSITIONAL_ONLY, Parameter.POSITIONAL_OR_KEYWORD):
            self.kind = "opt" if has_default else "req"
        elif sigp.kind == Parameter.VAR_POSITIONAL:
            self.kind = "rest"
        elif sigp.kind == Parameter.KEYWORD_ONLY:
            self.kind = "key" if has_default else "keyreq"
        elif sigp.kind == Parameter.VAR_KEYWORD:
            self.kind = "keyrest"
        if has_default:
            self.default = sigp.default
            self.default_class = fqname(type(self.default))

    def __repr__(self):
        return "<Param name: %s kind: %s>" % (self.name, self.kind)

    def to_dict(self, value):
        ret = {"kind": self.kind}
        ret.update(describe_value(self.name, value))
        return ret


class CallEvent(Event):
    __slots__ = ["_fn", "_fqfn", "static", "receiver", "parameters", "labels"]

    @staticmethod
    def make(fn, fntype):
        """
        Return a factory for creating new CallEvents based on
        introspecting the given function.
        """

        # Delete the labels so the app doesn't see them.
        labels = getattr(fn, "_appmap_labels", None)
        if labels:
            del fn._appmap_labels

        return partial(CallEvent, fn, fntype, labels=labels)

    @staticmethod
    def make_params(filterable):
        try:
            fn = filterable.obj
            if filterable.fntype != FnType.CLASS:
                sig = inspect.signature(fn, follow_wrapped=True)
            else:
                sig = inspect.signature(
                    filterable.static_fn.__func__, follow_wrapped=True
                )
        except ValueError:
            # Can't get signatures built-ins
            return []

        if logger.isEnabledFor(logging.DEBUG):
            # inspect.signature is relatively expensive, and signature
            # mismatches are frequent. Only compare them if we're
            # going to log a message about a mismatch.
            wrapped_sig = inspect.signature(fn, follow_wrapped=True)
            if sig != wrapped_sig:
                logger.debug("signature of wrapper %r doesn't match wrapped", fn)
                logger.debug("sig: %r", sig)
                logger.debug("wrapped_sig: %r", wrapped_sig)

        return [Param(p) for p in sig.parameters.values()]

    @staticmethod
    def set_params(params, instance, args, kwargs):
        # Note that set_params expects args and kwargs as a tuple and
        # dict, respectively. It operates on them as collections, so
        # it doesn't unpack them.
        ret = []

        # HACK: this is to detect cases when this is a method, yet the self
        # parameter is None. Unfortunately wrapt tries to be too smart
        # by separating the instance argument, and as a consequence
        # we can't differentiate here between a function and a method
        # bound to None. Thus we rely on 'self' being the conventional
        # name for the self argument. This is usually correct but
        # theoretically could be wrong with code that's off-style.
        takes_self = params and params[0].name == "self"

        if instance is not None or takes_self:
            args = [instance, *args]
        else:
            # we're popping the front repeatedly, lists are better at this
            args = list(args)

        for p in params:
            if p.kind == "req":
                # A 'req' argument can be either keyword or
                # positional.
                if p.name in kwargs:
                    value = kwargs[p.name]
                else:
                    if args:
                        value = args.pop(0)
                    else:
                        continue  # required argument missing
            elif p.kind == "keyreq":
                if p.name in kwargs:
                    value = kwargs[p.name]
                else:
                    continue  # required argument missing
            elif p.kind in ("opt", "key"):
                value = kwargs.get(p.name, p.default)
            elif p.kind == "rest":
                value = tuple(args)
            elif p.kind == "keyrest":
                value = kwargs
            else:
                # If all the parameter types are handled, this
                # shouldn't ever happen...
                raise RuntimeError("Unknown parameter with desc %s" % (repr(p)))
            ret.append(p.to_dict(value))
        return ret

    @property
    @lru_cache(maxsize=None)
    def function_name(self):
        return self._fqfn.fqfn

    @property
    @lru_cache(maxsize=None)
    def defined_class(self):
        return self._fqfn.fqclass

    @property
    @lru_cache(maxsize=None)
    def method_id(self):
        return self._fqfn.fqfn[1]

    @property
    @lru_cache(maxsize=None)
    def function_location(self):
        return get_function_location(self._fn)

    @property
    @lru_cache(maxsize=None)
    def path(self):
        return self.function_location[0]

    @property
    @lru_cache(maxsize=None)
    def lineno(self):
        return self.function_location[1]

    @property
    @lru_cache(maxsize=None)
    def comment(self):
        comment = inspect.getdoc(self._fn)
        if comment is None:
            comment = inspect.getcomments(self._fn)
        return comment

    def __init__(self, fn, fntype, parameters, labels):
        super().__init__("call")
        self._fn = fn
        self._fqfn = FqFnName(fn)
        self.static = fntype in FnType.STATIC | FnType.CLASS | FnType.MODULE
        self.receiver = None
        if fntype in FnType.CLASS | FnType.INSTANCE:
            self.receiver = parameters[0]
            parameters = parameters[1:]
        self.parameters = parameters
        self.labels = labels

    def to_dict(self, attrs=None):
        ret = super().to_dict()  # get the attrs defined in __slots__
        if "labels" in ret:
            del ret["labels"]  # labels should only appear in the classmap

        # update with the computed properties
        ret.update(
            super().to_dict(attrs=["defined_class", "method_id", "path", "lineno"])
        )

        return ret


class SqlEvent(Event):  # pylint: disable=too-few-public-methods
    __slots__ = ["sql_query"]

    def __init__(self, sql, vendor=None, version=None):
        super().__init__("call")
        self.sql_query = compact_dict(
            {
                "sql": sql,
                "database_type": vendor,
                "server_version": ".".join([str(v) for v in version])
                if version
                else None,
            }
        )


class MessageEvent(Event):  # pylint: disable=too-few-public-methods
    __slots__ = ["message"]

    def __init__(self, message_parameters):
        super().__init__("call")
        self.message = []
        self.message_parameters = message_parameters

    @property
    def message_parameters(self):
        return self.message

    @message_parameters.setter
    def message_parameters(self, params):
        for name, value in params.items():
            message_object = describe_value(name, value)
            self.message.append(message_object)


def none_if_empty(collection):
    """Return collection or None if it's empty."""
    return collection if len(collection) > 0 else None


# pylint: disable=too-few-public-methods
class HttpClientRequestEvent(MessageEvent):
    """A call AppMap event representing an HTTP client request."""

    __slots__ = ["http_client_request"]

    def __init__(self, request_method, url, message_parameters, headers=None):
        super().__init__(message_parameters)

        request = {
            "request_method": request_method,
            "url": url,
        }

        if headers is not None:
            request.update(
                {
                    "headers": none_if_empty(dict(headers)),
                }
            )

        self.http_client_request = compact_dict(request)


# pylint: disable=too-few-public-methods
_NORMALIZED_PATH_INFO_ATTR = "normalized_path_info"
class HttpServerRequestEvent(MessageEvent):
    """A call AppMap event representing an HTTP server request."""

    __slots__ = ["http_server_request"]

    def __init__(
        self,
        request_method,
        path_info,
        message_parameters,
        normalized_path_info=None,
        protocol=None,
        headers=None,
    ):
        super().__init__(message_parameters)

        request = {
            "request_method": request_method,
            "protocol": protocol,
            "path_info": path_info,
            _NORMALIZED_PATH_INFO_ATTR: normalized_path_info,
        }

        if headers is not None:
            request.update(
                {
                    "mime_type": headers.get("Content-Type"),
                    "authorization": headers.get("Authorization"),
                    "headers": none_if_empty(dict(headers)),
                }
            )

        self.http_server_request = compact_dict(request)

    @property
    def normalized_path_info(self):
        return self.http_server_request.get(_NORMALIZED_PATH_INFO_ATTR, None)

    @normalized_path_info.setter
    def normalized_path_info(self, npi):
        self.http_server_request[_NORMALIZED_PATH_INFO_ATTR] = npi


class ReturnEvent(Event):
    __slots__ = ["parent_id", "elapsed"]

    def __init__(self, parent_id, elapsed):
        super().__init__("return")
        self.parent_id = parent_id
        self.elapsed = elapsed


class FuncReturnEvent(ReturnEvent):
    __slots__ = ["return_value"]

    def __init__(self, parent_id, elapsed, return_value):
        super().__init__(parent_id, elapsed)
        self.return_value = describe_value(None, return_value)


class HttpResponseEvent(ReturnEvent):
    """A generic HTTP response event."""

    def __init__(self, status_code, headers=None, **kwargs):
        super().__init__(**kwargs)

        response = {"status_code": status_code}

        if headers is not None:
            response.update(
                {
                    "mime_type": headers.get("Content-Type"),
                    "headers": none_if_empty(dict(headers)),
                }
            )

        self.response = compact_dict(response)


# pylint: disable=too-few-public-methods
class HttpServerResponseEvent(HttpResponseEvent):
    """An HTTP server response event."""

    __slots__ = ["http_server_response"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.http_server_response = self.response


# pylint: disable=too-few-public-methods
class HttpClientResponseEvent(HttpResponseEvent):
    """An HTTP client response event."""

    __slots__ = ["http_client_response"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.http_client_response = self.response


class ExceptionEvent(ReturnEvent):
    __slots__ = ["exceptions"]

    def __init__(self, parent_id, elapsed, exc_info):
        super().__init__(parent_id, elapsed)
        class_, exc, __ = exc_info
        self.exceptions = [
            {"class": fqname(class_), "message": str(exc), "object_id": id(exc)}
        ]


def initialize():
    appmap_tls().pop("thread_id", None)
    _EventIds.reset()
