import time
import yaml

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


class ExampleClass(Super, ClassMethodMixin):
    def __repr__(self):
        return 'ExampleClass and %s' % (self.another_method())

    @staticmethod
    def static_method():
        return yaml.dump('ExampleClass.static_method')

    def another_method(self):
        return "ExampleClass#another_method"

    def test_exception(self):
        raise Exception('test exception')

    what_time_is_it = time.gmtime

    @appmap.labels('super', 'important')
    def labeled_method(self):
        return 'super important'
