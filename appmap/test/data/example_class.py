

class ClassMethodMixin:
    @classmethod
    def class_method(cls):
        return f'ClassMethodMixin#class_method, cls {cls}'


class Super:
    def instance_method(self):
        return 'Super#instance_method'


class ExampleClass(Super, ClassMethodMixin):
    def __repr__(self):
        return f'ExampleClass and {self.another_method()}'

    @staticmethod
    def static_method():
        return 'ExampleClass.static_method'

    def another_method(self):
        return "ExampleClass#another_method"

    def test_exception(self):
        raise Exception('test exception')
