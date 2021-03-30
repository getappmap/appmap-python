from functools import wraps
import time


import appmap


class ClassMethodMixin:
    @classmethod
    def class_method(cls):
        return 'ClassMethodMixin#class_method, cls %s' % (cls.__name__)


class Super:
    def instance_method(self):
        return self.method_not_called_directly()

    def method_not_called_directly(self):
        return 'Super#instance_method'


def wrap_fn(fn):
    @wraps(fn)
    def wrapped_fn(*args, **kwargs):
        try:
            print('calling %s' % (fn.__name__))
            return fn(*args, **kwargs)
        finally:
            print('called %s' % (fn.__name__))

    return wrapped_fn


class ExampleClass(Super, ClassMethodMixin):
    def __repr__(self):
        return 'ExampleClass and %s' % (self.another_method())

    # Include some lines so the line numbers in the expected appmap
    # don't change:
    # <blank>

    def another_method(self):
        return "ExampleClass#another_method"

    def test_exception(self):
        raise Exception('test exception')

    what_time_is_it = time.gmtime

    @appmap.labels('super', 'important')
    def labeled_method(self):
        return 'super important'

    @staticmethod
    @wrap_fn
    def wrapped_static_method():
        return 'wrapped_static_method'

    @classmethod
    @wrap_fn
    def wrapped_class_method(cls):
        return 'wrapped_class_method'

    @wrap_fn
    def wrapped_instance_method(self):
        return 'wrapped_instance_method'

    def instance_with_param(self, p):
        return p

    @staticmethod
    def static_method():
        import yaml
        return yaml.dump('ExampleClass.static_method')

    @staticmethod
    def call_yaml():
        return ExampleClass.dump_yaml('ExampleClass.call_yaml')

    @staticmethod
    def dump_yaml(data):
        import io
        from yaml import Dumper
        stream = io.StringIO()
        dumper = Dumper(stream)
        try:
            dumper.open()
            dumper.represent(data)
            dumper.close()
        finally:
            dumper.dispose()
        return stream.getvalue()
