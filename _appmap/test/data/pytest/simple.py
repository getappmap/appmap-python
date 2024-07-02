class Simple:
    def hello(self):
        return "Hello"

    def world(self):
        return "world!"

    def hello_world(self):
        return "%s %s" % (self.hello(), self.world())

    def show_numpy_dict(self):
        from numpy import int64

        d = self.get_numpy_dict({int64(0): "zero", int64(1): "one"})
        print(d)
        return d

    def get_numpy_dict(self, d):
        return d