import inspect
import logging
import sys

import appmap.wrapt as wrapt

from .env import Env
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

    def __exit__(self, exc_type, exc_value, traceback):
        logger.debug("Recording.__exit__, stopping with exception %s", exc_type)
        self.stop()
        if self.exit_hook is not None:
            self.exit_hook(self)
        return False


class Filter(ABC):
    def __init__(self, next_filter):
        self.next_filter = next_filter

    @abstractmethod
    def filter(self, class_):
        """
        Determine whether the given class should have its methods
        instrumented.  Return True if it should be, False if it should
        not be, or call the next filter if this filter can't decide.
        """

    @abstractmethod
    def wrap(self, fn, fntype):
        """
        Determine whether the given function with the given type
        should be instrumented.  If so, return a new function that
        wraps the old.  If not, return the original function.

        NB: fntype is the type of the function based on its
        declaration.  It's not necessarily the same as
        FnType.classify(fn), e.g. if fn is a staticmethod or a
        classmethod.
        """

class NullFilter(Filter):
    def __init__(self, next_filter=None):
        super().__init__(next_filter)

    def filter(self, class_):
        return False

    def wrap(self, fn, fntype):
        return fn


def is_class(c):
    # We don't want to use inspect.isclass here. It uses isinstance to
    # check the class of the object, which will invoke any method
    # bound to __class__. (For example, celery.local.Proxy uses this
    # mechanism to return the class of the proxied object.)
    #
    # We want the *real* class of c, not whatever it wants to claim as
    # its class. type() give us that.
    return type(c) == type


def get_classes(module):
    return [v for __, v in module.__dict__.items() if is_class(v)]


def get_members(class_):
    """
    Get the function members of the given class.  Unlike
    inspect.getmembers, this function only calls getattr on functions,
    to avoid potential side effects.

    Returns a list of tuples of the form (key, dict_value, attr_value):
      * key is the attribute name
      * dict_value is class_.__dict__[key]
      * and attr_value is getattr(class_, key)
    """
    def is_member_func(m):
        return (inspect.isfunction(m)
                or inspect.ismethod(m)
                or FnType.classify(m) in FnType.STATIC | FnType.CLASS)

    ret = []
    for key in dir(class_):
        if key.startswith('__'):
            continue
        value = inspect.getattr_static(class_, key)
        if not is_member_func(value):
            continue
        ret.append((key, value))
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

    def start_recording(self):
        logger.debug('AppMap recording started')
        self.enabled = True

    def stop_recording(self):
        logger.debug('AppMap recording stopped')
        self.enabled = False
        return self._events

    def add_event(self, event):
        """
        Add an event to the current recording
        """
        self._events.append(event)

    def events(self):
        """
        Get the events from the current recording
        """
        return self._events

    def do_import(self, *args, **kwargs):
        mod = args[0]
        logger.debug('do_import, mod %s args %s kwargs %s', mod, args, kwargs)
        if not self.filter_chain:
            logger.debug('  filter_stack %s', self.filter_stack)
            self.filter_chain = self.filter_stack[0](None)
            for filter_ in self.filter_stack[1:]:
                self.filter_chain = filter_(self.filter_chain)
                logger.debug('  self.filter chain: %s', self.filter_chain)

        if mod.__name__.startswith('appmap'):
            return

        classes = get_classes(mod)
        logger.debug('  classes %s', classes)
        for class_ in classes:
            if not self.filter_chain.filter(class_):
                continue

            logger.debug('  looking for members')
            functions = get_members(class_)
            logger.debug('  functions %s', functions)

            for fn_name, fn in functions:
                fntype = FnType.classify(fn)
                if fntype in FnType.STATIC | FnType.CLASS:
                    # Static methods created with staticmethod will
                    # have a `__func__` attribute. Other static
                    # methods (e.g. builtins assigned to an attribute
                    # of a class) won't. So, use `__func__` if it's
                    # available, otherwise just wrap fn.
                    fn = getattr(fn, '__func__', fn)
                new_fn = self.filter_chain.wrap(fn, fntype)

                if new_fn != fn:
                    if fntype & FnType.STATIC:
                        new_fn = staticmethod(new_fn)
                    elif fntype & FnType.CLASS:
                        new_fn = classmethod(new_fn)
                    setattr(class_, fn_name, new_fn)


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


def wrap_find_spec(find_spec):
    return wrap_finder_function(find_spec, wrapped_find_spec)


def initialize():
    Recorder.initialize()
    # If we're not enabled, there's no reason to hook the finders.
    if Env.current.enabled:
        logger.debug('sys.metapath: %s', sys.meta_path)
        for finder in sys.meta_path:
            find_spec = getattr(finder, 'find_spec', None)
            if find_spec is None:
                logger.debug('no find_spec for finder %r', finder)
                continue
            finder.find_spec = wrap_find_spec(finder.find_spec)


def instrument_module(module):
    """
    Force (re-)instrumentation of a module.
    This can be useful if a module was already loaded before appmap hooks
    were set up or configured to instrument that module.
    """
    Recorder().do_import(module)
