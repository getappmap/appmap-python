import pytest

# Copied from pytest-dev/pytest. When recorded, this test case will raise an OutcomeException
# (specifically _pytest.outcomes.Skipped).
def test_skipped(pytester):
    pytester.makeconftest(
        """
        import pytest
        def pytest_ignore_collect():
            pytest.skip("intentional")
    """
    )
    pytester.makepyfile("def test_hello(): pass")
    result = pytester.runpytest_inprocess()
    assert result.ret == pytest.ExitCode.NO_TESTS_COLLECTED
    result.stdout.fnmatch_lines(["*1 skipped*"])
