import unittest
from unittest.mock import patch

class UnitTestTest(unittest.TestCase):
    def test_hello_world(self):
        import simple
        self.assertEqual(simple.Simple().hello_world('!'), 'Hello world!')

    @patch('simple.Simple.hello_world')
    def test_patch(self, patched_hw):
        import simple
        simple.Simple().hello_world('!')
        patched_hw.assert_called_once_with('!')
