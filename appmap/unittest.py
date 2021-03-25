import unittest

from appmap._implementation import testing_framework


original_run = unittest.TestCase.run
session = testing_framework.session('unittest')

def get_test_location(cls, method_name):
    from appmap._implementation.utils import get_function_location
    fn = getattr(cls, method_name)
    return get_function_location(fn)


def run(self, result=None):
    method_name = self.id().split('.')[-1]
    # Use the result's location if provided (e.g. by pytest),
    # otherwise cobble one together ourselves.
    if hasattr(result, 'location'):
        location = result.location
    else:
        location = get_test_location(self.__class__, method_name)
    with session.record(
            self.__class__,
            method_name,
            location=location):
        original_run(self, result)


unittest.TestCase.run = run


if __name__ == '__main__':
    unittest.main(module=None)
