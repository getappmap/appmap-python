import types


def is_staticmethod(m):
    return isinstance(m, (staticmethod, types.BuiltinMethodType))


def is_classmethod(m):
    return isinstance(m, (classmethod, types.BuiltinMethodType))


def split_function_name(fn):
    """
    Given a method, return a tuple containing its fully-qualified
    class name and the method name.
    """
    qualname = fn.__qualname__
    if '.' in qualname:
        class_name, fn_name = qualname.rsplit('.', 1)
        class_name = f'{fn.__module__}.{class_name}'
    else:
        class_name = ''
        class_name = fn.__module__
        fn_name = qualname
    return (class_name, fn_name)
