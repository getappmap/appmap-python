from functools import partialmethod

import pytest

import appmap
from appmap._implementation import generation

from .appmap_test_base import AppMapTestBase


class TestLabels(AppMapTestBase):
    @pytest.mark.usefixtures('appmap_enabled')
    def test_labeled_function(self, monkeypatch):

        def check_labels(self, to_dict):
            if self.name == 'labeled_method':
                assert list(self.labels) == ['super', 'important']
            elif self.name == 'instance_method':
                assert not self.labels
            ret = to_dict(self)
            return ret

        monkeypatch.setattr(generation.FuncEntry, 'to_dict',
                            partialmethod(
                                check_labels,
                                generation.FuncEntry.to_dict))

        from example_class import ExampleClass  # pylint: disable=import-error
        rec = appmap.Recording()
        with rec:
            ExampleClass().labeled_method()
            ExampleClass().instance_method()

        generation.dump(rec)
