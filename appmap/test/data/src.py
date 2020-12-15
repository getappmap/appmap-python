class Src:
    def __str__(self):
        return f"It's a {self.__module__}.{self.__class__.__qualname__}!"

    @staticmethod
    def static_method():
        return 'Src#static_method'

    @classmethod
    def class_method(cls):
        return f'Src#class_method, cls {cls}'

    def instance_method(self):
        return 'Src#instance_method'
