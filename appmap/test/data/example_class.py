

class ClassMethodMixin:
    @classmethod
    def class_method(cls):
        return f'ClassMethodMixin#class_method, cls {cls}'


class Super:
    def instance_method(self):
        return 'Super#instance_method'


class ExampleClass(Super, ClassMethodMixin):
    def __str__(self):
        return f"It's a {self.__module__}.{self.__class__.__qualname__}!"

    @staticmethod
    def static_method():
        return 'ExampleClass#static_method'
