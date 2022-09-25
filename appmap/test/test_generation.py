from functools import partialmethod

import pytest

import appmap
from appmap._implementation import generation


@pytest.fixture(name="verify_appmap")
def fixture_verify_appmap(monkeypatch):
    def _generate(check_fn, method_name):
        monkeypatch.setattr(
            generation.FuncEntry,
            "to_dict",
            partialmethod(check_fn, generation.FuncEntry.to_dict),
        )

        from example_class import ExampleClass  # pylint: disable=import-error

        rec = appmap.Recording()
        with rec:
            m = getattr(ExampleClass(), method_name)
            m()

        return generation.dump(rec)

    return _generate


@pytest.mark.appmap_enabled
@pytest.mark.usefixtures("with_data_dir")
class TestGeneration:
    def test_labeled(self, verify_appmap):
        def check_labels(self, to_dict):
            if self.name == "labeled_method":
                assert list(self.labels) == ["super", "important"]
            ret = to_dict(self)
            return ret

        verify_appmap(check_labels, "labeled_method")

    def test_unlabeled(self, verify_appmap):
        def check_labels(self, to_dict):
            if self.name == "instance_method":
                assert not self.labels
            ret = to_dict(self)
            return ret

        verify_appmap(check_labels, "instance_method")

    def test_docstring(self, verify_appmap):
        def check_comment(self, to_dict):
            if self.name == "with_docstring":
                assert self.comment == "docstrings can have\nmultiple lines"
            ret = to_dict(self)
            return ret

        verify_appmap(check_comment, "with_docstring")

    def test_comment(self, verify_appmap):
        def check_comment(self, to_dict):
            if self.name == "with_comment":
                assert self.comment == "# comments can have\n# multiple lines\n"
            ret = to_dict(self)
            return ret

        verify_appmap(check_comment, "with_comment")

    def test_none(self, verify_appmap):
        def check_comment(self, to_dict):
            if self.name == "instance_method":
                assert not self.comment
            ret = to_dict(self)
            return ret

        verify_appmap(check_comment, "instance_method")
