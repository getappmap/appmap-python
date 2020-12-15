class Src:
    @staticmethod
    def static_method():
        return 'Src#static_method'

    @classmethod
    def class_method(cls):
        return f'Src#class_method, cls {cls}'

    def instance_method(self):
        return 'Src#instance_method'
