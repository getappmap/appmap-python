from abc import ABC, abstractmethod
from collections import namedtuple
from collections.abc import MutableSequence

import inspect
import logging
import sys
import traceback
import types

import appmap.wrapt as wrapt

from .env import Env
from .event import _EventIds
from .metadata import Metadata
from .utils import FnType

logger = logging.getLogger(__name__)


class Recording:
    """
    Context manager to make it easy to capture a Recording.  exit_hook
    will be called when the block exits, before any exceptions are
    raised.
    """
    def __init__(self, exit_hook=None):
        self.events = []
        self.exit_hook = exit_hook

    def start(self):

        if not Env.current.enabled:
            return

        r = Recorder()
        r.clear()
        r.start_recording()

    def stop(self):
        if not Env.current.enabled:
            return False

        self.events += Recorder().stop_recording()

    def is_running(self):
        if not Env.current.enabled:
            return False

        return Recorder().enabled

    def __enter__(self):
        self.start()

    def __exit__(self, exc_type, exc_value, tb):
        logger.debug("Recording.__exit__, stopping with exception %s", exc_type)
        self.stop()
        if self.exit_hook is not None:
            self.exit_hook(self)
        return False


Filterable = namedtuple('Filterable', 'fqname obj')


class FilterableMod(Filterable):
    __slots__ = ()

    def __new__(c, mod):
        fqname = mod.__name__
        return super(FilterableMod, c).__new__(c, fqname, mod)

    def classify_fn(self, _):
        return FnType.MODULE


class FilterableCls(Filterable):
    __slots__ = ()

    def __new__(c, cls):
        fqname = '%s.%s' % (cls.__module__, cls.__qualname__)
        return super(FilterableCls, c).__new__(c, fqname, cls)

    def classify_fn(self, static_fn):
        return FnType.classify(static_fn)


class FilterableFn(
        namedtuple('FilterableFn', Filterable._fields + ('scope', 'static_fn',))):
    __slots__ = ()

    def __new__(c, scope, fn, static_fn):
        fqname = '%s.%s' % (scope.fqname, fn.__qualname__)
        self = super(FilterableFn, c).__new__(c, fqname, fn, scope, static_fn)
        return self

    @property
    def fntype(self):
        return self.scope.classify_fn(self.static_fn)


class Filter(ABC):
    def __init__(self, next_filter):
        self.next_filter = next_filter

    @abstractmethod
    def filter(self, filterable):
        """
        Determine whether the given class should have its methods
        instrumented.  Return True if it should be, False if it should
        not be, or call the next filter if this filter can't decide.
        """

    @abstractmethod
    def wrap(self, filterable):
        """
        Determine whether the given filterable function should be
        instrumented.  If so, return a new function that wraps the
        old.  If not, return the original function.
        """


class NullFilter(Filter):
    def __init__(self, next_filter=None):
        super().__init__(next_filter)

    def filter(self, filterable):
        return False

    def wrap(self, filterable):
        return filterable.obj


def is_class(c):
    # We don't want to use inspect.isclass here. It uses isinstance to
    # check the class of the object, which will invoke any method
    # bound to __class__. (For example, celery.local.Proxy uses this
    # mechanism to return the class of the proxied object.)
    #
    return inspect._is_type(c)  # pylint: disable=protected-access


def get_classes(module):
    return [v for __, v in module.__dict__.items() if is_class(v)]


def get_members(cls):
    """
    Get the function members of the given class.  Unlike
    inspect.getmembers, this function only calls getattr on functions,
    to avoid potential side effects.

    Returns a list of tuples of the form (key, dict_value, attr_value):
      * key is the attribute name
      * dict_value is cls.__dict__[key]
      * and attr_value is getattr(cls, key)
    """
    def is_member_func(m):
        t = type(m)
        if (t == types.BuiltinFunctionType or  # noqa: E721
            t == types.BuiltinMethodType):  # noqa: E129
            return False

        return (t == types.FunctionType  # noqa: E721
                or t == types.MethodType
                or FnType.classify(m) in FnType.STATIC | FnType.CLASS)

    # Note that we only want to instrument the functions that are
    # defined within the class itself, i.e. those which get added to
    # the class' __dict__ when the class is created. If we were to
    # instead iterate over dir(cls), we would see functions from
    # superclasses, too. Those don't need to be instrumented here,
    # they'll get taken care of when the superclass is imported.
    ret = []
    modname = cls.__module__ if hasattr(cls, '__module__') else cls.__name__
    for key in cls.__dict__:
        if key.startswith('__'):
            continue
        static_value = inspect.getattr_static(cls, key)
        if not is_member_func(static_value):
            continue
        value = getattr(cls, key)
        if value.__module__ != modname:
            continue
        ret.append((key, static_value, value))
    return ret


