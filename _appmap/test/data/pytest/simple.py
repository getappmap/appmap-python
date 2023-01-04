class Simple:
    def hello(self):
        return "Hello"

    def world(self):
        return "world!"

    def hello_world(self):
        return "%s %s" % (self.hello(), self.world())
