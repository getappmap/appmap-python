import os
import unittest


def test_hello_world():
    import simple
    os.chdir('/tmp')
    assert simple.Simple().hello_world() == 'Hello world!'


class UnitTestTest(unittest.TestCase):
    def test_hello_unitworld(self):
        import simple
        self.assertEqual(simple.Simple().hello_world(), 'Hello world!')