class Recorder:
    """ Singleton Recorder class """
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            logger.debug('Creating the Recorder object')
            cls._instance = super(Recorder, cls).__new__(cls)

            # Put any __init__ here.
            cls._instance._initialized = False

        return cls._instance

    def __init__(self):
        if self.__getattribute__('_initialized'):  # keep pylint happy
            return
        self._initialized = True
        self.enabled = False
        self.start_tb = None
        self.filter_stack = [NullFilter]
        self.filter_chain = []
        self._events = []

    @classmethod
    def initialize(cls):
        cls._instance = None

    def use_filter(self, filter_class):
        self.filter_stack.append(filter_class)

    def clear(self):
        self._events = []
        _EventIds.reset()
        Metadata.reset()

    def start_recording(self):
        logger.debug('AppMap recording started')
        if self.enabled:
            logger.error('Recording already in progress, previous start:')
            logger.error(''.join(traceback.format_list(self.start_tb)))
            raise RuntimeError('Recording already in progress')
        self.start_tb = traceback.extract_stack()
        self.enabled = True

    def stop_recording(self):
        logger.debug('AppMap recording stopped')
        self.enabled = False
        self.start_tb = None
        return self._events

    def add_event(self, event):
        """
        Add an event to the current recording
        """
        self._events.append(event)

    @property
    def events(self):
        """
        Get the events from the current recording
        """
        return self._events

    def do_import(self, *args, **kwargs):
        mod = args[0]
        if mod.__name__.startswith('appmap'):
            return

        logger.debug('do_import, mod %s args %s kwargs %s', mod, args, kwargs)
        if not self.filter_chain:
            logger.debug('  filter_stack %s', self.filter_stack)
            self.filter_chain = self.filter_stack[0](None)
            for filter_ in self.filter_stack[1:]:
                self.filter_chain = filter_(self.filter_chain)
                logger.debug('  self.filter chain: %s', self.filter_chain)

        def instrument_functions(filterable):
            if not self.filter_chain.filter(filterable):
                return

            logger.info('  looking for members of %s', filterable.obj)
            functions = get_members(filterable.obj)
            logger.debug('  functions %s', functions)

            for fn_name, static_fn, fn in functions:
                new_fn = self.filter_chain.wrap(
                    FilterableFn(filterable, fn, static_fn))
                if fn != new_fn:
                    wrapt.wrap_function_wrapper(filterable.obj, fn_name, new_fn)

        instrument_functions(FilterableMod(mod))
        classes = get_classes(mod)
        logger.debug('  classes %s', classes)
        for c in classes:
            instrument_functions(FilterableCls(c))


def wrap_finder_function(fn, decorator):
    ret = fn
    marker = '_appmap_wrapped_%s' % fn.__name__

    # Figure out which object should get the marker attribute. If fn
    # is a bound function, put it on the object it's bound to,
    # otherwise put it on the function itself.
    obj = fn.__self__ if hasattr(fn, '__self__') else fn

    if getattr(obj, marker, None) is None:
        logger.debug('wrapping %r', fn)
        ret = decorator(fn)
        setattr(obj, marker, True)
    else:
        logger.debug('already wrapped, %r', fn)

    return ret


@wrapt.decorator
def wrapped_exec_module(exec_module, _, args, kwargs):
    logger.debug('exec_module %r args %s kwargs %s',
                 exec_module, args, kwargs)
    exec_module(*args, **kwargs)
    # Only process imports if we're currently enabled. This
    # handles the case where we previously hooked the finders, but
    # were subsequently disabled (e.g. during testing).
    if Env.current.enabled:
        Recorder().do_import(*args, **kwargs)


def wrap_exec_module(exec_module):
    return wrap_finder_function(exec_module, wrapped_exec_module)


@wrapt.decorator
def wrapped_find_spec(find_spec, _, args, kwargs):
    spec = find_spec(*args, **kwargs)
    if spec is not None:
        if getattr(spec.loader, "exec_module", None) is not None:
            loader = spec.loader
            loader.exec_module = wrap_exec_module(loader.exec_module)
        else:
            logger.debug("no exec_module for loader %r", spec.loader)
    return spec


def wrap_finder_find_spec(finder):
    find_spec = getattr(finder, 'find_spec', None)
    if find_spec is None:
        logger.debug('no find_spec for finder %r', finder)
        return

    finder.find_spec = wrap_finder_function(find_spec, wrapped_find_spec)


class MetapathObserver(MutableSequence):
    def __init__(self, meta_path):
        self._meta_path = meta_path

    def __getitem__(self, key):
        return self._meta_path.__getitem__(key)

    def __setitem__(self, key, value):
        self._meta_path.__setitem__(key, value)

    def __delitem__(self, key):
        self._meta_path.__delitem__(key)

    def __len__(self):
        return self._meta_path.__len__()

    def insert(self, index, value):
        wrap_finder_find_spec(value)
        self._meta_path.insert(index, value)

    def copy(self):
        return self._meta_path.copy()

def initialize():
    Recorder.initialize()
    # If we're not enabled, there's no reason to hook the finders.
    if Env.current.enabled:
        logger.debug('sys.metapath: %s', sys.meta_path)
        for finder in sys.meta_path:
            wrap_finder_find_spec(finder)

        # Make sure we instrument any finders that get added in the
        # future.
        sys.meta_path = MetapathObserver(sys.meta_path.copy())


def instrument_module(module):
    """
    Force (re-)instrumentation of a module.
    This can be useful if a module was already loaded before appmap hooks
    were set up or configured to instrument that module.
    """
    Recorder().do_import(module)
