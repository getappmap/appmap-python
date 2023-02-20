import functools
import inspect
import sys
import types
from abc import ABC, abstractmethod
from collections import namedtuple
from collections.abc import MutableSequence
from functools import reduce

from appmap import wrapt

from .env import Env
from .utils import FnType

logger = Env.current.getLogger(__name__)


Filterable = namedtuple("Filterable", "fqname obj")


class FilterableMod(Filterable):
    __slots__ = ()

    def __new__(cls, mod):
        fqname = mod.__name__
        return super(FilterableMod, cls).__new__(cls, fqname, mod)

    def classify_fn(self, _):
        return FnType.MODULE


class FilterableCls(Filterable):
    __slots__ = ()

    def __new__(cls, clazz):
        fqname = "%s.%s" % (clazz.__module__, clazz.__qualname__)
        return super(FilterableCls, cls).__new__(cls, fqname, clazz)

    def classify_fn(self, static_fn):
        return FnType.classify(static_fn)


class FilterableFn(
    namedtuple(
        "FilterableFn",
        Filterable._fields
        + (
            "scope",
            "static_fn",
        ),
    )
):
    __slots__ = ()

    def __new__(cls, scope, fn, static_fn):
        fqname = "%s.%s" % (scope.fqname, fn.__name__)
        self = super(FilterableFn, cls).__new__(cls, fqname, fn, scope, static_fn)
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


class NullFilter(Filter):
    def __init__(self, next_filter=None):
        super().__init__(next_filter)

    def filter(self, filterable):
        return False


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
        if t in (types.BuiltinFunctionType, types.BuiltinMethodType):
            return False

        return (
            t == types.FunctionType  # noqa: E721
            or t == types.MethodType
            or FnType.classify(m) in FnType.STATIC | FnType.CLASS
        )

    # Note that we only want to instrument the functions that are
    # defined within the class itself, i.e. those which get added to
    # the class' __dict__ when the class is created. If we were to
    # instead iterate over dir(cls), we would see functions from
    # superclasses, too. Those don't need to be instrumented here,
    # they'll get taken care of when the superclass is imported.
    ret = []
    modname = cls.__module__ if hasattr(cls, "__module__") else cls.__name__
    for key in cls.__dict__:
        if key.startswith("__"):
            continue
        static_value = inspect.getattr_static(cls, key)
        if not is_member_func(static_value):
            continue
        value = getattr(cls, key)
        if value.__module__ != modname:
            continue
        ret.append((key, static_value, value))
    return ret


class Importer:
    filter_stack = [NullFilter]
    filter_chain = None

    def get_filter_stack(self):
        return self.filter_stack

    @classmethod
    def initialize(cls):
        cls.filter_stack = []
        cls.filter_chain = []
        cls._skip_instrumenting = ("appmap", "_appmap")

    @classmethod
    def use_filter(cls, filter_class):
        cls.filter_stack.append(filter_class)

    @classmethod
    def do_import(cls, *args, **kwargs):
        mod = args[0]
        if mod.__name__.startswith(cls._skip_instrumenting):
            return

        logger.debug("do_import, mod %s args %s kwargs %s", mod, args, kwargs)
        if not cls.filter_chain:
            cls.filter_chain = reduce(
                lambda acc, e: e(acc), cls.filter_stack, NullFilter(None)
            )

        def instrument_functions(filterable, selected_functions=None):
            logger.debug("  looking for members of %s", filterable.obj)
            functions = get_members(filterable.obj)
            logger.debug("  functions %s", functions)

            for fn_name, static_fn, fn in functions:
                if selected_functions and fn_name not in selected_functions:
                    continue

                new_fn = cls.filter_chain.wrap(FilterableFn(filterable, fn, static_fn))
                if fn != new_fn:
                    wrapt.wrap_function_wrapper(filterable.obj, fn_name, new_fn)

        # Import Config here, to avoid circular top-level imports.
        from .configuration import Config  # pylint: disable=import-outside-toplevel

        package_functions = Config().package_functions
        fm = FilterableMod(mod)
        if fm.fqname in package_functions:
            instrument_functions(fm, package_functions.get(fm.fqname))
        elif cls.filter_chain.filter(fm):
            instrument_functions(fm)

        classes = get_classes(mod)
        logger.debug("  classes %s", classes)
        for c in classes:
            fc = FilterableCls(c)
            if fc.fqname.startswith(cls._skip_instrumenting):
                logger.debug("  not instrumenting %s", fc.fqname)
                continue
            if fc.fqname in package_functions:
                instrument_functions(fc, package_functions.get(fc.fqname))
            elif cls.filter_chain.filter(fc):
                instrument_functions(fc)


def wrap_finder_function(fn, decorator):
    ret = fn
    fn_name = fn.func.__name__ if isinstance(fn, functools.partial) else fn.__name__
    marker = "_appmap_wrapped_%s" % fn_name

    # Figure out which object should get the marker attribute. If fn
    # is a bound function, put it on the object it's bound to,
    # otherwise put it on the function itself.
    obj = fn.__self__ if hasattr(fn, "__self__") else fn

    if getattr(obj, marker, None) is None:
        logger.debug("wrapping %r", fn)
        ret = decorator(fn)
        setattr(obj, marker, True)
    else:
        logger.debug("already wrapped, %r", fn)

    return ret


@wrapt.decorator
def wrapped_exec_module(exec_module, _, args, kwargs):
    logger.debug("exec_module %r args %s kwargs %s", exec_module, args, kwargs)
    exec_module(*args, **kwargs)
    # Only process imports if we're currently enabled. This
    # handles the case where we previously hooked the finders, but
    # were subsequently disabled (e.g. during testing).
    if Env.current.enabled:
        Importer.do_import(*args, **kwargs)


def wrap_exec_module(exec_module):
    return wrap_finder_function(exec_module, wrapped_exec_module)


@wrapt.decorator
def wrapped_find_spec(find_spec, _, args, kwargs):
    spec = find_spec(*args, **kwargs)
    if spec is not None:
        if getattr(spec.loader, "exec_module", None) is not None:
            loader = spec.loader
            # This is kind of gross. As the comment linked to below describes, wrapt has trouble
            # identifying methods decorated with @staticmethod. It offers two suggested fixes:
            # update the class definition, or patch the function found in __dict__. We can't do the
            # former, so do the latter instead.
            #   https://github.com/GrahamDumpleton/wrapt/blob/1.14.1/src/wrapt/wrappers.py#L730
            #
            # TODO: determine if we can use wrapt.wrap_function_wrapper to simplify this code
            exec_module = inspect.getattr_static(loader, "exec_module")
            if isinstance(exec_module, staticmethod):
                loader.exec_module = wrap_exec_module(exec_module)
            else:
                loader.exec_module = wrap_exec_module(loader.exec_module)
        else:
            logger.debug("no exec_module for loader %r", spec.loader)
    return spec


def wrap_finder_find_spec(finder):
    find_spec = getattr(finder, "find_spec", None)
    if find_spec is None:
        logger.debug("no find_spec for finder %r", finder)
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
    Importer.initialize()
    # If we're not enabled, there's no reason to hook the finders.
    if Env.current.enabled:
        logger.debug("sys.metapath: %s", sys.meta_path)
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
    Importer.do_import(module)
