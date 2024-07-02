class Simple:
    def hello(self):
        return "Hello"

    def world(self):
        return "world!"

    def hello_world(self):
        return "%s %s" % (self.hello(), self.world())

    def get_json_unserializable(self):
        import numpy

        return {"zero": numpy.int64(0), "one": numpy.int64(1)}
