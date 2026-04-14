from simple import Simple

import appmap


def test_recorded():
    print(Simple().hello_world())


@appmap.noappmap
def test_unrecorded_fn():
    print(Simple().hello_world())


@appmap.noappmap
class TestNotRecorded:
    def test_unrecorded_method(self):
        print(Simple().hello_world())
