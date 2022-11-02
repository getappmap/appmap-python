# pylint: disable=missing-module-docstring,missing-function-docstring

from django.utils.functional import SimpleLazyObject

def evaluate():
    raise Exception("lazy object evaluated")

def lazy():
    return SimpleLazyObject(evaluate)
