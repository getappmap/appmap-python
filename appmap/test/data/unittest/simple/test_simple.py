import unittest
from unittest.mock import patch

import appmap.unittest

import simple


class UnitTestTest(unittest.TestCase):
    def test_hello_world(self):
        self.assertEqual(simple.Simple().hello_world('!'), 'Hello world!')

    @patch('simple.Simple.hello_world')
    def test_patch(self, patched_hw):
        simple.Simple().hello_world('!')
        patched_hw.assert_called_once_with('!')

    def test_status_failed(self):
        self.assertTrue(False)

    @unittest.expectedFailure
    def test_status_xfailed(self):
        self.assertTrue(False)

    @unittest.expectedFailure
    def test_status_xsucceeded(self):
        self.assertTrue(True)

    @staticmethod
    def test_status_errored():
        raise RuntimeError('test error')

    def setUp(self):
        simple.Simple().getReady()

    def tearDown(self):
        simple.Simple().finishUp()
