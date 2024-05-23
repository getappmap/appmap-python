import numpy

zero = numpy.int64(0)
one = numpy.int64(1)

class Simple:
    def hello(self):
        return "Hello"

    def world(self):
        return "world!"

    def get_non_json_serializable(self):
        return { zero: self.hello(), one: self.world() }

    def hello_world(self):
        result = self.get_non_json_serializable()
        return "%s %s" % (result[zero], result[one])
