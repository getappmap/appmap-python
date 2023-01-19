import pytest

from appmap.wrapt import BoundFunctionWrapper


@pytest.mark.appmap_enabled
@pytest.mark.usefixtures("with_data_dir")
class TestLabels:
    def test_labeled(self, verify_example_appmap):
        def check_labels(self, to_dict):
            if self.name == "labeled_method":
                assert list(self.labels) == ["super", "important"]
            ret = to_dict(self)
            return ret

        verify_example_appmap(check_labels, "labeled_method")

    def test_unlabeled(self, verify_example_appmap):
        def check_labels(self, to_dict):
            if self.name == "instance_method":
                assert not self.labels
            ret = to_dict(self)
            return ret

        verify_example_appmap(check_labels, "instance_method")

    def test_instrumented_for_preset(self, verify_example_appmap):
        def check_labels(*_):
            from http.client import (  # pyright: ignore[reportMissingImports] pylint: disable=import-error,import-outside-toplevel
                HTTPConnection,
            )

            assert isinstance(
                HTTPConnection.request, BoundFunctionWrapper
            ), "HTTPConnection.request should be instrumented"

            assert not isinstance(
                HTTPConnection.getresponse, BoundFunctionWrapper
            ), "HTTPConnection.getresponse should not be instrumented"

        verify_example_appmap(check_labels, "instance_method")
