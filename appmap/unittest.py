import unittest

from appmap._implementation import testing_framework


original_run = unittest.TestCase.run
session = testing_framework.session('unittest')


def run(self, result=None):
    # There doesn't seem to be a public way to get to the test method name.
    # pylint: disable=protected-access
    with session.record(self.__class__, self._testMethodName):
        original_run(self, result)


unittest.TestCase.run = run


if __name__ == '__main__':
    unittest.main(module=None)
