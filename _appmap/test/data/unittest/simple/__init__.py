class Simple:
    def hello(self):
        return "Hello"

    def world(self):
        return "world"

    def hello_world(self, bang):
        return "%s %s%s" % (self.hello(), self.world(), bang)

    def getReady(self):
        pass

    def finishUp(self):
        pass
