import inspect
import types


def is_static_method(m):
    return isinstance(m, (staticmethod, types.BuiltinMethodType))


def is_class_method(m):
    return isinstance(m, (classmethod, types.BuiltinMethodType))


def split_method_name(method):
    """
    Given a method, return a tuple containing its fully-qualified
    class name and the method name.
    """
    qualname = method.__qualname__
    if '.' in qualname:
        class_name, fn_name = qualname.rsplit('.', 1)
        class_name = f'{method.__module__}.{class_name}'
    else:
        class_name = ''
        class_name = method.__module__
        fn_name = qualname
    return (class_name, fn_name)
