# pylint: disable=missing-function-docstring

import sys

from appmap._implementation.importer import Importer, wrap_exec_module


def test_exec_module_protection(monkeypatch):
    """
    Test that recording.wrap_exec_module properly protects against
    rewrapping a wrapped exec_module function.  Repeatedly wrap
    the function, up to the recursion limit, then call the wrapped
    function.  If wrapping protection is working properly, there
    won't be a problem.  If wrapping protection is broken, this
    test will fail with a RecursionError.
    """

    def exec_module():
        pass

    def do_import(*args, **kwargs):  # pylint: disable=unused-argument
        pass

    monkeypatch.setattr(Importer, "do_import", do_import)
    f = exec_module
    for _ in range(sys.getrecursionlimit()):
        f = wrap_exec_module(f)

    f()
    assert True
