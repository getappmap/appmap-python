import unittest

import simple

import appmap


@appmap.noappmap
class TestNoAppMap(unittest.TestCase):
    def test_unrecorded(self):
        print(simple.Simple().hello_world("!"))
