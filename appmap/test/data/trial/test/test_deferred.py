import time

from twisted.internet import defer, reactor
from twisted.trial import unittest


class TestDeferred(unittest.TestCase):
    def test_hello_world(self):
        d = defer.Deferred()

        def cb(_):
            self.assertTrue(False)

        d.addCallback(cb)

        reactor.callLater(1, d.callback, None)

        return d

    test_hello_world.todo = "don't fix me"
