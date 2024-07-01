"""A class using all the slightly different ways a function could be defined
and called. Used for testing appmap instrumentation.
"""
# pylint: disable=missing-function-docstring

import time
from functools import lru_cache, wraps

import appmap


class ClassMethodMixin:
    @classmethod
    def class_method(cls):
        return "ClassMethodMixin#class_method, cls %s" % (cls.__name__)


class Super:
    def instance_method(self):
        return self.method_not_called_directly()

    def method_not_called_directly(self):
        return "Super#instance_method"


def wrap_fn(fn):
    @wraps(fn)
    def wrapped_fn(*args, **kwargs):
        try:
            print("calling %s" % (fn.__name__))
            return fn(*args, **kwargs)
        finally:
            print("called %s" % (fn.__name__))

    return wrapped_fn


class ExampleClass(Super, ClassMethodMixin):
    def __repr__(self):
        return "ExampleClass and %s" % (self.another_method())

    # Include some lines so the line numbers in the expected appmap
    # don't change:
    # <blank>

    def another_method(self):
        return "ExampleClass#another_method"

    def test_exception(self):
        raise Exception("test exception")

    what_time_is_it = time.gmtime

    @appmap.labels("super", "important")
    def labeled_method(self):
        return "super important"

    @staticmethod
    @wrap_fn
    def wrapped_static_method():
        return "wrapped_static_method"

    @classmethod
    @wrap_fn
    def wrapped_class_method(cls):
        return "wrapped_class_method"

    @wrap_fn
    def wrapped_instance_method(self):
        return "wrapped_instance_method"

    @staticmethod
    @lru_cache(maxsize=1)
    def static_cached(value):
        return value + 1

    def instance_with_param(self, p):
        return p

    @staticmethod
    def static_method():
        import io

        import yaml  # Formatting is funky to minimize changes to expected appmap

        yaml.Dumper(io.StringIO()).open()
        return "ExampleClass.static_method\n...\n"

    @staticmethod
    def call_yaml():
        return ExampleClass.dump_yaml("ExampleClass.call_yaml")

    @staticmethod
    def dump_yaml(data):
        import yaml

        # Call twice, to make sure both show up in the recording
        yaml.dump(data)
        yaml.dump(data)

    def with_docstring(self):
        """
        docstrings can have
        multiple lines
        """
        return True

    # comments can have
    # multiple lines
    def with_comment(self):
        return True

    def return_self(self):
        return self

    def __init__(self):
        self._read_only = "read only"
        self._fully_accessible = "fully accessible"
        self._undecorated = "undecorated"

    @property
    def read_only(self):
        """Read-only"""
        return self._read_only

    @property
    def fully_accessible(self):
        """Fully-accessible"""
        return self._fully_accessible

    @fully_accessible.setter
    def fully_accessible(self, v):
        self._fully_accessible = v

    @fully_accessible.deleter
    def fully_accessible(self):
        del self._fully_accessible

    def get_undecorated(self):
        return self._undecorated

    def set_undecorated(self, value):
        self._undecorated = value

    def delete_undecorated(self):
        del self._undecorated

    undecorated_property = property(get_undecorated, set_undecorated, delete_undecorated)

    def set_write_only(self, v):
        self._write_only = v

    def del_write_only(self):
        del self._write_only

    write_only = property(None, set_write_only, del_write_only, "Write-only")


def modfunc():
    return "Hello world!"

if __name__ == "__main__":
    ec = ExampleClass()
    ec.fully_accessible = "updated"
    print(ec.fully_accessible)